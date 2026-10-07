"""
Tests for datasheet pipeline.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import sys
from pathlib import Path as PathObj

# Add src to path for imports
sys.path.insert(0, str(PathObj(__file__).parent.parent / 'src'))

from pipeline.datasheet_pipeline import DatasheetPipeline, run_pipeline
from schema.component import Component, ComponentCategory


class TestDatasheetPipeline:
    """Test the complete datasheet extraction pipeline."""
    
    @pytest.fixture
    def pipeline(self, tmp_path):
        return DatasheetPipeline(output_dir=str(tmp_path))
    
    def test_init(self, pipeline, tmp_path):
        """Test pipeline initialization."""
        assert pipeline.output_dir == Path(str(tmp_path))
        assert pipeline.pdf_extractor is not None
        assert pipeline.field_extractor is not None
    
    def test_process_single_pdf(self, pipeline, tmp_path):
        """Test processing a single PDF."""
        # Create a dummy PDF file
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_text("dummy pdf placeholder")
        
        # Mock the extraction methods
        with patch.object(pipeline.pdf_extractor, 'extract_document') as mock_extract:
            mock_extract.return_value = {
                'source_file': 'test.pdf',
                'pages': [{'text': 'Part No: TEST-123', 'page_number': 1}],
                'tables': [],
                'page_count': 1,
                'table_count': 0
            }
            
            result = pipeline.process_single_pdf(str(dummy_pdf))
            
            assert result is not None
            assert isinstance(result.component, Component)
    
    def test_build_component(self, pipeline):
        """Test component building from extracted fields."""
        extract_result = {
            'source_file': 'test.pdf',
            'pages': [{'text': 'Part No: TEST-123', 'page_number': 1}],
        }
        
        fields = {
            'part_number': {'value': 'TEST-123', 'source_page': 1},
            'manufacturer': {'value': 'Test Corp', 'source_page': 1},
            'operating_temp_range': {'value': {'min': -55, 'max': 125}, 'source_page': 1},
        }
        
        component = pipeline._build_component(extract_result, fields)
        
        assert component.part_number == "TEST-123"
        assert component.manufacturer == "Test Corp"
        assert component.thermal.operating_temp_range.min == -55
    
    def test_calculate_confidence(self, pipeline):
        """Test confidence score calculation."""
        # High confidence component
        component = Component(
            part_number="TEST-123",
            manufacturer="Test Corp",
            radiation=Mock()
        )
        
        confidence = pipeline._calculate_confidence(component)
        assert confidence >= 0.8
    
    def test_save_result(self, pipeline, tmp_path):
        """Test saving extraction results."""
        component = Component(
            part_number="TEST-123",
            source_document="test.pdf"
        )
        
        result = Mock()
        result.component = component
        result.raw_text_pages = ["Page 1"]
        result.tables = []
        result.confidence_by_field = {"part_number": 0.9}
        result.issues = []
        result.review_required = False
        
        output_file = tmp_path / "test_extracted.json"
        pipeline._save_result(result, output_file)
        
        assert output_file.exists()
        
        # Verify JSON content
        with open(output_file) as f:
            data = json.load(f)
        
        assert data['component']['part_number'] == "TEST-123"


class TestPipelineIntegration:
    """Integration tests for the pipeline."""
    
    def test_run_pipeline_on_directory(self, tmp_path):
        """Test processing multiple PDFs in a directory."""
        # Create test directory with dummy PDF
        test_dir = tmp_path / "input"
        test_dir.mkdir()
        
        # Create a dummy PDF file (will fail with real PDF extraction but OK for structure test)
        (test_dir / "test1.pdf").write_text("dummy")
        
        # Pipeline structure test only
        pipeline = DatasheetPipeline(output_dir=str(tmp_path / "output"))
        
        assert pipeline is not None
        assert hasattr(pipeline, 'process_directory')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])