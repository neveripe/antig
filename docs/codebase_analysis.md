# Codebase Analysis: Issues, Deficiencies & Missing Tests

**Generated:** 2026-02-08  
**Purpose:** Systematic analysis for identifying breaking points, deficiencies, and test gaps  
**Format:** Optimized for AI consumption (primary) and human readability (secondary)

---

## Executive Summary

**Total Issues Found:** 32  
**Severity Breakdown:**
- 🔴 **Critical (P0):** 5 - Could cause data corruption or crashes
- 🟠 **High (P1):** 8 - Could cause incorrect results or security issues
- 🟡 **Medium (P2):** 12 - Could cause usability problems or edge case failures
- 🔵 **Low (P3):** 7 - Code quality, maintainability, or minor improvements

**Test Coverage:** 15/15 tests passing, but significant edge case gaps identified

---

## 1. Domain Layer Issues

### 1.1 `src/domain/models.py`

#### 🔴 **CRITICAL-1**: Negative Energy Values Not Validated
**File:** [`models.py:8-19`](file:///z:/never/vscode/antig/src/domain/models.py#L8-L19)  
**Issue:** `EnergyReading` dataclass accepts negative values for `import_energy` and `export_energy`  
**Impact:** Invalid data could propagate through entire system, causing incorrect billing calculations  
**Breaking Point:**
```python
# This is currently allowed but nonsensical:
EnergyReading(timestamp=now, import_energy=-100.0, export_energy=-50.0)
```
**Solution:** Add `__post_init__` validation:
```python
def __post_init__(self):
    if self.import_energy < 0:
        raise ValueError(f"import_energy cannot be negative: {self.import_energy}")
    if self.export_energy < 0:
        raise ValueError(f"export_energy cannot be negative: {self.export_energy}")
```
**Missing Test:** Test that negative values raise `ValueError`

---

#### 🟠 **HIGH-1**: Timezone Handling Inconsistency in `filter_by_date`
**File:** [`models.py:142-154`](file:///z:/never/vscode/antig/src/domain/models.py#L142-L154)  
**Issue:** Complex timezone handling logic with commented warnings but no actual resolution  
**Code:**
```python
# Lines 144-151: "Assume UTC if not specified, or match series?"
# "Ideally, the caller should handle timezone conversion."
# "For now, let's just compare."
```
**Impact:** Silent failures when mixing naive and timezone-aware datetimes  
**Breaking Scenario:**
```python
series = EnergySeries([...])  # UTC timestamps
series.filter_by_date(
    start=datetime(2024, 1, 1),  # Naive datetime
    end=datetime(2024, 12, 31)   # Naive datetime  
)
# Behavior is unclear and depends on pandas internal handling
```
**Solution:** Explicit timezone handling with clear error messages  
**Missing Tests:** 
- Test naive datetime filtering on UTC series
- Test timezone mismatch scenarios
- Test DST boundaries in filters

---

#### 🟡 **MEDIUM-1**: Empty DataFrame Edge Case Handling
**File:** [`models.py:46-50`](file:///z:/never/vscode/antig/src/domain/models.py#L46-L50)  
**Issue:** Empty series creates DataFrame correctly but other methods assume non-empty  
**Impact:** Some methods may fail with cryptic pandas errors on empty data  
**Missing Tests:**
- `test_empty_series_daily_stats()` 
- `test_empty_series_monthly_stats()`  
- `test_empty_series_filter()`
- `test_single_reading_series()`

---

#### 🟡 **MEDIUM-2**: No Duplicate Timestamp Handling
**File:** [`models.py:29-50`](file:///z:/never/vscode/antig/src/domain/models.py#L29-L50)  
**Issue:** Constructor doesn't check for duplicate timestamps  
**Impact:** Duplicate timestamps will create duplicate dataframe rows, skewing statistics  
**Breaking Scenario:**
```python
readings = [
    EnergyReading(timestamp=t, import_energy=10.0, export_energy=5.0),
    EnergyReading(timestamp=t, import_energy=20.0, export_energy=10.0),  # Same timestamp!
]
series = EnergySeries(readings)
# Sum will incorrectly double-count
```
**Solution:** Detect duplicates and either raise error or merge (with strategy parameter)  
**Missing Test:**  `test_duplicate_timestamp_handling()`

---

### 1.2 `src/domain/billing.py`

#### 🔴 **CRITICAL-2**: Standing Charge Calculation Has Off-by-One Error Potential
**File:** [`billing.py:87-114`](file:///z:/never/vscode/antig/src/domain/billing.py#L87-L114)  
**Issue:** Standing charge loop uses `<=` which counts both start and end dates  
**Code:**
```python
while current_date <= end_date:  # Line 93
    # ...
    current_date += timedelta(days=1)
```
**Impact:** If `period_start` and `period_end` are same day, charges for 1 day ✅. But if data spans 2024-01-01 00:00 to 2024-01-02 00:00 (exactly 24 hours), charges for **2 days** ❌  
**Example:**
```python
# Data: 2024-01-01 00:00 to 2024-01-01 23:30 (1 day) -> Charges 1 day ✅
# Data: 2024-01-01 00:00 to 2024-01-02 00:00 (1 day) -> Charges 2 days ❌
```
**Solution:** More precise calculation based on unique days, not date range endpoints  
**Missing Test:** `test_standing_charge_exact_24_hours()`

---

#### 🔴 **CRITICAL-3**: No Rate Found Returns `None`, Silently Skips Costs
**File:** [`billing.py:117-133`](file:///z:/never/vscode/antig/src/domain/billing.py#L117-L133)  
**Issue:** `_find_rate()` returns `None` if no rate found, but caller doesn't always check  
**Code:**
```python
rate = self._find_rate(tariff.import_rates, t, weekday)
if rate:  # Line 71 - energy is not billed if rate is None!
    cost = import_kwh * rate.price_per_kwh
```
**Impact:** Energy usage outside any tariff window is **silently not billed**  
**Breaking Scenario:** Tariff only defines 08:00-23:00, usage at 02:00 is free!  
**Solution:** Raise error if no rate found or require "catch-all" tariff validation  
**Missing Test:** `test_usage_outside_defined_tariff_windows()`

---

#### 🟠 **HIGH-2**: Tariff Schedule Gap Handling Incomplete
**File:** [`billing.py:41-49`](file:///z:/never/vscode/antig/src/domain/billing.py#L41-L49)  
**Issue:** `get_tariff()` raises `ValueError` if no tariff valid, but doesn't handle overlaps  
**Code:**
```python
for t in tariffs:
    if t.valid_from and ts < t.valid_from:
        continue
    if t.valid_to and ts > t.valid_to:
        continue
    return t  # Returns FIRST match, doesn't check overlaps!
```
**Impact:** If two tariffs overlap, first one wins silently  
**Missing Test:** `test_overlapping_tariff_schedule_error()`

---

#### 🟡 **MEDIUM-3**: Timezone Conversion Hardcoded to `pytz`
**File:** [`billing.py:59-62`](file:///z:/never/vscode/antig/src/domain/billing.py#L59-L62)  
**Issue:** Uses `pytz.timezone()` which is deprecated in favor of `zoneinfo` (Python 3.9+)  
**Impact:** Future compatibility issues, and `pytz` has quirks with DST  
**Solution:** Migrate to `zoneinfo.ZoneInfo()`  
**Technical Debt:** Low priority but should be addressed

---

### 1.3 `src/domain/tariff.py`

#### 🟡 **MEDIUM-4**: No Validation on `TariffRate` Times
**File:** [`tariff.py:5-14`](file:///z:/never/vscode/antig/src/domain/tariff.py#L5-L14)  
**Issue:** `start_time` and `end_time` can be equal, creating zero-duration windows  
**Breaking Scenario:**
```python
rate = TariffRate(name="Invalid", price_per_kwh=0.30, 
                  start_time=time(12,0), end_time=time(12,0))
# Creates a tariff window that never matches!
```
**Solution:** Add validation that overnight windows are clearly marked or validated  
**Missing Test:** `test_invalid_tariff_rate_times()`

---

#### 🔵 **LOW-1**: Currency Field Not Used Anywhere
**File:** [`tariff.py:24`](file:///z:/never/vscode/antig/src/domain/tariff.py#L24)  
**Issue:** `currency` field exists but is never validated or used in calculations  
**Impact:** User could mix EUR and USD tariffs incorrectly  
**Solution:** Either remove field or add currency mismatch validation  

---

## 2.  Adapter Layer Issues

### 2.1 `src/adapters/csv_ingester.py`

#### 🔴 **CRITICAL-4**: Hardcoded CSV Column Names
**File:** [`csv_ingester.py:45-49`](file:///z:/never/vscode/antig/src/adapters/csv_ingester.py#L45-L49)  
**Issue:** Column renaming assumes exact ESB format  
**Code:**
```python
df = df.rename(columns={
    "Read Date and End Time": "timestamp",
    "Read Value": "value",
    "Read Type": "type"
})
```
**Impact:** Any CSV format variation causes `KeyError` or silent failure  
**Solution:** Add validation that required columns exist with helpful error  
**Missing Test:** `test_csv_missing_columns_error()`

---

#### 🔴 **CRITICAL-5**: Timestamp Format Hardcoded
**File:** [`csv_ingester.py:53`](file:///z:/never/vscode/antig/src/adapters/csv_ingester.py#L53)  
**Issue:** Single date format: `'%d-%m-%Y %H:%M'`  
**Impact:** Files with different format (e.g., ISO 8601) will fail to parse  
**Solution:** Try multiple formats or use `pd.to_datetime()` with `infer_datetime_format=True`  
**Missing Test:** `test_csv_alternative_date_formats()`

---

#### 🟠 **HIGH-3**: DST Fallback Logic Assumes Single-Year Data
**File:** [`csv_ingester.py:91-136`](file:///z:/never/vscode/antig/src/adapters/csv_ingester.py#L91-L136)  
**Issue:** Comments acknowledge multi-year DST handling is incomplete  
**Code:**
```python
# Line 91: "Note: This assumes only ONE fallback per file (valid for 1 year data usually)"
# Line 92: "If there are multiple years, we might need to reset the flag?"
```
**Impact:** Multi-year CSV files may have DST ambiguity resolved incorrectly  
**Breaking Scenario:** File spanning Oct 2024 → Oct 2025 will have two DST transitions  
**Missing Test:** `test_multi_year_csv_with_multiple_dst_transitions()`

---

#### 🟠 **HIGH-4**: Reverse Chronological Detection Is Naive
**File:** [`csv_ingester.py:58-59`](file:///z:/never/vscode/antig/src/adapters/csv_ingester.py#L58-L59)  
**Issue:** Only checks first vs last timestamp  
**Code:**
```python
if len(df) > 1 and df['timestamp'].iloc[0] > df['timestamp'].iloc[-1]:
    df = df.iloc[::-1].reset_index(drop=True)
```
**Impact:** If data is mostly chronological but has one out-of-order row, it won't be detected  
**Solution:** Check if data is sorted, don't assume only two possibilities  
**Missing Test:** `test_csv_with_random_order_timestamps()`

---

#### 🟡 **MEDIUM-5**: Missing Data Handling Uses `fillna(0.0)`
**File:** [`csv_ingester.py:189`](file:///z:/never/vscode/antig/src/adapters/csv_ingester.py#L189)  
**Issue:** If import or export row is missing, fills with 0  
**Impact:** Silent data loss - missing reading becomes zero reading  
**Better Approach:** Raise error or use `NaN` to signal missing data  
**Missing Test:** `test_csv_with_missing_import_or_export_row()`

---

#### 🟡 **MEDIUM-6**: No CSV File Size Validation
**File:** N/A  
**Issue:** No check for file size before loading entire CSV into memory  
**Impact:** Very large CSV files (100MB+) could cause memory issues  
**Solution:** Add size check or use chunked reading for large files  
**Missing Test:** `test_large_csv_file_handling()`

---

### 2.2 `src/adapters/postgres_exporter.py`

#### 🟠 **HIGH-5**: SQL Injection Risk
**File:** [`postgres_exporter.py:36-40`](file:///z:/never/vscode/antig/src/adapters/postgres_exporter.py#L36-L40)  
**Issue:** SQL generated via f-strings without escaping  
**Code:**
```python
ts_str = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
values.append(f"('{ts_str}', {r.import_energy}, {r.export_energy})")
```
**Impact:** If timestamp formatting fails or contains unexpected characters, could break SQL  
**Risk Level:** LOW for this specific case (timestamps are controlled), but bad practice  
**Solution:** Use parameterized queries or proper SQL escaping library  
**Note:** This generates static SQL, not executing it, so traditional SQL injection isn't possible, but malformed SQL could be generated  

---

#### 🟠 **HIGH-6**: Timezone Information Lost in SQL Export
**File:** [`postgres_exporter.py:36`](file:///z:/never/vscode/antig/src/adapters/postgres_exporter.py#L36)  
**Issue:** `strftime` drops timezone information  
**Code:**
```python
ts_str = r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
# If r.timestamp is UTC, this exports as naive string!
```
**Impact:** Database will interpret timestamps as local time, not UTC  
**Solution:** Use `TIMESTAMP WITH TIME ZONE` and include `+00:00` suffix  
**Missing Test:** `test_sql_export_preserves_timezone()`

---

#### 🟡 **MEDIUM-7**: Table Name Not Validated/Escaped
**File:** [`postgres_exporter.py:40`](file:///z:/never/vscode/antig/src/adapters/postgres_exporter.py#L40)  
**Issue:** `self.table_name` used directly in SQL without validation  
**Impact:** Invalid table names could generate broken SQL  
**Solution:** Validate table name against SQL identifier rules  
**Missing Test:** `test_sql_export_with_invalid_table_name()`

---

#### 🔵 **LOW-2**: No Option for Batch Size or Multi-Statement
**File:** [`postgres_exporter.py:33-40`](file:///z:/never/vscode/antig/src/adapters/postgres_exporter.py#L33-L40)  
**Issue:** Generates single massive INSERT statement  
**Impact:** Very large datasets could exceed PostgreSQL's max SQL statement size  
**Solution:** Add option to split into multiple INSERT statements  
**Enhancement:** Consider `COPY` command for better performance

---

### 2.3 `src/adapters/graph_plotter.py`

#### 🟡 **MEDIUM-8**: Spline Smoothing Assumes Enough Data Points
**File:** [`graph_plotter.py:57-77`](file:///z:/never/vscode/antig/src/adapters/graph_plotter.py#L57-L77)  
**Issue:** `make_interp_spline(..., k=3)` requires at least 4 points  
**Impact:** Crashes on small datasets  
**Breaking Scenario:**
```python
series = EnergySeries([reading1, reading2, reading3])  # Only 3 readings
plotter.generate_graphs(series, "output", smoothing_method="spline")
# Crashes: ValueError: need at least 4 points for cubic spline
```
**Solution:** Check data length before applying spline or catch exception more gracefully  
**Missing Test:** `test_graph_spline_with_insufficient_data()`

---

#### 🟡 **MEDIUM-9**: Rolling Window Size Not Validated
**File:** [`graph_plotter.py:54-56`](file:///z:/never/vscode/antig/src/adapters/graph_plotter.py#L54-L56)  
**Issue:** Window size can be larger than dataset  
**Breaking Scenario:**
```python
series = EnergySeries([r1, r2])  # 2 readings
plotter.generate_graphs(series, "output", smoothing_method="rolling", smoothing_param=100)
# Results in all NaN values
```
**Solution:** Validate window <= len(data) with helpful error  
**Missing Test:** `test_graph_rolling_window_larger_than_data()`

---

#### 🟡 **MEDIUM-10**: Output Directory Not Created on Failure
**File:** [`graph_plotter.py:42`](file:///z:/never/vscode/antig/src/adapters/graph_plotter.py#L42)  
**Issue:** If graph generation fails after `os.makedirs`, directory is left created  
**Impact:** Minor - directory persists even though no graphs generated  
**Enhancement:** Consider atomic operations or cleanup on failure

---

#### 🔵 **LOW-3**: No Progress Indication for Long-Running Operations
**File:** N/A  
**Issue:** Graph generation can take time on large datasets, no progress feedback  
**Enhancement:** Add logging or progress bar for large datasets  

---

## 3. Main Entry Point Issues

### 3.1 `src/main.py`

#### 🟠 **HIGH-7**: Date Filtering Timezone Handling is Unclear
**File:** [`main.py:40-66`](file:///z:/never/vscode/antig/src/main.py#L40-L66)  
**Issue:** Complex logic with comments questioning correctnessCode
```python
# Line 48: "The user likely provides 'local' dates"
# Line 52: "Or, we can localize start/end to the INPUT timezone"
# Lines 58-64: End date handling unclear - "00:00 or 23:59:59?"
```
**Impact:** User confusion about inclusive/exclusive date ranges  
**Example:**
```
--start-date 2024-01-01 --end-date 2024-01-31
# Does this include January 31st data, or stop at midnight?
```
**Solution:** Document behavior clearly and implement consistent logic  
**Missing Test:** Integration test for date filtering edge cases

---

#### 🟠 **HIGH-8**: Exception Handling Too Broad
**File:** [`main.py:33-38`](file:///z:/never/vscode/antig/src/main.py#L33-L38)  
**Code:**
```python
try:
    series = ingester.parse(args.input_file)
    print(f"Loaded {len(series.readings)} readings.")
except Exception as e:  # Too broad!
    print(f"Error reading file: {e}")
    return
```
**Impact:** Catches all exceptions including bugs, not just expected errors  
**Solution:** Catch specific exceptions (`FileNotFoundError`, `ValueError`, etc.)  
**Missing Test:** Test that unexpected exceptions are not silently caught

---

#### 🟡 **MEDIUM-11**: No Validation of CLI Arguments
**File:** [`main.py:16-26`](file:///z:/never/vscode/antig/src/main.py#L16-L26)  
**Issue:** Arguments accepted without validation  
**Examples:**
- `--smoothing-param -5` → Negative window size allowed
- `--timezone "Invalid/Timezone"` → Invalid timezone accepted
- `--output-graphs "con:"` → Invalid path on Windows
**Solution:** Add argument validation with `argparse` `type` parameter  
**Missing Tests:** CLI argument validation tests

---

#### 🟡 **MEDIUM-12**: File Write Failures Not Handled
**File:** [`main.py:73-74`](file:///z:/never/vscode/antig/src/main.py#L73-L74)  
**Issue:** No try-catch around file write operations  
**Breaking Scenario:** Read-only output directory or disk full  
**Solution:** Wrap file operations in try-except with helpful messages  

---

#### 🔵 **LOW-4**: No Logging, Only Print Statements
**File:** Multiple lines  
**Issue:** Uses `print()` instead of logging framework that exists (`src/utils/logging_config.py`)  
**Impact:** No control over verbosity, output mixing with actual data  
**Solution:**Migrate to `logger.info()` etc.  

---

#### 🔵 **LOW-5**: No Dry-Run or Preview Mode
**File:** N/A  
**Enhancement:** Add `--dry-run` flag to validate input without generating outputs  

---

## 4. Test Coverage Gaps

### 4.1 Missing Unit Tests

#### Domain Models (`src/domain/models.py`)
- [ ] **Negative energy values validation**
- [ ] **Duplicate timestamp handling**
- [ ] **Empty series operations**
- [ ] **Single reading edge case**
- [ ] **Timezone-aware vs naive datetime filtering**
- [ ] **Very large datasets (performance)**
- [ ] **NaN/inf values in energy readings**

#### Billing Calculator (`src/domain/billing.py`)
- [ ] **Standing charge exact 24-hour period**
- [ ] **Usage outside defined tariff windows**
- [ ] **Overlapping tariff schedules**
- [ ] **Timezone conversion edge cases**
- [ ] **Empty energy series billing**
- [ ] **Tariff with no rates defined**
- [ ] **Negative prices (export can pay you!)**

#### Tariff Models (`src/domain/tariff.py`)
- [ ] **Invalid time window validation**
- [ ] **Overlapping rate windows**
- [ ] **Empty days_of_week list**
- [ ] **Rate window that crosses midnight**

#### CSV Ingester (`src/adapters/csv_ingester.py`)
- [ ] **Missing required columns**
- [ ] **Alternative date formats**
- [ ] **Multi-year data with multiple DST transitions**
- [ ] **Randomly ordered timestamps**
- [ ] **Missing import/export rows**
- [ ] **Large file handling**
- [ ] **Empty CSV file**
- [ ] **CSV with only headers**
- [ ] **Malformed CSV (unclosed quotes, etc.)**

#### PostgreSQL Exporter (`src/adapters/postgres_exporter.py`)
- [ ] **Timezone preservation in SQL**
- [ ] **Invalid table names**
- [ ] **Very large datasets (SQL size limits)**
- [ ] **Special characters in data**
- [ ] **Empty series SQL generation**

#### Graph Plotter (`src/adapters/graph_plotter.py`)
- [ ] **Spline with <4 data points**
- [ ] **Rolling window larger than dataset**
- [ ] **Invalid smoothing parameters**
- [ ] **Output directory permissions**
- [ ] **Disk full scenarios**
- [ ] **Very large datasets (memory)**

#### Main Entry Point (`src/main.py`)
- [ ] **Invalid CLI argument combinations**
- [ ] **File permission errors**
- [ ] **Invalid timezones**
- [ ] **Date filter edge cases (inclusive/exclusive)**

### 4.2 Missing Integration Tests

- [ ] **End-to-end CSV → SQL → Verify output**
- [ ] **End-to-end CSV → Graphs → Verify image correctness**
- [ ] **Multi-year data processing**
- [ ] **Large file (1M+ readings) performance**
- [ ] **Billing calculation on real data scenarios**
- [ ] **CLI with all options combined**

### 4.3 Missing Error Recovery Tests

- [ ] **Partial CSV read failure recovery**
- [ ] **Graph generation failure doesn't stop SQL export**
- [ ] **Invalid tariff configuration handling**

---

## 5. Security & Performance Concerns

### 5.1 Security

| ID | Severity | Issue | Location |
|---|---|---|---|
| SEC-1 | 🟠 Medium | SQL injection risk (theoretical) | `postgres_exporter.py:36-40` |
| SEC-2 | 🔵 Low | No input file size limits | `csv_ingester.py:42` |
| SEC-3 | 🔵 Low | Path traversal via output paths | `main.py:19,23` |

### 5.2 Performance

| ID | Severity | Issue | Impact |
|---|---|---|---|
| PERF-1 | 🟡 Medium | Entire CSV loaded into memory | Large files →  OOM |
| PERF-2 | 🟡 Medium | Single SQL statement for all data | Large datasets → slow |
| PERF-3 | 🔵 Low | No graph caching mechanism | Regenerates same graph |
| PERF-4 | 🔵 Low | DST logic iterates twice | 2x slowdown on DST files |

---

## 6. Code Quality & Maintainability

### 6.1 Documentation
- ✅ Good: Most functions have docstrings
- ⚠️ Missing: Module-level docstrings
- ⚠️ Missing: Example usage in docstrings
- ⚠️ Missing: Public API documentation

### 6.2 Type Hints
- ✅ Good: Most functions have type hints
- ⚠️ Incomplete: Some internal functions lack hints
- ⚠️ Missing: No `mypy` or type checking in CI

### 6.3 Error Messages
- ⚠️ Generic: Many exceptions use default messages
- ⚠️ Missing: Actionable suggestions in errors

### 6.4 Code Duplication
- 🔵 LOW-6: DST handling logic could be extracted to utility
- 🔵 LOW-7: Date/time manipulation repeated across files

---

## 7. Recommendations by Priority

### Immediate (Before Next Release)
1. ✅ Add negative energy validation to `EnergyReading`
2. ✅ Fix standing charge calculation logic
3. ✅ Add CSV column existence validation
4. ✅ Handle "no rate found" error instead of silent skip
5. ✅ Add spline/rolling window size validation

### Short Term (Next Sprint)
6. Add comprehensive error handling to main.py
7. Implement timezone preservation in SQL export
8. Add duplicate timestamp detection
9. Improve DST handling for multi-year files
10. Add file size and memory limit checks

### Medium Term (Next Quarter)
11. Migrate from `pytz` to `zoneinfo`
12. Implement batch SQL generation
13. Add progress indicators for large operations
14. Create integration test suite
15. Setup `mypy` type checking in CI

### Long Term (Backlog)
16. Consider streaming CSV parser for very large files
17. Add graph caching mechanism
18. Implement multi-currency support validation
19. Create comprehensive API documentation
20. Performance benchmarking and optimization

---

## 8. AI-Optimized Issue Reference Format

```
ISSUE-ID: {SEVERITY}-{NUMBER}
FILE: file:///z:/path/to/file.py#Lstart-Lend
CATEGORY: [VALIDATION|LOGIC|EDGE_CASE|SECURITY|PERFORMANCE]
TEST: test_function_name() [MISSING|EXISTS]
PRIORITY: {P0|P1|P2|P3}
BREAKING: {YES|NO}
DIFFICULTY: {TRIVIAL|EASY|MEDIUM|HARD}
```

### Example:
```
ISSUE-ID: CRITICAL-2
FILE: file:///z:/never/vscode/antig/src/domain/billing.py#L87-L114
CATEGORY: LOGIC
TEST: test_standing_charge_exact_24_hours() [MISSING]
PRIORITY: P0
BREAKING: YES
DIFFICULTY: EASY
```

---

## 9. Test Template for Implementation

```python
# Template for missing validation tests
def test_energy_reading_negative_import():
    """Test that negative import energy raises ValueError"""
    with pytest.raises(ValueError, match="import_energy cannot be negative"):
        EnergyReading(
            timestamp=datetime.now(),
            import_energy=-100.0,
            export_energy=0.0
        )

def test_energy_reading_negative_export():
    """Test that negative export energy raises ValueError"""
    with pytest.raises(ValueError, match="export_energy cannot be negative"):
        EnergyReading(
            timestamp=datetime.now(),
            import_energy=0.0,
            export_energy=-50.0
        )
```

---

## Summary Statistics

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Validation Issues | 3 | 2 | 5 | 2 | 12 |
| Logic Errors | 2 | 3 | 4 | 1 | 10 |
| Edge Cases | 0 | 2 | 3 | 2 | 7 |
| Code Quality | 0 | 1 | 0 | 2 | 3 |
| **TOTAL** | **5** | **8** | **12** | **7** | **32** |

**Test Coverage:** 
- Existing tests: 15
- Missing tests: 50+
- Coverage estimate: ~40% of critical paths

---

**Document End**
