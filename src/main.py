import argparse
import os
import sys
from pathlib import Path
from src.adapters.csv_ingester import CSVIngester
from src.adapters.postgres_exporter import PostgresExporter
from src.adapters.graph_plotter import GraphPlotter
from src.utils.logging_config import setup_logging, get_logger
from datetime import datetime
import pandas as pd

logger = get_logger(__name__)

def main():
    """
    Main entry point for the Energy Stats Processor CLI.

    Parses command-line arguments, orchestrates the data ingestion, processing,
    SQL generation, and graph plotting workflows.
    """
    parser = argparse.ArgumentParser(description="Energy Stats Processor")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("--output-sql", default="output.sql", help="Path to output SQL file")
    parser.add_argument("--output-graphs", default="graphs", help="Directory to output graphs")
    parser.add_argument("--timezone", default="Europe/Dublin", help="Timezone of input data (default: Europe/Dublin)")
    parser.add_argument("--start-date", help="Start date for filtering (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for filtering (YYYY-MM-DD)")
    parser.add_argument("--output-graph-file", help="Filename for the output graph (e.g. my_graph.png)")
    parser.add_argument("--smoothing-method", choices=["rolling", "spline"], help="Smoothing method for graphs")
    parser.add_argument("--smoothing-param", type=float, help="Smoothing parameter (window size for rolling)")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity (-v for INFO, -vv for DEBUG)")
    
    args = parser.parse_args()
    
    # Setup logging based on verbosity
    setup_logging(args.verbose)
    
    # Validate input file exists
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"File not found: {args.input_file}")
        return 1
    
    if not input_path.is_file():
        logger.error(f"Not a file: {args.input_file}")
        return 1
    
    logger.info(f"Processing {args.input_file}")
    
    # 1. Ingest
    ingester = CSVIngester(timezone=args.timezone)
    try:
        series = ingester.parse(args.input_file)
        logger.info(f"Loaded {len(series.readings)} readings")
    except FileNotFoundError:
        logger.error(f"File not found: {args.input_file}")
        return 1
    except pd.errors.EmptyDataError:
        logger.error(f"File is empty: {args.input_file}")
        return 1
    except pd.errors.ParserError as e:
        logger.error(f"Invalid CSV format: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        logger.debug("Full error details:", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error reading file: {e}")
        logger.debug("Full traceback:", exc_info=True)
        return 1

    # Filter by date if requested
    if args.start_date or args.end_date:
        try:
            start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
            end = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
        except ValueError as e:
            logger.error(f"Invalid date format. Use YYYY-MM-DD (e.g., 2023-01-15)")
            logger.debug(f"Date parsing error: {e}")
            return 1
        
        # Convert dates to UTC using the input timezone
        # This matches user expectation: "I want data from 2022-10-30 (Irish time)"
        if args.timezone:
            if start:
                start = pd.Timestamp(start).tz_localize(args.timezone).tz_convert('UTC')
            if end:
                end = pd.Timestamp(end).tz_localize(args.timezone).tz_convert('UTC')
        
        logger.debug(f"Filtering data from {start} to {end} (UTC)")
        series = series.filter_by_date(start, end)
        logger.info(f"Filtered to {len(series.readings)} readings")

    # 2. Generate SQL
    logger.info("Generating SQL")
    exporter = PostgresExporter(table_name="energy_readings")
    try:
        sql_content = exporter.generate_sql(series)
        with open(args.output_sql, "w") as f:
            f.write(sql_content)
        logger.info(f"SQL written to {args.output_sql}")
    except PermissionError:
        logger.error(f"Permission denied: cannot write to {args.output_sql}")
        return 1
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        logger.debug("Full traceback:", exc_info=True)
        return 1

    # 3. Generate Graphs
    logger.info("Generating graphs")
    plotter = GraphPlotter()
    try:
        files = plotter.generate_graphs(series, args.output_graphs, output_file=args.output_graph_file,
                                       smoothing_method=args.smoothing_method, smoothing_param=args.smoothing_param)
        logger.info(f"Graphs generated in {args.output_graphs}:")
        for f in files:
            logger.info(f"  - {f}")
    except Exception as e:
        logger.error(f"Error generating graphs: {e}")
        logger.debug("Full traceback:", exc_info=True)
        return 1

    # 4. Summary Stats (always shown)
    logger.warning("\nSummary Stats:")  # WARNING level always displays
    logger.warning(f"Net Consumption: {series.calculate_net_consumption():.2f} kWh")
    
    daily = series.get_daily_stats()
    logger.warning(f"Days processed: {len(daily)}")
    
    return 0

if __name__ == "__main__":
    main()
