# Bundled Web Application - Manual Verification Guide

## 🎯 What to Test

The bundled web application should now be open in your browser. This guide will help you verify it works correctly with the `file://` protocol.

---

## ✅ Step-by-Step Verification

### 1. Initial Page Load

**What to check:**
- Page displays the title "Energy Data Processor"
- Two tabs are visible: "📁 Upload CSV" and "📋 Paste Data"
- No JavaScript errors in browser console (press F12 to check)

**Expected behavior:**
- ✅ Clean page load with no errors
- ✅ Professional UI with dark theme

---

### 2. PyScript Initialization

**What to check:**
- Wait 5-10 seconds after page load
- Look for the status indicator at the top of the page
- Status should change from loading to ready

**Expected status message:**
```
✅ Ready to process your energy data
```

**If you see errors:**
- Check browser console (F12) for PyScript errors
- Verify the file opened with `file://` protocol (not `http://`)

---

### 3. Tab Switching

**What to test:**
- Click on "📋 Paste Data" tab
- Click back to "📁 Upload CSV" tab
- Repeat several times

**Expected behavior:**
- ✅ Active tab highlights in blue
- ✅ Content area switches between upload and paste sections
- ✅ Smooth transitions with no errors

---

### 4. CSV Paste Processing

This is the **most important test** - the paste functionality was previously broken with `file://` protocol.

**Test data to use:**
```csv
timestamp,import_kwh,export_kwh
2024-01-01 00:00:00,0.5,0.0
2024-01-01 00:30:00,0.6,0.1
2024-01-01 01:00:00,0.4,0.2
2024-01-01 01:30:00,0.7,0.0
2024-01-01 02:00:00,0.5,0.1
```

**Steps:**
1. Click "📋 Paste Data" tab
2. Paste the test data above into the text area
3. Click "✅ Process Pasted Data" button
4. Wait 2-3 seconds for processing

**Expected results:**
- ✅ Status shows: "✅ Data processed successfully! 5 readings loaded."
- ✅ Controls card appears with date range inputs
- ✅ Graph is generated below the controls
- ✅ Statistics show correct values

**If processing fails:**
- Check browser console for errors
- Verify PyScript initialized properly (step 2)
- Check that domain models are inlined (run verification command below)

---

### 5. Graph Verification

**What to check:**
- Graph displays with two lines (Import and Export)
- X-axis shows timestamps
- Y-axis shows energy values (kWh)
- Legend is visible

**Expected behavior:**
- ✅ Interactive graph with Plotly controls
- ✅ Can zoom, pan, and hover over data points
- ✅ Import line shows values: 0.5, 0.6, 0.4, 0.7, 0.5
- ✅ Export line shows values: 0.0, 0.1, 0.2, 0.0, 0.1

---

## 🔍 Technical Verification

If everything works, verify the bundled file is truly self-contained:

```powershell
# Check that domain models are inlined
Select-String -Path "Z:\never\vscode\antig\web\dist\index.html" -Pattern "class EnergySeries"

# Check that web processor is inlined
Select-String -Path "Z:\never\vscode\antig\web\dist\index.html" -Pattern "class WebCSVIngester"

# Verify no external imports remain
Select-String -Path "Z:\never\vscode\antig\web\dist\index.html" -Pattern "from src.domain.models"
```

**Expected results:**
- ✅ `EnergySeries` found in bundled HTML
- ✅ `WebCSVIngester` found in bundled HTML
- ✅ Import statement replaced with comment (not actual import)

---

## 📊 Test Results

Please report back with your findings:

1. **Did the page load successfully?** (Yes/No)
2. **Did PyScript initialize?** (Status message shown)
3. **Do tabs switch correctly?** (Yes/No)
4. **Did CSV paste work?** (Yes/No - most critical!)
5. **Did the graph generate?** (Yes/No)
6. **Any errors or issues?** (Describe)

---

## 🐛 Common Issues

### Issue: PyScript never finishes loading
**Solution:** Check internet connection - PyScript CDN needs to download packages (pandas, matplotlib, numpy)

### Issue: "Module not found" error
**Solution:** Build script may have failed - rebuild with `python web/build.py`

### Issue: CSV paste doesn't work
**Solution:** This likely means external imports weren't properly inlined - check technical verification above

### Issue: Graph doesn't appear
**Solution:** Check browser console for Matplotlib/Plotly errors

---

## 🎉 Success Criteria

All of these must pass:
- ✅ Page loads with `file://` protocol
- ✅ PyScript initializes successfully
- ✅ Tabs switch without errors
- ✅ CSV paste processing works
- ✅ Graph generates correctly
- ✅ No external file references remain
