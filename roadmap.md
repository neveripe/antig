# Project Roadmap & Improvement Ideas

This document outlines potential future directions for the Energy Stats Processor, specifically focusing on evolving it into a generic, reusable library.

## 1. Evolution into a Generic Library (`energy-lib`)

The goal is to decouple the core logic from the specific ESB Networks CSV format and CLI, creating a standardized API for energy data analysis.

### Core Abstractions
-   **Standardized Data Model**: Define a strict schema for `EnergyDataFrame` (extending pandas DataFrame) with enforced columns: `timestamp` (UTC index), `import_kwh`, `export_kwh`.
-   **Pluggable Ingesters**: Create a registry for data sources.
    ```python
    from energy_lib import read_energy
    # Auto-detect format or specify
    df = read_energy("data.csv", format="esb_networks")
    df = read_energy("shelly_cloud.json", format="shelly")
    ```

### API Design
-   **Fluent Interface**:
    ```python
    (df.energy
       .filter_date("2023-01-01", "2023-12-31")
       .resample("1D")
       .calculate_net()
       .plot())
    ```
-   **Pandas Accessor**: Implement a custom pandas accessor (e.g., `df.energy.daily_stats()`) to leverage existing pandas knowledge.

## 2. Advanced Analysis Features

-   **Tariff Engine**: Support for time-of-use (TOU) tariffs to calculate costs.
    -   Configurable tariff structures (Day/Night/Peak).
-   **Solar Simulation**: If location data is provided, simulate expected solar generation vs. actual export to detect efficiency gaps.
-   **Battery Simulation**: Simulate how a battery of size X kWh would have performed given the historical import/export data (Arbitrage/Self-consumption optimization).

## 3. Data Storage & Integration

-   **Direct Database Support**: Instead of generating SQL files, use SQLAlchemy to write directly to any supported database (PostgreSQL, SQLite, DuckDB).
-   **Parquet Support**: For long-term storage of high-frequency data (e.g., minute-level smart meter data), support Parquet for performance.

## 4. Visualization & Reporting

-   **Interactive Dashboards**: Move beyond static PNGs to HTML-based interactive plots (Plotly/Altair) or a lightweight dashboard (Streamlit).
-   **Heatmaps**: "Day of Year" vs "Time of Day" heatmaps to visualize usage patterns instantly.

## 5. Developer Experience (CI/CD)

-   **Package Publishing**: Automate publishing to PyPI via GitHub Actions.
-   **Documentation**: Host documentation on ReadTheDocs (Sphinx/MkDocs).
-   **Pre-commit Hooks**: Enforce code quality (Black, ruff, mypy) before commits.
