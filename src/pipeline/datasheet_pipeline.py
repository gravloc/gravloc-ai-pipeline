"""
Pipeline for processing datasheets and extracting component data.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from extract.pdf_extractor import PDFExtractor
from extract.field_extractor import FieldExtractor
from schema.component import Component, ExtractionResult, ComponentCategory
import json


class DatasheetPipeline:
    """Complete datasheet extraction pipeline."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else None
        self.pdf_extractor = PDFExtractor(use_ocr=True)
        self.field_extractor = FieldExtractor()
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_single_pdf(self, pdf_path: str) -> ExtractionResult:
        """Process a single PDF datasheet."""
        # Extract content
        extract_result = self.pdf_extractor.extract_document(pdf_path)
        
        # Extract fields from all pages
        pages_text = [page['text'] for page in extract_result['pages']]
        fields = self.field_extractor.extract_from_document(pages_text)
        
        # Build component model
        component = self._build_component(extract_result, fields)
        
        # Calculate confidence
        confidence_score = self._calculate_confidence(component)
        
        # Check if review required
        review_required = confidence_score < 0.7
        
        return ExtractionResult(
            component=component,
            raw_text_pages=pages_text,
            tables=extract_result['tables'],
            confidence_by_field=self._get_field_confidence(fields),
            issues=self._get_issues(fields),
            review_required=review_required
        )
    
    def _build_component(self, extract_result: Dict, fields: Dict) -> Component:
        """Build component model from extracted data."""
        component_data = {
            'part_number': fields.get('part_number', {}).get('value'),
            'manufacturer': fields.get('manufacturer', {}).get('value'),
            'source_document': Path(extract_result['source_file']).name,
            'extracted_at': datetime.now(timezone.utc).isoformat(),
            'extraction_version': '1.0.0',
        }
        
        # Process radiation fields
        tid = fields.get('tid_total_dose', {}).get('value')
        if tid:
            component_data['radiation'] = {'tid_total_dose': tid}
        
        sel = fields.get('sel_threshold', {}).get('value')
        if sel:
            if 'radiation' not in component_data:
                component_data['radiation'] = {}
            component_data['radiation']['sel_threshold'] = sel
        
        seu = fields.get('seu_threshold', {}).get('value')
        if seu:
            if 'radiation' not in component_data:
                component_data['radiation'] = {}
            component_data['radiation']['seu_threshold'] = seu
        
        # Process package fields
        package_type = fields.get('package_type', {}).get('value')
        pin_count = fields.get('pin_count', {}).get('value')
        
        package_fields = {}
        if package_type:
            package_fields['type'] = package_type
        if pin_count:
            package_fields['pin_count'] = pin_count
        
        if package_fields:
            component_data['package'] = package_fields
        
        # Process temperature fields
        op_temp = fields.get('operating_temp_range', {}).get('value')
        stor_temp = fields.get('storage_temp_range', {}).get('value')
        
        temp_fields = {}
        if op_temp:
            temp_fields['operating_temp_range'] = op_temp
        if stor_temp:
            temp_fields['storage_temp_range'] = stor_temp
        
        if temp_fields:
            component_data['thermal'] = temp_fields
        
        # Process other fields
        lead_time = fields.get('lead_time', {}).get('value')
        if lead_time:
            component_data['lead_time'] = lead_time
        
        moq = fields.get('moq', {}).get('value')
        if moq:
            component_data['moq'] = moq
        
        qualification = fields.get('qualification_standards', {}).get('value')
        if qualification:
            component_data['qualification_standards'] = [qualification]
        
        trl = fields.get('trl', {}).get('value')
        if trl:
            component_data['trl'] = trl
        
        return Component(**{k: v for k, v in component_data.items() if v is not None})
    
    def _calculate_confidence(self, component: Component) -> float:
        """Calculate overall confidence score."""
        if not component.part_number:
            return 0.3
        
        confidence = 0.7  # Base confidence for basic extraction
        
        # Bonus for radiation data
        if component.radiation:
            confidence += 0.15
        
        # Bonus for package data
        if component.package and (component.package.type or component.package.pin_count):
            confidence += 0.1
        
        # Penalty for missing critical fields
        if not component.manufacturer:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def _get_field_confidence(self, fields: Dict) -> Dict[str, float]:
        """Get confidence scores per field."""
        confidence = {}
        
        for field, data in fields.items():
            value = data.get('value')
            if value:
                confidence[field] = 0.85 if isinstance(value, str) else 0.9
            else:
                confidence[field] = 0.0
        
        return confidence
    
    def _get_issues(self, fields: Dict) -> List[Dict[str, str]]:
        """Get list of extraction issues."""
        issues = []
        
        for field, data in fields.items():
            if not data.get('value'):
                issues.append({
                    'field': field,
                    'issue': 'Value not found in document',
                    'severity': 'warning'
                })
        
        return issues
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None) -> List[ExtractionResult]:
        """Process all PDFs in a directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else self.output_dir
        
        results = []
        pdf_files = list(input_path.glob('*.pdf'))
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            result = self.process_single_pdf(str(pdf_file))
            results.append(result)
            
            # Save individual result
            if output_path:
                output_file = output_path / f"{pdf_file.stem}_extracted.json"
                self._save_result(result, output_file)
        
        return results
    
    def _save_result(self, result: ExtractionResult, output_file: Path):
        """Save extraction result to JSON file."""
        output_data = {
            'component': result.component.model_dump(),
            'raw_text_pages': result.raw_text_pages,
            'tables': result.tables,
            'confidence_by_field': result.confidence_by_field,
            'issues': result.issues,
            'review_required': result.review_required,
            'schema_version': '1.0.0'
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)


def run_pipeline(input_path: str, output_dir: Optional[str] = None):
    """Run the datasheet extraction pipeline."""
    pipeline = DatasheetPipeline(output_dir=output_dir)
    
    input_path = Path(input_path)
    
    if input_path.is_file():
        # Single file
        result = pipeline.process_single_pdf(str(input_path))
        print(f"Processed: {input_path.name}")
        return result
    else:
        # Directory
        results = pipeline.process_directory(str(input_path), output_dir)
        print(f"Processed {len(results)} files")
        return results