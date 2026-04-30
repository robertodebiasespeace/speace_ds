"""SPEACE Monitoring — Web Dashboard.

Serves a minimal HTTP dashboard on localhost showing KPIs, brain status,
energy usage, and evolutionary metrics. Uses Streamlit if available,
otherwise falls back to a simple HTTP server.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SPEACE Digital Brain — Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a1a; color: #e0e0e0; padding: 20px; }
  h1 { color: #00ff88; text-align: center; margin-bottom: 30px; font-size: 2rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; max-width: 1400px; margin: 0 auto; }
  .card { background: #1a1a2e; border: 1px solid #2a2a4e; border-radius: 12px; padding: 16px; }
  .card h2 { color: #00ccff; font-size: 1rem; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 6px; }
  .kpi { font-size: 2.5rem; font-weight: bold; text-align: center; padding: 10px; }
  .kpi.green { color: #00ff88; } .kpi.yellow { color: #ffcc00; } .kpi.red { color: #ff4444; }
  .metric { display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.9rem; }
  .metric .label { color: #888; } .metric .value { color: #ccc; font-family: monospace; }
  .bar-bg { background: #222; border-radius: 4px; height: 8px; margin: 4px 0; }
  .bar-fill { background: #00ff88; border-radius: 4px; height: 8px; transition: width 0.5s; }
  .bar-fill.warn { background: #ffcc00; } .bar-fill.danger { background: #ff4444; }
  .tag { display: inline-block; background: #222; color: #888; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px; }
  .tag.active { background: #1a4a2e; color: #00ff88; }
  #footer { text-align: center; color: #555; margin-top: 20px; font-size: 0.8rem; }
</style>
</head>
<body>
  <h1>🧠 SPEACE Digital Brain — Dashboard</h1>
  <div class="grid">
    <div class="card">
      <h2>⚡ EMERGENZA</h2>
      <div id="emergence" class="kpi green">--</div>
      <div class="metric"><span class="label">Novelty</span><span id="novelty" class="value">--</span></div>
      <div class="metric"><span class="label">Coherence</span><span id="coherence" class="value">--</span></div>
      <div class="metric"><span class="label">Adaptation</span><span id="adaptation" class="value">--</span></div>
    </div>
    <div class="card">
      <h2>🧬 CRITICALITY</h2>
      <div id="crit-zone" class="kpi" style="font-size:1.5rem">--</div>
      <div class="metric"><span class="label">Branching</span><span id="branching" class="value">--</span></div>
      <div class="metric"><span class="label">Order</span><span id="order" class="value">--</span></div>
      <div class="metric"><span class="label">Chaos</span><span id="chaos" class="value">--</span></div>
    </div>
    <div class="card">
      <h2>💭 COSCIENZA (C-Index)</h2>
      <div id="cindex" class="kpi green">--</div>
      <div class="metric"><span class="label">Phi (IIT)</span><span id="phi" class="value">--</span></div>
      <div class="metric"><span class="label">GWT Activation</span><span id="gwt" class="value">--</span></div>
    </div>
    <div class="card">
      <h2>🔬 MEMORIA</h2>
      <div class="metric"><span class="label">Fatti</span><span id="facts" class="value">--</span></div>
      <div class="metric"><span class="label">Episodi</span><span id="episodes" class="value">--</span></div>
      <div class="metric"><span class="label">Working</span><span id="working" class="value">--</span></div>
      <div class="metric"><span class="label">Semantici</span><span id="semantic" class="value">--</span></div>
    </div>
    <div class="card">
      <h2>⚡ ENERGIA</h2>
      <div class="metric"><span class="label">RAM Used</span><span id="ram" class="value">--</span></div>
      <div class="metric"><span class="label">CPU%</span><span id="cpu" class="value">--</span></div>
      <div class="metric"><span class="label">Total Thoughts</span><span id="thoughts" class="value">--</span></div>
      <div class="metric"><span class="label">Uptime</span><span id="uptime" class="value">--</span></div>
    </div>
    <div class="card">
      <h2>🧠 NEUROTRASMETTITORI</h2>
      <div class="metric"><span class="label">DA (reward)</span><span id="da" class="value">--</span></div>
      <div class="bar-bg"><div id="bar-da" class="bar-fill" style="width:50%"></div></div>
      <div class="metric"><span class="label">NE (arousal)</span><span id="ne" class="value">--</span></div>
      <div class="bar-bg"><div id="bar-ne" class="bar-fill" style="width:55%"></div></div>
      <div class="metric"><span class="label">ACh (encoding)</span><span id="ach" class="value">--</span></div>
      <div class="bar-bg"><div id="bar-ach" class="bar-fill" style="width:60%"></div></div>
      <div class="metric"><span class="label">5-HT (patience)</span><span id="ht" class="value">--</span></div>
      <div class="bar-bg"><div id="bar-ht" class="bar-fill" style="width:50%"></div></div>
    </div>
  </div>
  <div id="footer">SPEACE Digital Brain v1.0 — Rigene Project — MIT License</div>

  <script>
    async function refresh() {
      try {
        const r = await fetch('/api/status');
        const d = await r.json();
        document.getElementById('emergence').textContent = (d.metrics?.emergence || 0).toFixed(3);
        document.getElementById('novelty').textContent = (d.metrics?.novelty || 0).toFixed(3);
        document.getElementById('coherence').textContent = (d.metrics?.coherence || 0).toFixed(3);
        document.getElementById('adaptation').textContent = (d.metrics?.adaptation || 0).toFixed(3);
        document.getElementById('crit-zone').textContent = d.criticality?.zone || '--';
        document.getElementById('branching').textContent = (d.criticality?.branching_ratio || 0).toFixed(3);
        document.getElementById('order').textContent = (d.criticality?.order_score || 0).toFixed(3);
        document.getElementById('chaos').textContent = (d.criticality?.chaos_score || 0).toFixed(3);
        document.getElementById('cindex').textContent = (d.consciousness?.c_index || 0).toFixed(3);
        document.getElementById('phi').textContent = '--';
        document.getElementById('gwt').textContent = (d.consciousness?.threshold || 0).toFixed(2);
        document.getElementById('facts').textContent = d.memory?.facts || 0;
        document.getElementById('episodes').textContent = d.memory?.episodes || 0;
        document.getElementById('working').textContent = d.memory?.working_turns || 0;
        document.getElementById('semantic').textContent = d.memory?.semantic_items || 0;
        document.getElementById('ram').textContent = ((d.energy?.ram_used_mb || 0)).toFixed(0) + ' MB';
        document.getElementById('cpu').textContent = '--';
        document.getElementById('thoughts').textContent = d.stats?.total_thoughts || 0;
        document.getElementById('uptime').textContent = (d.stats?.uptime_minutes || 0).toFixed(1) + 'm';
        const nt = d.neurotransmitters || {};
        document.getElementById('da').textContent = (nt.dopamine || 0).toFixed(3);
        document.getElementById('ne').textContent = (nt.norepinephrine || 0).toFixed(3);
        document.getElementById('ach').textContent = (nt.acetylcholine || 0).toFixed(3);
        document.getElementById('ht').textContent = (nt.serotonin || 0).toFixed(3);
        document.getElementById('bar-da').style.width = ((nt.dopamine || 0) * 100) + '%';
        document.getElementById('bar-ne').style.width = ((nt.norepinephrine || 0) * 100) + '%';
        document.getElementById('bar-ach').style.width = ((nt.acetylcholine || 0) * 100) + '%';
        document.getElementById('bar-ht').style.width = ((nt.serotonin || 0) * 100) + '%';
      } catch(e) { console.error(e); }
    }
    setInterval(refresh, 2000);
    refresh();
  </script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    brain_instance = None

    def log_message(self, format, *args):
        pass  # Silence HTTP logs

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            self._serve_html(DASHBOARD_HTML)
        elif path == "/api/status":
            self._serve_json(self._get_status())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def _get_status(self):
        import asyncio
        if not self.brain_instance:
            return {"error": "Brain non inizializzato"}
        try:
            loop = asyncio.new_event_loop()
            status = loop.run_until_complete(self.brain_instance.status())
            loop.close()
            return status
        except Exception as e:
            return {"error": str(e)}

    def _serve_html(self, html: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _serve_json(self, data: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))


def run_dashboard(brain, port: int = 8765):
    DashboardHandler.brain_instance = brain
    server = HTTPServer(("localhost", port), DashboardHandler)
    print(f"[DASHBOARD] Accesso: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
