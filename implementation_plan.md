# Implementation Plan - Energy Stats Processor

## Goal Description
Create a Python application to process electricity import/export data.
The application will:
1.  Ingest data from an electricity supplier (format to be defined, assuming time-series).
2.  Process business logic (statistics, aggregations).
3.  Output a PostgreSQL compatible `.sql` file for data insertion.
4.  Output various graphs representing statistical aspects.

Methodology: Test-Driven Development (TDD).

## User Review Required
> [!IMPORTANT]
> **Input Data Format**: Please specify the format of the input data (e.g., CSV, JSON, Excel, API response) and the structure (columns/fields).
> For now, I am assuming a canonical internal model of `Reading(timestamp, import_kwh, export_kwh)`.

> [!NOTE]
> **Graph Types**: What specific statistical aspects should be graphed? (e.g., Daily totals, Peak usage, Net consumption).

## Proposed Architecture

### Domain Model (Business Logic)
We will define the core logic independent of input/output details.

#### `src/domain/models.py`
- `EnergyReading`: Dataclass representing a single point in time.
    - `timestamp`: datetime
    - `import_energy`: float (kWh)
    - `export_energy`: float (kWh)
- `EnergySeries`: Collection of readings with methods for aggregations.
    - `get_daily_stats()`
    - `get_monthly_stats()`
    - `calculate_net_consumption()`
    - `filter_by_date(start, end)`

#### `src/interfaces.py`
- `IDataSource`: Abstract base class for reading data.
- `ISQLGenerator`: Abstract base class for generating SQL.
- `IGraphGenerator`: Abstract base class for plotting.

### Components

#### [NEW] `src/domain/`
- `models.py`: Core data structures.
- `stats.py`: Statistical calculation functions.

#### [NEW] `src/adapters/`
- `postgres_exporter.py`: Implements SQL generation.
- `graph_plotter.py`: Uses `matplotlib` or `plotly` to generate graphs.
    - Supports smoothing: `rolling_mean`, `spline`.
    - [NEW] Displays total Import/Export amounts on the graph.
- `csv_ingester.py` (Provisional): Reads CSV input.
    - Supports timezone and DST handling.

### CI/CD & Build
- **PyInstaller**: Used to package the application as a standalone executable.
- **GitHub Actions**: Automated workflow to:
    - Run tests on push/pull request.
    - Build executables for Windows, Linux, and macOS.
    - Upload build artifacts.

## Verification Plan

### Automated Tests
- Unit tests for `EnergySeries` aggregations (sum, avg, max).
- Unit tests for `PostgresExporter` (string output verification).
- Unit tests for `GraphGenerator` (mocking plotting library calls).
- Unit tests for `CSVIngester` (parsing, TZ, DST).

### Manual Verification
- Run the tool against a sample dataset.
- Inspect the generated `.sql` file.
- Open generated image files/HTML graphs.
- **Build Verification**: Run the generated executable on the local machine.
