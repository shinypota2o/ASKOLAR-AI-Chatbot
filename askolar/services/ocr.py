"""OCR Service (Adapter pattern, System Design v0.3).

OCRAdapter gives the rest of ASKOLAR one interface: extract(file) -> candidate fields.
The OCR tool itself (here: local Tesseract) sits behind a small engine class, so the tool
can be changed without touching the Conversation Manager.

Privacy (SRS NFR-07, RA 10173): the uploaded image is written to a private temporary
file, read once, and deleted immediately in a finally-block, even if OCR fails.
Nothing is logged. Extracted values are only CANDIDATES until the student confirms them.
"""
import os
import re
import shutil
import tempfile
from pathlib import Path

from PIL import Image

SUPPORTED_TYPES = {'image/png': '.png', 'image/jpeg': '.jpg'}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SUPPORTED_DOCUMENT = 'class card, grade report or certificate of grades (PNG or JPG photo or scan)'
DEFAULT_WINDOWS_PATHS = [
    r'D:\Programming\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
]


class OCRError(Exception):
    """A problem the student should see; manual entry is always the fallback."""


class TesseractEngine:
    """Adaptee: calls the local Tesseract program through pytesseract."""
    name = 'tesseract'

    def __init__(self, cmd=None):
        import pytesseract  # imported here so the app still starts without OCR installed
        self.pytesseract = pytesseract
        cmd = cmd or os.environ.get('TESSERACT_CMD') or shutil.which('tesseract')
        if not cmd:
            cmd = next((p for p in DEFAULT_WINDOWS_PATHS if Path(p).exists()), None)
        if not cmd:
            raise OCRError('Tesseract is not installed on this computer.')
        pytesseract.pytesseract.tesseract_cmd = cmd

    def image_to_text(self, path):
        """Read the card twice: once with table lines removed, once cropped and enlarged.

        Both texts are returned; parse_fields() takes the first value it finds.
        """
        texts = []
        cleaned = remove_table_lines(path)
        if cleaned is not None:
            texts.append(self.pytesseract.image_to_string(cleaned, lang='eng', config='--psm 6', timeout=30))
        with Image.open(path) as img:
            texts.append(self.pytesseract.image_to_string(prepare_image(img), lang='eng', config='--psm 6', timeout=30))
        return '\n'.join(texts)


def remove_table_lines(path):
    """Remove the table borders of a class card so the totals row can be read (needs OpenCV)."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        return None
    ink = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 15)
    horizontal = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (60, 1)))
    vertical = cv2.morphologyEx(ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))
    lines = cv2.dilate(horizontal | vertical, np.ones((3, 3), np.uint8))
    return Image.fromarray(255 - cv2.bitwise_and(ink, cv2.bitwise_not(lines)))


def prepare_image(img):
    """Crop the white card out of a phone photo, enlarge it and raise contrast.

    PGPC class cards are often photographed on a patterned table; the background
    confuses OCR, so only the bright card area is kept.
    """
    from PIL import ImageOps
    img = ImageOps.exif_transpose(img).convert('L')
    try:
        import numpy as np
        pixels = np.asarray(img) > 200
        rows = np.where(pixels.mean(axis=1) > 0.45)[0]
        cols = np.where(pixels.mean(axis=0) > 0.35)[0]
        if len(rows) and len(cols) and (rows[-1] - rows[0]) > img.height * 0.2 and (cols[-1] - cols[0]) > img.width * 0.2:
            img = img.crop((int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1])))
    except ImportError:
        pass
    if img.width < 2400:  # small photos read better when enlarged
        scale = 2400 / img.width
        img = img.resize((int(img.width * scale), int(img.height * scale)))
    return ImageOps.autocontrast(img)


# ---------- field extraction from OCR text ----------
def parse_fields(text):
    """Find candidate GWA and total units in a class card or grade report.

    Year level is not taken from the document: an old class card shows the year level
    of that semester, not the student's current one.
    """
    t = text.lower().replace(',', '.')
    fields = {}
    sep = r'[\s:=|\-_\]\[]*'

    m = re.search(r'(?:gwa|general\s+weighted\s+average|weighted\s+average|gen\.?\s*ave(?:rage)?)' + sep + r'([1-5]\.\d{1,4})', t)
    if m:
        fields['gwa'] = round(float(m.group(1)), 2)
    else:
        # A handwritten "1." is often read as "[" or "|" (e.g., "GWA= [35" for 1.35); the student confirms it.
        m = re.search(r'gwa\s*[=:]?\s*[\[|l]\s*\.?\s*(\d{2})\b', t)
        if m:
            fields['gwa'] = round(float('1.' + m.group(1)), 2)

    m = re.search(r'(?:total\s*(?:no\.?\s*of\s*)?units(?:\s*enrolled)?|units\s*enrolled)[\s’\'.:=|\-_\]\[]*(\d{1,2})(?:\.\d+)?\b', t)
    if m:
        fields['units'] = int(m.group(1))
    return fields


class OCRAdapter:
    """Target interface used by the rest of ASKOLAR."""

    def __init__(self, engine=None, temp_dir=None):
        self._engine = engine
        self.temp_dir = temp_dir  # None = system temp folder

    @property
    def engine(self):
        if self._engine is None:
            self._engine = TesseractEngine()
        return self._engine

    def extract(self, data, content_type):
        """Return {'fields': {...}, 'text_length': n}. The file never stays on disk."""
        if content_type not in SUPPORTED_TYPES:
            raise OCRError('Only PNG or JPG images of a grade report are supported.')
        if not data or len(data) > MAX_UPLOAD_BYTES:
            raise OCRError('The image must be smaller than 5 MB.')
        fd, path = tempfile.mkstemp(suffix=SUPPORTED_TYPES[content_type], dir=self.temp_dir)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            try:
                from PIL import Image
                with Image.open(path) as img:
                    img.verify()
            except Exception:
                raise OCRError('This file is not a readable image.')
            try:
                text = self.engine.image_to_text(path)
            except OCRError:
                raise
            except Exception:
                raise OCRError('The document could not be read. Please type your answers instead.')
            return {'fields': parse_fields(text), 'text_length': len(text)}
        finally:
            try:
                os.remove(path)  # delete right after processing (NFR-07)
            except FileNotFoundError:
                pass
