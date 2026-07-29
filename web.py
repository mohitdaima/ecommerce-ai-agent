#!/usr/bin/env python3
"""
E-COMMERCE AI TEAM - web app (browser interface).

This gives you a friendly chat window in your browser instead of the terminal.
Start it with the double-click launcher (start_windows.bat / start_mac.command)
or by running:  python web.py

It then opens http://127.0.0.1:5000 automatically. 100% local & free.
"""

from __future__ import annotations

import os
import threading
import uuid
import webbrowser

import yaml
from flask import (Flask, jsonify, request, render_template,
                   send_from_directory)
from werkzeug.utils import secure_filename

from core.llm import LLM
from core.store import Store
from agents.manager import Manager

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(HERE, "data", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

app = Flask(__name__, template_folder=os.path.join(HERE, "templates"))
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB uploads

# --- load everything once ---------------------------------------------
with open(os.path.join(HERE, "config.yaml"), "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
LLM_BRAIN = LLM(CONFIG)
STORE = Store(os.path.join(HERE, "data"))
MANAGER = Manager(LLM_BRAIN, STORE, CONFIG)


# --- pages ------------------------------------------------------------
@app.route("/")
def index():
    biz = CONFIG.get("business", {})
    team = [{"emoji": MANAGER.emoji, "name": MANAGER.name, "role": MANAGER.role}]
    for a in MANAGER.team.values():
        team.append({"emoji": a.emoji, "name": a.name, "role": a.role})
    return render_template(
        "index.html",
        business_name=biz.get("name", "My Store"),
        channels=biz.get("channels", []),
        currency=biz.get("currency", "INR"),
        brain_status=LLM_BRAIN.status_line(),
        team=team,
        language=biz.get("language", "english"),
        gst_percent=biz.get("gst_percent", 18),
        gst_mode=biz.get("gst_mode", "inclusive"),
        category=biz.get("category", "general"),
    )


# --- api --------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400
    result = MANAGER.delegate(message)
    return jsonify({
        "assigned": [
            {"emoji": r["agent"].emoji, "name": r["agent"].name,
             "role": r["agent"].role, "output": r["output"]}
            for r in result["results"]
        ],
        "product": (result["product"] or {}).get("name") if result["product"] else None,
    })


@app.route("/api/product", methods=["POST"])
def add_product():
    # Uses multipart form-data so we can accept image files too.
    f = request.form
    name = (f.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Product name is required"}), 400

    def _split(v):
        return [x.strip() for x in (v or "").split(",") if x.strip()]

    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    # save uploaded images
    image_files = []
    for file in request.files.getlist("images"):
        if not file or not file.filename:
            continue
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        fname = f"{uuid.uuid4().hex[:10]}{ext}"
        file.save(os.path.join(IMAGE_DIR, secure_filename(fname)))
        image_files.append(fname)

    saved = STORE.add_product({
        "name": name,
        "category": (f.get("category") or "").strip(),
        "price": (f.get("price") or "").strip(),
        "cost": (f.get("cost") or "").strip(),
        "stock": _int(f.get("stock")),
        "features": _split(f.get("features")),
        "keywords": _split(f.get("keywords")),
        "description": (f.get("description") or "").strip(),
        "images": image_files,
    })
    return jsonify({"ok": True, "product": saved})


@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(IMAGE_DIR, filename)


@app.route("/api/settings", methods=["POST"])
def settings():
    """Update India settings (language / GST / category) live + persist them."""
    d = request.get_json(force=True) or {}
    biz = CONFIG.setdefault("business", {})
    if d.get("language") in ("english", "hindi", "hinglish"):
        biz["language"] = d["language"]
    if str(d.get("gst_percent", "")).strip():
        try:
            biz["gst_percent"] = int(d["gst_percent"])
        except (TypeError, ValueError):
            pass
    if d.get("gst_mode") in ("inclusive", "extra"):
        biz["gst_mode"] = d["gst_mode"]
    if (d.get("category") or "").strip():
        biz["category"] = d["category"].strip().lower()
    # persist to config.yaml so it survives restarts
    try:
        with open(os.path.join(HERE, "config.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(CONFIG, f, sort_keys=False, allow_unicode=True)
    except Exception:
        pass
    return jsonify({"ok": True, "language": biz.get("language"),
                    "gst_percent": biz.get("gst_percent"),
                    "gst_mode": biz.get("gst_mode"),
                    "category": biz.get("category")})


@app.route("/api/automate", methods=["POST"])
def automate():
    """One-click: list a product everywhere, fully automated."""
    d = request.get_json(force=True) or {}
    product = None
    if d.get("product_id"):
        product = STORE.get_product(d["product_id"])
    if product is None:
        return jsonify({"error": "Product not found. Add a product first."}), 400
    result = MANAGER.automate_listing(product)
    return jsonify(result)


@app.route("/api/products")
def products():
    return jsonify(STORE.list_products())


@app.route("/api/returns")
def returns():
    return jsonify(STORE.list_returns())


@app.route("/api/tasks")
def tasks():
    return jsonify(STORE.list_tasks()[-30:])


def _open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    # open the browser a moment after the server starts
    threading.Timer(1.2, _open_browser).start()
    print("\n  E-Commerce AI Team is running!")
    print("  Open this in your browser if it didn't open automatically:")
    print("  >>> http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
