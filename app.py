from flask import Flask, request, jsonify, render_template_string
import time
import requests

from auto_brain_core import process_video

app = Flask(__name__)

# ✅ Web zaštita (da ne ubije worker)
MAX_LINKS_PER_RUN = 6
SLEEP_BETWEEN_LINKS = 1.2

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Encrypted Money Code - Auto Likes</title>
  <style>
    body{font-family:system-ui;background:#0b1220;color:#e5e7eb;display:flex;justify-content:center;padding:24px}
    .card{width:100%;max-width:900px;background:#0f172a;border:1px solid #334155;border-radius:16px;padding:18px}
    textarea{width:100%;min-height:220px;background:#0b1220;color:#e5e7eb;border:1px solid #334155;border-radius:12px;padding:12px}
    button{margin-top:10px;padding:10px 16px;border-radius:999px;border:none;background:#6366f1;color:white;font-weight:700;cursor:pointer}
    .hint{color:#94a3b8;font-size:12px;margin-top:8px;line-height:1.4}
    pre{white-space:pre-wrap;background:#0b1220;border:1px solid #334155;border-radius:12px;padding:12px;margin-top:14px}
  </style>
</head>
<body>
  <div class="card">
    <h2>Encrypted Money Code - Auto Likes</h2>
    <div class="hint">
      Paste linkove (1 po liniji). Web limit: <b>{{max_links}}</b> po run-u da Railway ne puca.
    </div>
    <form method="post">
      <textarea name="links" placeholder="https://www.tiktok.com/t/Z...">{{links or ""}}</textarea>
      <button type="submit">Run</button>
    </form>

    {% if out %}
      <pre>{{out}}</pre>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    links_text = ""
    out_lines = []

    if request.method == "POST":
        links_text = request.form.get("links", "")
        raw_links = [l.strip() for l in links_text.splitlines() if l.strip()]

        if len(raw_links) > MAX_LINKS_PER_RUN:
            raw_links = raw_links[:MAX_LINKS_PER_RUN]
            out_lines.append(f"[INFO] Skraćeno na {MAX_LINKS_PER_RUN} linkova (web safe mode).")

        for i, url in enumerate(raw_links, start=1):
            try:
                res = process_video(url)
                out_lines.append(f"{i}) {url} -> {res}")
            except Exception as e:
                # ✅ Nikad ne ruši cijeli request
                out_lines.append(f"{i}) {url} -> {{'status':'error','message':'{type(e).__name__}: {e}'}}")

            time.sleep(SLEEP_BETWEEN_LINKS)

    return render_template_string(HTML, links=links_text, out="\n".join(out_lines), max_links=MAX_LINKS_PER_RUN)


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(force=True, silent=True) or {}
    urls = data.get("links") or []
    urls = [u.strip() for u in urls if isinstance(u, str) and u.strip()]

    urls = urls[:MAX_LINKS_PER_RUN]

    results = []
    for url in urls:
        try:
            results.append({"url": url, "result": process_video(url)})
        except Exception as e:
            results.append({"url": url, "result": {"status": "error", "message": f"{type(e).__name__}: {e}"}})
        time.sleep(SLEEP_BETWEEN_LINKS)

    return jsonify({"ok": True, "results": results})
