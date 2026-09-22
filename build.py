#!/usr/bin/env python3
"""
Five Towns Garage Door — static site builder (Python 3 standard library only).

    python3 build.py            # builds ./site  (the deployable web root)

Each file in src/pages/ is one production URL. The file name IS the URL, so the
legacy file names (including Genieopeners.html / LocationServices.html casing)
are preserved exactly. A page file starts with a JSON metadata block:

    <!--META
    { "title": "...", "description": "...", ... }
    META-->
    ...page <main> content...

The builder wraps the content in the shared head / header / footer, generates
JSON-LD (business entity, WebSite, WebPage, BreadcrumbList, Service, and
FAQPage built FROM the visible <details class="faq-item"> accordions so the
schema can never drift from on-page content), and writes sitemap.xml.

Production does NOT need Python or Node — upload the contents of ./site.
"""
import datetime
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
STATIC = SRC / "static"
OUT = ROOT / "site"

SITE = "https://fivetownsgaragedoor.com"
YEAR = 2026
BUILD_DATE = datetime.date.today().isoformat()

BUSINESS = {
    "name": "Five Towns Garage Door",
    "street": "579 Central Avenue",
    "city": "Cedarhurst",
    "region": "NY",
    "zip": "11516",
    "email": "service@fivetownsgaragedoor.com",
}
PHONES = {
    "main": {"tel": "+15164900931", "display": "(516) 490-0931", "label": "Main Line"},
    "south": {"tel": "+15166129317", "display": "(516) 612-9317", "label": "South Shore Line"},
    "north": {"tel": "+15166129316", "display": "(516) 612-9316", "label": "North Shore Line"},
}
TOWNS = [
    ("Cedarhurst", "11516", "cedarhurst-garage-door.html", "https://en.wikipedia.org/wiki/Cedarhurst,_New_York"),
    ("Hewlett", "11557", "hewlett-garage-door.html", "https://en.wikipedia.org/wiki/Hewlett,_New_York"),
    ("Lawrence", "11559", "lawrence-garage-door.html", "https://en.wikipedia.org/wiki/Lawrence,_Nassau_County,_New_York"),
    ("Woodmere", "11598", "woodmere-garage-door.html", "https://en.wikipedia.org/wiki/Woodmere,_New_York"),
    ("Inwood", "11096", "inwood-garage-door.html", "https://en.wikipedia.org/wiki/Inwood,_New_York"),
]

# --------------------------------------------------------------------------
# Icons (inline SVG sprite; simple stroke icons drawn for this site)
# --------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z"/>',
    "spring": '<path d="M4 4h16M4 20h16"/><path d="M6 7l12 2.5L6 12l12 2.5L6 17"/>',
    "cable": '<path d="M8 3v5a4 4 0 0 0 8 0V3"/><path d="M12 12v9"/><circle cx="12" cy="21" r="1"/>',
    "opener": '<rect x="3" y="4" width="18" height="8" rx="1"/><path d="M7 12v3M17 12v3M12 12v8"/><circle cx="12" cy="8" r="1.5"/>',
    "door": '<path d="M3 21V7l9-4 9 4v14"/><path d="M6 21v-9h12v9M6 15h12M6 18h12"/>',
    "building": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M7 21v-8h10v8M7 16h10M7 7h2M11 7h2M15 7h2"/>',
    "home": '<path d="M3 11 12 3l9 8"/><path d="M5 10v11h14V10"/><path d="M9 21v-6h6v6"/>',
    "bolt": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "wave": '<path d="M2 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0 2 2 2 2"/><path d="M2 18c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 6c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    "wifi": '<path d="M5 12.6a10 10 0 0 1 14 0M8.5 16.1a5 5 0 0 1 7 0M2 8.8a15 15 0 0 1 20 0"/><path d="M12 20h.01"/>',
    "battery": '<rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 11v2M6 10v4M10 10v4"/>',
    "volume": '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "snow": '<path d="M12 2v20M2 12h20M4.9 4.9l14.2 14.2M19.1 4.9 4.9 19.1"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.1-6"/>',
    "flower": '<circle cx="12" cy="12" r="3"/><path d="M12 2a3 3 0 0 1 0 7M12 15a3 3 0 0 1 0 7M2 12a3 3 0 0 1 7 0M15 12a3 3 0 0 1 7 0"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 2h6v4H9zM9 12h6M9 16h6"/>',
    "truck": '<path d="M1 4h14v12H1zM15 9h4l4 4v3h-8"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/>',
    "dollar": '<path d="M12 2v20M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "thermo": '<path d="M14 14.8V4a2 2 0 0 0-4 0v10.8a4 4 0 1 0 4 0z"/>',
    "window": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M9 9v12M15 9v12"/>',
    "fire": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.4-.5-2-1-3-1.1-2.1-.2-4.1 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.2.4-2.3 1-3.3.2 1.5 1.3 2.8 2.5 2.8z"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
}
ICON_RE = re.compile(r"\{\{icon:([a-z-]+)\}\}")


def icon(name, cls="icon"):
    if name not in ICONS:
        sys.exit(f"Unknown icon: {name}")
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{name}"></use></svg>'


def sprite(used):
    symbols = "".join(
        f'<symbol id="i-{n}" viewBox="0 0 24 24">{ICONS[n]}</symbol>' for n in sorted(used)
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">{symbols}</svg>'


LOGO_MARK = (
    '<svg class="logo__mark" viewBox="0 0 48 48" aria-hidden="true" focusable="false">'
    '<rect width="48" height="48" rx="4" fill="#c8002a"/>'
    '<path d="M8 40V18L24 9l16 9v22" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round"/>'
    '<g fill="#fff"><rect x="13" y="22" width="22" height="3.6"/><rect x="13" y="27.6" width="22" height="3.6"/>'
    '<rect x="13" y="33.2" width="22" height="3.6"/></g></svg>'
)

# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------
NAV = [
    ("services", "Services", None, [
        ("repair.html", "Garage Door Repair", ""),
        ("installation.html", "New Door Installation", ""),
        ("openers.html", "Garage Door Openers", ""),
        ("residential.html", "Residential Service", ""),
        ("commercial.html", "Commercial Service", ""),
        None,
        ("liftmasteropeners.html", "LiftMaster Openers", ""),
        ("Genieopeners.html", "Genie Openers", ""),
    ]),
    ("repair", "Repair", "repair.html", None),
    ("installation", "Installation", "installation.html", None),
    ("openers", "Openers", "openers.html", None),
    ("locations", "Locations", None, [("LocationServices.html", "All Service Locations", "")] + [None] +
        [(f, t, z) for t, z, f, _ in TOWNS]),
    ("faq", "FAQ", "faq.html", None),
    ("contact", "Contact", "contact.html", None),
]


def render_nav(current_file, active):
    items = []
    for key, label, href, sub in NAV:
        is_active = key == active
        if sub is None:
            cur = ' aria-current="page"' if href == current_file else ""
            cls = "nav__item nav__item--active" if is_active else "nav__item"
            items.append(f'<li class="{cls}"><a class="nav__link" href="{href}"{cur}>{label}</a></li>')
            continue
        links = []
        for s in sub:
            if s is None:
                links.append("<li><hr></li>")
                continue
            f, t, z = s
            cur = ' aria-current="page"' if f == current_file else ""
            small = f"<small>NY {z}</small>" if z else ""
            links.append(f'<li><a href="{f}"{cur}>{t}{small}</a></li>')
        cls = "nav__item nav__item--active" if is_active else "nav__item"
        items.append(
            f'<li class="{cls}"><button class="nav__link nav__toggle" type="button" aria-expanded="false" '
            f'aria-controls="sub-{key}">{label}{icon("chevron")}</button>'
            f'<ul class="nav__sub" id="sub-{key}">{"".join(links)}</ul></li>'
        )
    return "".join(items)


def render_header(page):
    ph = PHONES[page["phone"]]
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="dispatch-bar">
  <div class="wrap">
    <span class="dispatch-bar__item"><span class="live" aria-hidden="true"></span>24/7 Direct Local Dispatch</span>
    <span class="dispatch-bar__item dispatch-bar__item--hide-sm">{icon("pin")}Cedarhurst · Hewlett · Lawrence · Woodmere · Inwood</span>
    <span class="dispatch-bar__item">Call <a href="tel:{PHONES["main"]["tel"]}" class="js-call" data-cta="topbar-call">{PHONES["main"]["display"]}</a></span>
  </div>
</div>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Five Towns Garage Door — home">{LOGO_MARK}<span class="logo__text">Five Towns <span>Garage Door</span><small>Nassau County · South Shore</small></span></a>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">{render_nav(page["file"], page.get("nav"))}</ul>
      <div class="nav-mobile-cta">
        <a class="btn btn--primary btn--block js-call" href="tel:{ph["tel"]}" data-cta="menu-call">{icon("phone")}Call {ph["display"]}</a>
        <a class="btn btn--outline btn--block" href="contact.html">All Phone Lines &amp; Contact</a>
        <p>Open 24 hours · 7 days · Holidays included</p>
      </div>
    </nav>
    <div class="header-actions">
      <a class="header-call js-call" href="tel:{ph["tel"]}" data-cta="header-call" aria-label="Call {ph["display"]}">{icon("phone")}<span class="header-call__txt"><small>Call 24/7</small><strong>{ph["display"]}</strong></span></a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">{icon("menu", "icon icon-open")}{icon("close", "icon icon-close")}</button>
    </div>
  </div>
</header>'''


def render_footer(page):
    town_links = "".join(f'<li><a href="{f}">{t} NY {z}</a></li>' for t, z, f, _ in TOWNS)
    m, s, n = PHONES["main"], PHONES["south"], PHONES["north"]
    ph = PHONES[page["phone"]]
    return f'''<footer class="site-footer">
  <div class="wrap site-footer__top">
    <div class="site-footer__brand">
      <a class="logo" href="index.html" aria-label="Five Towns Garage Door — home">{LOGO_MARK}<span class="logo__text">Five Towns <span>Garage Door</span></span></a>
      <p class="site-footer__about">Dedicated garage door repair and installation throughout Cedarhurst, Hewlett, Lawrence, Woodmere, and Inwood, Nassau County NY.</p>
      <address class="footer-nap">
        <a class="footer-nap__main js-call" href="tel:{m["tel"]}" data-cta="footer-call">{icon("phone")}{m["display"]}</a>
        <a class="js-call" href="tel:{s["tel"]}" data-cta="footer-call-south">South Shore: {s["display"]}</a>
        <a class="js-call" href="tel:{n["tel"]}" data-cta="footer-call-north">North Shore: {n["display"]}</a>
        <a href="mailto:{BUSINESS["email"]}">{icon("mail")}{BUSINESS["email"]}</a>
        <span>{BUSINESS["street"]}, {BUSINESS["city"]}, {BUSINESS["region"]} {BUSINESS["zip"]}</span>
        <span>Monday – Sunday: 24 Hours</span>
      </address>
    </div>
    <div>
      <h2>Services</h2>
      <ul>
        <li><a href="repair.html">Garage Door Repair</a></li>
        <li><a href="installation.html">New Door Installation</a></li>
        <li><a href="openers.html">Opener Repair &amp; Install</a></li>
        <li><a href="residential.html">Residential Service</a></li>
        <li><a href="commercial.html">Commercial Service</a></li>
      </ul>
    </div>
    <div>
      <h2>Openers &amp; Help</h2>
      <ul>
        <li><a href="liftmasteropeners.html">LiftMaster Openers</a></li>
        <li><a href="Genieopeners.html">Genie Openers</a></li>
        <li><a href="openers.html">All Opener Types</a></li>
        <li><a href="faq.html">Garage Door FAQ</a></li>
        <li><a href="contact.html">Contact &amp; Dispatch</a></li>
      </ul>
    </div>
    <div>
      <h2>Communities</h2>
      <ul>
        {town_links}
        <li><a href="LocationServices.html">All Service Locations</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap site-footer__bottom">
    <span>&copy; {YEAR} Five Towns Garage Door · fivetownsgaragedoor.com · Nassau County NY · Licensed &amp; Insured</span>
    <span>Same-day service · Free written estimates</span>
  </div>
</footer>
<nav class="mobile-bar" aria-label="Quick contact">
  <a class="mobile-bar__call js-call" href="tel:{ph["tel"]}" data-cta="sticky-call">{icon("phone")}<span>Call Now<small>{ph["display"]}</small></span></a>
  <a class="mobile-bar__req" href="contact.html#request" data-cta="sticky-request">{icon("clipboard")}Request</a>
</nav>'''


def render_breadcrumbs(crumbs):
    items = ['<li><a href="index.html">Home</a></li>']
    for c in crumbs:
        if len(c) > 1 and c[1]:
            items.append(f'<li><a href="{c[1]}">{c[0]}</a></li>')
        else:
            items.append(f'<li><span aria-current="page">{c[0]}</span></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


# --------------------------------------------------------------------------
# Structured data
# --------------------------------------------------------------------------
def business_entity():
    return {
        "@type": ["HomeAndConstructionBusiness", "LocalBusiness"],
        "@id": f"{SITE}/#business",
        "name": BUSINESS["name"],
        "legalName": BUSINESS["name"],
        "url": SITE,
        "logo": f"{SITE}/assets/images/logo-512.png",
        "image": f"{SITE}/assets/images/og-default.png",
        "telephone": "+1-516-490-0931",
        "email": BUSINESS["email"],
        "priceRange": "$$",
        "currenciesAccepted": "USD",
        "paymentAccepted": "Cash, Credit Card, Check",
        "openingHours": "Mo-Su 00:00-23:59",
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00",
            "closes": "23:59",
        },
        "address": {
            "@type": "PostalAddress",
            "streetAddress": BUSINESS["street"],
            "addressLocality": BUSINESS["city"],
            "addressRegion": BUSINESS["region"],
            "postalCode": BUSINESS["zip"],
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 40.6234, "longitude": -73.7296},
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": "+1-516-490-0931", "contactType": "customer service",
             "name": "Main Line — 24/7 Dispatch & Emergency Service", "areaServed": "US-NY", "availableLanguage": "English"},
            {"@type": "ContactPoint", "telephone": "+1-516-612-9317", "contactType": "customer service",
             "name": "South Shore Line", "areaServed": "US-NY", "availableLanguage": "English"},
            {"@type": "ContactPoint", "telephone": "+1-516-612-9316", "contactType": "customer service",
             "name": "North Shore Line", "areaServed": "US-NY", "availableLanguage": "English"},
        ],
        "areaServed": [
            {"@type": "City", "name": t, "postalCode": z, "sameAs": w} for t, z, _, w in TOWNS
        ],
        "knowsAbout": [
            "Garage Door Repair", "Torsion Spring Replacement", "Extension Spring Replacement",
            "LiftMaster Garage Door Openers", "Genie Garage Door Openers", "MyQ Smart Garage Control",
            "Marine-Grade 316 Stainless Steel Cables", "Coastal Salt Air Corrosion Prevention",
            "Emergency Off-Track Door Alignment", "Commercial Rolling Steel Doors",
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Emergency & Standard Garage Door Services",
            "itemListElement": [
                {"@type": "Offer", "name": n, "price": p, "priceCurrency": "USD",
                 "availability": "https://schema.org/InStock", "priceValidUntil": "2027-12-31"}
                for n, p in [
                    ("Broken Torsion Spring Replacement", "295.00"),
                    ("Extension Spring Replacement Pair", "145.00"),
                    ("Lifting Cable Replacement Pair", "125.00"),
                    ("22-Point Annual Safety Tune-Up", "99.00"),
                ]
            ],
        },
    }


TAG_RE = re.compile(r"<[^>]+>")
FAQ_RE = re.compile(
    r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div class="faq-answer">(.*?)</div>\s*</details>',
    re.S,
)


def plain(s):
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", s))).strip().replace(" ,", ",").replace(" .", ".")


def build_graph(page, content):
    url = page["canonical"]
    graph = [business_entity()]
    graph.append({
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "url": SITE,
        "name": BUSINESS["name"],
        "publisher": {"@id": f"{SITE}/#business"},
        "inLanguage": "en-US",
    })
    webpage = {
        "@type": page.get("webpage_type", "WebPage"),
        "@id": f"{url}#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "isPartOf": {"@id": f"{SITE}/#website"},
        "about": {"@id": f"{SITE}/#business"},
        "inLanguage": "en-US",
        "speakable": {"@type": "SpeakableSpecification",
                      "cssSelector": page.get("speakable", ["h1", ".page-hero .lede", ".faq-answer"])},
    }
    if page.get("breadcrumbs"):
        webpage["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/index.html"}]
        for i, c in enumerate(page["breadcrumbs"], start=2):
            href = c[1] if len(c) > 1 and c[1] else page["file"]
            items.append({"@type": "ListItem", "position": i, "name": c[0], "item": f"{SITE}/{href}"})
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": items})
    graph.append(webpage)

    svc = page.get("service")
    if svc:
        area = svc.get("areaServed")
        if area:
            town = next(t for t in TOWNS if t[0] == area)
            area_val = {"@type": "City", "name": town[0], "postalCode": town[1], "sameAs": town[3]}
        else:
            area_val = [{"@type": "City", "name": t, "postalCode": z} for t, z, _, _ in TOWNS]
        s = {
            "@type": "Service",
            "@id": f"{url}#service",
            "name": svc["name"],
            "serviceType": svc.get("serviceType", svc["name"]),
            "description": svc.get("description", page["description"]),
            "provider": {"@id": f"{SITE}/#business"},
            "areaServed": area_val,
            "url": url,
        }
        if svc.get("brand"):
            s["brand"] = {"@type": "Brand", "name": svc["brand"]}
        graph.append(s)

    faqs = FAQ_RE.findall(content)
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntityOfPage": {"@id": f"{url}#webpage"},
            "mainEntity": [
                {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
                for q, a in faqs
            ],
        })
    data = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------
META_RE = re.compile(r"^\s*<!--META\s*(\{.*?\})\s*META-->\s*", re.S)


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


def esc(s):
    return html.escape(s, quote=True)


def render_page(page, content, css_href, js_href):
    used = set(ICON_RE.findall(content)) | {"phone", "pin", "chevron", "menu", "close", "mail", "clipboard"}
    content = ICON_RE.sub(lambda m: icon(m.group(1)), content)
    if "{{breadcrumbs}}" in content:
        content = content.replace("{{breadcrumbs}}", render_breadcrumbs(page.get("breadcrumbs", [])))
    content = content.replace("{{year}}", str(YEAR))
    unresolved = re.findall(r"\{\{[^}]+\}\}", content)
    if unresolved:
        sys.exit(f"{page['file']}: unresolved placeholders {unresolved}")

    title, desc = page["title"], page["description"]
    og_title = page.get("og_title", title)
    og_desc = page.get("og_description", desc)
    robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large"
    canonical = f'<link rel="canonical" href="{page["canonical"]}">' if not page.get("noindex") else ""
    og_image = f"{SITE}/assets/images/og-default.png"
    jsonld = "" if page.get("noindex") else f'<script type="application/ld+json">\n{build_graph(page, content)}\n</script>'

    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
{canonical}
<meta name="theme-color" content="#0f0f0f">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="US-NY">
<meta name="geo.placename" content="{esc(page.get("geo_place", "Cedarhurst"))}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Five Towns Garage Door">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(og_desc)}">
<meta property="og:url" content="{page["canonical"]}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Five Towns Garage Door — same-day garage door repair and installation, Cedarhurst NY">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(og_desc)}">
<meta name="twitter:image" content="{og_image}">
<link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/icons/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/oswald-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/source-sans-3-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{css_href}">
{jsonld}
</head>
<body class="page-{esc(page.get("body_class", page["file"].rsplit(".", 1)[0].lower()))}">
{sprite(used)}
{render_header(page)}
<main id="main">
{content.strip()}
</main>
{render_footer(page)}
<script src="{js_href}" defer></script>
</body>
</html>
'''
    if page.get("noindex"):
        # Error pages can be served at any depth: make local URLs root-absolute.
        head = re.sub(r'((?:href|src)=")(?!https?:|tel:|mailto:|#|/)', r"\1/", head)
    return head


def load_pages():
    pages = []
    for path in sorted(PAGES.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            sys.exit(f"{path.name}: missing <!--META {{...}} META--> block")
        try:
            meta = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            sys.exit(f"{path.name}: bad META JSON: {e}")
        meta["file"] = path.name
        meta.setdefault("phone", "main")
        meta.setdefault("canonical", f"{SITE}/{path.name}")
        for req in ("title", "description"):
            if req not in meta:
                sys.exit(f"{path.name}: META missing '{req}'")
        pages.append((meta, raw[m.end():]))
    return pages


def check(names):
    """Render pages in memory and run basic structural checks (does not touch ./site)."""
    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.h1 = 0
            self.a_depth = 0
            self.nested = 0
            self.ids = []
            self.headings = []
            self._h = None

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "h1":
                self.h1 += 1
            if tag == "a":
                if self.a_depth:
                    self.nested += 1
                self.a_depth += 1
            if "id" in a:
                self.ids.append(a["id"])
            if tag in ("h1", "h2", "h3", "h4"):
                self._h = int(tag[1])

        def handle_endtag(self, tag):
            if tag == "a":
                self.a_depth -= 1
            if tag in ("h1", "h2", "h3", "h4") and self._h:
                self.headings.append(self._h)
                self._h = None

    ok = True
    pages = {m["file"]: (m, c) for m, c in load_pages()}
    for name in names:
        if name not in pages:
            print(f"{name}: not found in src/pages")
            ok = False
            continue
        meta, content = pages[name]
        out = render_page(meta, content, "x.css", "x.js")
        p = P()
        p.feed(out)
        faqs = len(FAQ_RE.findall(out))
        dup = sorted({i for i in p.ids if p.ids.count(i) > 1})
        errs = []
        if p.h1 != 1:
            errs.append(f"{p.h1} <h1> elements")
        if p.nested:
            errs.append(f"{p.nested} nested <a>")
        if dup:
            errs.append(f"duplicate ids {dup}")
        if out.count('<details class="faq-item"') != faqs:
            errs.append("FAQ markup not matching the required pattern")
        skips = [(a, b) for a, b in zip(p.headings, p.headings[1:]) if b > a + 1]
        if skips:
            errs.append(f"heading level skips {skips}")
        if "style=" in content:
            errs.append("inline style attribute found")
        status = "OK" if not errs else "FAIL: " + "; ".join(errs)
        print(f"{name}: {status} | title={len(meta['title'])}ch desc={len(meta['description'])}ch faqs={faqs}")
        ok = ok and not errs
    return ok


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        sys.exit(0 if check(sys.argv[2:]) else 1)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT, ignore=shutil.ignore_patterns(".DS_Store", "site.css"))

    css = minify_css((STATIC / "assets/css/site.css").read_text(encoding="utf-8"))
    css_hash = hashlib.sha1(css.encode()).hexdigest()[:10]
    (OUT / "assets/css/site.min.css").write_text(css, encoding="utf-8")
    js_hash = hashlib.sha1((STATIC / "assets/js/site.js").read_bytes()).hexdigest()[:10]
    css_href = f"assets/css/site.min.css?v={css_hash}"
    js_href = f"assets/js/site.js?v={js_hash}"

    sitemap = []
    for meta, content in load_pages():
        out = render_page(meta, content, css_href, js_href)
        (OUT / meta["file"]).write_text(out, encoding="utf-8")
        if not meta.get("noindex"):
            sitemap.append((meta["canonical"], meta.get("priority", "0.8")))
        print(f"  built {meta['file']}")

    order = {u: i for i, u in enumerate(json.loads((SRC / "sitemap-order.json").read_text()))}
    sitemap.sort(key=lambda x: order.get(x[0].rsplit("/", 1)[1], 999))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in sitemap:
        xml.append(f"  <url><loc>{loc}</loc><lastmod>{BUILD_DATE}</lastmod><priority>{pri}</priority></url>")
    xml.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print(f"Built {len(sitemap)} indexable pages -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
