# Build Script for Self-Contained Web Application

## Background

The current web application uses PyScript with external file references:
- `<script type="py" src="./energy_processor_web.py">` in `index.html`
- `from src.domain.models import EnergySeries, EnergyReading` in `energy_processor_web.py`

These external references fail when opening `index.html` as `file://` due to browser security restrictions (CORS), breaking all functionality including CSV paste processing.

## Solution Overview

Create a build script that generates a self-contained HTML file with all Python code inlined, while maintaining **zero code duplication in source files**. Users only edit source files; the bundled version is 100% auto-generated.

## Proposed Changes

### Build System

#### [NEW] [build.py](file:///Z:/never/vscode/antig/web/build.py)
Python script that:
1. Reads `index.html` as a template
2. Reads `energy_processor_web.py` for web-specific Python code
3. Reads `src/domain/models.py` for domain models
4. Combines them into a single HTML file with inline Python
5. Outputs to `web/dist/index.html`

**Key features:**
- Simple string replacement approach (no complex templating)
- Replace `<script type="py" src="./energy_processor_web.py">` with inline `<script type="py">...</script>`
- Inline domain models before the web processor code
- Remove import statement that references external `src/` directory

---

### Source File Changes

#### [MODIFY] [index.html](file:///Z:/never/vscode/antig/web/index.html)
- Change line 530 from external script reference to a placeholder comment
- Add comment: `<!-- BUILD_INJECT_PYTHON_HERE -->`
- This makes it clear this is a template that needs building

**Note:** The template file won't work directly, users must run build script

---

### Output

#### [NEW] web/dist/ directory
Generated output directory containing:
- `index.html` - Self-contained bundled file ready for `file://` usage
- `.gitignore` - Ensure dist/ is not committed (it's generated)

---

## Verification Plan

### Automated Tests

**Test 1: JavaScript UI Tests (Existing)**
```powershell
cd Z:\never\vscode\antig\web\tests
npm test
```
These tests verify tab switching, paste functionality, and status messages work correctly.

**Test 2: Python Unit Tests (Existing)**
```powershell
cd Z:\never\vscode\antig
pytest tests/test_web_ingester.py -v
```
Verifies `WebCSVIngester` logic matches the original CSV ingester behavior.

### Build Script Testing

**Test 3: Build Script Execution**
```powershell
cd Z:\never\vscode\antig\web
python build.py
```
Should successfully create `web/dist/index.html` without errors.

**Test 4: Verify Inlined Content**
Manual inspection of `web/dist/index.html` to confirm:
- Contains domain models code (search for `class EnergySeries`)
- Contains web processor code (search for `class WebCSVIngester`)
- No external `src=` references in PyScript tags
- No import statements referencing `src/domain/models`

### Manual Browser Testing

**Test 5: File Protocol Functionality**
1. Run build script: `python web/build.py`
2. Open `web/dist/index.html` in browser using `file://` protocol (double-click or File > Open)
3. Switch to "Paste Data" tab
4. Paste sample CSV data from existing test files
5. Click "Process Pasted Data" button
6. Verify:
   - Status message shows success (not PyScript loading error)
   - Controls card appears with date inputs
   - Graph is generated
   - Stats show correct values
