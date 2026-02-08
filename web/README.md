# Energy Stats Processor - Web Edition

A single-page web application that runs your Python code directly in the browser using PyScript.

## Features

- ✅ **No Server Required** - Runs entirely in your browser
- ✅ **Privacy First** - Data never leaves your computer
- ✅ **Zero Code Duplication** - Uses existing Python codebase
- ✅ **Modern UI** - Clean, responsive design
- ✅ **Full Functionality** - Upload CSV, filter by date, generate graphs

## How to Use

1. **Open** [`index.html`](file:///z:/never/vscode/antig/web/index.html) in your browser
2. **Upload** your ESB Networks CSV file (drag & drop or click)
3. **Select** date range (optional)
4. **View** your energy usage graph and statistics

## Architecture

This web app uses **PyScript** to run Python directly in the browser:

- **HTML/CSS/JS**: User interface only (`index.html`)
- **Python**: Business logic (`energy_processor_web.py`)
- **Existing Code**: Imports from `../src/domain/` (zero duplication!)

```
web/
├── index.html                   # UI (HTML + CSS + JS)
└── energy_processor_web.py      # Python bridge
    ↓ imports from
    ../src/domain/
    ├── models.py                # Source of truth!
    ├── billing.py
    └── tariff.py
```

## Technical Details

- **Framework**: PyScript 2024.1.1
- **Python Packages**: pandas, matplotlib, numpy
- **Code Reuse**: Imports `EnergySeries`, `EnergyReading` from existing codebase
- **Load Time**: ~5-10 seconds (one-time download of Python runtime)
- **File Size**: ~15MB total (cached after first load)

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 90+
- ✅ Edge 90+
- ✅ Safari 15+

## Limitations

- First load requires internet (to download PyScript and packages)
- Processing large files (100K+ rows) may be slower than native Python
- Graphs are limited to matplotlib capabilities in Pyodide

## Benefits vs CLI

| Feature | CLI | Web App |
|---------|-----|---------|
| Installation | Python + deps required | Just open HTML |
| Platform | Windows/Mac/Linux | Any browser |
| Privacy | Local | Local (better!) |
| Speed | Fast | Moderate |
| User-Friendly | Technical users | Everyone |
| Updates | Manual | Automatic |

## Development

No build process needed! Just edit:
- `index.html` for UI changes
- `energy_processor_web.py` for Python logic
- `../src/domain/*.py` for core business logic (affects both CLI and web!)

---

**Created by Tavi** (Google Antigravity AI)
