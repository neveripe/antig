# Tariff Engine Implementation Plan

## Goal
Implement a flexible **Tariff Engine** capable of calculating energy costs based on various pricing structures (Flat, Time-of-Use, Tiered).

## 1. Domain Models

We need to introduce new models to represent tariffs and costs.

### `src/domain/tariff.py`

*   **`TariffRate`**: Represents a specific price for a specific time window.
    *   `price_per_kwh` (float): Cost in currency units.
    *   `start_time` (time): Start time of the rate (e.g., 08:00).
    *   `end_time` (time): End time of the rate (e.g., 23:00).
    *   `days_of_week` (List[int]): Applicable days (0=Monday, 6=Sunday).
    *   `name` (str): Label (e.g., "Day", "Night", "Peak").

*   **`Tariff`**: A collection of rates and standing charges.
    *   `name` (str): e.g., "Standard Day/Night".
    *   `import_rates` (List[TariffRate]): List of applicable rates for IMPORTED energy.
    *   `export_rates` (List[TariffRate]): List of applicable rates for EXPORTED energy (Feed-in Tariff).
    *   `standing_charge` (float): Daily fixed cost.
    *   `currency` (str): e.g., "EUR".

*   **`Bill`**: The result of a calculation.
    *   `total_import_cost` (float): Cost of imported energy.
    *   `total_export_credit` (float): Value of exported energy (usually negative or positive credit).
    *   `standing_charge_cost` (float): Total standing charges.
    *   `net_cost` (float): `total_import_cost + standing_charge_cost - total_export_credit`.
    *   `breakdown` (Dict[str, float]): Cost per rate name.
    *   `period_start` (datetime)
    *   `period_end` (datetime)

## 2. Business Logic

### `src/domain/billing.py`

*   **`CostCalculator`**: Service to apply a `Tariff` to an `EnergySeries`.
    *   `calculate_cost(series: EnergySeries, tariff: Tariff) -> Bill`
    *   **Logic**:
        1.  Resample series to ensure consistent intervals (if needed).
        2.  Iterate through readings.
        3.  **Import**: Determine applicable `import_rate` based on timestamp.
            *   `import_cost = reading.import_kwh * rate.price`
        4.  **Export**: Determine applicable `export_rate` based on timestamp.
            *   `export_credit = reading.export_kwh * rate.price`
        5.  Accumulate totals (Import Cost, Export Credit) and breakdown.
        6.  Add `standing_charge * number_of_days`.
        7.  Calculate `net_cost`.

## 3. Configuration

We need a way to define tariffs, likely via a JSON or YAML configuration file.

**Example `tariffs.json`:**
```json
{
  "electric_ireland_day_night": {
    "standing_charge": 0.50,
    "currency": "EUR",
    "import_rates": [
      {
        "name": "Night",
        "price": 0.20,
        "start": "23:00",
        "end": "08:00",
        "days": [0, 1, 2, 3, 4, 5, 6]
      },
      {
        "name": "Day",
        "price": 0.40,
        "start": "08:00",
        "end": "23:00",
        "days": [0, 1, 2, 3, 4, 5, 6]
      }
    ],
    "export_rates": [
      {
        "name": "Standard Feed-in",
        "price": 0.21,
        "start": "00:00",
        "end": "23:59",
        "days": [0, 1, 2, 3, 4, 5, 6]
      }
    ]
  }
}
```

## 4. Implementation Steps

1.  **Define Models**: Create `src/domain/tariff.py`.
2.  **Implement Calculator**: Create `src/domain/billing.py` with the matching logic.
3.  **Create Config Loader**: Implement a loader for `tariffs.json`.
4.  **CLI Integration**:
    *   Add `--tariff-file` argument.
    *   Add `--tariff-name` argument.
    *   Output cost calculation in the summary stats.
5.  **Visualization Update**:
    *   (Optional) Add a "Cost over Time" graph.

## 5. Verification

*   **Unit Tests**:
    *   Test `CostCalculator` with simple synthetic data (e.g., 1 kWh every hour).
    *   Verify Day/Night switching logic.
    *   Verify Weekend logic (if applicable).
*   **Integration Tests**:
    *   Run with sample CSV and a sample tariff file.
