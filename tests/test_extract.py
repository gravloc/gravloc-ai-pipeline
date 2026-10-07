"""
Tests for PDF extraction module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys
from pathlib import Path as PathObj

# Add src to path for imports
sys.path.insert(0, str(PathObj(__file__).parent.parent / 'src'))

from extract.pdf_extractor import PDFExtractor


class TestPDFExtractor:
    """Test PDF extraction functionality."""
    
    @pytest.fixture
    def extractor(self):
        return PDFExtractor(use_ocr=False)
    
    def test_init(self, extractor):
        """Test extractor initialization."""
        assert extractor.use_ocr is False
    
    @patch('fitz.open')
    def test_extract_text_from_page(self, mock_fitz_open):
        """Test text extraction from a single page."""
        # Mock document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Test text content"
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz_open.return_value = mock_doc
        
        extractor = PDFExtractor()
        text = extractor.extract_text_from_page("test.pdf", 0)
        
        assert text == "Test text content"
        mock_fitz_open.assert_called_once()
    
    def test_extract_all_text(self):
        """Test extraction of text from all pages."""
        extractor = PDFExtractor()
        
        # This test would require a real PDF file
        # For now, just verify the method exists and is callable
        assert hasattr(extractor, 'extract_all_text')
        assert callable(getattr(extractor, 'extract_all_text'))
    
    def test_extract_tables(self):
        """Test table extraction."""
        extractor = PDFExtractor()
        
        # Verify method exists
        assert hasattr(extractor, 'extract_tables')
        assert callable(getattr(extractor, 'extract_tables'))
    
    def test_extract_document(self):
        """Test complete document extraction."""
        extractor = PDFExtractor()
        
        # Verify method exists
        assert hasattr(extractor, 'extract_document')
        assert callable(getattr(extractor, 'extract_document'))


class TestFieldExtractor:
    """Test field extraction using regex patterns."""
    
    @pytest.fixture
    def extractor(self):
        from extract.field_extractor import FieldExtractor
        return FieldExtractor()
    
    def test_extract_part_number(self, extractor):
        """Test part number extraction."""
        text = "Part No: ABC-12345"
        result = extractor.extract_field(text, 'part_number')
        
        assert result == "ABC-12345"
    
    def test_extract_manufacturer(self, extractor):
        """Test manufacturer extraction."""
        text = "Manufacturer: Texas Instruments"
        result = extractor.extract_field(text, 'manufacturer')
        
        assert result == "Texas Instruments"
    
    def test_extract_tid(self, extractor):
        """Test TID (Total Ionizing Dose) extraction."""
        text = "Total Ionizing Dose: 100 krad"
        result = extractor.extract_field(text, 'tid_total_dose')
        
        assert result == "100 krad"
    
    def test_extract_temperature_range(self, extractor):
        """Test temperature range extraction."""
        text = "Operating Temperature: -55 to 125 °C"
        result = extractor.extract_field(text, 'operating_temp_range')
        
        assert result == {'min': -55, 'max': 125}
    
    def test_extract_package_type(self, extractor):
        """Test package type extraction."""
        text = "Package Type: QFN"
        result = extractor.extract_field(text, 'package_type')
        
        assert result == "QFN"
    
    def test_extract_pin_count(self, extractor):
        """Test pin count extraction."""
        text = "Number of Pins: 32"
        result = extractor.extract_field(text, 'pin_count')
        
        assert result == 32


class TestFieldExtractorIntegration:
    """Integration tests for field extraction."""
    
    def test_extract_from_document(self):
        """Test extraction from multiple pages."""
        from extract.field_extractor import FieldExtractor
        
        extractor = FieldExtractor()
        
        pages = [
            "Part No: ABC-12345\nManufacturer: Test Corp",
            "Operating Temperature: -40 to 85 °C\nPackage: SOIC"
        ]
        
        result = extractor.extract_from_document(pages)
        
        assert 'part_number' in result
        assert 'manufacturer' in result
        assert 'operating_temp_range' in result
        assert 'package_type' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])