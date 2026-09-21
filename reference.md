# Aankoopfactuur SL — reference

## Portal paths

| Item | Value |
|------|--------|
| Menu | Aankoop → **Nieuwe aankoopfactuur SL** |
| URL | `https://mijn.starterslabo.be/Views/PurchaseForm.aspx` |
| Hidden type | `hfInvoiceType` = **P** |
| Onkostennota | `PurchaseForm.aspx?Type=E` (type **E**) — different workflow |

## Form field → CLI

| Portal label | CLI flag |
|--------------|----------|
| Onderwerp | `--title` |
| Rekening | `--account` (6-digit value) |
| Bedrag | `--amount` (comma decimal) |
| Datum | `--date` (`YYYY-MM-DD`) |
| Factuurnummer | `--invoice-nr` |
| Motivatie beroepskosten | `--description` |
| Nog te betalen aan leverancier | `--to-be-paid` / `--no-to-be-paid` |
| Leverancier (dropdown) | `--supplier-id` (empty = new) |
| Naam / Btw-nummer | `--supplier-name`, `--supplier-vat` |
| BTW Regime | `--supplier-tax-regime` |
| Adres / IBAN / … | see `create_draft_purchase.py --help` |
| Bijlagen | `--attachment` |

## Selectors

Prefix `ctl00_ContentPlaceLabo_PurchaseForm_` — see `starterslabo/purchase.py` (`SEL`).

## Exploration

```bash
uv run python explore_purchase_form.py
```

Writes `docs/aankoopform-raw.json` (gitignored; may contain session-specific hidden fields).
