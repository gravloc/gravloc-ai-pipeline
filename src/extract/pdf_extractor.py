# PDF Extraction Module

"""
PDF extraction using PyMuPDF (native text), pdfplumber (tables), and Tesseract OCR.
"""

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import io


class PDFExtractor:
    """Extract text, tables, and images from PDF documents."""
    
    def __init__(self, use_ocr: bool = True):
        self.use_ocr = use_ocr
        self.ocr_config = {
            'lang': 'eng',
            'config': '--psm 6'
        }
    
    def extract_text_from_page(self, pdf_path: str, page_num: int) -> str:
        """Extract text from a specific page using PyMuPDF."""
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            return page.get_text()
        finally:
            doc.close()
    
    def extract_all_text(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from all pages."""
        doc = fitz.open(pdf_path)
        try:
            pages_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                pages_text.append({
                    'page_number': page_num + 1,
                    'text': page.get_text(),
                    'width': page.rect.width,
                    'height': page.rect.height
                })
            return pages_text
        finally:
            doc.close()
    
    def extract_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF using pdfplumber."""
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table:
                        # Convert to list of dicts using first row as headers
                        headers = table[0]
                        rows = table[1:]
                        
                        table_data = []
                        for row in rows:
                            row_dict = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    row_dict[header] = row[i]
                            table_data.append(row_dict)
                        
                        all_tables.append({
                            'page_number': page_num + 1,
                            'table_index': table_idx + 1,
                            'headers': headers,
                            'rows': table_data,
                            'row_count': len(rows)
                        })
        
        return all_tables
    
    def ocr_image(self, image: Image.Image) -> str:
        """Perform OCR on an image."""
        return pytesseract.image_to_string(image, **self.ocr_config)
    
    def extract_images_from_page(self, pdf_path: str, page_num: int) -> List[Image.Image]:
        """Extract images from a specific page."""
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            images = []
            
            # Get image list from page
            image_list = page.get_images(full=True)
            
            for img_idx, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL Image
                    image = Image.open(io.BytesIO(image_bytes))
                    images.append(image)
                except Exception as e:
                    # Skip problematic images
                    continue
            
            return images
        finally:
            doc.close()
    
    def extract_tables_with_ocr(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables with fallback OCR for scanned PDFs."""
        tables = self.extract_tables(pdf_path)
        
        # If no tables found, try OCR-based extraction
        if not tables and self.use_ocr:
            tables = self._ocr_table_extraction(pdf_path)
        
        return tables
    
    def _ocr_table_extraction(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using OCR on scanned PDFs."""
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Get page image for OCR
                page_image = page.to_image(resolution=300)
                
                # Perform OCR
                ocr_text = self.ocr_image(page_image.original)
                
                # Simple table detection from OCR text
                # This is a basic implementation - can be enhanced
                lines = ocr_text.split('\n')
                
                # Look for table-like patterns
                table_data = []
                for line in lines:
                    # Split by common delimiters
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) > 1:
                        table_data.append(parts)
                
                if table_data:
                    headers = table_data[0] if table_data else []
                    rows = table_data[1:] if len(table_data) > 1 else []
                    
                    tables.append({
                        'page_number': page_num + 1,
                        'table_index': 1,
                        'headers': headers,
                        'rows': [{'col_' + str(i): row[i] if i < len(row) else None 
                                 for i in range(len(headers))} for row in rows],
                        'row_count': len(rows),
                        'source': 'ocr'
                    })
        
        return tables
    
    def extract_document(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all content from a PDF document."""
        pages_text = self.extract_all_text(pdf_path)
        tables = self.extract_tables(pdf_path)
        
        return {
            'source_file': Path(pdf_path).name,
            'pages': pages_text,
            'tables': tables,
            'page_count': len(pages_text),
            'table_count': len(tables)
        }


def extract_datasheet(pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Extract datasheet content and save to output directory if specified."""
    extractor = PDFExtractor(use_ocr=True)
    result = extractor.extract_document(pdf_path)
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save extracted content
        import json
        output_file = output_path / f"{Path(pdf_path).stem}_extracted.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        result['output_file'] = str(output_file)
    
    return result