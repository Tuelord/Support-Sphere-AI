import sys
import argparse
import logging
import asyncio
from dependency_injector.wiring import inject, Provide
from app.container import Container
from app.application.ingestion_pipeline import IngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

@inject
def run_ingestion(
        source_uri: str,
        kb_id: str,
        pipeline: IngestionPipeline = Provide[Container.ingestion_pipeline]
):
    """
    Wrapper to run the pipeline from the CLI.
    """
    print(f"--- Starting Ingestion ---")
    print(f"Source: {source_uri}")
    print(f"Target KB: {kb_id}")

    try:
        result = pipeline.run(source_uri, kb_id)
        print(f"--- Success ---")
        print(f"Document ID: {result['document_id']}")
        print(f"Chunks Created: {result['chunks_processed']}")
    except Exception as e:
        print(f"--- Failed ---")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 1. Initialize Container
    container = Container()
    container.wire(modules=[__name__])

    # 2. Parse Arguments
    parser = argparse.ArgumentParser(description="SupportSphere AI Ingestion Tool")
    parser.add_argument("--source", required=True, help="URI of the document (File path or URL)")
    parser.add_argument("--kb", required=True, help="Knowledge Base ID")

    args = parser.parse_args()

    # 3. Run
    run_ingestion(args.source, args.kb)