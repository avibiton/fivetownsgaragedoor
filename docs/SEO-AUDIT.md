# Pre-rebuild audit — fivetownsgaragedoor.com

Source audited: `legacy-source/` (the supplied *FiveTownsGarageDoor_Production_Site_With_Legacy_Redirects* package),
`FiveTownsGarageDoor_CleanSite_contact.html` (identical to `legacy-source/contact.html`), and
`DEVELOPER_URL_MAPPING_AND_301_REDIRECTS.txt` (copied to `docs/`).

## Inventory
16 HTML pages, `sitemap.xml` (16 URLs), `.htaccess`, `_redirects`. No images, CSS or JS files — every page
carried its own inline `<style>` block and Google Fonts link. No `robots.txt`, no favicon, no 404 page.

## Per-page SEO (legacy)

| URL | Title | H1 | OG | JSON-LD | Schema FAQ questions shown verbatim on page |
|---|---|---|---|---|---|
| /index.html | Five Towns Garage Door \| Same-Day Repair & Installation \| (516) 490-0931 | Garage Door Repair & Installation Services | no | LocalBusiness, WebPage, FAQPage | 1 of 4 |
| /repair.html | Garage Door Repair Five Towns NY \| Same-Day \| … | Garage Door Repair Five Towns, NY | yes | + FAQPage | 1 of 4 |
| /installation.html | Garage Door Installation Five Towns NY \| … | New Garage Door Installation — Five Towns, NY | yes | + FAQPage | 1 of 4 |
| /openers.html | Garage Door Openers Five Towns NY \| LiftMaster Genie … | Garage Door Openers Five Towns, NY | yes | + FAQPage | 1 of 4 |
| /residential.html | Residential Garage Door Service Five Towns NY \| … | Residential Garage Door Service — Five Towns, NY | yes | + FAQPage | 0 of 3 |
| /commercial.html | Commercial Garage Door Service Five Towns NY \| … | Commercial Garage Door Service — Five Towns, NY | yes | + FAQPage | 0 of 3 |
| /liftmasteropeners.html | LiftMaster Garage Door Openers Five Towns NY \| … | LiftMaster Garage Door Openers Five Towns, Nassau County NY | no | + FAQPage | 1 of 4 |
| /Genieopeners.html | Genie Garage Door Openers Five Towns NY \| … | Genie Garage Door Openers Five Towns, Nassau County NY | no | + FAQPage | 0 of 3 |
| /LocationServices.html | Five Towns Garage Door Locations \| Nassau County NY \| … | Service Locations | no | LocalBusiness, WebPage | n/a |
| /cedarhurst-garage-door.html | Garage Door Repair Cedarhurst NY 11516 \| … \| (516) 612-9317 | Garage Door Repair Cedarhurst, NY | yes | + FAQPage | 1 of 4 |
| /hewlett-garage-door.html | … Hewlett NY 11557 … | Garage Door Repair Hewlett, NY | yes | + FAQPage | 1 of 4 |
| /lawrence-garage-door.html | … Lawrence NY 11559 … | Garage Door Repair Lawrence, NY | yes | + FAQPage | 2 of 4 |
| /woodmere-garage-door.html | … Woodmere NY 11598 … | Garage Door Repair Woodmere, NY | yes | + FAQPage | 2 of 4 |
| /inwood-garage-door.html | … Inwood NY 11096 … | Garage Door Repair Inwood, NY | yes | + FAQPage | 1 of 4 |
| /faq.html | FAQ \| Five Towns Garage Door \| (516) 490-0931 | Frequently Asked Questions | no | + FAQPage (8) | 8 of 8 ✓ |
| /contact.html | Contact Us \| Five Towns Garage Door \| (516) 490-0931 | Contact Five Towns Garage Door | no | **none** | n/a |

All canonicals were correct absolute `https://fivetownsgaragedoor.com/<file>` URLs; every page had one H1 and a unique title/description.

## Inconsistencies found (and how they were handled)
1. **FAQ schema ≠ visible FAQ** on 13 of the 14 pages with FAQ markup (only faq.html matched) (Google's guidelines require FAQ markup to match visible content).
   → The builder now generates FAQPage JSON-LD *from* the visible accordions; each page's visible FAQ is the union of the old visible + old schema questions, so no Q&A was lost.
2. **Homepage WebPage `@id`/`url` was `/`** while the canonical is `/index.html`. → WebPage now uses the canonical URL.
3. **Orphan / weakly linked pages**: `contact.html` had **zero** inbound links; `faq.html`, `commercial.html`, `residential.html`, `LocationServices.html`, `Genieopeners.html`, `liftmasteropeners.html` were linked from only a few pages. `contact.html`, `faq.html` and `LocationServices.html` had no site navigation at all. → Global header/footer navigation; every page now has 17 inbound internal links.
4. **Missing Open Graph** on index, contact, faq, LocationServices, Genie, LiftMaster. → OG + Twitter tags on every page.
5. **contact.html had no structured data.** → Now ContactPage + business entity + breadcrumbs.
6. **Speakable selectors** pointed at `.hero p` / `.faq-ans p`, which did not exist on LocationServices.html (it used `.page-hero`). → Updated per page to real selectors.
7. **Manufacturer authorization claims** ("Authorized LiftMaster…", "Authorized LiftMaster & Genie dealer") in openers.html and liftmasteropeners.html meta descriptions and copy — not verifiable from the supplied material. → Removed (the only meta-description edits made). Restore if the business holds dealer authorization.
8. **Price inconsistencies across pages** (kept as-is per page, flagged for the owner): stainless/marine cables $155 (home, Cedarhurst) vs $175 (Lawrence, Inwood table); LiftMaster logic board from $85 (openers) vs $165 (LiftMaster page).
9. **Legacy redirect configs**: `.htaccess` mixed `mod_alias` `Redirect` with `mod_rewrite`, had no www→non-www rule, and HTTPS-forcing kept the requested host (so `http://www.` → `https://www.`, a two-hop chain once www is normalized). The `_redirects` line `http://* https://:splat` in the developer notes is not valid Netlify syntax. → Rewritten; all rules go to the final canonical URL in one hop.
10. **No robots.txt**, no favicon, no 404 page. → Added.
