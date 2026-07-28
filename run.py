#!/usr/bin/env python3
"""
E-COMMERCE AI TEAM - the "meeting room".

Run:  python run.py

You sit down with your AI team lead (Max the Manager). Type what you need in
plain English and Max delegates to the right specialist. 100% free: the AI
brain runs locally via Ollama; if it's offline, built-in templates keep
everything working.

Meeting commands (type these anytime):
  team                     -> show who's on the team
  add product              -> add a product (guided)
  products                 -> list your products
  tasks                    -> show task history
  returns                  -> show all returns / RMAs
  demo                     -> load a sample product + run a few tasks
  help                     -> show this help
  quit / exit              -> leave the meeting

Anything else is treated as a task for the team, e.g.:
  "write listings for my product"
  "suggest prices for all marketplaces"
  "make an instagram post and hashtags"
  "give me a business overview"
"""

from __future__ import annotations

import os
import sys

import yaml

from core.llm import LLM
from core.store import Store
from agents.manager import Manager

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    _console = Console()

    def say(text, title=None, style="cyan"):
        if title:
            _console.print(Panel(text, title=title, border_style=style))
        else:
            _console.print(text)
except Exception:  # rich is optional
    def say(text, title=None, style=None):
        if title:
            print(f"\n== {title} ==")
        print(text)


def load_config() -> dict:
    path = os.path.join(HERE, "config.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def add_product_interactive(store: Store):
    say("Let's add a product. Press Enter to skip any field.", title="Add Product")
    name = input("  Product name: ").strip()
    if not name:
        say("Cancelled - name is required.")
        return
    category = input("  Category: ").strip()
    price = input("  Selling price: ").strip()
    cost = input("  Your unit cost: ").strip()
    stock = input("  Stock quantity: ").strip()
    features = input("  Key features (comma separated): ").strip()
    keywords = input("  Keywords (comma separated): ").strip()
    description = input("  Short description: ").strip()

    product = {
        "name": name,
        "category": category,
        "price": price,
        "cost": cost,
        "stock": _int_or(stock, 0),
        "features": [f.strip() for f in features.split(",") if f.strip()],
        "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
        "description": description,
    }
    saved = store.add_product(product)
    say(f"Saved '{saved['name']}' with id {saved['id']}.", style="green")


def _int_or(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def show_products(store: Store):
    products = store.list_products()
    if not products:
        say("No products yet. Type 'add product' or 'demo'.")
        return
    lines = []
    for p in products:
        lines.append(f"- [{p['id']}] {p['name']} | {p.get('category','-')} | "
                     f"price {p.get('price','-')} | stock {p.get('stock','-')}")
    say("\n".join(lines), title="Your Products")


def show_tasks(store: Store):
    tasks = store.list_tasks()
    if not tasks:
        say("No tasks yet.")
        return
    lines = [f"- {t['assigned_to']}: {t['description']}" for t in tasks[-15:]]
    say("\n".join(lines), title="Recent Tasks")


def show_returns(store: Store):
    rets = store.list_returns()
    if not rets:
        say("No returns logged. Ask the team: 'log a return for <product> ...'")
        return
    lines = [f"- {r['rma']} | {r['product_name']} | {r['channel']} | "
             f"{r['reason']} | {r['status']}" for r in rets]
    say("\n".join(lines), title="Returns / RMAs")


def run_task(manager: Manager, task: str):
    result = manager.delegate(task)
    assigned = ", ".join(result["assigned"])
    prod = result["product"]
    header = f"Max assigned this to: {assigned}"
    if prod:
        header += f"\nProduct: {prod['name']} (id {prod['id']})"
    say(header, title="Team Meeting", style="yellow")
    for r in result["results"]:
        say(r["output"], title=f"{r['agent'].emoji} {r['agent'].name}",
            style="cyan")


def load_demo(store: Store, manager: Manager):
    demo = {
        "name": "Bamboo Travel Mug",
        "category": "Kitchen",
        "price": "499",
        "cost": "180",
        "stock": 3,
        "features": ["Eco-friendly bamboo", "Leak-proof lid",
                     "Keeps drinks hot 6h", "500ml capacity",
                     "Dishwasher safe"],
        "keywords": ["bamboo mug", "eco travel mug", "reusable cup"],
        "description": "A sustainable, leak-proof travel mug made from natural "
                       "bamboo fiber - perfect for coffee on the go.",
    }
    store.add_product(demo)
    say("Loaded demo product 'Bamboo Travel Mug'. Running a few tasks...",
        style="green")
    for task in [
        "write listings for the bamboo travel mug",
        "suggest prices for all marketplaces",
        "make an instagram caption and hashtags",
        "give me a business overview",
    ]:
        say(f"\n>>> Owner: {task}")
        run_task(manager, task)


def main():
    config = load_config()
    llm = LLM(config)
    store = Store(os.path.join(HERE, "data"))
    manager = Manager(llm, store, config)

    biz = config.get("business", {}).get("name", "your store")
    say(
        f"Welcome to the {biz} AI Team meeting room!\n"
        f"{llm.status_line()}\n\n"
        f"I'm Max, your General Manager. Tell me what you need and I'll get "
        f"the right specialist on it.\nType 'help' for commands, 'demo' to see "
        f"it in action, or 'quit' to leave.",
        title="E-Commerce AI Team", style="magenta",
    )
    say(manager.roster_text(), title="Your Team", style="blue")

    while True:
        try:
            user = input("\nYou (to the team): ").strip()
        except (EOFError, KeyboardInterrupt):
            say("\nMeeting ended. See you next time!")
            break
        if not user:
            continue
        cmd = user.lower()
        if cmd in ("quit", "exit"):
            say("Meeting ended. The team saved all work to /data. Bye!")
            break
        elif cmd == "help":
            say(__doc__)
        elif cmd == "team":
            say(manager.roster_text(), title="Your Team", style="blue")
        elif cmd in ("add product", "add"):
            add_product_interactive(store)
        elif cmd == "products":
            show_products(store)
        elif cmd == "tasks":
            show_tasks(store)
        elif cmd == "returns":
            show_returns(store)
        elif cmd == "demo":
            load_demo(store, manager)
        else:
            run_task(manager, user)


if __name__ == "__main__":
    sys.exit(main())
