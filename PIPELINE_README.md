# AI Datasheet Pipeline MVP

## Overview

This repository contains the MVP implementation of the GRAVLOC AI Datasheet Pipeline - extracting structured component data from PDF datasheets.

## Installation

```bash
cd gravloc-ai-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### CLI

```bash
# Process a single PDF
python -m src.cli path/to/datasheet.pdf

# Process all PDFs in a directory
python -m src.cli path/to/pdf/directory

# With output directory
python -m src.cli path/to/datasheet.pdf -o output/

# Verbose mode
python -m src.cli path/to/datasheet.pdf -v

# Show schema version
python -m src.cli --schema
```

### Python API

```python
from src.pipeline.datasheet_pipeline import DatasheetPipeline

# Create pipeline
pipeline = DatasheetPipeline(output_dir="output/")

# Process single PDF
result = pipeline.process_single_pdf("datasheet.pdf")

# Access results
print(f"Part Number: {result.component.part_number}")
print(f"Confidence: {result.component.confidence_score}")
print(f"Review Required: {result.review_required}")

# Process directory
results = pipeline.process_directory("pdfs/", "output/")
```

## Pipeline Stages

1. **PDF Extraction**: Text, tables, and images using PyMuPDF, pdfplumber, and Tesseract OCR
2. **Field Extraction**: Regex-based extraction of component parameters
3. **Schema Mapping**: Map extracted fields to GRAVLOC canonical schema
4. **Standardization**: Unit normalization and validation
5. **Quality Assurance**: Confidence scoring and review queue

## Output Format

```json
{
  "component": {
    "part_number": "LMC6482AIN",
    "manufacturer": "Texas Instruments",
    "category": "active",
    "parameters": [...],
    "radiation": {...},
    "package": {...},
    "thermal": {...},
    "qualification_standards": [...],
    "lead_time": "4 weeks",
    "moq": 100
  },
  "raw_text_pages": [...],
  "tables": [...],
  "confidence_by_field": {...},
  "issues": [...],
  "review_required": false
}
```

## Project Structure

```
src/
├── cli.py                    # CLI entry point
├── extract/
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF text/table extraction
│   └── field_extractor.py   # Field extraction rules
├── pipeline/
│   ├── __init__.py
│   └── datasheet_pipeline.py # Main pipeline
└── schema/
    ├── __init__.py
    └── component.py         # Pydantic models

tests/
├── __init__.py
├── conftest.py
├── test_extract.py
├── test_field_extractor.py
└── test_pipeline.py
```

## Tech Stack

- **PDF Processing**: PyMuPDF, pdfplumber, Tesseract OCR
- **Schema**: Pydantic
- **Testing**: pytest

## Development

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=src tests/

# Type checking
mypy src/
```

## License

MIT License