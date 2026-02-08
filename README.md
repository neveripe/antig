# Energy Stats Processor

A Python tool to process electricity supplier data, generate SQL for database insertion, and visualize energy usage with graphs.

## ⚠️ Disclaimer: AI-Generated Code

**This project was fully written by Tavi (Google Antigravity AI agent). The project owner has never written a single line of code.**

*   **100% AI-Authored:** Every line of code, test, documentation, and configuration was written by Tavi.
*   **No Human Code Review:** The code in this repository has **never** been reviewed by a human being from a code quality perspective.
*   **"Vibecoding":** This project represents a "vibecoding" experience — building software purely through natural language interaction with AI.
*   **Collaborative Development:** The project owner (neveripe) provided requirements, feedback, and testing, while Tavi implemented all technical solutions.
*   **Future Development:** Any future development or maintenance might get stalled unless:
    *   New data samples are provided.
    *   "Good" prompts for Tavi (Google Antigravity) are supplied to guide the AI.

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

See [docs/walkthrough.md](docs/walkthrough.md) for a detailed explanation of the implementation, design choices, and verification results.

For project planning and roadmap, see the [docs/](docs/) directory.

## Contributors

- **neveripe** - Project Owner & Maintainer *(did not write any code, all code was AI-generated)*
- **Tavi** - AI Development Collaborator (Google Antigravity) *(wrote 100% of the codebase)*
