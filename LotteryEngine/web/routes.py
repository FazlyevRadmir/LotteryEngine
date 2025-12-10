from flask import Blueprint, request, jsonify, send_file, render_template_string, url_for

from core.participants import (
    load_participants_from_csv_fileobj,
    load_participants_from_json_fileobj,
    normalize_participants,
    validate_participants,
)
from core.checksum import participants_checksum
from core.draw import run_draw
from core.verify import verify_draw
from core.export import export_result_csv, export_result_pdf

from storage.results import save_result, load_result
from storage.public import register_public_token, get_rid_by_token

import os

routes = Blueprint("routes", __name__)

INDEX_TEMPLATE = """
<!doctype html>
<title>Lottery Engine</title>
<h1>Lottery Engine</h1>
<form action="/draw" method="post" enctype="multipart/form-data">
  <input type="text" name="title" placeholder="Название" /><br/>
  <input type="text" name="seed" placeholder="seed" /><br/>
  <input type="number" name="winners_count" value="1" /><br/>
  <input type="file" name="participants_file" /><br/>
  <input type="checkbox" name="public" checked /> Публичная ссылка<br/>
  <button>Запустить</button>
</form>
"""

@routes.get("/")
def index():
    return render_template_string(INDEX_TEMPLATE)

@routes.post("/draw")
def draw_endpoint():
    if request.content_type.startswith("multipart"):
        f = request.files.get("participants_file")
        if not f:
            return jsonify({"error": "participants_file required"}), 400

        name = f.filename.lower()
        if name.endswith(".csv"):
            raw = load_participants_from_csv_fileobj(f.stream)
        else:
            raw = load_participants_from_json_fileobj(f.stream)

        seed = request.form.get("seed", "")
        winners_count = int(request.form.get("winners_count", 1))
        public_flag = bool(request.form.get("public"))
        title = request.form.get("title", "")
    else:
        return jsonify({"error": "Use multipart/form-data"}), 400

    normalized = normalize_participants(raw)
    ok, msg = validate_participants(normalized)
    if not ok:
        return jsonify({"error": msg}), 400

    checksum = participants_checksum(normalized)
    draw_obj = run_draw(normalized, seed, winners_count)

    rid = save_result(draw_obj, checksum, {"title": title})
    token = register_public_token(rid) if public_flag else None

    return jsonify({
        "result_id": rid,
        "public_url": url_for("routes.public_view", token=token, _external=True) if token else None
    })

@routes.get("/result/<rid>")
def result_by_id(rid):
    try:
        return jsonify(load_result(rid))
    except FileNotFoundError:
        return jsonify({"error": "not found"}), 404

@routes.get("/public/<token>")
def public_view(token):
    from jinja2 import Template

    try:
        rid = get_rid_by_token(token)
        obj = load_result(rid)
    except:
        return jsonify({"error": "invalid token"}), 404

    winners_html = "".join(f"<li>{w['id']} — {w['name']}</li>" for w in obj["draw"]["winners"])

    return f"""
    <h1>Результаты</h1>
    <p>id: {obj['id']}</p>
    <p>seed: {obj['draw']['seed']}</p>
    <h2>Победители:</h2>
    <ol>{winners_html}</ol>
    """

@routes.post("/verify")
def verify_endpoint():
    data = request.get_json(force=True)
    rid = data.get("result_id")
    participants = data.get("participants")
    seed = data.get("seed")
    winners_count = data.get("winners_count")

    saved = load_result(rid)
    res = verify_draw(seed, participants, winners_count, saved)
    return jsonify(res)
