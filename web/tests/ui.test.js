/**
 * Tests for web UI functionality
 * Uses Jest framework for JavaScript testing
 */

// Import the functions we're testing
const {
    showStatus,
    showControls,
    showLoader,
    hideLoader,
    showStats,
    generateGraph,
    switchTab,
    switchPlatform,
    processPastedData
} = require('./ui-functions.js');

// Mock DOM elements for testing
beforeEach(() => {
    document.body.innerHTML = `
        <div id="status" class="status"></div>
        <div id="uploadTab" class="tab-content active"></div>
        <div id="pasteTab" class="tab-content"></div>
        <div id="windowsInstructions" class="platform-content active"></div>
        <div id="macInstructions" class="platform-content"></div>
        <textarea id="pasteArea"></textarea>
        <div id="controlsCard" style="display: none;"></div>
        <div id="resultsCard" style="display: none;"></div>
        <div id="statsGrid"></div>
        <div id="loader"></div>
        <div id="graph-container"></div>
        <input id="startDate" type="date">
        <input id="endDate" type="date">
        <button class="tab active"></button>
        <button class="tab"></button>
        <button class="platform-tab active"></button>
        <button class="platform-tab"></button>
    `;
});

describe('Status Display Functions', () => {
    test('showStatus displays info message', () => {
        showStatus('Test message', 'info');
        const status = document.getElementById('status');
        expect(status.textContent).toBe('Test message');
        expect(status.className).toBe('status info');
    });

    test('showStatus displays success message', () => {
        showStatus('Success!', 'success');
        const status = document.getElementById('status');
        expect(status.textContent).toBe('Success!');
        expect(status.className).toBe('status success');
    });

    test('showStatus displays error message', () => {
        showStatus('Error!', 'error');
        const status = document.getElementById('status');
        expect(status.textContent).toBe('Error!');
        expect(status.className).toBe('status error');
    });
});

describe('UI Control Functions', () => {
    test('showControls makes cards visible', () => {
        showControls();
        expect(document.getElementById('controlsCard').style.display).toBe('block');
        expect(document.getElementById('resultsCard').style.display).toBe('block');
    });

    test('showLoader displays loader and clears graph', () => {
        const graphContainer = document.getElementById('graph-container');
        graphContainer.innerHTML = 'Some content';

        showLoader();

        expect(document.getElementById('loader').style.display).toBe('block');
        expect(graphContainer.innerHTML).toBe('');
    });

    test('hideLoader hides loader', () => {
        showLoader(); // First show it
        hideLoader();
        expect(document.getElementById('loader').style.display).toBe('none');
    });
});

describe('Statistics Display', () => {
    test('showStats displays correct values', () => {
        const stats = {
            total_readings: 1000,
            total_import: 123.45,
            total_export: 67.89,
            net_consumption: 55.56
        };

        showStats(stats);

        const statsGrid = document.getElementById('statsGrid');
        expect(statsGrid.style.display).toBe('grid');
        expect(statsGrid.innerHTML).toContain('1,000'); // Localized number
        expect(statsGrid.innerHTML).toContain('123.45');
        expect(statsGrid.innerHTML).toContain('67.89');
        expect(statsGrid.innerHTML).toContain('55.56');
    });

    test('showStats formats numbers with 2 decimals', () => {
        const stats = {
            total_readings: 100,
            total_import: 100,
            total_export: 50,
            net_consumption: 50
        };

        showStats(stats);

        const statsGrid = document.getElementById('statsGrid');
        expect(statsGrid.innerHTML).toContain('100.00');
        expect(statsGrid.innerHTML).toContain('50.00');
    });
});

describe('Tab Switching', () => {
    test('switchTab switches to paste tab', () => {
        // Mock event object
        global.event = { target: document.querySelectorAll('.tab')[1] };

        switchTab('paste');

        expect(document.getElementById('uploadTab').classList.contains('active')).toBe(false);
        expect(document.getElementById('pasteTab').classList.contains('active')).toBe(true);
    });

    test('switchTab switches to upload tab', () => {
        // Start with paste tab active
        document.getElementById('uploadTab').classList.remove('active');
        document.getElementById('pasteTab').classList.add('active');

        global.event = { target: document.querySelectorAll('.tab')[0] };

        switchTab('upload');

        expect(document.getElementById('uploadTab').classList.contains('active')).toBe(true);
        expect(document.getElementById('pasteTab').classList.contains('active')).toBe(false);
    });
});

describe('Platform Switching', () => {
    test('switchPlatform switches to Mac instructions', () => {
        global.event = { target: document.querySelectorAll('.platform-tab')[1] };

        switchPlatform('mac');

        expect(document.getElementById('windowsInstructions').classList.contains('active')).toBe(false);
        expect(document.getElementById('macInstructions').classList.contains('active')).toBe(true);
    });

    test('switchPlatform switches to Windows instructions', () => {
        // Start with Mac active
        document.getElementById('windowsInstructions').classList.remove('active');
        document.getElementById('macInstructions').classList.add('active');

        global.event = { target: document.querySelectorAll('.platform-tab')[0] };

        switchPlatform('windows');

        expect(document.getElementById('windowsInstructions').classList.contains('active')).toBe(true);
        expect(document.getElementById('macInstructions').classList.contains('active')).toBe(false);
    });
});

describe('Paste Data Processing', () => {
    test('processPastedData shows error when textarea is empty', () => {
        document.getElementById('pasteArea').value = '';

        processPastedData();

        const status = document.getElementById('status');
        expect(status.textContent).toContain('Please paste your CSV data first');
        expect(status.className).toContain('error');
    });

    test('processPastedData validates CSV format', () => {
        document.getElementById('pasteArea').value = 'Not CSV data - no commas or newlines';

        processPastedData();

        const status = document.getElementById('status');
        expect(status.textContent).toContain('doesn\'t look like CSV data');
        expect(status.className).toContain('error');
    });

    test('processPastedData accepts valid CSV format', () => {
        const validCSV = 'MPRN,Value,Type\n12345,1.0,Import\n12345,0.5,Export';
        document.getElementById('pasteArea').value = validCSV;

        // Mock window.processCSV
        window.processCSV = jest.fn();

        processPastedData();

        expect(window.processCSV).toHaveBeenCalledWith(validCSV, 'pasted-data.csv');
    });

    test('processPastedData waits for PyScript if not loaded', () => {
        jest.useFakeTimers();

        const validCSV = 'MPRN,Value\n12345,1.0';
        document.getElementById('pasteArea').value = validCSV;

        // PyScript not loaded yet
        window.processCSV = undefined;

        processPastedData();

        const status = document.getElementById('status');
        expect(status.textContent).toContain('PyScript is still loading');

        // Verify setTimeout was called
        expect(setTimeout).toHaveBeenCalledTimes(1);

        jest.useRealTimers();
    });
});

describe('Graph Generation', () => {
    test('generateGraph calls Python function with dates', () => {
        window.generateGraphPython = jest.fn();

        document.getElementById('startDate').value = '2025-01-01';
        document.getElementById('endDate').value = '2025-12-31';

        generateGraph();

        expect(window.generateGraphPython).toHaveBeenCalledWith('2025-01-01', '2025-12-31');
    });

    test('generateGraph handles missing Python function gracefully', () => {
        window.generateGraphPython = undefined;

        // Should not throw error
        expect(() => generateGraph()).not.toThrow();
    });
});

describe('Integration Tests', () => {
    test('Full workflow: paste data → process → show controls', () => {
        const validCSV = 'MPRN,Value,Type\n12345,1.0,Import';
        document.getElementById('pasteArea').value = validCSV;

        window.processCSV = jest.fn();

        // User pastes and processes
        processPastedData();

        // Python should be called
        expect(window.processCSV).toHaveBeenCalled();

        // Simulate successful processing
        showControls();
        showStatus('Loaded successfully', 'success');

        // Controls should be visible
        expect(document.getElementById('controlsCard').style.display).toBe('block');
        expect(document.getElementById('resultsCard').style.display).toBe('block');

        // Status should show success
        expect(document.getElementById('status').textContent).toContain('Loaded successfully');
    });

    test('Error workflow: invalid CSV → show error', () => {
        document.getElementById('pasteArea').value = 'Invalid data';

        processPastedData();

        const status = document.getElementById('status');
        expect(status.className).toContain('error');

        // Controls should still be hidden
        expect(document.getElementById('controlsCard').style.display).toBe('none');
    });
});
