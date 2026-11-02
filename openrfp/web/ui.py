"""Single-page Dashboard User Interface for OpenRFP."""


def get_dashboard_html() -> str:
    """Return the interactive HTML/CSS/JS dashboard string."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRFP | Autonomous Proposal & RFP Response Agent</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --green: #10b981;
            --amber: #f59e0b;
            --red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text-main); line-height: 1.5; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header h1 { font-size: 22px; font-weight: 700; color: #0284c7; }
        .grid { display: grid; grid-template-columns: 350px 1fr; gap: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card h2 { font-size: 16px; margin-bottom: 12px; color: var(--text-main); }
        label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; color: var(--text-muted); }
        input, textarea, select { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 12px; font-size: 13px; }
        textarea { height: 160px; font-family: monospace; resize: vertical; }
        button { background: var(--primary); color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; width: 100%; transition: background 0.15s; }
        button:hover { background: var(--primary-hover); }
        .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text-main); width: auto; padding: 6px 12px; font-size: 12px; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
        .stat-card { background: #f1f5f9; padding: 12px; border-radius: 6px; text-align: center; }
        .stat-val { font-size: 20px; font-weight: 700; }
        .val-green { color: var(--green); }
        .val-amber { color: var(--amber); }
        .val-red { color: var(--red); }
        .val-score { color: var(--primary); }
        .stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
        th, td { padding: 10px 12px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
        th { background: #f8fafc; font-weight: 600; color: var(--text-muted); }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; color: white; }
        .badge-green { background: var(--green); }
        .badge-amber { background: var(--amber); }
        .badge-red { background: var(--red); }
        .filter-row { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }
        .tab-btn { background: #e2e8f0; color: var(--text-main); border: none; padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; }
        .tab-btn.active { background: var(--primary); color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRFP Agent</h1>
        <div><span style="font-size:12px; color:var(--text-muted);">Enterprise Autonomous Response System</span></div>
    </div>
    <div class="grid">
        <div class="card">
            <h2>Process Solicitation</h2>
            <label for="buyerName">Buyer / Client Name</label>
            <input type="text" id="buyerName" value="Acme Enterprise" placeholder="e.g. Acme Corp">
            <label for="rfpTitle">RFP Solicitation Title</label>
            <input type="text" id="rfpTitle" value="Global Cloud Security Platform" placeholder="e.g. Cloud Security RFP">
            <label for="rfpText">Solicitation Text or Markdown</label>
            <textarea id="rfpText" placeholder="Paste RFP requirements here..."># Section 1: Security & Compliance
* REQ-001: Vendor must provide SOC 2 Type II and ISO 27001 certifications.
* REQ-002: System must encrypt data at rest using AES-256 and TLS 1.3 in transit.
* REQ-003: Must support SAML 2.0 and SCIM user provisioning.

# Section 2: Technical Architecture
* REQ-004: Platform must guarantee 99.99% monthly availability with financially-backed SLA.
* REQ-005: Must provide REST APIs and webhooks for SIEM log streaming.</textarea>
            <button onclick="handleProcessRfp()" id="processBtn">Shred & Synthesize Proposal</button>
        </div>
        <div>
            <div class="card" id="metricsCard" style="display:none; margin-bottom:20px;">
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-val val-score" id="scoreVal">--%</div><div class="stat-label">Win Readiness</div></div>
                    <div class="stat-card"><div class="stat-val val-green" id="greenVal">0</div><div class="stat-label">Verified (Green)</div></div>
                    <div class="stat-card"><div class="stat-val val-amber" id="amberVal">0</div><div class="stat-label">Review (Amber)</div></div>
                    <div class="stat-card"><div class="stat-val val-red" id="redVal">0</div><div class="stat-label">Gaps (Red)</div></div>
                </div>
                <div style="font-size:13px; color:var(--text-muted); margin-bottom:8px;" id="execSummary"></div>
            </div>
            <div class="card">
                <div class="filter-row">
                    <h2>Compliance Matrix</h2>
                    <div style="margin-left:auto; display:flex; gap:6px;">
                        <button class="tab-btn active" onclick="setFilter('ALL')">All</button>
                        <button class="tab-btn" onclick="setFilter('GREEN')">Green</button>
                        <button class="tab-btn" onclick="setFilter('AMBER')">Amber</button>
                        <button class="tab-btn" onclick="setFilter('RED')">Red</button>
                    </div>
                </div>
                <table id="matrixTable">
                    <thead><tr><th>ID</th><th>Requirement</th><th>Confidence</th><th>Draft Response</th></tr></thead>
                    <tbody id="matrixBody"><tr><td colspan="4" style="text-align:center; color:var(--text-muted);">Paste or upload an RFP on the left to generate the matrix.</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        let currentDrafts = [];
        let activeFilter = 'ALL';
        async function handleProcessRfp() {
            const btn = document.getElementById('processBtn');
            btn.innerText = "Analyzing & Drafting...";
            btn.disabled = true;
            try {
                const res = await fetch('/api/v1/rfp/parse-and-draft', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        title: document.getElementById('rfpTitle').value,
                        buyer_name: document.getElementById('buyerName').value,
                        raw_text: document.getElementById('rfpText').value
                    })
                });
                const data = await res.json();
                renderResults(data);
            } catch (err) {
                alert("Failed to process RFP: " + err);
            } finally {
                btn.innerText = "Shred & Synthesize Proposal";
                btn.disabled = false;
            }
        }
        function renderResults(data) {
            document.getElementById('metricsCard').style.display = 'block';
            document.getElementById('scoreVal').innerText = data.win_probability_score + '%';
            document.getElementById('greenVal').innerText = data.gap_report.green_count;
            document.getElementById('amberVal').innerText = data.gap_report.amber_count;
            document.getElementById('redVal').innerText = data.gap_report.red_count;
            document.getElementById('execSummary').innerText = data.executive_summary;
            currentDrafts = data.drafts || [];
            applyFilter();
        }
        function setFilter(filter) {
            activeFilter = filter;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.innerText.toUpperCase() === filter);
            });
            applyFilter();
        }
        function applyFilter() {
            const tbody = document.getElementById('matrixBody');
            tbody.innerHTML = '';
            const filtered = currentDrafts.filter(d => {
                if (activeFilter === 'ALL') return true;
                if (activeFilter === 'GREEN') return d.confidence.includes('Green');
                if (activeFilter === 'AMBER') return d.confidence.includes('Amber');
                if (activeFilter === 'RED') return d.confidence.includes('Red');
                return true;
            });
            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No requirements matching filter.</td></tr>';
                return;
            }
            filtered.forEach(d => {
                const badgeClass = d.confidence.includes('Green') ? 'badge-green' : (d.confidence.includes('Amber') ? 'badge-amber' : 'badge-red');
                const row = document.createElement('tr');
                row.innerHTML = `<td><strong>${d.requirement_id}</strong></td>
                    <td>${d.requirement_text || d.requirement_id}</td>
                    <td><span class="badge ${badgeClass}">${d.confidence}</span></td>
                    <td>${d.answer_text}</td>`;
                tbody.appendChild(row);
            });
        }
    </script>
</body>
</html>"""
