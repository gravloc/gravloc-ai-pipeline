"""
Component data schema for AI Datasheet Pipeline.

This module defines Pydantic models for structured component data following
the GRAVLOC canonical schema.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ComponentCategory(str, Enum):
    """Component categories supported by GRAVLOC."""
    ACTIVE = "active"
    PASSIVE = "passive"
    ELECTROMECHANICAL = "electromechanical"
    SENSOR = "sensor"
    POWER = "power"
    RF_MICROWAVE = "rf_microwave"


class RadiationTestStandard(str, Enum):
    """Radiation test standards."""
    MIL_STD_883 = "MIL-STD-883"
    ECSS_Q_ST_60C = "ECSS-Q-ST-60C"
    NASA_NTRS = "NASA-NTRS"
    JEDEC_JESD57 = "JEDEC JESD57"


class Tolerance(BaseModel):
    """Tolerance specification with min/max values."""
    min: Optional[float] = None
    max: Optional[float] = None
    nominal: Optional[float] = None
    unit: Optional[str] = None


class Parameter(BaseModel):
    """Electrical or physical parameter with value and tolerance."""
    name: str = Field(..., description="Parameter name")
    value: Union[float, int, str, None] = Field(None, description="Parameter value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    tolerance: Optional[Tolerance] = Field(None, description="Tolerance range")
    condition: Optional[str] = Field(None, description="Test condition (temperature, voltage, etc.)")
    test_standard: Optional[str] = Field(None, description="Test standard used")


class RadiationSpec(BaseModel):
    """Radiation performance specifications."""
    tid_total_dose: Optional[Tolerance] = Field(
        None, 
        description="Total Ionizing Dose tolerance (krad/Mrad)"
    )
    sel_threshold: Optional[float] = Field(
        None, 
        description="Single Event Latchup threshold (MeV·cm²/Mg)"
    )
    seu_threshold: Optional[float] = Field(
        None, 
        description="Single Event Upset threshold"
    )
    test_standard: Optional[RadiationTestStandard] = Field(
        None, 
        description="Radiation test standard"
    )
    test_date: Optional[str] = Field(None, description="Date of radiation testing")


class PackageSpec(BaseModel):
    """Package and physical specifications."""
    type: Optional[str] = Field(None, description="Package type (e.g., DIP, SOIC, QFN)")
    pin_count: Optional[int] = Field(None, description="Number of pins")
    dimensions: Optional[Dict[str, float]] = Field(
        None, 
        description="Package dimensions (length, width, height)"
    )
    weight: Optional[Tolerance] = Field(None, description="Weight with tolerance")
    lead_material: Optional[str] = Field(None, description="Lead/final finish material")


class ThermalSpec(BaseModel):
    """Thermal specifications."""
    operating_temp_range: Optional[Tolerance] = Field(
        None, 
        description="Operating temperature range (°C)"
    )
    storage_temp_range: Optional[Tolerance] = Field(
        None, 
        description="Storage temperature range (°C)"
    )
    thermal_resistance: Optional[Dict[str, float]] = Field(
        None, 
        description="Thermal resistance values (θJA, θJC, etc.)"
    )


class ComplianceSpec(BaseModel):
    """Regulatory and compliance specifications."""
    rohs: Optional[bool] = Field(None, description="RoHS compliance")
    lead_free: Optional[bool] = Field(None, description="Lead-free")
    halogen_free: Optional[bool] = Field(None, description="Halogen-free")
    aec_q100: Optional[bool] = Field(None, description="AEC-Q100 qualified")
    mil_grade: Optional[bool] = Field(None, description="Military grade")
    space_grade: Optional[bool] = Field(None, description="Space grade")


class Component(BaseModel):
    """Main component data model."""
    # Identification
    part_number: Optional[str] = Field(None, description="Manufacturer part number")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    alternate_part_numbers: Optional[List[str]] = Field(
        None, 
        description="Alternate/compatible part numbers"
    )
    
    # Specifications
    category: Optional[ComponentCategory] = Field(None, description="Component category")
    parameters: Optional[List[Parameter]] = Field(
        None, 
        description="Electrical and physical parameters"
    )
    
    # Radiation (for space applications)
    radiation: Optional[RadiationSpec] = Field(
        None, 
        description="Radiation performance specifications"
    )
    
    # Package
    package: Optional[PackageSpec] = Field(
        None, 
        description="Package and physical specifications"
    )
    
    # Thermal
    thermal: Optional[ThermalSpec] = Field(
        None, 
        description="Thermal specifications"
    )
    
    # Compliance
    compliance: Optional[ComplianceSpec] = Field(
        None, 
        description="Regulatory compliance"
    )
    
    # Qualification
    qualification_standards: Optional[List[str]] = Field(
        None, 
        description=" qualification standards (MIL-STD, ECSS, NASA, etc.)"
    )
    trl: Optional[int] = Field(
        None, 
        ge=1, 
        le=9, 
        description="Technology Readiness Level (1-9)"
    )
    heritage_missions: Optional[List[str]] = Field(
        None, 
        description="Flights heritage missions"
    )
    
    # Availability
    lead_time: Optional[str] = Field(None, description="Standard lead time")
    moq: Optional[int] = Field(None, description="Minimum order quantity")
    
    # Source tracking (for traceability)
    source_document: Optional[str] = Field(
        None, 
        description="Source PDF filename"
    )
    source_page: Optional[int] = Field(
        None, 
        description="Page number where data was extracted"
    )
    extracted_at: Optional[str] = Field(
        None, 
        description="Extraction timestamp (ISO 8601)"
    )
    confidence_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Overall confidence score (0.0-1.0)"
    )
    
    # Extraction metadata
    extraction_version: Optional[str] = Field(
        None, 
        description="Extraction pipeline version"
    )
    model_used: Optional[str] = Field(
        None, 
        description="LLM model used for extraction (if any)"
    )


class ExtractionResult(BaseModel):
    """Complete extraction result with provenance."""
    component: Component
    raw_text_pages: Optional[List[str]] = Field(
        None, 
        description="Raw extracted text from PDF pages"
    )
    tables: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Extracted tables"
    )
    confidence_by_field: Optional[Dict[str, float]] = Field(
        None, 
        description="Confidence scores per field"
    )
    issues: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Extraction issues or warnings"
    )
    review_required: bool = Field(
        False, 
        description="Flag indicating if human review is required"
    )


# Schema version
SCHEMA_VERSION = "1.0.0"