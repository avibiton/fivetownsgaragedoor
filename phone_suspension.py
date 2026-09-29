"""
Temporary phone-line suspension (build-time only; page sources are NOT modified).

Since 2026-09-29 the South Shore (516) 612-9317 and North Shore (516) 612-9316
lines are not operational, so the built site shows ONLY the main line
(516) 490-0931 / tel:+15164900931.

TO RESTORE THE LINES: set  SUSPENDED_LINES = set()  and run  python3 build.py.
Everything (titles, descriptions, dispatch cards, footer, contact page,
structured data, town-page call buttons) returns to the original content,
because the page sources in src/pages/ still contain the original numbers.
"""
import re

# Keys from build.PHONES. Empty set = all lines shown (normal operation).
SUSPENDED_LINES = {"south", "north"}

MAIN_TEL = "+15164900931"
MAIN_DISPLAY = "(516) 490-0931"
_NUMBERS = {
    "south": ("+15166129317", "(516) 612-9317", "+1-516-612-9317", "5166129317"),
    "north": ("+15166129316", "(516) 612-9316", "+1-516-612-9316", "5166129316"),
}


def active():
    return bool(SUSPENDED_LINES)


def _alts(i):
    return "|".join(re.escape(_NUMBERS[k][i]) for k in sorted(SUSPENDED_LINES))


def leftovers(text):
    """Suspended numbers still present in text (used as a build-time guard)."""
    if not active():
        return []
    pats = [re.escape(v) for k in SUSPENDED_LINES for v in _NUMBERS[k]] + [r"612-931[67]"]
    return re.findall("|".join(pats), text)


def suspend_text(text):
    """Plain-text rewrite (titles, meta descriptions, prose). Order matters."""
    if not active() or not text:
        return text
    disp = _alts(1)
    rules = [
        # LocationServices FAQ answer describing all three lines
        (r"The main line, \(516\) 490-0931, handles 24/7 dispatch and emergency service for every community\. "
         r"The South Shore line, \(516\) 612-9317, is a direct line for waterfront communities, and the North Shore line, "
         r"\(516\) 612-9316, serves northern Nassau County\.",
         "Call the main line, (516) 490-0931. It handles 24/7 dispatch and emergency service for every community."),
        # "Call the [Town] [South Shore] line at <number>" -> "Call us at <number>" (number may sit inside a link)
        (r"(?:the )?(?:[A-Z][a-z]+ )?(?:South Shore|North Shore|[A-Z][a-z]+) line at (?=(?:<a\b[^>]*>)?(?:" + disp + "))", "us at "),
        # "the South Shore line, <number>" -> "<number>"
        (r"(?:the )?(?:South|North) Shore line,? (?=(?:<a\b[^>]*>)?(?:" + disp + "))", ""),
    ]
    for pat, rep in rules:
        text = re.sub(pat, rep, text)
    return re.sub(disp, MAIN_DISPLAY, text)


def suspend_html(html):
    """Rewrite page body HTML before schema generation."""
    if not active():
        return html
    tel = _alts(0)
    link = r'<a\b[^>]*href="tel:(?:' + tel + r')"[^>]*>.*?</a>'
    # 1. Dedicated line entries: list items / contact line cards built around a suspended number.
    html = re.sub(r"<li>\s*" + link + r"\s*</li>", "", html, flags=re.S)
    html = re.sub(r'<a\b[^>]*class="line-card[^"]*"[^>]*href="tel:(?:' + tel + r')"[^>]*>.*?</a>', "", html, flags=re.S)
    # 2. Labelled inline mentions: "South Shore: <a>…</a>", "Waterfront & South Shore line: <a>…</a>"
    html = re.sub(r"(?:\s*·\s*)?(?:[\w&;]+ )*(?:South|North) Shore(?: [Ll]ine)?:\s*" + link, "", html, flags=re.S)
    # 3. Any other link to a suspended number becomes a main-line link.
    html = re.sub(r'href="tel:(?:' + tel + r')"', f'href="tel:{MAIN_TEL}"', html)
    # 4. Copy that only made sense with several lines.
    for old, new in [
        ("Call the Line That Fits Your Location", "Call Dispatch Directly"),
        (">Phone Lines<", ">Phone<"),
        ("Call the Line for Your Area", "Call Dispatch"),
        ("Direct Dispatch Lines", "Direct Dispatch"),
        ("Same-Day Repair Lines", "Same-Day Repair Dispatch"),
        ("All Phone Lines &amp; Contact", "Contact &amp; Dispatch"),
    ]:
        html = html.replace(old, new)
    # Drop a trailing "Main line: <main number>" add-on when it would just repeat the main number.
    html = re.sub(r"(?:\s*·\s*)?Main line:\s*<a\b[^>]*href=\"tel:\+15164900931\"[^>]*>.*?</a>", "", html, flags=re.S)
    html = re.sub(r'(<p class="dispatch-card__title">.*?) Lines</p>', r"\1 Dispatch</p>", html)
    # 5. Prose/number rewrite, then tidy separators and emptied containers.
    html = suspend_text(html)
    html = re.sub(r"(<p class=\"cta-band__alt\">)\s*·\s*", r"\1", html)
    html = re.sub(r"\s*·\s*(</p>)", r"\1", html)
    html = re.sub(r"<p class=\"[^\"]*\">\s*(?:·\s*)*</p>", "", html)
    html = re.sub(r"<ul class=\"dispatch-card__lines\">\s*</ul>", "", html)
    return html
