from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", include_in_schema=False, response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Luthor AI Systems Framework</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; background: #0b1020; color: #e8eefc; }
    .wrap { max-width: 920px; margin: 0 auto; padding: 56px 20px; }
    .card { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 22px; }
    h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: 0.2px; }
    p { margin: 0 0 18px; color: rgba(232,238,252,0.85); line-height: 1.5; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-top: 14px; }
    a.btn { display:block; text-decoration:none; padding: 14px 14px; border-radius: 12px;
            background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
            color: #e8eefc; font-weight: 600; }
    a.btn:hover { background: rgba(255,255,255,0.12); }
    code { background: rgba(0,0,0,0.35); padding: 2px 6px; border-radius: 8px; }
    .small { font-size: 13px; opacity: 0.85; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Luthor AI Systems Framework</h1>
      <p>Deterministic governance tools: policy evaluation, scenario runs, compliance reports.</p>

      <div class="grid">
        <a class="btn" href="/docs">Open API Docs →</a>
        <a class="btn" href="/project">Open Project Board →</a>
        <a class="btn" href="/health">Health Check →</a>
        <a class="btn" href="/evaluate">Evaluate Endpoint (POST) →</a>
      </div>

      <p class="small" style="margin-top:16px;">
        Scenario runner: <code>python -m laf run scenarios/examples</code> (outputs to <code>reports/</code>)
      </p>
    </div>
  </div>
</body>
</html>
"""
