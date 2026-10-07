# src

Main source code for the AI Datasheet Pipeline.

## Structure

```
src/
├── pipeline/          # Core pipeline stages
│   ├── ingest.py      # Ingestion logic
│   ├── validate.py    # Validation rules
│   ├── extract.py     # PDF/text extraction
│   ├── map_schema.py  # Schema mapping (rules + LLM)
│   ├── standardise.py # Unit normalisation, validation
│   └── qa.py          # Quality assurance, confidence scoring
├── schema/            # Canonical schema definitions
│   └── component.py   # Pydantic models
├── storage/           # Supabase integration
├── utils/             # Helper functions
└── cli/               # CLI entry points
```