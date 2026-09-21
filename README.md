# starterslabo-expenses

Unofficial [Cursor](https://cursor.com) / [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill plus Playwright scripts to enter **Nieuwe aankoopfactuur SL** on [mijn.starterslabo.be](https://mijn.starterslabo.be).

For personal out-of-pocket expenses (onkostennota), use a separate workflow on `PurchaseForm.aspx?Type=E`.

Not affiliated with Starterslabo.

## Install (CLI)

```bash
# Cursor — this project
git clone https://github.com/c1sc0c0/starterslabo-expenses.git .cursor/skills/starterslabo-expenses

# Cursor — all projects
git clone https://github.com/c1sc0c0/starterslabo-expenses.git ~/.cursor/skills/starterslabo-expenses

# Claude Code — this project
git clone https://github.com/c1sc0c0/starterslabo-expenses.git .claude/skills/starterslabo-expenses

# Claude Code — all projects
git clone https://github.com/c1sc0c0/starterslabo-expenses.git ~/.claude/skills/starterslabo-expenses
```

Then install browser automation deps (from the clone directory):

```bash
cd .cursor/skills/starterslabo-expenses   # or your clone path
uv sync
uv run playwright install chromium
cp .env.example .env
# Edit .env — never commit it
```

Restart the agent chat so the skill is discovered.

**Claude.ai:** zip this repo so `SKILL.md` is at the zip root and upload as a custom skill. You still run the Python scripts locally with `uv` as above.

## Usage

Dry run (fill form, no save):

```bash
uv run python create_draft_purchase.py \
  --title "SaaS abonnement Q2" \
  --account 612125 \
  --amount "49,99" \
  --date 2026-06-15 \
  --invoice-nr "INV-2026-001" \
  --description "Software abonnement voor productontwikkeling." \
  --supplier-name "Example SaaS BV" \
  --supplier-vat "BE0123456789" \
  --attachment ~/Downloads/invoice.pdf \
  --dry-run
```

Save as concept after confirming output: same command without `--dry-run`.

Visible browser for debugging: `HEADED=1 uv run python create_draft_purchase.py ...`

## Security

- **No credentials in git.** Only `.env.example` is tracked.
- Put secrets in `.env` or export `STARTERSLABO_EMAIL` / `STARTERSLABO_PASSWORD` for one-off runs.
- Do not paste passwords into agent chat; the scripts read env vars locally.
- `explore_purchase_form.py` output under `docs/` is gitignored (can contain session tokens in hidden fields).

## Repository layout

| Path | Role |
|------|------|
| `SKILL.md` | Agent instructions |
| `reference.md` | Field / URL reference |
| `create_draft_purchase.py` | Main automation |
| `attach_purchase_receipt.py` | Add PDF to existing entry |
| `explore_purchase_form.py` | Form crawler |
| `starterslabo/` | Shared Playwright helpers |

## Related

- [starterslabo-eval](https://github.com/c1sc0c0/starterslabo-eval) — monthly LABO evaluatiefiche Excel
- [starterslabo-faq](https://github.com/c1sc0c0/starterslabo-faq) — portal FAQ crawl / Q&A

## License

MIT — see [LICENSE](LICENSE). Starterslabo’s portal and templates remain their property.
