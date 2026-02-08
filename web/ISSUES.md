# Web Application Issues & Fixes

## Critical Issues Found

### Issue 1: PyScript File Loading ❌
**Problem:** `<script type="py" src="./energy_processor_web.py">` doesn't work with `file://` protocol
**Impact:** Python code never loads, paste functionality doesn't work at all

### Issue 2: Import from `src/` Fails ❌  
**Problem:** `from src.domain.models import EnergySeries` requires file system access
**Impact:** Even if Python loads, imports fail due to CORS

### Issue 3: No Large File Handling ❌
**Problem:** 6MB CSV (18,000+ rows) will freeze browser
**Impact:** Poor user experience, potential browser crash

---

## Solution: Self-Contained HTML

Create a single HTML file with:
1. ✅ Python code embedded inline (no external file loading)
2. ✅ Domain models copied inline (no imports)
3. ✅ Large file progress indicator
4. ✅ Chunked processing for big datasets

This sacrifices "zero duplication" principle but is the **only way** to make it work as a local `file://` HTML file.

---

## Alternative: Simple HTTP Server Required

If maintaining zero duplication is critical:
- User must serve via HTTP server (e.g., `python -m http.server`)
- Cannot open directly as `file://`
- PyScript can then fetch files properly

**Recommendation:** Create self-contained version for ease of use.
