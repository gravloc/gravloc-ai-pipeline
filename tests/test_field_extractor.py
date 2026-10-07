"""
Tests for field extractor rules.
"""

import pytest
import sys
from pathlib import Path as PathObj

# Add src to path for imports
sys.path.insert(0, str(PathObj(__file__).parent.parent / 'src'))

from extract.field_extractor import FieldExtractor


class TestFieldExtractorRules:
    """Test regex extraction rules."""
    
    @pytest.fixture
    def extractor(self):
        return FieldExtractor()
    
    def test_part_number_patterns(self, extractor):
        """Test various part number formats."""
        test_cases = [
            ("Part No: ABC-123", "ABC-123"),
            ("P/N: XYZ-456-789", "XYZ-456-789"),
            ("SKU: TEST-100", "TEST-100"),
            ("MPN: IC-555", "IC-555"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'part_number')
            assert result == expected, f"Failed for: {text}"
    
    def test_manufacturer_patterns(self, extractor):
        """Test manufacturer extraction."""
        text = "Manufacturer: Analog Devices Inc."
        result = extractor.extract_field(text, 'manufacturer')
        
        assert "Analog Devices" in result
    
    def test_tid_patterns(self, extractor):
        """Test TID extraction with various units."""
        test_cases = [
            ("TID: 100 krad", "100 krad"),
            ("Total Dose: 50 Mrad", "50 Mrad"),
            ("Radiation Dose: 10000 rad", "10000 rad"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'tid_total_dose')
            assert result == expected, f"Failed for: {text}"
    
    def test_temperature_range(self, extractor):
        """Test temperature range extraction."""
        test_cases = [
            ("Operating Temp: -55 to 125 °C", {'min': -55, 'max': 125}),
            ("T_op: -40 to 85 C", {'min': -40, 'max': 85}),
            ("Junction Temp: 0 to 70 °C", {'min': 0, 'max': 70}),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'operating_temp_range')
            assert result == expected, f"Failed for: {text}"
    
    def test_package_patterns(self, extractor):
        """Test package type extraction."""
        test_cases = [
            ("Package Type: DIP", "DIP"),
            ("Package: SOIC", "SOIC"),
            ("Style: QFN", "QFN"),
            ("Package: TO-220", "TO-220"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'package_type')
            assert result == expected, f"Failed for: {text}"
    
    def test_pin_count(self, extractor):
        """Test pin count extraction."""
        test_cases = [
            ("No. of Pins: 8", 8),
            ("Pins: 16", 16),
            ("Pin Count: 32", 32),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'pin_count')
            assert result == expected, f"Failed for: {text}"
    
    def test_lead_time(self, extractor):
        """Test lead time extraction."""
        test_cases = [
            ("Lead Time: 4 weeks", "4 weeks"),
            ("Ship Time: 2 days", "2 days"),
            ("Delivery: 6 weeks", "6 weeks"),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'lead_time')
            assert result == expected, f"Failed for: {text}"
    
    def test_moq(self, extractor):
        """Test MOQ extraction."""
        test_cases = [
            ("MOQ: 100", 100),
            ("Minimum Order Quantity: 500", 500),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'moq')
            assert result == expected, f"Failed for: {text}"
    
    def test_trl(self, extractor):
        """Test TRL extraction."""
        test_cases = [
            ("TRL: 5", 5),
            ("Technology Readiness Level: 9", 9),
        ]
        
        for text, expected in test_cases:
            result = extractor.extract_field(text, 'trl')
            assert result == expected, f"Failed for: {text}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])