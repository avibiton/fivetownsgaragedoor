#!/usr/bin/env python3
"""
QA crawler for the built site (Python 3 standard library only).

    python3 tools/qa.py http://localhost:8787          # crawl a local server serving ./site
    python3 tools/qa.py https://fivetownsgaragedoor.com

Checks every legacy URL, all internal links/assets, tel:/mailto: links,
titles/descriptions/canonicals/H1s, JSON-LD validity (and that FAQPage
questions match visible FAQ text), sitemap.xml and robots.txt.
Exit code 1 if any problem is found.
"""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser

LEGACY = [
    "index.html", "cedarhurst-garage-door.html", "commercial.html", "contact.html", "faq.html",
    "Genieopeners.html", "hewlett-garage-door.html", "installation.html", "inwood-garage-door.html",
    "lawrence-garage-door.html", "liftmasteropeners.html", "LocationServices.html", "openers.html",
    "repair.html", "residential.html", "woodmere-garage-door.html",
]
CANON = "https://fivetownsgaragedoor.com"
TEL_OK = {"tel:+15164900931", "tel:+15166129317", "tel:+15166129316"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url):
    try:
        with OPENER.open(url, timeout=15) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.canonical = None
        self.h1 = []
        self.links = []
        self.assets = []
        self.jsonld = []
        self.faq_q = []
        self._in = None
        self._buf = ""
        self._summary_in_faq = False
        self._details_faq = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in, self._buf = "title", ""
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content", "")
        elif tag == "link":
            if a.get("rel") == "canonical":
                self.canonical = a.get("href")
            elif a.get("href") and a.get("rel") in ("stylesheet", "icon", "apple-touch-icon"):
                self.assets.append(a["href"])
        elif tag == "h1":
            self._in, self._buf = "h1", ""
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag in ("script", "img") and a.get("src"):
            self.assets.append(a["src"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in, self._buf = "ld", ""
        elif tag == "details" and "faq-item" in (a.get("class") or ""):
            self._details_faq += 1
        elif tag == "summary" and self._details_faq:
            self._in, self._buf = "q", ""
        elif tag == "form" and a.get("action"):
            self.links.append(a["action"])

    def handle_endtag(self, tag):
        if self._in == "title" and tag == "title":
            self.title = self._buf.strip()
            self._in = None
        elif self._in == "h1" and tag == "h1":
            self.h1.append(re.sub(r"\s+", " ", self._buf).strip())
            self._in = None
        elif self._in == "ld" and tag == "script":
            self.jsonld.append(self._buf)
            self._in = None
        elif self._in == "q" and tag == "summary":
            self.faq_q.append(re.sub(r"\s+", " ", self._buf).strip())
            self._in = None

    def handle_data(self, data):
        if self._in:
            self._buf += data


def types_of(node, out):
    if isinstance(node, dict):
        t = node.get("@type")
        if t:
            out.extend(t if isinstance(t, list) else [t])
        for v in node.values():
            types_of(v, out)
    elif isinstance(node, list):
        for v in node:
            types_of(v, out)
    return out


def main(base):
    base = base.rstrip("/")
    problems = []
    pages = {}
    queue = list(LEGACY) + ["", "404.html"]
    seen = set()
    inbound = {p: set() for p in LEGACY}
    asset_set = set()

    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        status, body, _ = fetch(f"{base}/{path}")
        if status != 200:
            problems.append(f"/{path} returned HTTP {status}")
            continue
        p = Page()
        p.feed(body)
        pages[path] = (p, body)
        for href in p.links:
            if href.startswith("tel:"):
                if href not in TEL_OK:
                    problems.append(f"/{path}: unexpected tel link {href}")
                continue
            if href.startswith("mailto:"):
                if not re.match(r"^mailto:service@fivetownsgaragedoor\.com(\?.*)?$", href):
                    problems.append(f"/{path}: malformed mailto {href}")
                continue
            if href.startswith(("http://", "https://")):
                continue
            target = href.split("#")[0].split("?")[0].lstrip("/")
            if not target:
                continue
            if target in inbound and target != path:
                inbound[target].add(path)
            if target.endswith(".html") and target not in seen:
                queue.append(target)
        for a in p.assets:
            if not a.startswith("http"):
                asset_set.add(a.split("?")[0].lstrip("/"))

    for a in sorted(asset_set):
        s, _, _ = fetch(f"{base}/{a}")
        if s != 200:
            problems.append(f"asset /{a} returned HTTP {s}")

    # --- per-page SEO report ---
    rows = []
    titles, descs = {}, {}
    for path in LEGACY:
        if path not in pages:
            continue
        p, body = pages[path]
        desc = p.meta.get("description", "")
        robots = p.meta.get("robots", "")
        titles.setdefault(p.title, []).append(path)
        descs.setdefault(desc, []).append(path)
        expected = f"{CANON}/{path}"
        if p.canonical != expected:
            problems.append(f"/{path}: canonical {p.canonical!r} != {expected}")
        if len(p.h1) != 1:
            problems.append(f"/{path}: {len(p.h1)} H1 elements")
        if "noindex" in robots:
            problems.append(f"/{path}: is noindex")
        if not desc:
            problems.append(f"/{path}: missing meta description")
        for k in ("og:title", "og:description", "og:url", "og:image", "twitter:card"):
            if not p.meta.get(k):
                problems.append(f"/{path}: missing {k}")
        if p.meta.get("og:url") != expected:
            problems.append(f"/{path}: og:url mismatch")
        stypes = []
        for raw in p.jsonld:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                problems.append(f"/{path}: invalid JSON-LD ({e})")
                continue
            stypes = types_of(data, [])
            for node in data.get("@graph", []):
                if node.get("@type") == "FAQPage":
                    schema_q = [q["name"] for q in node["mainEntity"]]
                    if schema_q != p.faq_q:
                        problems.append(f"/{path}: FAQPage schema questions differ from visible FAQ")
                if node.get("@type") == "WebPage" or node.get("@type") in ("CollectionPage", "ContactPage"):
                    if node.get("url") != expected:
                        problems.append(f"/{path}: WebPage url {node.get('url')} != canonical")
        if p.faq_q and "FAQPage" not in stypes:
            problems.append(f"/{path}: visible FAQ but no FAQPage schema")
        internal = [l for l in p.links if not l.startswith(("http", "tel:", "mailto:", "#"))]
        rows.append((path, p.title, desc, p.canonical, p.h1[0] if p.h1 else "", robots,
                     sorted(set(t for t in stypes if t in (
                         "HomeAndConstructionBusiness", "WebPage", "CollectionPage", "ContactPage",
                         "FAQPage", "BreadcrumbList", "Service", "WebSite"))),
                     len(internal), len(set(internal)), len(inbound.get(path, ()))))

    for t, ps in titles.items():
        if len(ps) > 1:
            problems.append(f"duplicate title on {ps}")
    for d, ps in descs.items():
        if len(ps) > 1:
            problems.append(f"duplicate meta description on {ps}")
    for path, srcs in inbound.items():
        if path != "index.html" and len(srcs) < 3:
            problems.append(f"/{path}: weakly linked (only {len(srcs)} inbound pages)")

    # --- homepage root ---
    s, root_body, _ = fetch(f"{base}/")
    if s != 200:
        problems.append(f"/ returned {s}")
    elif f'<link rel="canonical" href="{CANON}/index.html">' not in root_body:
        problems.append("/ does not carry the index.html canonical")

    # --- sitemap ---
    s, sm, _ = fetch(f"{base}/sitemap.xml")
    locs = []
    if s != 200:
        problems.append(f"sitemap.xml HTTP {s}")
    else:
        try:
            root = ET.fromstring(sm)
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            locs = [e.text for e in root.findall("s:url/s:loc", ns)]
        except ET.ParseError as e:
            problems.append(f"sitemap.xml invalid XML: {e}")
        want = {f"{CANON}/{p}" for p in LEGACY}
        if set(locs) != want:
            problems.append(f"sitemap mismatch: missing={sorted(want - set(locs))} extra={sorted(set(locs) - want)}")
        if len(locs) != len(set(locs)):
            problems.append("sitemap has duplicate URLs")

    # --- robots ---
    s, rb, _ = fetch(f"{base}/robots.txt")
    if s != 200:
        problems.append(f"robots.txt HTTP {s}")
    else:
        if re.search(r"^Disallow:\s*/\s*$", rb, re.M):
            problems.append("robots.txt blocks the whole site")
        if f"Sitemap: {CANON}/sitemap.xml" not in rb:
            problems.append("robots.txt missing Sitemap line")

    # --- 404 ---
    s, _, _ = fetch(f"{base}/this-page-does-not-exist.html")
    if s != 404:
        problems.append(f"missing page returned {s}, expected 404")

    # --- output ---
    print(f"{'URL':32} {'H1':46} {'INT':>4} {'UNIQ':>4} {'IN':>3}  SCHEMA")
    for r in rows:
        print(f"/{r[0]:31} {r[4][:46]:46} {r[7]:>4} {r[8]:>4} {r[9]:>3}  {', '.join(r[6])}")
    print()
    for r in rows:
        print(f"/{r[0]}\n  title ({len(r[1])}): {r[1]}\n  desc  ({len(r[2])}): {r[2]}\n  canonical: {r[3]} | robots: {r[5]}")
    print(f"\nPages crawled: {len(pages)} | assets checked: {len(asset_set)} | sitemap URLs: {len(locs)}")
    if problems:
        print(f"\n{len(problems)} PROBLEM(S):")
        for pr in problems:
            print("  -", pr)
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8787"))
