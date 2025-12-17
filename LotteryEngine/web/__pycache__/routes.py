import os
from flask import Blueprint, request, jsonify, render_template_string, url_for
from core.export import export_result_csv
from storage.uploads import save_original_file
from flask import send_file
from core.participants import (
    load_participants_from_csv_fileobj,
    load_participants_from_json_fileobj,
    normalize_participants,
    validate_participants,
)
from core.checksum import participants_checksum
from core.draw import run_draw
from core.verify import verify_draw
from storage.results import save_result, load_result
from storage.public import register_public_token, get_rid_by_token

routes = Blueprint("routes", __name__)

INDEX_TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Lottery Engine</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f5f6fa;
    padding: 40px;
}
.container {
    max-width: 480px;
    margin: auto;
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}
h1 {
    text-align: center;
}
label {
    display: block;
    margin-top: 12px;
    font-weight: bold;
}
input, button {
    width: 100%;
    padding: 8px;
    margin-top: 6px;
}
button {
    margin-top: 16px;
    background: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
    border-radius: 6px;
}
button.secondary {
    background: #2196F3;
}
a.button-link {
    display: block;
    text-align: center;
    padding: 10px;
    margin-top: 16px;
    background: #673AB7;
    color: white;
    text-decoration: none;
    border-radius: 6px;
}
.footer {
    margin-top: 16px;
    font-size: 12px;
    color: #666;
    text-align: center;
}
</style>

<script>
function randomSeed() {
    const seed = Math.random().toString(36).substring(2, 10);
    document.getElementById("seed").value = seed;
}
</script>
</head>

<body>
<div class="container">
<h1>Lottery Engine</h1>

<form action="/draw" method="post" enctype="multipart/form-data">

<label>Название розыгрыша</label>
<input type="text" name="title" placeholder="Например: Новогодний розыгрыш">

<label>Seed</label>
<input id="seed" type="text" name="seed" placeholder="Введите seed или сгенерируйте">

<button type="button" class="secondary" onclick="randomSeed()">Случайный seed</button>

<label>Количество победителей</label>
<input type="number" name="winners_count" value="1" min="1">

<label>Файл с участниками (CSV)</label>
<input type="file" name="participants_file" required>

<button type="submit">Запустить розыгрыш</button>
</form>

{% if public_url %}
<a class="button-link" href="{{ public_url }}" target="_blank">
Результаты розыгрыша
</a>
{% endif %}

<div class="footer">
Детерминированный PRNG • Проверяемые результаты • Seed сохраняется
</div>
</div>
</body>
</html>
"""

@routes.get("/")
def index():
    return render_template_string(INDEX_TEMPLATE)

@routes.post("/draw")
def draw_endpoint():
    f = request.files.get("participants_file")
    if not f:
        return jsonify({"error": "participants_file required"}), 400

    filename = f.filename.lower()
    if filename.endswith(".csv"):
        raw = load_participants_from_csv_fileobj(f.stream)
    elif filename.endswith(".json"):
        raw = load_participants_from_json_fileobj(f.stream)
    else:
        return jsonify({"error": "Only CSV or JSON supported"}), 400

    seed = request.form.get("seed", "")
    winners_count = int(request.form.get("winners_count", 1))
    title = request.form.get("title", "")

    normalized = normalize_participants(raw)
    ok, msg = validate_participants(normalized)
    if not ok:
        return jsonify({"error": msg}), 400

    checksum = participants_checksum(normalized)
    draw_obj = run_draw(normalized, seed, winners_count)
    rid = save_result(draw_obj, checksum, {"title": title})
    save_original_file(f, rid)
    token = register_public_token(rid)
    public_url = url_for("routes.public_view", token=token, _external=True)

    print("RID:", rid)
    print("TOKEN:", token)

    return render_template_string(
        INDEX_TEMPLATE,
        public_url=public_url
    )

@routes.get("/public/<token>/export_csv")
def public_export_csv(token):
    rid = get_rid_by_token(token)
    if not rid:
        return jsonify({"error": "invalid token"}), 404

    try:
        obj = load_result(rid)
    except FileNotFoundError:
        return jsonify({"error": "result not found"}), 404

    print("=== EXPORT OBJ ===")
    print(obj)
    print(obj["draw"].get("winners"))

    os.makedirs("results", exist_ok=True)
    out_path = os.path.join("results", f"{rid}.csv")
    export_result_csv(obj, out_path)

    from flask import send_file
    return send_file(out_path, as_attachment=True)

@routes.get("/result/<rid>/download")
def download_original_file(rid):
    from storage.uploads import UPLOADS_DIR
    import os

    for ext in ("csv", "json"):
        path = os.path.join(UPLOADS_DIR, f"{rid}.{ext}")
        if os.path.exists(path):
            return send_file(path, as_attachment=True)

    return jsonify({"error": "original file not found"}), 404



@routes.get("/public/<token>")
def public_view(token):
    try:
        rid = get_rid_by_token(token)
        obj = load_result(rid)
    except:
        return jsonify({"error": "invalid token"}), 404

    winners_html = "".join(
        f"<li>{w['id']} — {w['name']}</li>"
        for w in obj["draw"]["winners"]
    )

    download_url = url_for("routes.download_original_file", rid=rid)

    return f"""
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Результаты розыгрыша</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f5f6fa;
    padding: 40px;
}}
.container {{
    max-width: 480px;
    margin: auto;
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}}
h1 {{
    text-align: center;
}}
button {{
    width: 100%;
    padding: 10px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    margin-top: 16px;
}}
</style>
</head>

<body>
<div class="container">
<h1>{obj['metadata'].get('title', 'Результаты розыгрыша')}</h1>

<p><b>Seed:</b> {obj['draw']['seed']}</p>
<p><b>Количество победителей:</b> {obj['draw']['winners_count']}</p>

<h2>🏆 Победители:</h2>
<ol>
{winners_html}
</ol>

<a href="{download_url}">
<button>⬇ Скачать файл участников (оригинал)</button>
</a>

<p style="margin-top:16px;font-size:12px;color:#666;">
Скачайте файл, укажите seed и воспроизведите розыгрыш самостоятельно
</p>
</div>
</body>
</html>
"""


@routes.post("/verify")
def verify_endpoint():
    data = request.get_json(force=True)

    rid = data.get("result_id")
    participants = data.get("participants")
    seed = data.get("seed")
    winners_count = data.get("winners_count")

    saved = load_result(rid)
    result = verify_draw(seed, participants, winners_count, saved)

    return jsonify(result)
