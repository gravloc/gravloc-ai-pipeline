"""
Tests for component schema models.
"""

import pytest
from datetime import datetime, timezone
import sys
from pathlib import Path as PathObj

# Add src to path for imports
sys.path.insert(0, str(PathObj(__file__).parent.parent / 'src'))

from schema.component import (
    Component, Parameter, Tolerance, RadiationSpec, 
    PackageSpec, ThermalSpec, ComponentCategory, ExtractionResult
)


class TestComponentSchema:
    """Test component schema models."""
    
    def test_create_component(self):
        """Test basic component creation."""
        component = Component(
            part_number="LMC6482AIN",
            manufacturer="Texas Instruments",
            category=ComponentCategory.ACTIVE
        )
        
        assert component.part_number == "LMC6482AIN"
        assert component.manufacturer == "Texas Instruments"
        assert component.category == ComponentCategory.ACTIVE
    
    def test_component_with_parameters(self):
        """Test component with electrical parameters."""
        component = Component(
            part_number="LMC6482AIN",
            parameters=[
                Parameter(
                    name="Supply Voltage",
                    value=15,
                    unit="V",
                    tolerance=Tolerance(min=12, max=18, nominal=15)
                ),
                Parameter(
                    name="Operating Temperature",
                    value=25,
                    unit="°C",
                    condition="Ambient"
                )
            ]
        )
        
        assert len(component.parameters) == 2
        assert component.parameters[0].name == "Supply Voltage"
    
    def test_component_with_radiation(self):
        """Test component with radiation specifications."""
        component = Component(
            part_number="RAD-100",
            radiation=RadiationSpec(
                tid_total_dose=Tolerance(min=100, max=100, unit="krad"),
                sel_threshold=35,
                test_standard="MIL-STD-883"
            )
        )
        
        assert component.radiation.tid_total_dose.min == 100
        assert component.radiation.test_standard == "MIL-STD-883"
    
    def test_component_with_package(self):
        """Test component with package specifications."""
        component = Component(
            part_number="LMC6482AIN",
            package=PackageSpec(
                type="DIP",
                pin_count=8,
                weight=Tolerance(nominal=10, unit="g")
            )
        )
        
        assert component.package.type == "DIP"
        assert component.package.pin_count == 8
    
    def test_component_with_thermal(self):
        """Test component with thermal specifications."""
        component = Component(
            part_number="LMC6482AIN",
            thermal=ThermalSpec(
                operating_temp_range=Tolerance(min=-55, max=125),
                storage_temp_range=Tolerance(min=-65, max=150)
            )
        )
        
        assert component.thermal.operating_temp_range.min == -55
        assert component.thermal.operating_temp_range.max == 125
    
    def test_extraction_result(self):
        """Test extraction result with component."""
        component = Component(
            part_number="LMC6482AIN",
            manufacturer="Texas Instruments",
            source_document="datasheet.pdf",
            extracted_at=datetime.now(timezone.utc).isoformat(),
            confidence_score=0.85
        )
        
        result = ExtractionResult(
            component=component,
            raw_text_pages=["Page 1 content"],
            tables=[],
            confidence_by_field={"part_number": 0.95, "manufacturer": 0.80},
            review_required=False
        )
        
        assert result.component.part_number == "LMC6482AIN"
        assert len(result.raw_text_pages) == 1
        assert result.review_required is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])