#!/usr/bin/env python3
"""
H.R. Tent House & Caterers — static site generator.

Edit the CONFIG / content below, then run:   python build.py
Output goes to ./docs  (GitHub Pages serves from main branch /docs).
Needs Python 3.8+ and Pillow (pip install pillow) for image sizes.
"""
import html, json, os, shutil, datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Install Pillow first:  pip install pillow")

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

# ======================================================================
# CONFIG — change these when things change
# ======================================================================
# When you buy a domain, change SITE_URL to e.g. "https://hrtenthouse.in"
# and set CNAME_DOMAIN = "hrtenthouse.in"
SITE_URL = "https://mdzeeansari.github.io/hrtenthouse-website"
CNAME_DOMAIN = ""
# Free key from https://web3forms.com (sign up with the shop email).
# Until it is set, the enquiry form sends the enquiry on WhatsApp instead.
WEB3FORMS_KEY = "YOUR_WEB3FORMS_ACCESS_KEY"
# Google Search Console "HTML tag" verification code (only the content="..." part)
GOOGLE_SITE_VERIFICATION = "v8gOomj9TuxrqPu7_e7NrRgDYlEJWcbPzF5r-07Grlw"

BIZ = {
    "name": "H.R. Tent House & Caterers",
    "short": "H.R. Tent House",
    "street": "9th Cross Road, Bhuvaneshwari Nagar, Acharya College Main Road",
    "city": "Bengaluru",
    "region": "Karnataka",
    "pin": "560032",
    "phone_display": "+91 99020 20244",
    "phone_tel": "+919902020244",
    "whatsapp": "919902020244",
    "email": "hrtenthouse2021@gmail.com",
    "hours_long": "Open all 7 days · 8:00 AM – 9:00 PM",
    "hours_short": "Mon–Sun · 8 AM – 9 PM",
    "founded": 2021,
    "lat": 13.0349618,
    "lng": 77.6028398,
    "maps_url": "https://maps.google.com/?cid=11158288635927384955",
    # Replace with the "Ask for reviews" link from your Google Business Profile
    "review_url": "https://maps.google.com/?cid=11158288635927384955",
}
WA_TEXT = "Hi H.R. Tent House, I'd like a quote for my event."
WA_URL = f"https://wa.me/{BIZ['whatsapp']}?text=" + WA_TEXT.replace(" ", "%20").replace(",", "%2C").replace("'", "%27")

TODAY = datetime.date.today().isoformat()
E = html.escape

# ======================================================================
# IMAGES  (file stem -> alt text, gallery categories)
# ======================================================================
IMAGES = {
    "german-hangar-banquet-setup": ("German hangar tent on a lawn with long tables in white frills and banquet chairs with gold bows", "structures seating"),
    "german-hangar-corporate-dinner": ("Inside a German hangar set up for a corporate dinner, with long tables, chair covers and stage lighting", "structures corporate"),
    "german-pagoda-stalls": ("Row of white German pagoda tents with drapes, set up as stalls", "structures corporate"),
    "pagoda-walkway-red-carpet": ("Covered pagoda walkway with red carpet and blue drapes", "structures decor"),
    "chiavari-chairs-outdoor-ceremony": ("Gold Chiavari chairs arranged in rows for an outdoor garden ceremony", "seating"),
    "banquet-chairs-gold-bows-long-tables": ("Long tables with white frills and banquet chairs with gold bows in front of a pleated drape backdrop", "seating decor"),
    "round-tables-pink-banquet-hall": ("Round tables with pink cloths and chairs with pink bows in a banquet hall", "seating"),
    "long-tables-white-frills-seminar": ("Long tables with white frills and covered chairs in a classroom-style indoor layout", "seating corporate"),
    "round-tables-conference-setup": ("Round tables with white skirting and chairs with navy blue bands in a conference room", "seating corporate"),
    "plastic-chairs-outdoor-school-event": ("Rows of red and blue plastic chairs arranged for an outdoor school event", "seating corporate"),
    "banquet-chairs-gold-bows-lawn": ("Rows of banquet chairs with white covers and gold bows on a lawn", "seating"),
    "long-tables-frills-drape-backdrop": ("Long tables with white frills and covered chairs in a hall with pleated drapes", "seating decor"),
    "floral-canopy-decor": ("Floral canopy with sheer drapes over floor seating", "decor"),
    "black-chair-covers-gold-round-tables": ("Round tables with gold cloths and chairs with black covers on a garden lawn", "seating"),
    "graduation-stage-red-carpet": ("Graduation stage with red carpet steps and white stage skirting", "decor corporate"),
    "u-shape-tables-plastic-chairs": ("U-shaped layout of tables with white frills and blue plastic chairs under blue drapes", "seating corporate"),
    "floor-baithak-seating-bolsters": ("Floor baithak seating with white gaddis and round bolsters on a lawn", "decor seating"),
    "stage-decoration-lawn-function": ("Decorated temple-style stage set up on a lawn for a function", "decor"),
}
GALLERY_ORDER = list(IMAGES.keys())
CATS = [("all", "All"), ("structures", "Hangars & pagodas"), ("seating", "Chairs & tables"), ("decor", "Stage & decor"), ("corporate", "Corporate & schools")]
VIDEOS = [
    ("german-hangar-exterior", "German hangar tent standing on site"),
    ("german-hangar-lawn-setup", "German hangar on a lawn, mid-setup with round tables"),
    ("hangars-pagodas-canopies", "Hangars, pagodas and canopies across one venue"),
    ("banquet-hall-chair-covers", "Banquet hall with black chair covers and lilac bows"),
]

_size_cache = {}
def size(stem, thumb=False):
    f = SRC / "assets" / "img" / (stem + ("-thumb" if thumb else "") + ".webp")
    if f not in _size_cache:
        _size_cache[f] = Image.open(f).size
    return _size_cache[f]

def img(p, stem, sizes="100vw", cls="", eager=False, alt=None):
    w, h = size(stem); tw, _ = size(stem, True)
    a = E(alt if alt is not None else IMAGES[stem][0])
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{p}assets/img/{stem}.webp" srcset="{p}assets/img/{stem}-thumb.webp {tw}w, {p}assets/img/{stem}.webp {w}w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{a}" {load} decoding="async">')

# ======================================================================
# ICONS
# ======================================================================
I = {
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
 "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.1 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.9 11.9 0 0 0 4.6 4c1.7.7 2.3.8 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.4-.3z"/></svg>',
 "quote": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/></svg>',
 "gallery": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-4.5-4.5L6 21"/></svg>',
 "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
 "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
 "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
 "close": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
 "prev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>',
 "next": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
 "tent": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 20 12 4l9 16M12 4v16M8 20l4-7 4 7"/></svg>',
 "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/></svg>',
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
 "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/></svg>',
}

DIYA = ('<div class="diya" role="status" aria-live="polite"><svg viewBox="0 0 64 64" aria-hidden="true">'
        '<defs><radialGradient id="fl" cx="50%" cy="70%" r="60%"><stop offset="0" stop-color="#FFF4D2"/><stop offset=".45" stop-color="#FFC861"/><stop offset="1" stop-color="#E8862A" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="br" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#E2C892"/><stop offset="1" stop-color="#8C6B32"/></linearGradient></defs>'
        '<ellipse cx="32" cy="34" rx="16" ry="10" fill="rgba(255,200,97,.18)"/>'
        '<path class="flame" d="M32 14c4 6 6 9 6 13a6 6 0 0 1-12 0c0-4 2-7 6-13z" fill="url(#fl)"/>'
        '<path d="M10 40c4 8 12 12 22 12s18-4 22-12c-6 2-14 3-22 3s-16-1-22-3z" fill="url(#br)"/>'
        '<path d="M44 40c4-1 8-3 10-6" stroke="#C9A96E" stroke-width="2" fill="none" stroke-linecap="round"/></svg>'
        '<span class="diya__cap">Lighting the lamps…</span></div>')

# ======================================================================
# SITE STRUCTURE / CONTENT
# ======================================================================
SERVICES = [
 {
  "slug": "german-hangar-pagoda-shamiana", "tag": "Tents & structures",
  "name": "German Hangars, Pagodas, Shamianas & Canopies",
  "nav": "Tents & structures",
  "title": "German Hangar, Pagoda & Shamiana Tent Rental in Bengaluru",
  "desc": "Rent German hangar tents, German pagodas, shamianas and canopies in Bengaluru for weddings, receptions, corporate events and functions. Delivered and set up by H.R. Tent House.",
  "card": "Large German hangars, peaked German pagodas, traditional shamianas and quick canopies for any venue size.",
  "hero": "german-hangar-banquet-setup",
  "lead": "From one big German hangar that covers your whole guest list, to a row of pagodas for stalls and entrances, to a classic shamiana for a pooja at home — we bring the right structure and put it up for you.",
  "included": [
   ("German hangar", "Aluminium-frame hangar tent (often searched as “German hanger”) with a white roof and side walls and no poles in the middle, so the full floor is usable for seating, stage and dining."),
   ("German pagoda", "Square, peaked-roof tents for entrances, registration desks, food counters, stalls and covered walkways."),
   ("Shamiana", "Traditional fabric tent with drapes, ideal for poojas, house functions, community events and religious gatherings."),
   ("Canopies", "Quick-to-set canopies for shade, stalls, small gatherings and overflow areas."),
   ("Side drapes & walls", "Pleated drapes and side walls in white and colours to close off or dress up a structure."),
   ("Red carpet & walkways", "Carpeted, covered walkways that connect parking, entrance and the main tent."),
  ],
  "photos": ["german-hangar-banquet-setup", "german-hangar-corporate-dinner", "german-pagoda-stalls", "pagoda-walkway-red-carpet"],
  "videos": ["german-hangar-exterior", "hangars-pagodas-canopies"],
  "events": ["Weddings", "Receptions", "Nikah", "Corporate events", "Exhibitions", "School functions", "Poojas", "Birthday parties"],
  "faq": [
   ("What is the difference between a German hangar and a shamiana?", "A German hangar is a rigid aluminium-frame structure with a waterproof roof and walls, best for large guest counts and events that need a fully covered hall. A shamiana is a lighter fabric tent with drapes, best for smaller functions, poojas and house events."),
   ("Can a German hangar be set up on a lawn or open ground?", "Yes. Hangars, pagodas and shamianas are regularly set up on lawns, open grounds, school campuses and parking areas. Share your venue and guest count and we'll suggest the right size."),
   ("Can you combine structures at one venue?", "Yes. A common setup is a German hangar for the main hall, pagodas for the entrance and counters, and a covered walkway with red carpet between them."),
  ],
 },
 {
  "slug": "chairs-tables-rental", "tag": "Seating",
  "name": "Chairs & Tables with Covers, Bows and Frills",
  "nav": "Chairs & tables",
  "title": "Chair & Table Rental in Bengaluru — Banquet, Chiavari & Plastic Chairs",
  "desc": "Rent banquet chairs with covers and bows, Chiavari chairs, plastic chairs, long tables, round tables and small tables with frills in Bengaluru. H.R. Tent House delivers and arranges them.",
  "card": "Plastic, banquet and Chiavari chairs with covers and bows; long, round and small tables with frills.",
  "hero": "banquet-chairs-gold-bows-lawn",
  "lead": "Every chair comes with its own cover and bow, and every table comes dressed in cloth and frills, so your seating looks finished the moment it is laid out.",
  "included": [
   ("Banquet chairs", "Stretch-covered banquet chairs with bows in gold, pink, navy, black, lilac and more to match your theme."),
   ("Chiavari chairs", "Elegant Chiavari chairs for wedding ceremonies, receptions and head tables."),
   ("Plastic chairs", "Sturdy plastic chairs in bulk for school events, community programs and large gatherings."),
   ("Long tables (2' × 6')", "For dining, buffet counters, registration desks and classroom or seminar layouts."),
   ("Round tables", "For banquet-style seating at receptions, parties and corporate dinners."),
   ("Small tables (2' × 1.5')", "For side tables, gift tables, counters and compact setups."),
  ],
  "photos": ["banquet-chairs-gold-bows-long-tables", "chiavari-chairs-outdoor-ceremony", "round-tables-pink-banquet-hall", "black-chair-covers-gold-round-tables", "round-tables-conference-setup", "u-shape-tables-plastic-chairs", "plastic-chairs-outdoor-school-event", "long-tables-white-frills-seminar"],
  "videos": ["banquet-hall-chair-covers"],
  "events": ["Weddings", "Receptions", "Conferences", "Seminars", "Exams", "School events", "Birthday parties", "Dinners"],
  "faq": [
   ("Do chairs and tables come with covers and frills?", "Yes. Chairs come with their covers and bows, and tables come with cloth and frills (skirting) at no separate setup hassle for you."),
   ("Can I choose the bow colour?", "Yes. Tell us your theme colour when you ask for a quote and we'll confirm what's available for your date."),
   ("Which layouts can you arrange?", "Theatre rows, banquet rounds, long dining tables, classroom/seminar style and U-shape layouts, indoors or under a tent."),
  ],
 },
 {
  "slug": "stage-decoration-lighting", "tag": "Stage & decor",
  "name": "Stage, Decoration & Lighting",
  "nav": "Stage, decor & lighting",
  "title": "Stage Decoration & Event Lighting in Bengaluru",
  "desc": "Stage setup with skirting and red carpet, drape backdrops, floral decoration and event lighting in Bengaluru for weddings, functions and school and corporate events.",
  "card": "Stages with skirting and red carpet, drape backdrops, floral decor and lighting that makes the evening glow.",
  "hero": "stage-decoration-lawn-function",
  "lead": "The stage is where every photo is taken. We build it, dress it with drapes, flowers and carpet, and light it so it looks as good at night as it does by day.",
  "included": [
   ("Stage platforms", "Raised stages with white skirting and steps, sized for speeches, ceremonies and performances."),
   ("Backdrops & drapes", "Pleated white and coloured drape backdrops for stages, halls and photo areas."),
   ("Floral decoration", "Floral canopies, entrance decor and stage florals for weddings and functions."),
   ("Red carpet", "Red carpet for stages, aisles, entrances and walkways."),
   ("Decorative lighting", "Warm string lights, fairy lights and decorative lighting for tents and lawns."),
   ("Stage lighting", "Lighting for stages and halls so speeches and performances look their best."),
  ],
  "photos": ["stage-decoration-lawn-function", "graduation-stage-red-carpet", "floral-canopy-decor", "long-tables-frills-drape-backdrop"],
  "videos": [],
  "events": ["Weddings", "Mehendi", "Sangeet", "Graduations", "Annual days", "Poojas", "Corporate events"],
  "faq": [
   ("Can you set up a stage at a school or office campus?", "Yes. We regularly set up stages with skirting, steps and red carpet for graduations, annual days and corporate programs."),
   ("Do you provide lighting for outdoor evening events?", "Yes. We light tents, lawns and stages for evening functions. Tell us the venue and timing when you ask for a quote."),
  ],
 },
 {
  "slug": "sound-system-rental", "tag": "Sound",
  "name": "Sound System Rental",
  "nav": "Sound",
  "title": "Sound System Rental in Bengaluru for Events & Functions",
  "desc": "Rent speakers and microphones in Bengaluru for weddings, poojas, school functions and corporate events. Delivered and set up along with your tent and seating by H.R. Tent House.",
  "card": "Speakers and microphones for speeches, announcements and music, set up with your tent.",
  "hero": "german-hangar-corporate-dinner",
  "lead": "Speeches, announcements, prayers and music need to reach every guest. We set up sound along with your tent and seating, so one call covers it all.",
  "included": [
   ("Speakers", "Speakers sized for your venue, from a house function to a large hangar or open ground."),
   ("Microphones", "Microphones for speeches, hosts, prayers and announcements."),
   ("Music playback", "Play your own music for receptions, parties and celebrations."),
   ("Set up with your tent", "Sound is installed together with your structure, seating and lighting, so everything is ready on time."),
  ],
  "photos": ["german-hangar-corporate-dinner", "plastic-chairs-outdoor-school-event", "graduation-stage-red-carpet"],
  "videos": [],
  "events": ["Weddings", "Poojas", "School functions", "Corporate events", "Community programs", "Birthday parties"],
  "faq": [
   ("Can I rent only sound without a tent?", "Yes. Call or WhatsApp us with your venue, date and the type of event and we'll suggest a setup."),
  ],
 },
 {
  "slug": "utensils-generator-cooler-rental", "tag": "Essentials",
  "name": "Utensils, Generators, AC/Coolers & Baithak Seating",
  "nav": "Utensils, power & cooling",
  "title": "Utensils, Generator, AC & Cooler Rental in Bengaluru",
  "desc": "Rent cooking and serving utensils, generators for power backup, ACs and air coolers, and floor baithak seating with gaddis and bolsters in Bengaluru from H.R. Tent House.",
  "card": "Utensils and vessels, generator backup, ACs and coolers, plus floor baithak seating with bolsters.",
  "hero": "floor-baithak-seating-bolsters",
  "lead": "The details that keep an event comfortable: power that doesn't cut out, cool air under the tent, vessels for cooking and serving, and traditional floor seating.",
  "included": [
   ("Utensils & vessels", "Cooking and serving utensils for functions where your own cooks or caterer take care of the food."),
   ("Generators", "Generator backup so lights, sound and cooling keep running through the event."),
   ("ACs & air coolers", "Tower ACs and air coolers to keep hangars, tents and halls comfortable."),
   ("Baithak seating", "Floor seating with white gaddis and round bolsters for poojas, mehendi, nikah and traditional functions."),
  ],
  "photos": ["floor-baithak-seating-bolsters", "german-hangar-banquet-setup", "german-hangar-corporate-dinner"],
  "videos": [],
  "events": ["Poojas", "Mehendi", "Nikah", "House functions", "Weddings", "Corporate events"],
  "faq": [
   ("Can you provide cooling under a German hangar?", "Yes. ACs and air coolers can be placed inside hangars and tents. The number depends on the size of the structure and your guest count."),
  ],
 },
]

AREAS = [
 {"slug": "tent-house-hebbal", "name": "Hebbal",
  "near": ["R.T. Nagar", "Kempapura", "Sahakar Nagar", "Ganganagar", "Manorayanapalya"],
  "intro": "Hebbal is right next door to our base in Bhuvaneshwari Nagar, so it is one of the areas we serve most often. Whether it's a function on your terrace, a wedding at a community hall or an event on an open ground, we can bring the tent, seating and decor and set it all up.",
  "photo": "banquet-chairs-gold-bows-long-tables"},
 {"slug": "tent-house-yelahanka", "name": "Yelahanka",
  "near": ["Yelahanka New Town", "Jakkur", "Kogilu", "Attur", "Puttenahalli"],
  "intro": "Yelahanka has plenty of large lawns, farmhouses and layouts with open space — perfect for German hangars and pagodas. We set up full event venues here, from the main tent to seating, stage, lighting and sound.",
  "photo": "german-hangar-banquet-setup"},
 {"slug": "tent-house-peenya", "name": "Peenya",
  "near": ["Jalahalli", "Dasarahalli", "T. Dasarahalli", "Chikkabanavara", "Bagalagunte"],
  "intro": "From factory and office events in the Peenya industrial area to family functions in Jalahalli and Dasarahalli, we provide tents, chairs, tables, stage and sound for events of every size.",
  "photo": "long-tables-white-frills-seminar"},
 {"slug": "tent-house-nelamangala", "name": "Nelamangala",
  "near": ["Madanayakanahalli", "Makali", "Dabaspet", "Tumakuru Road", "Adakamaranahalli"],
  "intro": "Nelamangala and the Tumakuru Road belt have open grounds and farm venues that suit big setups. We bring German hangars, shamianas, seating and cooling out to the outskirts so you get the same city-quality setup.",
  "photo": "banquet-chairs-gold-bows-lawn"},
]
AREA_CHIPS = ["Hebbal", "R.T. Nagar", "Yelahanka", "Jalahalli", "Peenya", "Dasarahalli", "Vidyaranyapura", "Mathikere",
              "Rajajinagar", "Malleshwaram", "Soladevanahalli", "Chikkabanavara", "Hesaraghatta", "Nelamangala",
              "Doddaballapur", "Devanahalli", "Hoskote"]
EVENTS = ["Weddings", "Nikah", "Mehendi", "Sangeet", "Receptions", "Birthdays", "Pooja", "Corporate events", "Graduations", "Exhibitions"]

GENERAL_FAQ = [
 ("What does H.R. Tent House & Caterers provide?", "We rent and set up German hangars, German pagodas, shamianas and canopies; banquet, Chiavari and plastic chairs with covers and bows; long, round and small tables with frills; stage, decoration and lighting; sound; utensils, generators, ACs and coolers; and floor baithak seating."),
 ("How much does tent rental cost in Bengaluru?", "It depends on the structure and its size, the number of chairs and tables, decor, lighting and sound, the venue location and how many days you need it. Send us your date, venue and guest count on WhatsApp and we'll send a clear quote."),
 ("Do you deliver and set up?", "Yes. We bring everything to your venue, set it up before the event and take it down afterwards."),
 ("Which areas do you serve?", "We serve Bengaluru and its outskirts, including Hebbal, R.T. Nagar, Yelahanka, Jalahalli, Peenya, Dasarahalli, Vidyaranyapura, Nelamangala, Doddaballapur, Devanahalli and Hoskote. Our base is in Bhuvaneshwari Nagar."),
 ("How early should I book?", "As early as you can, especially for weekends and the wedding season. Once your date is fixed, message us to block the structures and seating you need."),
 ("Can you set up indoors?", "Yes. Besides tents, we set up chairs, tables, stages and decor inside banquet halls, offices, conference rooms and school halls."),
 ("What is a German hangar (German hanger) tent?", "A German hangar is a large aluminium-frame tent with a white waterproof roof and side walls and no poles in the middle. It works like a temporary hall for weddings, receptions, corporate events and exhibitions."),
 ("What are your working hours?", "We are open all 7 days, 8:00 AM to 9:00 PM. Setups and take-downs for your event can happen outside these hours. Call or WhatsApp us anytime."),
 ("How do I get a quote?", "Fill in the quote form, WhatsApp us on +91 99020 20244, or call us. Share your event date, venue, type of event and number of guests."),
]

# ======================================================================
# SHARED PIECES
# ======================================================================
def nav_items(p):
    return [("Home", f"{p}"), ("Services", f"{p}services/"), ("Gallery", f"{p}gallery/"),
            ("About", f"{p}about/"), ("FAQ", f"{p}faq/"), ("Contact", f"{p}contact/")]

def local_business():
    return {
        "@context": "https://schema.org", "@type": "LocalBusiness", "@id": SITE_URL + "/#business",
        "name": BIZ["name"], "alternateName": ["HR Tent House", "H R Tent House", "HRTH"],
        "url": SITE_URL + "/", "logo": SITE_URL + "/assets/img/icon-512.png", "image": SITE_URL + "/assets/img/og-image.jpg",
        "description": "Tent house in Bengaluru renting German hangars, pagodas, shamianas, chairs, tables, stage, decoration, lighting and sound for weddings, functions and corporate events.",
        "telephone": BIZ["phone_tel"], "email": BIZ["email"], "priceRange": "₹₹", "foundingDate": str(BIZ["founded"]),
        "address": {"@type": "PostalAddress", "streetAddress": BIZ["street"], "addressLocality": BIZ["city"],
                    "addressRegion": BIZ["region"], "postalCode": BIZ["pin"], "addressCountry": "IN"},
        "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
        "hasMap": BIZ["maps_url"],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "08:00", "closes": "21:00"}],
        "areaServed": [{"@type": "City", "name": "Bengaluru"}] + [{"@type": "Place", "name": a} for a in AREA_CHIPS],
        "sameAs": [BIZ["maps_url"]],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f"{SITE_URL}/services/{s['slug']}/"}} for s in SERVICES],
    }

def breadcrumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}

def crumbs_html(p, items):
    lis = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li aria-current="page">{E(n)}</li>')
        else:
            href = p + u.lstrip("/")
            lis.append(f'<li><a href="{href or "./"}">{E(n)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'

def lights_svg():
    # three swags of wire with bulbs hanging along each curve
    swags = [(0, 10, 240, 92, 480, 16), (480, 16, 720, 92, 960, 16), (960, 16, 1200, 92, 1440, 10)]
    wire = "M0,10 Q240,92 480,16 Q720,92 960,16 Q1200,92 1440,10"
    bulbs, b = [], 0
    for (x0, y0, cx, cy, x1, y1) in swags:
        for k in range(1, 7):
            t = k / 7
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
            bulbs.append(f'<g class="bulb" style="--b:{b}" transform="translate({x:.1f},{y:.1f})">'
                         f'<line x1="0" y1="0" x2="0" y2="7" stroke="rgba(245,242,236,.45)" stroke-width="1.2"/>'
                         f'<circle class="glow" cx="0" cy="13" r="15"/><circle class="core" cx="0" cy="13" r="3.6"/></g>')
            b += 1
    return ('<div class="lights" aria-hidden="true"><svg viewBox="0 0 1440 120" preserveAspectRatio="xMidYMin slice">'
            '<defs><radialGradient id="bulbGlow"><stop offset="0" stop-color="#FFE3A6" stop-opacity=".95"/>'
            '<stop offset=".35" stop-color="#FFC66B" stop-opacity=".45"/><stop offset="1" stop-color="#FFB347" stop-opacity="0"/></radialGradient></defs>'
            f'<g class="sway"><path class="wire" d="{wire}"/>{"".join(bulbs)}</g></svg></div>')

TASSEL = ('<svg viewBox="0 0 44 90" aria-hidden="true"><path d="M22 0v26" stroke="#E2C892" stroke-width="2"/>'
          '<circle cx="22" cy="30" r="6" fill="#C9A96E"/><path d="M14 36h16l4 40H10z" fill="#C9A96E"/>'
          '<path d="M14 36h16l-2 6H16z" fill="#E2C892"/><path d="M13 50h18M12 62h20" stroke="#80602A" stroke-width="1" opacity=".5"/></svg>')

def head(p, page):
    title = page["title"]
    full_title = title if BIZ["short"] in title else f"{title} | {BIZ['name']}"
    canon = SITE_URL + page["path"]
    og_img = SITE_URL + "/assets/img/og-image.jpg"
    preload = ""
    if page.get("hero_img") and page["path"] != "/":
        preload = f'<link rel="preload" as="image" href="{p}assets/img/{page["hero_img"]}-thumb.webp" fetchpriority="high">'
    elif page.get("hero_img"):
        stem = page["hero_img"]; w, _ = size(stem); tw, _ = size(stem, True)
        preload = (f'<link rel="preload" as="image" href="{p}assets/img/{stem}.webp" '
                   f'imagesrcset="{p}assets/img/{stem}-thumb.webp {tw}w, {p}assets/img/{stem}.webp {w}w" imagesizes="100vw" fetchpriority="high">')
    schemas = [local_business()] + page.get("schema", [])
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    intro_flag = "1" if page.get("intro") else "0"
    robots = '<meta name="robots" content="noindex">' if page.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large">'
    gsv = f'<meta name="google-site-verification" content="{E(GOOGLE_SITE_VERIFICATION)}">\n' if GOOGLE_SITE_VERIFICATION else ""
    return f"""<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full_title)}</title>
<meta name="description" content="{E(page['desc'])}">
{robots}
<link rel="canonical" href="{canon}">
{gsv}<meta name="theme-color" content="#141416">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{E(BIZ['name'])}">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(page['desc'])}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(full_title)}">
<meta name="twitter:description" content="{E(page['desc'])}">
<meta name="twitter:image" content="{og_img}">
<meta name="geo.region" content="IN-KA"><meta name="geo.placename" content="Bengaluru">
<meta name="geo.position" content="{BIZ['lat']};{BIZ['lng']}"><meta name="ICBM" content="{BIZ['lat']}, {BIZ['lng']}">
<link rel="icon" href="{p}assets/img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{p}assets/img/favicon-64.png">
<link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{p}site.webmanifest">
<link rel="preload" href="{p}assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="{p}assets/css/style.css">
<script>(function(d){{var h=d.documentElement;h.classList.add("js");try{{var rm=matchMedia("(prefers-reduced-motion: reduce)").matches,s=sessionStorage,l=s.getItem("hrth-drape");s.removeItem("hrth-drape");if(l&&!rm){{h.classList.add("drape-in");window.__drapeLabel=l}}if({intro_flag}&&!rm&&!l&&!s.getItem("hrth-intro"))h.classList.add("intro");s.setItem("hrth-intro","1")}}catch(e){{}}}})(document);
window.HRTH={{whatsapp:"{BIZ['whatsapp']}",web3formsKey:"{WEB3FORMS_KEY}"}};</script>
{ld}
</head>"""

def header(p, active):
    nav = "".join(f'<li><a href="{u or "./"}"{" aria-current=page" if n == active else ""}>{n}</a></li>' for n, u in nav_items(p) if n != "Home")
    mob = "".join(f'<li><a href="{u or "./"}"{" aria-current=page" if n == active else ""}>{n}</a></li>' for n, u in nav_items(p))
    home = p or "./"
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container">
    <a class="brand" href="{home}" data-label="Home">
      <img src="{p}assets/img/logo-light-160.webp" width="52" height="52" alt="">
      <span class="brand__name">H.R. Tent House<small>&amp; Caterers · Est. {BIZ['founded']}</small></span>
    </a>
    <nav class="nav" aria-label="Main"><ul>{nav}</ul></nav>
    <a class="btn btn--primary header-cta" href="{p}contact/#quote" data-label="Get a quote">Get a free quote</a>
    <button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span></button>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <nav aria-label="Mobile"><ul>{mob}</ul></nav>
  <div class="btn-row"><a class="btn btn--primary" href="{p}contact/#quote">Get a free quote</a><a class="btn btn--wa" href="{WA_URL}" target="_blank" rel="noopener">{I['wa']} WhatsApp</a></div>
  <p class="meta"><a href="tel:{BIZ['phone_tel']}">{BIZ['phone_display']}</a><br>{BIZ['hours_long']}</p>
</div>"""

def footer(p):
    svc = "".join(f'<li><a href="{p}services/{s["slug"]}/">{E(s["nav"])}</a></li>' for s in SERVICES)
    areas = "".join(f'<li><a href="{p}areas/{a["slug"]}/">Tent house in {E(a["name"])}</a></li>' for a in AREAS)
    return f"""<footer class="site-footer dark">
  <canvas class="bokeh" aria-hidden="true"></canvas>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="{p}assets/img/logo-light-320.webp" width="120" height="120" alt="H.R. Tent House &amp; Caterers logo" loading="lazy">
        <address><strong style="color:var(--on-dark)">{E(BIZ['name'])}</strong><br>{E(BIZ['street'])},<br>{BIZ['city']}, {BIZ['region']} {BIZ['pin']}<br>
        <a href="tel:{BIZ['phone_tel']}">{BIZ['phone_display']}</a> · <a href="mailto:{BIZ['email']}">{BIZ['email']}</a></address>
        <span class="hours-pill">{BIZ['hours_long']}</span>
      </div>
      <div><h3>Services</h3><ul>{svc}<li><a href="{p}services/">All services</a></li></ul></div>
      <div><h3>Areas</h3><ul>{areas}<li><a href="{p}#areas">All areas we serve</a></li></ul></div>
      <div><h3>Explore</h3><ul>
        <li><a href="{p}gallery/">Gallery</a></li><li><a href="{p}about/">About us</a></li><li><a href="{p}faq/">FAQ</a></li><li><a href="{p}contact/">Contact</a></li>
        <li><a href="{BIZ['maps_url']}" target="_blank" rel="noopener">Find us on Google Maps</a></li>
        <li><a href="{BIZ['review_url']}" target="_blank" rel="noopener">Rate us on Google</a></li></ul></div>
    </div>
    <p class="footer-big" aria-hidden="true">H.R. Tent House</p>
    <div class="footer-bottom"><span>© <span data-year>{datetime.date.today().year}</span> {E(BIZ['name'])}. Tent house in Bengaluru since {BIZ['founded']}.</span>
      <a href="{p}sitemap.xml">Sitemap</a></div>
  </div>
</footer>"""

def dock(p, active):
    items = [("call", f"tel:{BIZ['phone_tel']}", I["phone"], "Call", ""),
             ("wa", WA_URL, I["wa"], "WhatsApp", ' target="_blank" rel="noopener"'),
             ("quote", f"{p}contact/#quote", I["quote"], "Quote", ' data-label="Get a quote"'),
             ("gallery", f"{p}gallery/", I["gallery"], "Gallery", ' data-label="Our gallery"')]
    a = "".join(f'<a href="{h}"{x}{" class=is-active" if k == active else ""}>{ic}<span>{t}</span></a>' for k, h, ic, t, x in items)
    return f'<nav class="dock" aria-label="Quick contact"><span class="dock__pill" aria-hidden="true"></span>{a}</nav>'

def curtain():
    return ('<div class="curtain" aria-hidden="true"><div class="drape drape--l"></div><div class="drape drape--r"></div>'
            f'<div class="curtain__tag">{TASSEL}<span>Home</span></div></div>'
            '<script>if(window.__drapeLabel){var t=document.querySelector(".curtain__tag span");if(t)t.textContent=window.__drapeLabel}</script>')

def intro_overlay(p):
    bulbs = "".join(f'<i style="left:{6 + k * 8}%;top:{int(18 * abs(((k % 6) - 2.5) / 2.5))}px;animation-delay:{.2 + k * .06:.2f}s"></i>' for k in range(12))
    return (f'<div class="intro-overlay" aria-hidden="true"><div class="intro-overlay__bg"></div>'
            f'<div class="drape drape--l"></div><div class="drape drape--r"></div>'
            f'<div class="intro-overlay__lights">{bulbs}</div>'
            f'<img class="intro-overlay__logo" src="{p}assets/img/logo-light-320.webp" width="220" height="220" alt=""></div>')

def scripts(p, gallery=False):
    s = [f'<script src="{p}assets/vendor/gsap.min.js" defer></script>',
         f'<script src="{p}assets/vendor/ScrollTrigger.min.js" defer></script>',
         f'<script src="{p}assets/vendor/lenis.min.js" defer></script>']
    if gallery:
        s.append(f'<script src="{p}assets/vendor/Flip.min.js" defer></script>')
    s.append(f'<script src="{p}assets/js/main.js" defer></script>')
    return "\n".join(s)

def layout(page, main):
    p = page["prefix"]
    extra_top = intro_overlay(p) if page.get("intro") else ""
    return f"""{head(p, page)}
<body>
{curtain()}
{extra_top}
{header(p, page.get('active', ''))}
<main id="main">
{main}
</main>
{footer(p)}
{dock(p, page.get('dock', ''))}
{page.get('after', '')}
{scripts(p, page.get('gallery', False))}
</body>
</html>
"""

# ======================================================================
# REUSABLE SECTIONS
# ======================================================================
def page_hero(p, h1, lead, crumbs, stem=None, eyebrow=None, extra=""):
    if stem:
        tw, th = size(stem, True)
        media = (f'<div class="page-hero__media"><img src="{p}assets/img/{stem}-thumb.webp" width="{tw}" height="{th}" alt="" '
                 f'fetchpriority="high" loading="eager" decoding="async"></div>')
    else:
        media = ""
    eb = f'<span class="eyebrow">{E(eyebrow)}</span>' if eyebrow else ""
    return f"""<section class="page-hero dark">{media}
  <div class="container">{crumbs_html(p, crumbs)}{eb}
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>{extra}
  </div>
</section>"""

def service_cards(p):
    cards = []
    for s in SERVICES:
        cards.append(f"""<a class="card" href="{p}services/{s['slug']}/" data-label="{E(s['nav'])}">
  <div class="card__media">{img(p, s['hero'], sizes="(min-width:1000px) 33vw, (min-width:700px) 50vw, 100vw")}<span class="card__tag">{E(s['tag'])}</span></div>
  <div class="card__body"><h3>{E(s['name'])}</h3><p>{E(s['card'])}</p><span class="card__more">View details {I['arrow']}</span></div>
</a>""")
    return f'<div class="grid grid--services" data-reveal-stagger>{"".join(cards)}</div>'

def marquee():
    items = []
    for e in EVENTS:
        items.append(f"<li>{E(e)}</li><li class=dot>✦</li>")
    ul = "".join(items)
    return f'<div class="marquee"><p class="sr-only">Events we set up for: {E(", ".join(EVENTS))}</p><div class="marquee__track"><ul aria-hidden="true">{ul}</ul><ul aria-hidden="true">{ul}</ul></div></div>'

def cta_band(p, title="Planning an event? Let's set it up.", text="Share your date, venue and guest count. We'll suggest the right setup and send a clear quote."):
    return f"""<section class="section--tight"><div class="container">
<div class="cta-band dark" data-reveal><span class="eyebrow">Free quote · {BIZ['hours_short']}</span>
<h2>{E(title)}</h2><p class="lead">{E(text)}</p>
<div class="btn-row"><a class="btn btn--primary" href="{p}contact/#quote" data-label="Get a quote">Get a free quote {I['arrow']}</a>
<a class="btn btn--wa" href="{WA_URL}" target="_blank" rel="noopener">{I['wa']} WhatsApp us</a>
<a class="btn btn--ghost" href="tel:{BIZ['phone_tel']}">{I['phone']} {BIZ['phone_display']}</a></div></div>
</div></section>"""

def map_embed():
    src = f"https://www.google.com/maps?q={BIZ['lat']},{BIZ['lng']}&z=16&output=embed"
    return (f'<div class="map"><iframe src="{src}" title="Map showing {E(BIZ["name"])} in Bhuvaneshwari Nagar, Bengaluru" '
            f'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>'
            f'<p style="margin-top:12px"><a class="text-link" href="{BIZ["maps_url"]}" target="_blank" rel="noopener">Open in Google Maps</a></p>')

def area_section(p, title="Bengaluru and its outskirts"):
    linked = {a["name"]: f'{p}areas/{a["slug"]}/' for a in AREAS}
    chips = ['<li><span class="chip is-home">Bhuvaneshwari Nagar · our base</span></li>']
    for c in AREA_CHIPS:
        if c in linked:
            chips.append(f'<li><a class="chip" href="{linked[c]}" data-label="Tent house in {E(c)}">{E(c)}</a></li>')
        else:
            chips.append(f'<li><span class="chip">{E(c)}</span></li>')
    return f"""<section class="section" id="areas"><div class="container"><div class="areas">
<div data-reveal><span class="eyebrow">Where we work</span><h2>{E(title)}</h2>
<p class="lead">We're based in Bhuvaneshwari Nagar and set up events across Bengaluru and the outskirts. Don't see your area? Ask us — we probably go there.</p>
<ul class="chips">{"".join(chips)}</ul></div>
<div data-reveal>{map_embed()}</div>
</div></div></section>"""

def enquiry_form(p, heading="Get a free quote", h_tag="h2"):
    opts = "".join(f"<option>{E(e)}</option>" for e in ["Wedding", "Nikah", "Mehendi / Sangeet", "Reception", "Birthday", "Pooja / House function", "Corporate event", "School / College event", "Exhibition", "Other"])
    return f"""<section class="section section--sand" id="quote"><div class="container"><div class="enquiry">
<div data-reveal><span class="eyebrow">Enquiry</span><{h_tag}>{E(heading)}</{h_tag}>
<p class="lead">Tell us a little about your event. We usually reply the same day. For the fastest answer, WhatsApp or call us.</p>
<ul class="contact-list">
<li><a href="tel:{BIZ['phone_tel']}">{I['phone']}<div><strong>Call</strong><span>{BIZ['phone_display']}</span></div></a></li>
<li><a href="{WA_URL}" target="_blank" rel="noopener">{I['wa']}<div><strong>WhatsApp</strong><span>{BIZ['phone_display']}</span></div></a></li>
<li><a href="mailto:{BIZ['email']}">{I['mail']}<div><strong>Email</strong><span>{BIZ['email']}</span></div></a></li>
<li><div>{I['clock']}<div><strong>Hours</strong><span>{BIZ['hours_long']}</span></div></div></li>
</ul></div>
<form class="form enquiry-form" action="https://api.web3forms.com/submit" method="POST" data-reveal>
<input type="hidden" name="access_key" value="{WEB3FORMS_KEY}" disabled>
<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<div class="form__grid">
<div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" required autocomplete="name"></div>
<div class="field"><label for="f-phone">Phone / WhatsApp</label><input id="f-phone" name="phone" type="tel" required inputmode="tel" autocomplete="tel" pattern="[0-9+ ()-]{{10,15}}"></div>
<div class="field"><label for="f-date">Event date</label><input id="f-date" name="event_date" type="date"></div>
<div class="field"><label for="f-type">Event type</label><select id="f-type" name="event_type"><option value="">Choose…</option>{opts}</select></div>
<div class="field"><label for="f-guests">Guests <span>(approx.)</span></label><input id="f-guests" name="guests" type="number" min="1" inputmode="numeric"></div>
<div class="field"><label for="f-venue">Venue / area</label><input id="f-venue" name="venue" placeholder="e.g. Hebbal, community hall"></div>
<div class="field full"><label for="f-msg">What do you need? <span>(optional)</span></label><textarea id="f-msg" name="message" placeholder="e.g. German hangar for 300 guests, round tables, stage and sound"></textarea></div>
</div>
<div class="form__foot"><button class="btn btn--primary" type="submit">Send enquiry {I['arrow']}</button>
<p class="form__note">Or <a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp us directly</a>.</p></div>
{DIYA}
<div class="form__status" role="status" aria-live="polite"></div>
</form>
</div></div></section>"""

def faq_html(items, reveal=True):
    det = "".join(f'<details><summary>{E(q)}</summary><div class="answer"><p>{E(a)}</p></div></details>' for q, a in items)
    return f'<div class="faq"{" data-reveal" if reveal else ""}>{det}</div>'

def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def video_block(p, stems):
    vids = {k: v for k, v in VIDEOS}
    out = []
    for s in stems:
        out.append(f'<figure><video controls muted playsinline preload="none" poster="{p}assets/video/{s}-poster.jpg" aria-label="{E(vids[s])}">'
                   f'<source src="{p}assets/video/{s}.mp4" type="video/mp4"></video><figcaption>{E(vids[s])}</figcaption></figure>')
    return f'<div class="videos" data-reveal-stagger>{"".join(out)}</div>'

# ======================================================================
# PAGES
# ======================================================================
pages = []  # (output path, html, sitemap priority)

def add(path, page, main, prio="0.7"):
    page["path"] = path
    pages.append((path, layout(page, main), prio, page.get("noindex", False)))

# ---------- HOME ----------
def home():
    p = ""
    h1_words = ["Tent", "house", "in", "<em>Bengaluru</em>"]
    h1 = " ".join(f'<span class="rise"><span style="--i:{i}">{w}</span></span>' for i, w in enumerate(h1_words))
    steps = [
     ("Visit & plan", "Call or WhatsApp us with your date, venue and guest count. We suggest the right structure, seating and layout, and send you a clear quote.", "german-pagoda-stalls"),
     ("We build it", "Our team arrives ahead of your event to put up the tent, lay out chairs and tables with covers and frills, and set up the stage, lights, sound and cooling.", "banquet-chairs-gold-bows-lawn"),
     ("You celebrate", "You focus on your guests. After the event, we take everything down and clear the venue.", "round-tables-pink-banquet-hall"),
    ]
    steps_list = "".join(f"""<li class="step{' is-active' if i == 0 else ''}"><span class="step__num">Step {i+1:02d}</span><h3>{E(t)}</h3><p>{E(d)}</p>
<div class="step__img">{img(p, s, sizes="100vw")}</div></li>""" for i, (t, d, s) in enumerate(steps))
    steps_panel = "".join(img(p, s, sizes="50vw", cls="is-active" if i == 0 else "") for i, (_, _, s) in enumerate(steps))
    years = datetime.date.today().year - BIZ["founded"]
    main = f"""
<section class="hero dark">
  <div class="hero__media">{img(p, 'german-hangar-banquet-setup', eager=True)}</div>
  <div class="hero__glow" aria-hidden="true"></div>
  <canvas class="bokeh" aria-hidden="true"></canvas>
  {lights_svg()}
  <div class="container hero__inner">
    <span class="eyebrow fade-up" style="--i:0">{E(BIZ['name'])} · Since {BIZ['founded']}</span>
    <h1>{h1}</h1>
    <p class="hero__promise fade-up" style="--i:1">German hangars, pagodas, shamianas, chairs, tables, stage, lighting and sound — delivered and set up for weddings, functions and corporate events across Bengaluru.</p>
    <div class="btn-row fade-up" style="--i:2"><a class="btn btn--primary" href="contact/#quote" data-label="Get a quote">Get a free quote {I['arrow']}</a>
      <a class="btn btn--wa" href="{WA_URL}" target="_blank" rel="noopener">{I['wa']} WhatsApp us</a></div>
    <div class="hero__meta fade-up" style="--i:3"><span>Open daily 8 AM – 9 PM</span><span>Bengaluru &amp; outskirts</span><span>Call {BIZ['phone_display']}</span></div>
  </div>
  <div class="scroll-cue" aria-hidden="true"></div>
</section>
{marquee()}
<section class="section" id="services"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">What we rent</span><h2>Everything your event needs, under one roof</h2>
  <p class="lead">One call for the tent, the seating, the stage, the lights, the sound and the cooling. We bring it, set it up and take it down.</p></div>
  {service_cards(p)}
</div></section>
<section class="section section--sand"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">How it works</span><h2>How we set up your event, in 3 steps</h2></div>
  <div class="steps"><ol class="steps__list"><span class="steps__rail" aria-hidden="true"><span class="steps__fill"></span></span>{steps_list}</ol>
  <div class="steps__panel" aria-hidden="true">{steps_panel}</div></div>
</div></section>
<section class="section dark"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">At a glance</span><h2>Setting up Bengaluru's celebrations since {BIZ['founded']}</h2></div>
  <div class="stats" data-reveal-stagger>
    <div class="stat"><div class="stat__num" data-count="{BIZ['founded']}" data-from="2000">{BIZ['founded']}</div><div class="stat__label">Year we started</div></div>
    <div class="stat"><div class="stat__num" data-count="{years}">{years}<sup>+</sup></div><div class="stat__label">Years of setups</div></div>
    <div class="stat"><div class="stat__num" data-count="7">7</div><div class="stat__label">Days a week, 8 AM – 9 PM</div></div>
    <div class="stat"><div class="stat__num" data-count="4">4</div><div class="stat__label">Tent types: hangar, pagoda, shamiana, canopy</div></div>
  </div>
</div></section>
<section class="section"><div class="container">
  <a class="teaser" href="gallery/" data-label="Our gallery">
    {img(p, 'banquet-chairs-gold-bows-long-tables', sizes="(min-width:1280px) 1200px, 100vw")}
    <span class="teaser__glow"></span>
    <span class="teaser__body"><span><span class="eyebrow">Real setups, real events</span><h2>See our work</h2><p>Hangars, pagodas, seating, stages and decor from events we've set up.</p></span>
    <span class="teaser__go">{I['arrow']}</span></span>
  </a>
</div></section>
<!-- TESTIMONIALS: add 3+ real Google reviews here later (name + event type). -->
{area_section(p)}
{enquiry_form(p)}
"""
    page = {"prefix": p, "title": f"{BIZ['name']} | Tent House in Bengaluru – German Hangars, Shamianas, Chairs & Stage",
            "desc": "H.R. Tent House & Caterers is a tent house in Bengaluru renting German hangars, pagodas, shamianas, chairs, tables, stage, decoration, lighting and sound. Open daily 8 AM–9 PM. Call +91 99020 20244.",
            "hero_img": "german-hangar-banquet-setup", "intro": True, "active": "Home"}
    page["schema"] = [{"@context": "https://schema.org", "@type": "WebSite", "name": BIZ["name"], "alternateName": "HR Tent House", "url": SITE_URL + "/"}]
    add("/", page, main, "1.0")

# ---------- SERVICES HUB ----------
def services_hub():
    p = "../"
    crumbs = [("Home", "/"), ("Services", "/services/")]
    main = page_hero(p, "Tent, seating &amp; event rentals in Bengaluru",
                     "Everything we rent and set up, from the structure over your head to the chairs, stage, lights and sound.", crumbs, "german-hangar-corporate-dinner", "Our services")
    main += f'<section class="section"><div class="container">{service_cards(p)}</div></section>' + cta_band(p)
    page = {"prefix": p, "title": "Tent House Services in Bengaluru – Hangars, Chairs, Stage, Sound",
            "desc": "All rental services from H.R. Tent House in Bengaluru: German hangars, pagodas, shamianas, canopies, chairs and tables, stage and decoration, lighting, sound, utensils, generators and coolers.",
            "hero_img": "german-hangar-corporate-dinner", "active": "Services", "schema": [breadcrumbs(crumbs)]}
    add("/services/", page, main, "0.9")

# ---------- SERVICE PAGES ----------
def service_page(s):
    p = "../../"
    url = f"/services/{s['slug']}/"
    crumbs = [("Home", "/"), ("Services", "/services/"), (s["nav"], url)]
    inc = "".join(f'<li><strong>{E(t)}</strong><span>{E(d)}</span></li>' for t, d in s["included"])
    photos = "".join(f'<figure>{img(p, ph, sizes="(min-width:1000px) 33vw, 100vw")}</figure>' for ph in s["photos"])
    tags = "".join(f"<li>{E(e)}</li>" for e in s["events"])
    others = [o for o in SERVICES if o is not s]
    other_links = "".join(f'<li><a class="chip" href="{p}services/{o["slug"]}/" data-label="{E(o["nav"])}">{E(o["nav"])}</a></li>' for o in others)
    vids = f'<section class="section--tight"><div class="container"><div class="section-head" data-reveal><span class="eyebrow">On video</span><h2>Walk through a setup</h2></div>{video_block(p, s["videos"])}</div></section>' if s["videos"] else ""
    main = page_hero(p, E(s["name"]), E(s["lead"]), crumbs, s["hero"], s["tag"] + " · Bengaluru",
                     f'<div class="btn-row" style="margin-top:28px"><a class="btn btn--primary" href="{p}contact/#quote" data-label="Get a quote">Get a free quote {I["arrow"]}</a><a class="btn btn--wa" href="{WA_URL}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a></div>')
    main += f"""
<section class="section"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">What's included</span><h2>What you can rent</h2></div>
  <ul class="included" data-reveal-stagger>{inc}</ul>
</div></section>
<section class="section--tight"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">From our events</span><h2>Photos</h2></div>
  <div class="photo-row" data-reveal-stagger>{photos}</div>
  <p style="margin-top:24px"><a class="text-link" href="{p}gallery/" data-label="Our gallery">See the full gallery</a></p>
</div></section>
{vids}
<section class="section"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">Typical events</span><h2>Perfect for</h2><ul class="tags">{tags}</ul></div>
  <div class="section-head" style="margin-top:56px" data-reveal><span class="eyebrow">Questions</span><h2>Good to know</h2></div>
  {faq_html(s['faq'])}
</div></section>
{cta_band(p)}
<section class="section--tight"><div class="container" data-reveal><span class="eyebrow">More services</span><ul class="chips" style="margin-top:8px">{other_links}</ul></div></section>
"""
    svc_schema = {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "serviceType": s["tag"],
                  "description": s["desc"], "url": SITE_URL + url, "provider": {"@id": SITE_URL + "/#business"},
                  "areaServed": {"@type": "City", "name": "Bengaluru"}}
    page = {"prefix": p, "title": s["title"], "desc": s["desc"], "hero_img": s["hero"], "active": "Services",
            "schema": [breadcrumbs(crumbs), svc_schema]}
    add(url, page, main, "0.8")

# ---------- AREA PAGES ----------
def area_page(a):
    p = "../../"
    url = f"/areas/{a['slug']}/"
    crumbs = [("Home", "/"), ("Areas", "/#areas"), (f"Tent house in {a['name']}", url)]
    near = ", ".join(a["near"])
    svc_list = "".join(f'<li><strong><a href="{p}services/{s["slug"]}/" data-label="{E(s["nav"])}" style="text-decoration:none">{E(s["name"])}</a></strong><span>{E(s["card"])}</span></li>' for s in SERVICES)
    main = page_hero(p, f"Tent house in <em>{E(a['name'])}</em>",
                     f"Tents, chairs, tables, stage, lighting and sound for weddings, functions and corporate events in {E(a['name'])} and nearby areas — delivered and set up by {E(BIZ['name'])}.",
                     crumbs, a["photo"], "Areas we serve",
                     f'<div class="btn-row" style="margin-top:28px"><a class="btn btn--primary" href="{p}contact/#quote" data-label="Get a quote">Get a free quote {I["arrow"]}</a><a class="btn btn--ghost" href="tel:{BIZ["phone_tel"]}">{I["phone"]} {BIZ["phone_display"]}</a></div>')
    main += f"""
<section class="section"><div class="container"><div class="split">
  <div class="prose" data-reveal><span class="eyebrow">{E(a['name'])} &amp; nearby</span><h2>Event setups in {E(a['name'])}</h2>
  <p>{E(a['intro'])}</p>
  <p>We also cover nearby localities including {E(near)}. Share your venue, date and guest count, and we'll suggest the right structure and seating and send a clear quote.</p>
  <p><strong>Open all 7 days, 8 AM – 9 PM.</strong> Call or WhatsApp <a href="tel:{BIZ['phone_tel']}">{BIZ['phone_display']}</a>.</p></div>
  <div class="split__img" data-clip>{img(p, a['photo'], sizes="(min-width:960px) 50vw, 100vw")}</div>
</div></div></section>
<section class="section section--sand"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">Available in {E(a['name'])}</span><h2>What we can set up for you</h2></div>
  <ul class="included" data-reveal-stagger>{svc_list}</ul>
</div></section>
{area_section(p, "Other areas we serve")}
{cta_band(p, f"Planning an event in {a['name']}?")}
"""
    page = {"prefix": p, "title": f"Tent House in {a['name']}, Bengaluru – Tents, Chairs, Stage & Sound",
            "desc": f"Looking for a tent house in {a['name']}? H.R. Tent House & Caterers sets up German hangars, shamianas, chairs, tables, stage, lighting and sound in {a['name']}, {a['near'][0]} and {a['near'][1]}. Call +91 99020 20244.",
            "hero_img": a["photo"], "schema": [breadcrumbs(crumbs)]}
    add(url, page, main, "0.7")

# ---------- GALLERY ----------
def gallery():
    p = "../"
    crumbs = [("Home", "/"), ("Gallery", "/gallery/")]
    filters = "".join(f'<button class="filter" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{E(l)}</button>' for k, l in CATS)
    tiles = []
    for stem in GALLERY_ORDER:
        alt, cats = IMAGES[stem]
        tw, th = size(stem, True)
        tiles.append(f'<figure class="tile" data-cat="{cats}"><button type="button" data-full="{p}assets/img/{stem}.webp" data-alt="{E(alt)}" aria-label="View larger: {E(alt)}">'
                     f'<img src="{p}assets/img/{stem}-thumb.webp" width="{tw}" height="{th}" alt="{E(alt)}" loading="lazy" decoding="async"></button>'
                     f'<figcaption>{E(alt)}</figcaption></figure>')
    main = page_hero(p, "Our work, <em>set up</em> and ready", "Real photos and videos from events we've set up: German hangars, pagodas, seating, stages and decor across Bengaluru.", crumbs, "german-pagoda-stalls", "Gallery")
    main += f"""
<section class="section"><div class="container">
  <div class="filters" role="group" aria-label="Filter photos">{filters}</div>
  <div class="masonry">{"".join(tiles)}</div>
</div></section>
<section class="section--tight"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">Videos</span><h2>Walk through our setups</h2></div>
  {video_block(p, [v for v, _ in VIDEOS])}
</div></section>
{cta_band(p, "Like what you see?", "Tell us about your event and we'll set up something just as good for you.")}
"""
    lightbox = f"""<div class="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
<img class="lightbox__img" alt=""><p class="lightbox__cap"></p>{DIYA}
<button class="lb-btn lb-close" type="button" aria-label="Close">{I['close']}</button>
<button class="lb-btn lb-prev" type="button" aria-label="Previous photo">{I['prev']}</button>
<button class="lb-btn lb-next" type="button" aria-label="Next photo">{I['next']}</button></div>"""
    gal_schema = {"@context": "https://schema.org", "@type": "ImageGallery", "name": f"{BIZ['name']} gallery",
                  "image": [{"@type": "ImageObject", "contentUrl": f"{SITE_URL}/assets/img/{s}.webp", "description": IMAGES[s][0]} for s in GALLERY_ORDER]}
    page = {"prefix": p, "title": "Gallery – Tent, Seating & Stage Setups in Bengaluru",
            "desc": "Photos and videos of German hangars, pagodas, banquet and Chiavari chair setups, tables with frills, stages and decor set up by H.R. Tent House in Bengaluru.",
            "hero_img": "german-pagoda-stalls", "active": "Gallery", "dock": "gallery", "gallery": True, "after": lightbox,
            "schema": [breadcrumbs(crumbs), gal_schema]}
    add("/gallery/", page, main, "0.8")

# ---------- ABOUT ----------
def about():
    p = "../"
    crumbs = [("Home", "/"), ("About", "/about/")]
    vals = [("tent", "One call for everything", "Tent, seating, stage, lighting, sound, cooling and power — planned and set up together, so nothing is missed."),
            ("check", "Clean, well-kept stock", "Covers, bows, frills and drapes come fresh and pressed, so your setup looks right in every photo."),
            ("clock", "On time, every time", "We plan the setup around your event timings, so everything is ready before your guests arrive."),
            ("spark", "Open every day", "We're open all 7 days, 8 AM to 9 PM, and reachable on call and WhatsApp.")]
    vhtml = "".join(f'<div class="value"><span class="icon-badge">{I[i]}</span><h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, t, d in vals)
    main = page_hero(p, "A Bengaluru tent house <em>since {}</em>".format(BIZ["founded"]),
                     f"{E(BIZ['name'])} rents and sets up tents, seating, stages, lighting and sound for weddings, functions and corporate events across Bengaluru.", crumbs, "banquet-chairs-gold-bows-lawn", "About us")
    main += f"""
<section class="section"><div class="container"><div class="split">
  <div class="prose" data-reveal><span class="eyebrow">Our story</span><h2>From a single shamiana to full event venues</h2>
  <p>{E(BIZ['name'])} started in {BIZ['founded']} in Bhuvaneshwari Nagar, Bengaluru. We're a family-run business, and since day one our aim has been simple: turn any open space — a lawn, a school ground, a terrace, a parking lot — into a comfortable, good-looking venue for your celebration.</p>
  <p>Today we set up German hangars, German pagodas, shamianas and canopies, along with banquet, Chiavari and plastic chairs, tables with frills, stages, decoration, lighting, sound, utensils, generators and cooling. We work on weddings and nikahs, poojas and house functions, school graduations and annual days, and corporate dinners and exhibitions.</p>
  </div>
  <div class="split__img" data-clip>{img(p, 'german-hangar-banquet-setup', sizes="(min-width:960px) 50vw, 100vw")}</div>
</div></div></section>
<section class="section section--sand"><div class="container">
  <div class="section-head" data-reveal><span class="eyebrow">Why people choose us</span><h2>What you can count on</h2></div>
  <div class="values" data-reveal-stagger>{vhtml}</div>
</div></section>
{cta_band(p)}
"""
    page = {"prefix": p, "title": "About H.R. Tent House & Caterers – Tent House in Bengaluru Since 2021",
            "desc": "H.R. Tent House & Caterers is a family-run tent house in Bhuvaneshwari Nagar, Bengaluru, setting up tents, seating, stages, lighting and sound for events since 2021.",
            "hero_img": "banquet-chairs-gold-bows-lawn", "active": "About", "schema": [breadcrumbs(crumbs)]}
    add("/about/", page, main, "0.6")

# ---------- CONTACT ----------
def contact():
    p = "../"
    crumbs = [("Home", "/"), ("Contact", "/contact/")]
    main = page_hero(p, "Get a free quote", "Share your event date, venue and guest count. We usually reply the same day — WhatsApp is fastest.", crumbs, "round-tables-pink-banquet-hall", "Contact",
                     f'<div class="btn-row" style="margin-top:28px"><a class="btn btn--wa" href="{WA_URL}" target="_blank" rel="noopener">{I["wa"]} WhatsApp us</a><a class="btn btn--ghost" href="tel:{BIZ["phone_tel"]}">{I["phone"]} {BIZ["phone_display"]}</a></div>')
    main += enquiry_form(p, "Tell us about your event")
    main += f"""<section class="section"><div class="container"><div class="areas">
<div data-reveal><span class="eyebrow">Visit or call</span><h2>Find us</h2>
<ul class="contact-list">
<li><a href="{BIZ['maps_url']}" target="_blank" rel="noopener">{I['pin']}<div><strong>Address</strong><span>{E(BIZ['name'])}<br>{E(BIZ['street'])}, {BIZ['city']}, {BIZ['region']} {BIZ['pin']}</span></div></a></li>
<li><div>{I['clock']}<div><strong>Hours</strong><span>{BIZ['hours_long']}<br><small style="color:var(--muted);font-weight:500">Event-day setups and take-downs are handled outside these hours too. Call or WhatsApp anytime.</small></span></div></div></li>
<li><a href="{BIZ['review_url']}" target="_blank" rel="noopener">{I['star']}<div><strong>Reviews</strong><span>Had an event with us? Rate us on Google</span></div></a></li>
</ul></div>
<div data-reveal>{map_embed()}</div>
</div></div></section>"""
    page = {"prefix": p, "title": "Contact H.R. Tent House – Get a Free Quote | Bengaluru",
            "desc": "Contact H.R. Tent House & Caterers, Bhuvaneshwari Nagar, Bengaluru. Call or WhatsApp +91 99020 20244, email hrtenthouse2021@gmail.com. Open all 7 days, 8 AM–9 PM.",
            "hero_img": "round-tables-pink-banquet-hall", "active": "Contact", "dock": "quote", "schema": [breadcrumbs(crumbs)]}
    add("/contact/", page, main, "0.8")

# ---------- FAQ ----------
def faq_page():
    p = "../"
    crumbs = [("Home", "/"), ("FAQ", "/faq/")]
    main = page_hero(p, "Questions, answered", "Everything people usually ask before booking a tent house in Bengaluru.", crumbs, "long-tables-frills-drape-backdrop", "FAQ")
    main += f'<section class="section"><div class="container">{faq_html(GENERAL_FAQ)}</div></section>' + cta_band(p, "Still have a question?", "Call or WhatsApp us. We're open all 7 days, 8 AM to 9 PM.")
    page = {"prefix": p, "title": "Tent House FAQ – Prices, Booking, Areas & Setup | Bengaluru",
            "desc": "Answers to common questions about renting German hangars, shamianas, chairs, tables, stage and sound from H.R. Tent House in Bengaluru: cost, booking, areas, setup and hours.",
            "hero_img": "long-tables-frills-drape-backdrop", "active": "FAQ", "schema": [breadcrumbs(crumbs), faq_schema(GENERAL_FAQ)]}
    add("/faq/", page, main, "0.6")

# ---------- 404 ----------
def notfound():
    base = "/" + SITE_URL.split("://", 1)[1].split("/", 1)[1].strip("/") + "/" if "/" in SITE_URL.split("://", 1)[1] else "/"
    p = base
    main = f"""<section class="notfound dark"><div class="container"><span class="eyebrow">Page not found</span><h1>404</h1>
<p class="lead" style="margin-inline:auto">This page has been packed up and taken away. Let's get you back to the main tent.</p>
<div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn btn--primary" href="{p}">Back to home</a><a class="btn btn--ghost" href="{p}contact/">Contact us</a></div></div></section>"""
    page = {"prefix": p, "title": "Page not found", "desc": "This page could not be found.", "noindex": True}
    page["path"] = "/404.html"
    pages.append(("/404.html", layout(page, main), "0", True))

# ======================================================================
# BUILD
# ======================================================================
def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    home(); services_hub()
    for s in SERVICES: service_page(s)
    for a in AREAS: area_page(a)
    gallery(); about(); contact(); faq_page(); notfound()
    for path, doc, _, _ in pages:
        f = OUT / (path.lstrip("/") if path.endswith(".html") else path.lstrip("/") + "index.html")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(doc, encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE_URL}{path}</loc><lastmod>{TODAY}</lastmod><priority>{prio}</priority></url>\n"
                   for path, _, prio, noindex in pages if not noindex)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "site.webmanifest").write_text(json.dumps({"name": BIZ["name"], "short_name": "HR Tent House", "start_url": "./", "display": "standalone",
        "background_color": "#141416", "theme_color": "#141416",
        "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1), encoding="utf-8")
    if CNAME_DOMAIN:
        (OUT / "CNAME").write_text(CNAME_DOMAIN + "\n", encoding="utf-8")
    print(f"Built {len(pages)} pages into {OUT}")

if __name__ == "__main__":
    build()
