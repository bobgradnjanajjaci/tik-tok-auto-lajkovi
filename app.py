from flask import Flask, request, render_template_string
from auto_brain_core import process_video

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <title>TikTok Auto Likes</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    *{box-sizing:border-box;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
    body{margin:0;background:radial-gradient(circle at top,#1f2937 0,#020617 55%);color:#e5e7eb;min-height:100vh;display:flex;align-items:center;justify-content:center}
    .card{width:100%;max-width:980px;background:rgba(15,23,42,.96);border:1px solid rgba(148,163,184,.35);border-radius:16px;box-shadow:0 20px 50px rgba(15,23,42,.9);padding:22px}
    h2{margin:0 0 6px;font-size:20px;text-transform:uppercase;letter-spacing:.04em}
    p{margin:0 0 14px;color:#9ca3af;font-size:13px}
    label{font-size:12px;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em}
    textarea{width:100%;min-height:220px;margin-top:6px;background:rgba(15,23,42,.85);border:1px solid rgba(55,65,81,.9);border-radius:10px;padding:10px;color:#e5e7eb;font-size:13px;resize:vertical}
    button{margin-top:12px;cursor:pointer;padding:10px 18px;border-radius:999px;border:none;font-weight:700;text-transform:uppercase;letter-spacing:.03em;background:linear-gradient(90deg,#6366f1,#a855f7);color:white;box-shadow:0 8px 22px rgba(79,70,229,.6)}
    pre{margin-top:12px;background:rgba(15,23,42,.9);border:1px solid rgba(55,65,81,.9);border-radius:10px;padding:10px;max-height:320px;overflow:auto;font-size:11px;white-space:pre-wrap}
  </style>
</head>
<body>
  <div class="card">
    <h2>TikTok Auto Likes</h2>
    <p>Ubaci TikTok video linkove (jedan po liniji). Sistem automatski nađe keyword komentar i pošalje lajkove.</p>

    <form method="post">
      <label>Video links</label>
      <textarea name="links" placeholder="https://www.tiktok.com/@user/video/123...&#10;https://www.tiktok.com/@user/video/456...">{{ links or '' }}</textarea>
      <button type="submit">🚀 Send Auto Likes</button>
    </form>

    {% if log %}
      <pre>{{ log }}</pre>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    links = ""
    log_lines = []

    if request.method == "POST":
        links = request.form.get("links", "")
        lines = [l.strip() for l in links.splitlines() if l.strip()]

        for url in lines:
            res = process_video(url)
            log_lines.append(f"{url} -> {res}")

    return render_template_string(HTML, links=links, log="\n".join(log_lines))

if __name__ == "__main__":
    app.run(debug=True)
