import argparse

from scraping.run import run_scraping
from extracting.run import run_extracting
from generating.run import run_generating
from utils.logger import setup_logger

# Logging Configuration
logger = setup_logger()

def main():
    parser = argparse.ArgumentParser(description="Scribd Processing Pipeline")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Run a specific phase")
    parser.add_argument("--run-all", action="store_true", help="Run all 3 phases in sequence")
    args = parser.parse_args()

    try:
        if args.run_all:
            logger.info("Starting full pipeline...")
            run_scraping()
            run_extracting()
            run_generating()
        elif args.phase == 1:
            logger.info("Running Phase 1: Scraping")
            run_scraping()
        elif args.phase == 2:
            logger.info("Running Phase 2: Extraction")
            run_extracting()
        elif args.phase == 3:
            logger.info("Running Phase 3: Semantics")
            run_generating()
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


if __name__ == "__main__":
    main()
