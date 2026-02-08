/**
 * UI functions for Energy Processor Web Application
 * These functions are extracted from index.html for testing purposes
 */

function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
}

function showControls() {
    document.getElementById('controlsCard').style.display = 'block';
    document.getElementById('resultsCard').style.display = 'block';
}

function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('graph-container').innerHTML = '';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

function showStats(stats) {
    const statsGrid = document.getElementById('statsGrid');
    statsGrid.style.display = 'grid';
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Total Readings</div>
            <div class="stat-value">${stats.total_readings.toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Import</div>
            <div class="stat-value">${stats.total_import.toFixed(2)} kWh</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Total Export</div>
            <div class="stat-value">${stats.total_export.toFixed(2)} kWh</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Net Consumption</div>
            <div class="stat-value">${stats.net_consumption.toFixed(2)} kWh</div>
        </div>
    `;
}

function generateGraph() {
    if (window.generateGraphPython) {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        window.generateGraphPython(startDate, endDate);
    }
}

// Tab switching
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    document.getElementById('uploadTab').classList.remove('active');
    document.getElementById('pasteTab').classList.remove('active');

    if (tab === 'upload') {
        document.getElementById('uploadTab').classList.add('active');
    } else {
        document.getElementById('pasteTab').classList.add('active');
    }
}

// Platform instructions switching
function switchPlatform(platform) {
    // Update platform buttons
    document.querySelectorAll('.platform-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update instructions
    document.getElementById('windowsInstructions').classList.remove('active');
    document.getElementById('macInstructions').classList.remove('active');

    if (platform === 'windows') {
        document.getElementById('windowsInstructions').classList.add('active');
    } else {
        document.getElementById('macInstructions').classList.add('active');
    }
}

// Process pasted data
function processPastedData() {
    const pasteArea = document.getElementById('pasteArea');
    const content = pasteArea.value.trim();

    if (!content) {
        showStatus('❌ Please paste your CSV data first', 'error');
        return;
    }

    // Validate it looks like CSV
    if (!content.includes(',') || !content.includes('\n')) {
        showStatus('❌ This doesn\'t look like CSV data. Make sure you copied the entire file content!', 'error');
        return;
    }

    showStatus('⏳ Processing pasted data...', 'info');

    // Call Python function with pasted content
    if (window.processCSV) {
        window.processCSV(content, 'pasted-data.csv');
    } else {
        showStatus('PyScript is still loading, please wait a moment...', 'info');
        setTimeout(() => processPastedData(), 1000);
    }
}

// Export for testing (if running in Node/Jest)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showStatus,
        showControls,
        showLoader,
        hideLoader,
        showStats,
        generateGraph,
        switchTab,
        switchPlatform,
        processPastedData
    };
}
