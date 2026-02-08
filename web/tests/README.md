# JavaScript Testing Setup

## Prerequisites

You need Node.js and npm installed to run the JavaScript tests.

### Installing Node.js

1. Download Node.js from: https://nodejs.org/
2. Install the LTS (Long Term Support) version
3. Verify installation:
   ```powershell
   node --version
   npm --version
   ```

## Running the Tests

Once Node.js is installed:

```powershell
cd Z:\never\vscode\antig\web

# Install test dependencies (first time only)
npm install

# Run the tests
npm test
```

## What We Set Up

The test infrastructure is ready with:

1. **package.json** - Jest configuration and dependencies
2. **tests/ui-functions.js** - Extracted JavaScript functions from index.html
3. **tests/ui.test.js** - Test suite (already existed, now imports functions)

The tests cover:
- ✅ Status message display (info, success, error)
- ✅ UI control visibility
- ✅ Statistics display and formatting
- ✅ Tab switching (upload/paste)
- ✅ Platform switching (Windows/Mac)
- ✅ Paste data validation
- ✅ Graph generation
