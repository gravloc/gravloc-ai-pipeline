# tests

Unit and integration tests for the pipeline.

## Structure

```
tests/
├── unit/              # Unit tests per module
│   ├── test_ingest.py
│   ├── test_extract.py
│   └── test_standardise.py
├── integration/       # End-to-end pipeline tests
│   └── test_full_pipeline.py
└── fixtures/          # Test data fixtures
    └── sample_datasheet.pdf
```