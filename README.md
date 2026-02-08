# Energy Stats Processor

A Python tool to process electricity supplier data, generate SQL for database insertion, and visualize energy usage with graphs.

## ⚠️ Disclaimer: AI-Generated Code

**This project was fully written by Google Antigravity (an AI agent).**

*   **No Human Review:** The code in this repository has **never** been reviewed by a human being.
*   **"Vibecoding":** This project represents the user's first experience in "vibecoding" — building software purely through AI interaction.
*   **Future Development:** Any future development or maintenance might get stalled unless:
    *   New data samples are provided.
    *   "Good" prompts for Google Antigravity are supplied to guide the AI.

## Input Data Format

This tool is specifically designed to process the **"30-minute readings in calculated kWh"** format downloaded from **[esbnetworks.ie](https://www.esbnetworks.ie/)**.

It expects a CSV file with columns including:
*   `MPRN`
*   `Meter Serial Number`
*   `Read Value`
*   `Read Type`
*   `Read Date and End Time`

## Features

*   **Data Ingestion:** Parses ESB Networks CSV files.
    *   Handles **Timezones** (default: `Europe/Dublin`).
    *   Robustly handles **Daylight Saving Time (DST)** transitions, even with reverse chronological or duplicate data.
*   **SQL Generation:** Outputs PostgreSQL-compatible `INSERT` statements.
*   **Graphing:** Generates "Import vs Export" plots.
    *   **Smoothing:** Supports `rolling` mean and `spline` interpolation.
    *   **Totals:** Displays total Import/Export amounts.
*   **Filtering:** Filter data by date range.

## Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Tool:**
    ```bash
    python -m src.main <input_csv_file> [options]
    ```

### Options

*   `--output-sql <file>`: Path to output SQL file (default: `output.sql`).
*   `--output-graphs <dir>`: Directory to save graphs (default: `graphs`).
*   `--output-graph-file <name>`: Filename for the graph (default: `energy_over_time.png`).
*   `--timezone <tz>`: Input timezone (default: `Europe/Dublin`).
*   `--start-date <YYYY-MM-DD>`: Filter start date.
*   `--end-date <YYYY-MM-DD>`: Filter end date.
*   `--smoothing-method <method>`: `rolling` or `spline`.
*   `--smoothing-param <value>`: Window size for rolling mean (default: 3).

### Example

```bash
python -m src.main my_data.csv --output-sql my_data.sql --smoothing-method spline --timezone "Europe/Dublin"
```

## Documentation

See [walkthrough.md](walkthrough.md) for a detailed explanation of the implementation, design choices, and verification results.
