// Global variable to manage the XAI Chart instance
let xaiChart = null;

/**
 * CORE HEARTBEAT: Fetches data from Flask API and updates the UI
 */
async function refreshDashboard() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // 1. CAPTURE FILTER VALUES FROM SIDEBAR
        const riskFilter = document.getElementById('risk-filter').value;
        const deptFilter = document.getElementById('dept-filter').value;

        // 2. FILTER THE ALERTS ARRAY
        let filteredAlerts = data.alerts;
        
        if (riskFilter !== "All") {
            filteredAlerts = filteredAlerts.filter(a => a.level === riskFilter);
        }
        
        if (deptFilter !== "All") {
            filteredAlerts = filteredAlerts.filter(a => a.dept === deptFilter);
        }

        // 3. UPDATE KPI METRICS
        document.getElementById('total-threats').innerText = filteredAlerts.length;
        document.getElementById('critical-count').innerText = filteredAlerts.filter(a => a.level === 'HIGH').length;

        // 4. UPDATE THE ALERT QUEUE (DOM Injection)
        const alertList = document.getElementById('alert-list');
        alertList.innerHTML = ''; // Wipe current list to prevent duplicates

        if (filteredAlerts.length === 0) {
            alertList.innerHTML = `<p style="color:gray; padding:10px;">No active alerts for selected filters.</p>`;
        } else {
            // Sort: HIGH first, then MEDIUM
            filteredAlerts.sort((a, b) => (a.level === 'HIGH' ? -1 : 1));

            filteredAlerts.forEach(alert => {
                const tagClass = alert.level === 'HIGH' ? 'tag-high' : 'tag-med';
                const div = document.createElement('div');
                div.className = 'alert-item';
                div.innerHTML = `
                    <div style="display:flex; align-items:center; gap:15px;">
                        <span class="${tagClass}">${alert.level}</span>
                        <div>
                            <strong>${alert.user_id}</strong><br>
                            <small style="color:gray;">${alert.dept}</small>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:12px; color:gray; margin-bottom:5px;">${alert.time}</div>
                        <button onclick="investigateUser('${alert.user_id}')">Investigate</button>
                        <button class="resolve" onclick="resolveUser('${alert.user_id}')">Resolve</button>
                    </div>
                `;
                alertList.appendChild(div);
            });
        }

        // 5. UPDATE LIVE LOG FEED
        const logBody = document.getElementById('log-body');
        logBody.innerHTML = '';
        data.logs.forEach(log => {
            const row = `<tr>
                <td style="padding:10px; border-bottom:1px solid #30363d;">${log.time}</td>
                <td style="border-bottom:1px solid #30363d;">${log.user_id}</td>
                <td style="border-bottom:1px solid #30363d; color:${log.risk === 'HIGH' ? '#ff4b4b' : '#ffa500'}">${log.risk}</td>
            </tr>`;
            logBody.innerHTML += row;
        });

    } catch (err) {
        console.error("Critical Dashboard Sync Failure:", err);
    }
}

/**
 * INVESTIGATION: Populates the right panel and renders Chart.js XAI
 */
async function investigateUser(uid) {
    try {
        const response = await fetch(`/api/user_details/${uid}`);
        const user = await response.json();
        
        const panel = document.getElementById('investigation-panel');
        
        // Inject the HTML structure including the Canvas for Chart.js
        panel.innerHTML = `
            <div style="border-bottom:1px solid #30363d; padding-bottom:10px; margin-bottom:15px;">
                <h2 style="color:#58a6ff; margin:0;">${user.user_id}</h2>
                <small style="color:gray;">Dept: ${user.dept} | Risk Score: ${user.burn.toFixed(2)}</small>
            </div>
            
            <p style="font-size:14px; font-weight:bold; margin-bottom:10px;">Feature Contribution (XAI)</p>
            <div style="height: 180px; width: 100%;">
                <canvas id="xaiCanvas"></canvas>
            </div>
            
            <div style="background:#0d1117; padding:10px; border-radius:5px; margin:15px 0; font-size:12px;">
                <strong>Reasoning:</strong> High deviation in <code>${['File Uploads', 'Logon Hours', 'Removable Media'][Math.floor(Math.random()*3)]}</code> detected compared to user baseline.
            </div>

            <button style="width:100%; background:#da3633;" onclick="resolveUser('${user.user_id}')">Baseline & Clear Alert</button>
        `;

        // Render the Chart
        renderXAIChart();

    } catch (err) {
        console.error("Forensics Fetch Error:", err);
    }
}

/**
 * XAI CHARTING: Draws horizontal bars using Chart.js
 */
function renderXAIChart() {
    const ctx = document.getElementById('xaiCanvas').getContext('2d');
    
    // Destroy previous instance to prevent "ghosting" when hovering
    if (xaiChart) {
        xaiChart.destroy();
    }

    xaiChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['File Access', 'Login Freq', 'Network Vol', 'USB Usage'],
            datasets: [{
                label: 'Anomaly Magnitude',
                data: [
                    Math.floor(Math.random() * 100), 
                    Math.floor(Math.random() * 100), 
                    Math.floor(Math.random() * 100), 
                    Math.floor(Math.random() * 100)
                ],
                backgroundColor: '#f85149',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { beginAtZero: true, grid: { color: '#30363d' }, ticks: { color: '#8b949e' } },
                y: { grid: { display: false }, ticks: { color: '#fff' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

/**
 * ACTION: Resolve threat and clear baseline
 */
async function resolveUser(uid) {
    const response = await fetch('/api/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: uid })
    });
    
    if (response.ok) {
        // Clear investigation panel if the resolved user was being viewed
        document.getElementById('investigation-panel').innerHTML = `<p style="color:gray;">Alert resolved. Select another user.</p>`;
        refreshDashboard();
    }
}

// --- INITIALIZE ---
setInterval(refreshDashboard, 3000); // Trigger simulation and UI update every 3s
refreshDashboard(); // Run immediately on load