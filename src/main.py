import argparse
import os
from src.adapters.csv_ingester import CSVIngester
from src.adapters.postgres_exporter import PostgresExporter
from src.adapters.graph_plotter import GraphPlotter
from datetime import datetime
import pandas as pd

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
    
    args = parser.parse_args()
    
    print(f"Processing {args.input_file}...")
    
    # 1. Ingest
    ingester = CSVIngester(timezone=args.timezone)
    try:
        series = ingester.parse(args.input_file)
        print(f"Loaded {len(series.readings)} readings.")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Filter by date if requested
    if args.start_date or args.end_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
        end = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None
        
        # We need to handle timezone for start/end if the series is timezone aware (which it is, UTC)
        # The user likely provides "local" dates (e.g. "2022-10-30").
        # If we just compare naive start/end with UTC series, it might be off.
        # But `filter_by_date` handles naive comparison by assuming same TZ.
        # However, `series.df['timestamp']` is UTC.
        # So we should probably convert start/end to UTC?
        # Or, we can localize start/end to the INPUT timezone, then convert to UTC.
        # This matches user expectation: "I want data from 2022-10-30 (Irish time)".
        
        if args.timezone:
            if start:
                start = pd.Timestamp(start).tz_localize(args.timezone).tz_convert('UTC')
            if end:
                # For end date, we usually want the END of the day if only YYYY-MM-DD is provided?
                # Or exact timestamp?
                # If user says --end-date 2022-10-30, they probably mean inclusive of that day?
                # Or just 00:00?
                # Let's assume 00:00 for now to keep it simple, or maybe add 23:59:59 if it was just a date?
                # The prompt didn't specify. Let's stick to exact parsing for now.
                end = pd.Timestamp(end).tz_localize(args.timezone).tz_convert('UTC')
        
        series = series.filter_by_date(start, end)
        print(f"Filtered to {len(series.readings)} readings.")

    # 2. Generate SQL
    print("Generating SQL...")
    exporter = PostgresExporter(table_name="energy_readings")
    sql_content = exporter.generate_sql(series)
    with open(args.output_sql, "w") as f:
        f.write(sql_content)
    print(f"SQL written to {args.output_sql}")

    # 3. Generate Graphs
    print("Generating Graphs...")
    plotter = GraphPlotter()
    files = plotter.generate_graphs(series, args.output_graphs, output_file=args.output_graph_file,
                                   smoothing_method=args.smoothing_method, smoothing_param=args.smoothing_param)
    print(f"Graphs generated in {args.output_graphs}:")
    for f in files:
        print(f" - {f}")

    # 4. Print Stats
    print("\nSummary Stats:")
    print(f"Net Consumption: {series.calculate_net_consumption():.2f} kWh")
    
    daily = series.get_daily_stats()
    print(f"Days processed: {len(daily)}")

if __name__ == "__main__":
    main()
