# Page authoring guide — Five Towns Garage Door

Pages live in `src/pages/<ExactLegacyFileName>.html`. `python3 build.py` wraps them in the shared
head/header/footer/mobile bar and writes `site/`. **Do not edit `build.py` or `site.css`** — use the
components below. Reference implementations: `src/pages/index.html` (homepage) and
`src/pages/LocationServices.html` (inner page). Read both before writing a page.

## 1. META block (first thing in the file)

```html
<!--META
{
  "title": "...exact legacy <title>...",
  "description": "...exact legacy meta description...",
  "og_title": "...legacy og:title if it existed, else a short variant of the title...",
  "og_description": "...legacy og:description if it existed, else a short variant...",
  "nav": "repair",             // home|services|repair|installation|openers|locations|faq|contact
  "phone": "main",             // main (516) 490-0931 | south (516) 612-9317 — drives header + sticky call buttons
  "priority": "0.9",           // legacy sitemap priority
  "breadcrumbs": [["Services", null], ["Garage Door Repair"]],   // last item = current page, no href
  "service": {"name": "Garage Door Repair", "serviceType": "Garage Door Repair"},   // optional → Service schema
  "geo_place": "Cedarhurst"    // optional, town pages only
}
META-->
```

* Breadcrumb items: `["Label", "file.html"]` for a link, `["Label"]` for the current page.
  Use `["Service Locations", "LocationServices.html"]` as the parent for town pages.
  For service/brand pages use `[["Garage Door Openers","openers.html"],["LiftMaster Openers"]]` or just `[["Garage Door Repair"]]`.
* `service.areaServed` may be set to a town name ("Cedarhurst") on town pages.
* `service.brand` may be set ("LiftMaster" / "Genie") on brand pages.
* FAQ schema is generated automatically from the visible FAQ accordion — never write JSON-LD by hand.
* Business / WebSite / WebPage / BreadcrumbList schema is generated automatically.

## 2. Placeholders

* `{{icon:NAME}}` → inline SVG icon. Available: phone clock shield check pin wrench spring cable opener door
  building home bolt calendar mail arrow chevron menu close wave gear alert wifi battery volume sun snow leaf
  flower clipboard truck dollar star lock thermo window fire list
* `{{breadcrumbs}}` → breadcrumb nav (place inside the page hero, first child).

## 3. Phone links (analytics-ready)

Every tel link: `<a class="js-call" href="tel:+15164900931" data-cta="PAGEKEY-LOCATION-call">`.
Buttons add `btn btn--primary` etc. Numbers:

| Line | href | display |
|---|---|---|
| Main | `tel:+15164900931` | (516) 490-0931 |
| South Shore | `tel:+15166129317` | (516) 612-9317 |
| North Shore | `tel:+15166129316` | (516) 612-9316 |

`data-cta` examples: `repair-hero-call`, `repair-pricing-call`, `repair-faq-call`, `repair-final-call`,
`cedarhurst-hero-call`, `cedarhurst-final-call-main`. Keep them unique per page.

## 4. Components

### Page hero (every inner page, exactly one H1)
```html
<section class="page-hero" aria-labelledby="page-title">
  <div class="wrap page-hero__grid">
    <div>
      {{breadcrumbs}}
      <p class="page-hero__tag">{{icon:pin}}Cedarhurst NY · 11516 · Nassau County</p>
      <h1 id="page-title">Garage Door Repair <span>Cedarhurst, NY</span></h1>   <!-- <span> = red second line; keep the space before it -->
      <p class="lede">...</p>
      <div class="btn-row">
        <a class="btn btn--primary btn--lg js-call" href="tel:..." data-cta="...">{{icon:phone}}Call (516) ...</a>
        <a class="btn btn--ghost" href="#services">Our Services{{icon:arrow}}</a>
      </div>
      <ul class="hero-points"><li>{{icon:truck}}Same-Day Service</li>...</ul>
    </div>
    <aside class="dispatch-card"> ... see LocationServices.html ... </aside>   <!-- optional side card: phone lines, pricing teaser, or key facts -->
  </div>
</section>
```
Use `page-hero page-hero--compact` and drop the aside for a single-column hero.

### Sections
`<section class="section section--white|section--cream|section--off|section--dark" aria-labelledby="x-title"><div class="wrap">…</div></section>`
Alternate backgrounds; avoid two identical backgrounds in a row. `section--dark` = dark steel with white text.

Section header:
```html
<div class="section-head">
  <p class="eyebrow">Short label</p>
  <h2 class="h-section" id="x-title">Heading</h2>
  <p class="lede">Intro sentence.</p>
</div>
```

Layouts: `.split` (content + side column, stacks on mobile), `.split--even`, `.split--center`,
`.grid-2`, `.grid-3`, `.grid-4`. `.sticky-col` for a sticky left column (FAQ sections).
Body copy goes in `<div class="prose">` (supports p, ul, h3, strong, links).

### Cards
```html
<div class="card">                                   <!-- or <a class="card" href="..."> when the whole card is ONE link -->
  <span class="card__icon">{{icon:spring}}</span>
  <h3 class="card__title">Spring Repair</h3>
  <p class="card__text">...</p>
  <ul class="card__list"><li>{{icon:check}}Item</li></ul>
  <dl class="specs"><div><dt>Drive</dt><dd>Belt</dd></div></dl>
  <div class="card__foot"><span class="card__price">From $145</span><a class="card__link" href="repair.html">Spring repair{{icon:arrow}}</a></div>
</div>
```
**Never nest links**: if a card contains any inline `<a>`, the card must be a `<div>` (use `class="card card--link"` for the hover style) with a `<a class="card__link">` in the foot.
Variants: `card--dark` (on dark sections), `card--flat`, `card--accent` (red top rule). Badge: `<span class="badge badge--red">Recommended</span>` (first child).

Brand card: `<div class="brand-card"><div class="brand-card__head"><span class="brand-card__name">LiftMaster</span>{{icon:opener}}</div><div class="brand-card__body">…</div></div>`

### Price table (use for every legacy pricing table — keep every row and amount exactly)
```html
<table class="price-table">
  <caption><span>Cedarhurst Repair Pricing</span><span>From</span></caption>
  <tbody>
    <tr><th scope="row">Torsion Spring Replacement</th><td>$295</td></tr>
    <tr class="is-free"><th scope="row">Written Estimate</th><td>FREE</td></tr>
  </tbody>
</table>
<p class="price-note">Any legacy footnote under the table.</p>
```

### Comparison table
`<div class="table-wrap"><table class="data-table"><thead><tr><th scope="col">…</th></tr></thead><tbody><tr><th scope="row">…</th><td>…</td></tr></tbody></table></div>`

### Callout
```html
<div class="callout callout--coastal">   <!-- plain | callout--coastal (salt-air notes) | callout--alert (safety warnings) -->
  <h3 class="callout__title">{{icon:wave}}Cedarhurst South Shore Note</h3>
  <p>...</p>
</div>
```

### Steps (process)
`<ol class="steps">` (4 cols) / `steps steps--3` / `steps steps--5`, each `<li class="step"><h3>Title</h3><p>Text</p></li>`. Numbers are automatic. Looks best in `section--dark`.

### Checklist
`<ul class="checklist">` or `checklist checklist--2` (two columns) with plain `<li>` items.

### Town cards (nearby towns / service area)
```html
<div class="town-grid town-grid--4">        <!-- town-grid = 5 columns; --4 for "other towns" -->
  <a class="town-card" href="hewlett-garage-door.html">
    <span class="town-card__name">Hewlett</span><span class="town-card__zip">NY 11557</span>
    <span class="town-card__text">One factual line.</span>
    <span class="town-card__link">Hewlett garage door repair{{icon:arrow}}</span>
  </a>
</div>
```

### Link chips (related links row)
`<div class="link-row"><a class="link-chip" href="repair.html">{{icon:wrench}}Garage door repair</a>…</div>`

### FAQ accordion (MUST use exactly this markup — schema is generated from it)
```html
<div class="faq-list">
  <details class="faq-item">
    <summary>Question text?</summary>
    <div class="faq-answer"><p>Answer text.</p></div>
  </details>
</div>
```
No attributes on `<summary>`; no nested `<div>` inside `.faq-answer` (paragraphs/lists/links are fine).

### Emergency band
`<section class="section emergency">` — red band; see index.html.

### Final CTA (last section of every page)
```html
<section class="cta-band" aria-labelledby="cta-title">
  <div class="wrap">
    <div><h2 id="cta-title">...</h2><p>...</p></div>
    <div class="cta-band__actions">
      <a class="btn btn--light btn--lg js-call" href="tel:..." data-cta="PAGE-final-call">{{icon:phone}}Call (516) ...</a>
      <p class="cta-band__alt">Main line: <a class="js-call" href="tel:+15164900931" data-cta="PAGE-final-call-main">(516) 490-0931</a></p>
    </div>
  </div>
</section>
```

Utilities: `mt-sm mt-md mt-lg mb-md text-center muted small`.

## 5. Rules
* Exactly one `<h1>`; h2 for sections, h3 inside sections. Don't skip levels.
* Every `<section>` gets `aria-labelledby` pointing at its heading id (ids unique per page).
* No inline styles, no `<script>`, no emoji (use icons), no external images.
* Descriptive anchor text ("Cedarhurst garage door repair", not "click here").
* Escape `&` as `&amp;` in text.
