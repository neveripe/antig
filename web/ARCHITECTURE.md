# How PyScript Achieves Zero Code Duplication

This document explains how the web application achieves **TRUE** zero code duplication while maintaining Python as the source of truth.

## Architecture

```
energy-stats-processor/
├── src/                           # SOURCE OF TRUTH (Python)
│   ├── domain/
│   │   ├── models.py             ← Shared by CLI & Web
│   │   ├── billing.py            ← Shared by CLI & Web
│   │   └── tariff.py             ← Shared by CLI & Web
│   ├── adapters/
│   │   ├── csv_ingester.py       ← Used by CLI only
│   │   └── graph_plotter.py      ← Used by CLI only
│   └── main.py                    ← CLI entry point
│
├── web/
│   ├── index.html                 ← UI only (HTML/CSS/JS)
│   └── energy_processor_web.py    ← Thin adapter for browser
│
└── tests/                         ← Tests shared logic
```

## Code Reuse Strategy

### ✅ **Shared (100% reuse)**
- `src/domain/models.py` - `EnergySeries`, `EnergyReading` classes
- `src/domain/billing.py` - `CostCalculator`, billing logic
- `src/domain/tariff.py` - `Tariff`, `TariffRate` models

These files are **imported directly** by the web app using:
```python
# In web/energy_processor_web.py
from src.domain.models import EnergySeries, EnergyReading
```

PyScript loads the actual Python files - no transpilation, no duplication!

### 🔄 **Adapted (logic reused, I/O different)**
- CSV parsing: Same algorithm, different I/O (FileReader API vs file system)
- Graphing: Same data processing, different rendering (matplotlib in browser vs PNG files)

### ⚡ **Web-only**
- UI components (`index.html`)
- JavaScript bridge code (minimal, only for DOM manipulation)

## How PyScript Works

1. **Browser downloads PyScript** (~5MB, cached)
2. **PyScript includes Pyodide** (Python compiled to WebAssembly)
3. **Pyodide downloads packages** (pandas, matplotlib, numpy)
4. **Your Python code runs natively** in the browser JavaScript VM

### The Magic:
```html
<!-- index.html -->
<script type="py" src="./energy_processor_web.py"></script>
```

This literally runs `energy_processor_web.py` as Python!

```python
# energy_processor_web.py
import sys
sys.path.append('..')

from src.domain.models import EnergySeries  # Actual import!
```

PyScript's module loader fetches `../src/domain/models.py` and runs it in the browser.

## Example: Creating an EnergyReading

### CLI (main.py):
```python
from src.domain.models import EnergyReading

reading = EnergyReading(
    timestamp=datetime.now(),
    import_energy=10.0,
    export_energy=5.0
)
```

### Web (energy_processor_web.py):
```python
from src.domain.models import EnergyReading  # SAME IMPORT!

reading = EnergyReading(
    timestamp=datetime.now(),
    import_energy=10.0,
    export_energy=5.0
)
```

**Same class, same file, zero duplication.** ✅

## What Gets Adapted

Only **I/O adapters** differ:

| Function | CLI | Web | Shared Logic |
|----------|-----|-----|--------------|
| Read CSV | `open(file)` | `FileReader API` | ✅ Parsing algorithm |
| Save graph | `plt.savefig()` | `display(plt)` | ✅ Chart configuration |
| Print stats | `print()` | `window.showStats()` | ✅ Calculation logic |

The **business logic** (what to calculate, how to process data) is 100% shared.

## Benefits

1. **Single Source of Truth**: Fix a bug in `models.py` → fixed everywhere
2. **Guaranteed Consistency**: CLI and web use identical domain logic
3. **Easier Maintenance**: Only one codebase to maintain
4. **Better Testing**: Tests validate both CLI and web behavior

## Trade-offs

- **Load Time**: 5-10 seconds on first visit (Python runtime download)
- **File Size**: ~15MB total (but cached by browser)
- **Performance**: Slower than native Python for very large files
- **Browser Requirement**: Needs modern browser (not a real limitation in 2026)

## Comparison to Alternatives

### ❌ Manual JavaScript Rewrite
```javascript
// Would need to duplicate models.py logic:
class EnergyReading {
    constructor(timestamp, importEnergy, exportEnergy) {
        this.timestamp = timestamp;
        this.importEnergy = importEnergy;
        this.exportEnergy = exportEnergy;
    }
}
```
**Problem**: Now have Python AND JavaScript versions. Changes must be synced manually.

### ❌ Code Generation
```python
# generate_js.py
def convert_python_to_js(python_file):
    # Parse Python AST
    # Generate JavaScript
    pass
```
**Problem**: Two codebases exist (Python source + generated JS). Build step required.

### ✅ PyScript
```python
# models.py - ONE FILE, used by both CLI and web
@dataclass
class EnergyReading:
    timestamp: datetime
    import_energy: float
    export_energy: float
```
**Solution**: True single source of truth. Python runs everywhere.

## Future Improvements

- [ ] Preload common packages for faster startup
- [ ] Add service worker for offline mode
- [ ] Bundle PyScript locally to avoid CDN dependency
- [ ] Optimize for large files using Web Workers

---

**Conclusion**: PyScript enables true code reuse by running Python natively in the browser. This isn't code generation or transpilation - it's the actual Python code executing in a WebAssembly-based Python interpreter.
