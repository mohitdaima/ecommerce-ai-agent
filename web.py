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
import webbrowser

import yaml
from flask import Flask, jsonify, request, render_template

from core.llm import LLM
from core.store import Store
from agents.manager import Manager

HERE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(HERE, "templates"))

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
    d = request.get_json(force=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Product name is required"}), 400

    def _split(v):
        return [x.strip() for x in (v or "").split(",") if x.strip()]

    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    saved = STORE.add_product({
        "name": name,
        "category": (d.get("category") or "").strip(),
        "price": (str(d.get("price")) or "").strip(),
        "cost": (str(d.get("cost")) or "").strip(),
        "stock": _int(d.get("stock")),
        "features": _split(d.get("features")),
        "keywords": _split(d.get("keywords")),
        "description": (d.get("description") or "").strip(),
    })
    return jsonify({"ok": True, "product": saved})


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
