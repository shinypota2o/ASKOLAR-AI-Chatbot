class OCRAdapter:
    """Reserved interface. No OCR engine or upload processing is implemented yet."""
    def extract(self):
        return {'error':'ocr_not_implemented',
                'text':'OCR is not implemented in this first milestone. Use manual entry. No file is retained.'}
