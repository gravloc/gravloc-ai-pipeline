"""
Field extraction rules and regex patterns for datasheet parsing.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ExtractionRule:
    """Rule for extracting a specific field from text."""
    field_name: str
    patterns: List[str]
    unit_patterns: Optional[List[str]] = None
    value_transform: Optional[str] = None  # 'int', 'float', 'lower', 'upper'
    priority: int = 1  # Higher priority rules are tried first


class FieldExtractor:
    """Extract component fields using regex patterns and rules."""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict[str, List[ExtractionRule]]:
        """Initialize extraction rules for all fields."""
        return {
            'part_number': [
                ExtractionRule(
                    field_name='part_number',
                    patterns=[
                        r'(?:Part\s*No(?:\.|\.?:)?|P/N)\s*[:\-]?\s*([A-Z0-9\-_]+)',
                        r'(?:SKU|MPN)\s*[:\-]?\s*([A-Z0-9\-_]+)',
                    ]
                ),
            ],
            'manufacturer': [
                ExtractionRule(
                    field_name='manufacturer',
                    patterns=[
                        r'(?:Manufacturer|Brand|Vendor)\s*[:\-]?\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,)',
                        r'(?:Made\s*by|Distributed\s*by)\s*([A-Z][a-zA-Z\s]+?)(?:\n|$)',
                    ]
                ),
            ],
            'tid_total_dose': [
                ExtractionRule(
                    field_name='tid_total_dose',
                    patterns=[
                        r'Total\s*Ionizing\s*Dose\s*[:\-]?\s*([\d\.]+\s*(?:krad|Mrad|rad))',
                        r'TID\s*[:\-]?\s*([\d\.]+\s*(?:krad|Mrad|rad))',
                        r'Total\s*Dose\s*[:\-]?\s*([\d\.]+\s*(?:krad|Mrad|rad))',
                    ],
                    unit_patterns=[r'krad', r'Mrad', r'rad']
                ),
            ],
            'sel_threshold': [
                ExtractionRule(
                    field_name='sel_threshold',
                    patterns=[
                        r'SE\s*Latchup\s*[:\-]?\s*([\d\.]+)\s*(MeV·cm²/Mg|MeV·cm²)',
                        r'SEL\s*[:\-]?\s*([\d\.]+)\s*(MeV·cm²/Mg|MeV·cm²)',
                        r'LET\s*threshold\s*[:\-]?\s*([\d\.]+)\s*(MeV·cm²/Mg|MeV·cm²)',
                    ],
                    unit_patterns=[r'MeV·cm²/Mg', r'MeV·cm²']
                ),
            ],
            'seu_threshold': [
                ExtractionRule(
                    field_name='seu_threshold',
                    patterns=[
                        r'SE\s*Upset\s*[:\-]?\s*([\d\.]+)\s*(MeV·cm²/Mg|MeV·cm²)',
                        r'SEU\s*[:\-]?\s*([\d\.]+)\s*(MeV·cm²/Mg|MeV·cm²)',
                    ],
                    unit_patterns=[r'MeV·cm²/Mg', r'MeV·cm²']
                ),
            ],
            'operating_temp_range': [
                ExtractionRule(
                    field_name='operating_temp_range',
                    patterns=[
                        r'Operating\s*Temp(?:\s*Range)?\s*[:\-]?\s*([\-]?\d+)\s*to\s*([\-]?\d+)\s*°?C',
                        r'T_op\s*[:\-]?\s*([\-]?\d+)\s*to\s*([\-]?\d+)\s*°?C',
                        r'Junction\s*Temp(?:\s*Range)?\s*[:\-]?\s*([\-]?\d+)\s*to\s*([\-]?\d+)\s*°?C',
                    ],
                    value_transform='range'
                ),
            ],
            'storage_temp_range': [
                ExtractionRule(
                    field_name='storage_temp_range',
                    patterns=[
                        r'Storage\s*Temperature\s*[:\-]?\s*([\-]?\d+)\s*to\s*([\-]?\d+)\s*°?C',
                        r'T_stor\s*[:\-]?\s*([\-]?\d+)\s*to\s*([\-]?\d+)\s*°?C',
                    ],
                    value_transform='range'
                ),
            ],
            'package_type': [
                ExtractionRule(
                    field_name='package_type',
                    patterns=[
                        r'Package\s*Type\s*[:\-]?\s*(DIP|SOIC|QFN|BGA|SOT|TO-[\d]+|LGA|WLCSP)',
                        r'(?:Package|Style)\s*[:\-]?\s*(DIP|SOIC|QFN|BGA|SOT|TO-[\d]+|LGA|WLCSP)',
                    ]
                ),
            ],
            'pin_count': [
                ExtractionRule(
                    field_name='pin_count',
                    patterns=[
                        r'(?:No\.?|Number)\s*of\s*Pins\s*[:\-]?\s*(\d+)',
                        r'Pins\s*[:\-]?\s*(\d+)',
                        r'Pin\s*Count\s*[:\-]?\s*(\d+)',
                    ],
                    value_transform='int'
                ),
            ],
            'lead_time': [
                ExtractionRule(
                    field_name='lead_time',
                    patterns=[
                        r'Lead\s*Time\s*[:\-]?\s*(\d+\s*(?:weeks?|days?|months?))',
                        r'Ship\s*Time\s*[:\-]?\s*(\d+\s*(?:weeks?|days?|months?))',
                        r'Delivery\s*[:\-]?\s*(\d+\s*(?:weeks?|days?|months?))',
                    ]
                ),
            ],
            'moq': [
                ExtractionRule(
                    field_name='moq',
                    patterns=[
                        r'MOQ\s*[:\-]?\s*(\d+)',
                        r'Minimum\s*Order\s*Quantity\s*[:\-]?\s*(\d+)',
                    ],
                    value_transform='int'
                ),
            ],
            'qualification_standards': [
                ExtractionRule(
                    field_name='qualification_standards',
                    patterns=[
                        r'Qualification\s*[:\-]?\s*(MIL-STD-\d+|ECSS-Q-ST-\d+C|NASA|JEDEC|AEC-Q\d+)',
                        r'Compliance\s*[:\-]?\s*(MIL-STD-\d+|ECSS|NASA|AEC-Q\d+)',
                    ]
                ),
            ],
            'trl': [
                ExtractionRule(
                    field_name='trl',
                    patterns=[
                        r'TRL\s*[:\-]?\s*(\d)',
                        r'Technology\s*Readiness\s*Level\s*[:\-]?\s*(\d)',
                    ],
                    value_transform='int'
                ),
            ],
        }
    
    def extract_field(self, text: str, field_name: str) -> Optional[Any]:
        """Extract a specific field from text using rules."""
        if field_name not in self.rules:
            return None
        
        for rule in self.rules[field_name]:
            for pattern in rule.patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Get the first captured group (the value) if available
                    if match.groups():
                        value = self._apply_transform(match.group(1), rule.value_transform)
                    else:
                        value = self._apply_transform(match.group(0), rule.value_transform)
                    if value:
                        return value
        
        return None
    
    def _apply_transform(self, value: str, transform: Optional[str]) -> Any:
        """Apply transformation to extracted value."""
        if not transform:
            return value
        
        if transform == 'int':
            try:
                return int(re.search(r'\d+', value).group())
            except (AttributeError, ValueError):
                return None
        
        if transform == 'float':
            try:
                return float(re.search(r'[\d\.]+', value).group())
            except (AttributeError, ValueError):
                return None
        
        if transform == 'range':
            # Extract min and max from range pattern
            match = re.search(r'([\-]?\d+)\s*to\s*([\-]?\d+)', value, re.IGNORECASE)
            if match:
                return {'min': int(match.group(1)), 'max': int(match.group(2))}
            return None
        
        if transform == 'lower':
            return value.lower()
        
        if transform == 'upper':
            return value.upper()
        
        return value
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """Extract all supported fields from text."""
        result = {}
        
        for field_name in self.rules:
            value = self.extract_field(text, field_name)
            if value:
                result[field_name] = value
        
        return result
    
    def extract_from_page(self, page_text: str) -> Dict[str, Any]:
        """Extract fields from a single page of text."""
        return self.extract_all(page_text)
    
    def extract_from_document(self, pages_text: List[str]) -> Dict[str, Any]:
        """Extract fields from all pages of a document."""
        result = {}
        
        for page_num, page_text in enumerate(pages_text):
            page_result = self.extract_from_page(page_text)
            
            # Merge results (prefer earlier pages for critical fields)
            for field, value in page_result.items():
                if field not in result:
                    result[field] = {
                        'value': value,
                        'source_page': page_num + 1
                    }
                elif isinstance(result[field], dict):
                    # Already has source info, just update value if not set
                    if result[field].get('value') is None:
                        result[field]['value'] = value
                        result[field]['source_page'] = page_num + 1
        
        return result