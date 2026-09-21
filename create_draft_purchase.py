#!/usr/bin/env python3
"""
Create a DRAFT purchase invoice (aankoopfactuur SL) on mijn.starterslabo.be.

Navigation: Aankoop → Nieuwe aankoopfactuur SL → PurchaseForm.aspx

Safety:
- Only clicks "Opslaan als concept" (btnSaveConcept), never "Verstuur" (BtnSubmit),
  unless --send is passed explicitly.
- Use --dry-run to fill the form and report values WITHOUT saving anything.
- Attachments use Telerik RadAsyncUpload: must wait for ruUploadSuccess before save.
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from starterslabo.purchase import (
    PURCHASE_FORM_URL,
    SEL,
    fill_radnumeric,
    fill_supplier,
    open_purchase_invoice_form,
    read_filled,
    save_draft,
    upload_attachment,
)
from starterslabo.session import load_credentials, login, new_page


def set_to_be_paid(page: Page, value: bool) -> None:
    if value:
        page.check(SEL["to_be_paid"])
    else:
        page.uncheck(SEL["to_be_paid"])


def print_filled(filled: dict[str, str], attachment: Path | None) -> None:
    print("Filled purchase invoice:")
    print(f"  Onderwerp   : {filled['title']!r}")
    print(f"  Rekening    : {filled['account']}")
    print(f"  Bedrag      : {filled['amount']!r}")
    print(f"  Datum       : {filled['date']}")
    print(f"  Factuurnr   : {filled['invoice_nr']!r}")
    print(f"  Leverancier : {filled['supplier']!r}")
    print(f"  Btw-nummer  : {filled['supplier_vat']!r}")
    print(
        f"  Motivatie   : {filled['description'][:80]!r}"
        f"{'...' if len(filled['description']) > 80 else ''}"
    )
    if attachment:
        print(f"  Bijlage     : {attachment.name} (upload complete)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Onderwerp (short label)")
    parser.add_argument(
        "--account",
        required=True,
        help="Rekening code, e.g. 612125 for software/website",
    )
    parser.add_argument("--amount", required=True, help="Bedrag, e.g. 49,99")
    parser.add_argument("--date", required=True, help="Datum (YYYY-MM-DD)")
    parser.add_argument(
        "--invoice-nr",
        required=True,
        help="Factuurnummer from supplier invoice",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Motivatie beroepskosten (business justification)",
    )
    parser.add_argument(
        "--supplier-name",
        required=True,
        help="Leverancier naam (bedrijfsnaam)",
    )
    parser.add_argument(
        "--supplier-vat",
        default="",
        help="Leverancier btw-nummer (BE…)",
    )
    parser.add_argument(
        "--supplier-id",
        default="",
        help="Existing leverancier dropdown value (UUID). Omit for Nieuwe leverancier.",
    )
    parser.add_argument(
        "--supplier-tax-regime",
        default="Standaard",
        help="BTW-regime: Geen, Standaard, Medecontractant, …",
    )
    parser.add_argument("--supplier-phone", default="")
    parser.add_argument("--supplier-email", default="")
    parser.add_argument("--supplier-address", default="")
    parser.add_argument("--supplier-city", default="")
    parser.add_argument("--supplier-postal", default="")
    parser.add_argument("--supplier-country", default="BE")
    parser.add_argument("--supplier-iban", default="")
    parser.add_argument("--supplier-bic", default="")
    parser.add_argument("--supplier-contact", default="")
    parser.add_argument("--supplier-contact-email", default="")
    parser.add_argument(
        "--to-be-paid",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Nog te betalen aan leverancier (default: checked)",
    )
    parser.add_argument(
        "--attachment",
        default="",
        help="Path to supplier invoice PDF/image",
    )
    parser.add_argument(
        "--navigate-menu",
        action="store_true",
        help="Open form via Aankoop menu click instead of direct URL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fill the form but do NOT save anything",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Click Verstuur (final submit) instead of saving a draft. Avoid.",
    )
    args = parser.parse_args()

    if args.attachment:
        attachment = Path(args.attachment).expanduser().resolve()
        if not attachment.is_file():
            print(f"Attachment not found: {attachment}", file=sys.stderr)
            return 1
    else:
        attachment = None

    email, password = load_credentials()

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)
            if args.navigate_menu:
                open_purchase_invoice_form(page)
            else:
                page.goto(PURCHASE_FORM_URL, wait_until="networkidle", timeout=60_000)

            fill_supplier(
                page,
                supplier_id=args.supplier_id,
                name=args.supplier_name,
                vat=args.supplier_vat,
                tax_regime=args.supplier_tax_regime,
                phone=args.supplier_phone,
                email=args.supplier_email,
                address=args.supplier_address,
                city=args.supplier_city,
                postal=args.supplier_postal,
                country=args.supplier_country,
                iban=args.supplier_iban,
                bic=args.supplier_bic,
                contact=args.supplier_contact,
                contact_email=args.supplier_contact_email,
            )

            page.fill(SEL["title"], args.title)
            page.select_option(SEL["account"], args.account)
            fill_radnumeric(page, SEL["amount"], args.amount)
            page.fill(SEL["date"], args.date)
            page.fill(SEL["invoice_nr"], args.invoice_nr)
            page.fill(SEL["description"], args.description)
            set_to_be_paid(page, args.to_be_paid)

            if attachment:
                upload_attachment(page, attachment)

            filled = read_filled(page)
            print_filled(filled, attachment)
            print(f"  Nog te betalen: {'ja' if args.to_be_paid else 'nee'}")

            page.screenshot(path="draft-purchase-filled.png", full_page=True)

            if args.dry_run:
                print("Dry run: nothing saved. Screenshot: draft-purchase-filled.png")
                return 0

            if args.send:
                page.click(SEL["send"])
                page.wait_for_load_state("networkidle", timeout=60_000)
                action = "Verstuur (SENT)"
                blocked = ""
                summary = page.locator(SEL["validation_summary"])
                if summary.count() and summary.is_visible():
                    blocked = summary.inner_text().strip()
            else:
                action = "Opslaan als concept (DRAFT)"
                blocked = save_draft(page)

            page.screenshot(path="draft-purchase-result.png", full_page=True)

            if blocked:
                print(f"\nValidation blocked the save:\n{blocked}", file=sys.stderr)
                print("Screenshot: draft-purchase-result.png", file=sys.stderr)
                return 1

            print(f"\n{action} OK")
            print(f"  Final URL: {page.url}")
            print("  Screenshot: draft-purchase-result.png")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
