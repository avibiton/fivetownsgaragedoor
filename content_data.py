"""Hero photography and Google review data used by build.py."""
import html

# --------------------------------------------------------------------------
# Hero photography (Unsplash License; see docs/PHOTO-CREDITS.md). Stock photos,
# NOT Five Towns jobs: alt text describes the scene only. To use real job
# photos, replace the files in src/static/assets/images/hero/ (same names) or
# add a new key here.
# --------------------------------------------------------------------------
HERO_IMAGES = {
    "home-glass-doors": "Two-car garage with modern glass-panel sectional doors on a white home",
    "sectional-door-closeup": "Close-up of a white raised-panel sectional garage door with window lites",
    "wood-modern-door": "Contemporary wood-look garage door with horizontal window lites",
    "open-garage-cars": "Open garage bays on a stone-front home with cars parked inside",
    "modern-two-door": "Modern white home with two dark sectional garage doors",
    "twin-homes-black-doors": "Contemporary white homes with black sectional garage doors",
    "colonial-detached-garage": "Two-story colonial home with a detached two-car garage",
    "rollup-commercial": "Two closed commercial roll-up steel doors",
    "ranch-two-door": "Single-story home with two sectional garage doors and a paved driveway",
    "brick-colonial": "Brick colonial home with an attached garage",
    "split-level": "Split-level home with a raised-panel sectional garage door",
    "estate-three-car": "Large wooded home with a three-car garage",
    "two-story-garage": "Two-story home with an attached dark sectional garage door",
    "blue-colonial": "Colonial-style home with an attached garage",
}
HERO_BY_PAGE = {
    "index.html": "home-glass-doors",
    "repair.html": "sectional-door-closeup",
    "installation.html": "wood-modern-door",
    "openers.html": "open-garage-cars",
    "liftmasteropeners.html": "modern-two-door",
    "Genieopeners.html": "twin-homes-black-doors",
    "residential.html": "colonial-detached-garage",
    "commercial.html": "rollup-commercial",
    "LocationServices.html": "ranch-two-door",
    "cedarhurst-garage-door.html": "brick-colonial",
    "hewlett-garage-door.html": "split-level",
    "lawrence-garage-door.html": "estate-three-car",
    "woodmere-garage-door.html": "two-story-garage",
    "inwood-garage-door.html": "blue-colonial",
    "faq.html": "colonial-detached-garage",
    "contact.html": "sectional-door-closeup",
    "404.html": "two-story-garage",
}
HERO_WIDTHS = (768, 1280, 1920)


def hero_srcset(key, fmt):
    return ", ".join(f"assets/images/hero/{key}-{w}.{fmt} {w}w" for w in HERO_WIDTHS)


def hero_picture(key):
    return (
        '<picture class="hero-media">'
        f'<source type="image/avif" srcset="{hero_srcset(key, "avif")}" sizes="100vw">'
        f'<source type="image/webp" srcset="{hero_srcset(key, "webp")}" sizes="100vw">'
        f'<img src="assets/images/hero/{key}-1280.webp" alt="{HERO_IMAGES[key]}" width="1280" height="800" '
        'fetchpriority="high" decoding="async">'
        "</picture>"
    )


# --------------------------------------------------------------------------
# Google reviews, quoted verbatim from the Google Business Profile
# "Five Towns Garage Doors" (578 Central Ave, Cedarhurst). Snapshot taken
# 2026-09-22: 4.7 stars from 15 reviews (14 five-star, 1 one-star).
# All 14 five-star reviews are included; names shortened to first name + initial.
# No Review/AggregateRating schema is emitted: Google does not show
# self-serving review markup for a business on its own website.
# --------------------------------------------------------------------------
GOOGLE_RATING = "4.7"
GOOGLE_COUNT = 15
GOOGLE_AS_OF = "September 2026"
GOOGLE_URL = "https://maps.google.com/?cid=13986575148892573272"
REVIEWS = [
    ("Andy G.", "Both of my cars were stuck in the garage and I called at 8 AM expecting someone to not be able to get there until late or the next day. A service technician showed up within an hour after I had called. He was very professional and explained everything in depth. Without the typical pushy attitude, he fixed my garage door at an affordable price. I would definitely recommend Five Towns Garage Doors in Nassau County. Thank you."),
    ("Audrey Z.", "The spring of my garage broke late at night. I called first thing the next morning and someone came within a couple hours and quickly fixed it. They were great! I would highly recommend this Nassau County garage doors repair company to anyone."),
    ("Alex O.", "It was a great experience from start to finish. Sales rep helped us choose the door, and it turned out great. The young man who installed it did a great job. He was very pleasant and professional. Five Towns Garage Doors has my highest recommendations."),
    ("Oscar R.", "The garage door repair technician was friendly and helpful and he was there to fix my door not to just sell me a bunch of parts. He is the reason I would have this company back to my house. The scheduling was easy and the people were pleasant on the phone."),
    ("Sherie F.", "Having an issue with our external keypad/remote caused us to contact Five Towns Garage Doors. The company helped us contact the manufacturer for technical assistance instead of just charging us for a service call, saving us time and money. If we ever need garage door repair again, we will definitely use them."),
    ("Martha M.", "Just purchased a new garage door & opener for our home from one of their many styles of garage door for sale. From the first phone call to the installation everything has been smooth and easy I love the way it turned out! The new door updated our garage and now we can open and close the door with our phone, which is helpful! The best place on Long Island for garage doors near me."),
    ("Trudy H.", "My opener's lift chain completely derailed from the gear assembly, leaving our SUV totally trapped inside the bay. The tech arrived with all the correct replacement garage door parts right inside his work vehicle to fix the mechanism. He re-aligned the motor assembly and completed the entire garage door repair so we could finally get out of the house."),
    ("Reva M.", "The technician did a great job to fix my garage door ! I appreciate his recommendation to replace the one coil and to replace the cable too. he was effcient and fast, and polite. I was hesitant at first because of the additional cost, but he spoke to me safert issues are first! Thank you for a job well done !"),
    ("Shlomi K.", "I live in Oceanside, and I was in the market for a new garage door. I shopped around and came across Five Towns Garage Doors. Not only did they give me a good deal, but they were prompt, professional and extremely helpful. They showed up when they said they would and did a great job. If anyone is looking for a garage door, do not hesitate, call Five Towns Garage Doors!"),
    ("Ciara L.", "The repair guy came on time and he removed my old damaged garage door and replaced it with the new door quickly. He showed me what was different from the new garage doors for sale and the old door and explained why the parts were better than my old one. Highly recommended."),
    ("Arthur A.", "The old rollers on my tracking rails were making an absolute racket every single time I backed my sedan out. This local garage door company checked the balance and found out the tracking setup was completely warped. They replaced the warped steel rails and applied proper lube to the bearings during the garage door maintenance visit. Everything rolls open quietly now without that awful metal-on-metal scraping noise."),
    ("Isaac H.", "I called several garage door companies for an emergency repair they all promised same day service but no one showed up. I finally called Five Town Garage doors and they showed up in 1 and a half hours did the repair cleaned up and left. FANTASTIC AND SINCERE POLITE PROFDESSINALS. Rebbeca at the call center called me several times to make sure they were on time and clean."),
    ("Joseph N.", "I needed to find a reliable garage door supplier to look at our dented storefront entry gate. They helped me pick out heavy-duty commercial garage doors that handle constant daily use without jamming up. It was a completely straightforward experience getting this sorted out in Cedarhurst, NY."),
    ("Ilan E. M.", "Great company. Called back immediately and showed up on time. What more can you ask for!!!"),
]
# Reviews featured per page (indexes into REVIEWS). Unlisted pages get a rotating set of 3.
REVIEWS_BY_PAGE = {
    "index.html": list(range(len(REVIEWS))),
    "repair.html": [1, 6, 10],
    "installation.html": [2, 5, 9],
    "openers.html": [6, 4, 5],
    "liftmasteropeners.html": [6, 5, 4],
    "Genieopeners.html": [4, 6, 3],
    "commercial.html": [12, 11, 3],
    "residential.html": [10, 7, 3],
    "cedarhurst-garage-door.html": [12, 0, 1],
    "contact.html": [0, 11, 13],
    "faq.html": [3, 7, 4],
}
STARS = '<span class="stars" aria-hidden="true">★★★★★</span>'


def rating_badge(cta):
    return (
        f'<a class="rating-badge" href="{GOOGLE_URL}" target="_blank" rel="noopener" data-cta="{cta}">'
        f'<span class="rating-badge__g" aria-hidden="true">G</span>{STARS}'
        f"<span><strong>{GOOGLE_RATING}</strong> on Google · {GOOGLE_COUNT} reviews</span></a>"
    )


def render_reviews(page_file, idx):
    picks = REVIEWS_BY_PAGE.get(page_file)
    if picks is None:
        picks = [(idx * 3 + k) % len(REVIEWS) for k in range(3)]
    full = page_file == "index.html"
    cards = "".join(
        '<figure class="review-card"><div class="review-card__top">'
        f'{STARS}<span class="sr-only">5 out of 5 stars.</span><span class="review-card__src">Google review</span></div>'
        f"<blockquote><p>{html.escape(REVIEWS[i][1])}</p></blockquote>"
        f"<figcaption>{html.escape(REVIEWS[i][0])}</figcaption></figure>"
        for i in picks
    )
    grid_cls = "review-grid review-grid--all" if full else "review-grid"
    bg = "cream" if full else "off"
    return (
        f'<section class="section section--{bg} reviews" aria-labelledby="reviews-title">\n'
        '  <div class="wrap">\n'
        '    <div class="reviews__head">\n'
        "      <div>\n"
        '        <p class="eyebrow">Google Reviews</p>\n'
        '        <h2 class="h-section" id="reviews-title">What Customers Say</h2>\n'
        f'        <p class="lede">{GOOGLE_RATING} out of 5 stars from {GOOGLE_COUNT} Google reviews (as of {GOOGLE_AS_OF}). Reviews are quoted as written.</p>\n'
        "      </div>\n"
        '      <div class="reviews__actions">\n'
        f'        {rating_badge("reviews-google-badge")}\n'
        f'        <a class="btn btn--outline" href="{GOOGLE_URL}" target="_blank" rel="noopener" data-cta="reviews-read-all">Read All Reviews on Google{{{{icon:arrow}}}}</a>\n'
        "      </div>\n"
        "    </div>\n"
        f'    <div class="{grid_cls}">{cards}</div>\n'
        "  </div>\n"
        "</section>\n"
    )
