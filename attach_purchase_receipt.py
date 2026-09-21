#!/usr/bin/env python3
"""
Attach a PDF/image to an existing aankoopfactuur or onkostennota (concept).

Finds the entry by --invoice-nr (Factuurnummer) on the Aankoop list, opens
the edit form, uploads the file, waits for Telerik RadAsyncUpload to finish,
then saves as concept.
"""

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from starterslabo.purchase import (
    find_purchase_edit_url,
    open_purchase_list,
    save_draft,
    upload_attachment,
)
from starterslabo.session import load_credentials, login, new_page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--invoice-nr",
        required=True,
        help="Factuurnummer on the existing entry",
    )
    parser.add_argument(
        "--attachment",
        required=True,
        help="Path to receipt PDF/image",
    )
    parser.add_argument(
        "--edit-url",
        default="",
        help="Skip lookup; open this PurchaseForm.aspx?ID=... URL directly",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Upload and screenshot but do NOT save",
    )
    args = parser.parse_args()

    attachment = Path(args.attachment).expanduser().resolve()
    if not attachment.is_file():
        print(f"Attachment not found: {attachment}", file=sys.stderr)
        return 1

    email, password = load_credentials()

    with sync_playwright() as p:
        browser, page = new_page(p)
        try:
            login(page, email, password)

            if args.edit_url:
                edit_url = args.edit_url
            else:
                edit_url = find_purchase_edit_url(page, args.invoice_nr)
                if not edit_url:
                    print(
                        f"No purchase entry found with Factuurnummer {args.invoice_nr!r}",
                        file=sys.stderr,
                    )
                    return 1

            page.goto(edit_url, wait_until="networkidle", timeout=60_000)
            nr = page.input_value("#ctl00_ContentPlaceLabo_PurchaseForm_InputPurchaseNr")
            subject = page.input_value("#ctl00_ContentPlaceLabo_PurchaseForm_TxtBoxTitle")
            print(f"Editing: {subject!r} (Factuurnummer {nr!r})")

            upload_attachment(page, attachment)
            print(f"Uploaded: {attachment.name}")

            page.screenshot(path="purchase-attachment-filled.png", full_page=True)

            if args.dry_run:
                print("Dry run: attachment staged, not saved.")
                return 0

            blocked = save_draft(page)
            if blocked:
                print(f"Save blocked:\n{blocked}", file=sys.stderr)
                return 1

            open_purchase_list(page)
            has_att = page.evaluate(
                """(invoiceNr) => {
                    const tr = [...document.querySelectorAll('table tbody tr')]
                        .find(row => row.innerText.includes(invoiceNr));
                    return tr ? !!tr.querySelector('a[href*="DynamicDownload"]') : false;
                }""",
                args.invoice_nr,
            )
            print(f"Saved OK. Attachment visible in list: {has_att}")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
