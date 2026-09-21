---
name: starterslabo-expenses
description: >-
  Enter Starters Labo purchase expenses (aankoopfactuur SL) on
  mijn.starterslabo.be via Playwright automation. Use when the user mentions
  aankoopfactuur, purchase invoice, leverancier, supplier invoice, Nieuwe
  aankoopfactuur SL, Starters Labo expenses, or wants to register a supplier
  bill (not an onkostennota) on Starters Labo.
---

# Starters Labo — Nieuwe aankoopfactuur SL

Enter supplier purchase invoices on [mijn.starterslabo.be](https://mijn.starterslabo.be) via **Aankoop → Nieuwe aankoopfactuur SL** (`PurchaseForm.aspx`, invoice type **P**).

Not affiliated with Starterslabo. Credentials stay in `.env` at the **skill repo root** — never commit or print them.

## Onkostennota or aankoopfactuur?

| Situation | Use |
|-----------|-----|
| You paid personally and want reimbursement | **Onkostennota** (different form / skill) |
| Supplier invoice; register leverancier / payment to supplier | **Aankoopfactuur SL** → this skill |

When unsure, ask the user once.

## Setup (first run)

Resolve this skill’s directory (clone root). Then:

```bash
uv sync
uv run playwright install chromium
cp .env.example .env   # STARTERSLABO_EMAIL, STARTERSLABO_PASSWORD
```

Run all commands from the **repository root** (where `SKILL.md` and `pyproject.toml` live).

## Workflow

```
Progress:
- [ ] 1. Choose onkostennota vs aankoopfactuur
- [ ] 2. Extract fields from invoice PDF; propose rekening + motivatie
- [ ] 3. Check Aankoop list for duplicate Factuurnummer
- [ ] 4. Dry-run with --attachment
- [ ] 5. User confirms → save concept (omit --dry-run)
```

### Dry run (default before save)

```bash
uv run python create_draft_purchase.py \
  --title "..." \
  --account 612125 \
  --amount "49,99" \
  --date 2026-06-15 \
  --invoice-nr "INV-123" \
  --description "..." \
  --supplier-name "Leverancier BV" \
  --supplier-vat "BE0123456789" \
  --attachment /path/to/invoice.pdf \
  --dry-run
```

Optional: **`--navigate-menu`** — open form via Aankoop menu instead of direct URL.

### Save as concept

Same command **without** `--dry-run`, only after user confirms.

### Safety

- Default: **Opslaan als concept** only.
- Never **`--send`** unless the user explicitly asks to submit for coach review.
- Debug: `HEADED=1 uv run python create_draft_purchase.py ...`

## Leverancier flags

| Case | CLI |
|------|-----|
| New supplier | Omit `--supplier-id`; set `--supplier-name`, `--supplier-vat`, … |
| Existing dropdown entry | `--supplier-id <uuid>`; verify fields after postback |
| Already paid | `--no-to-be-paid` |
| BTW regime | `--supplier-tax-regime Standaard` (default) |

Optional: `--supplier-address`, `--supplier-city`, `--supplier-postal`, `--supplier-country BE`, `--supplier-iban`, `--supplier-bic`, `--supplier-email`, `--supplier-phone`.

## Attachments (critical)

Bijlagen use **Telerik RadAsyncUpload**. The script waits for upload success before save. Always pass **`--attachment`** when a file exists.

Retroactive PDF:

```bash
uv run python attach_purchase_receipt.py \
  --invoice-nr INV-123 \
  --attachment /path/to/invoice.pdf
```

## Rekening picker (common)

| User says… | Code |
|------------|------|
| software, SaaS, hosting | `612125` |
| telefoon, gsm, internet | `612105` |
| abonnement, tijdschrift | `612115` |
| kantoor, drukwerk | `612300` |
| opleiding, cursus | `613265` |
| restaurant | `614345` |
| openbaar vervoer, trein | `614330` |
| verzekering | `613160` |
| reclame | `614100` |
| onduidelijk | `610999` — confirm with user |

## Motivatie template

> [Product/dienst] voor [bedrijfsactiviteit]. Gebruikt voor [concrete taak].

## Scripts

| Script | Purpose |
|--------|---------|
| `create_draft_purchase.py` | Fill, upload, save draft |
| `attach_purchase_receipt.py` | Add PDF to existing entry |
| `explore_purchase_form.py` | Re-crawl form (local `docs/`, gitignored) |

Field map: [reference.md](reference.md).
