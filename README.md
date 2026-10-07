# README

# AI Datasheet Pipeline

**GRAVLOC's MVP wedge: extract structured data from PDF datasheets → enable comparison**

---

## Overview

The AI Datasheet Pipeline ingests supplier datasheets (PDF), extracts component specifications, validates and standardises data, and publishes to a component catalogue for space engineers.

**Mission:** Turn messy supplier datasheets into correct, traceable, standardised component data that space engineers can trust with mission decisions.

---

## Pipeline Architecture

```
Ingestion → Validation → Extraction → Schema Mapping → Standardisation → QA → Review Queue → Publish
```

### Stages

1. **Ingestion** - Bulk upload, email (`datasheets@gravloc.com`), admin upload
2. **Validation** - Approved supplier, authenticity, duplicates, format
3. **Extraction** - PDF text (PyMuPDF/pdfplumber), OCR for scans, tables, sections
4. **Schema Mapping** - Extracted content → GRAVLOC canonical schema (rules + LLM fallback)
5. **Standardisation** - Unit normalisation, min/max parsing, cross-field validation
6. **QA** - Confidence scoring, outlier detection, completeness check
7. **Review Queue** - Low-confidence fields flagged for human review
8. **Publish** - Approved data added to catalogue

---

## Tech Stack (CTO-Approved)

| Component | Technology |
|-----------|-----------|
| PDF Parsing | PyMuPDF, pdfplumber (native text & tables) |
| OCR | Tesseract (for scanned documents) |
| Layout/Table | Docling/Unstructured (evaluation phase) |
| LLM Extraction | OpenCode models (qwen3-coder-next) - schema mapping only |
| Schema Validation | Pydantic |
| Queue/Storage | Supabase Postgres + Storage |
| Vector DB | pgvector (for Phase 2 recommendations) |

**Design Stance:** Deterministic first (regex/rules), LLM only for schema mapping as fallback.

---

## Local Setup

```bash
cd gravloc-ai-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Folder Structure

```
gravloc-ai-pipeline/
├── src/           # Main source code
│   ├── cli.py                # CLI entry point
│   ├── extract/
│   │   ├── pdf_extractor.py  # PDF text/table extraction
│   │   └── field_extractor.py # Field extraction rules
│   ├── pipeline/
│   │   └── datasheet_pipeline.py # Main pipeline
│   └── schema/
│       └── component.py      # Pydantic models
├── tests/         # Unit and integration tests
├── docs/          # Documentation and ADRs
├── models/        # Trained models (Phase 3+)
├── data/          # Golden set, eval datasets, cache
├── README.md
├── requirements.txt
└── .gitignore
```

---

## CLI Usage

```bash
# Ingest and process a single datasheet
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

---

## Metrics

- **Target:** <5 min per datasheet
- **Critical fields (TID, temp range, SEL, package):** ≥98% precision on auto-published values
- **Review queue:** Human review for low-confidence fields only

---

## Security

- Supplier datasheets are UNTRUSTED (assume malicious PDFs, prompt injection)
- Process in sandbox; limit size/pages; strip active content
- Never log full document contents or buyer data

---

## Next Step

**Owner:** AI Developer (this bot)
**ETA:** 1-week sprint (CTO-approved)

Start implementation of core extraction pipeline.