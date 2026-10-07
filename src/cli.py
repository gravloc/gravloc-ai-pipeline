"""
CLI for datasheet extraction pipeline.
"""

import argparse
from pathlib import Path

from pipeline.datasheet_pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description='AI Datasheet Pipeline - Extract component data from PDF datasheets'
    )
    parser.add_argument(
        'input',
        help='Input PDF file or directory containing PDFs'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory for extracted data (JSON)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--schema',
        action='store_true',
        help='Output schema version and exit'
    )
    
    args = parser.parse_args()
    
    if args.schema:
        from schema.component import SCHEMA_VERSION
        print(f"Schema version: {SCHEMA_VERSION}")
        return
    
    if args.verbose:
        print(f"Processing: {args.input}")
        if args.output:
            print(f"Output directory: {args.output}")
    
    result = run_pipeline(args.input, args.output)
    
    if args.verbose:
        if isinstance(result, list):
            print(f"\nProcessed {len(result)} files")
        else:
            print(f"\nComponent: {result.component.part_number or 'Unknown'}")
            print(f"Confidence: {result.component.confidence_score or 'N/A'}")
            print(f"Review required: {result.review_required}")


if __name__ == '__main__':
    main()