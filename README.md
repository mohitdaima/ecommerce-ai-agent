# E-Commerce AI Team

A team of AI agents that help you run your online store across all your
marketplaces (Amazon, eBay, Etsy, Shopify, Facebook Marketplace, ...).

You **"meet" with the Manager** in a chat window, give tasks in plain English,
and it delegates to the right specialist. You only provide your **product
details once**.

**100% free. No paid API keys. No usage credits.** The AI "brain" runs locally
on your own computer via [Ollama](https://ollama.com). If Ollama isn't running,
the team automatically falls back to smart built-in templates so it never
breaks.

---

## Meet your team

| Agent | Role | What they do |
|-------|------|--------------|
| **Max** (Manager) | General Manager | The one you talk to. Understands your request and delegates. |
| **Livia** | Listing Specialist | Writes titles, bullets & descriptions per marketplace. |
| **Piero** | Pricing Analyst | Suggests prices/margins accounting for each marketplace's fees. |
| **Mara** | Marketing Creator | Social captions, ad copy, email campaigns, hashtags. |
| **Sam** | Customer Support | Drafts replies to customers, refunds/returns, FAQs. |
| **Ivan** | Inventory Manager | Tracks stock, flags low/out-of-stock items. |
| **Ana** | Analytics Advisor | Business snapshots + prioritized next actions. |
| **Seon** | SEO Specialist | Keywords, long-tail phrases, marketplace tags. |
| **Reggie** | Returns & RMA Manager | Logs returns, tracks RMA status, auto-restocks resellable items, spots return trends. |

---

## Quick start (2 minutes)

```bash
# 1. install the small free helper libraries
pip install -r requirements.txt

# 2. start the meeting room
python3 run.py
```

Then type `demo` to watch the whole team work on a sample product, or
`add product` to enter your own.

### Turn on the smart AI brain (optional but recommended, still free)

Without this it uses templates. With it, the agents get genuinely smart.

```bash
# 1. Install Ollama (free):  https://ollama.com/download
# 2. Pull a free model:
ollama pull llama3.2
# 3. That's it. Re-run:  python3 run.py
```

Ollama serves the model locally at `http://localhost:11434` — no internet
account, no key, no credits.

---

## How you use it (the "meeting")

```
You (to the team): add product
  ...enter name, price, cost, stock, features, keywords...

You (to the team): write listings for all marketplaces
  -> Max assigns Livia, who returns ready-to-paste listings.

You (to the team): what price should I sell at?
  -> Max assigns Piero, who returns per-marketplace pricing + margins.

You (to the team): a customer says their order is late, write a reply
  -> Max assigns Sam, who drafts an empathetic response.

You (to the team): give me a business overview
  -> Max assigns Ana, who returns a snapshot + next actions.
```

### Meeting commands
- `team` — show the roster
- `add product` — add a product (guided)
- `products` — list your products
- `tasks` — task history
- `returns` — show all returns / RMAs
- `demo` — load a sample product and run several tasks
- `help` — help
- `quit` — leave

Everything the team produces is saved locally in `data/` so you can copy it
into each marketplace.

---

## Honest scope (please read)

This tool does all the **thinking, writing and decision-support** work
automatically and for free. What it deliberately does **not** do is silently
log into your marketplaces and move real money/orders on its own — that
requires connecting *your own* marketplace accounts and is risky to fully
automate. The code has clear "connector" slots (`channels/`) so you can wire in
each marketplace's official (free) API later when you're ready.

## Configure your store
Edit `config.yaml` to set your store name, the marketplaces you sell on, your
currency, and which free Ollama model to use.
```
