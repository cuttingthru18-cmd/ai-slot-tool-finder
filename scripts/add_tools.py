#!/usr/bin/env python3
"""Add new tools to the machine. Dupe-safe, validated, idempotent.

Run it twice and nothing happens the second time — every candidate is checked against the
existing TOYS array by BOTH url and name before it goes anywhere near the file.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")

NEW = [
    # ── 🎪 fun · neal.fun (five more he made that the machine doesn't have) ──
    {"n": "The Password Game", "e": "🔐", "c": "fun", "d": "Pick a password. Then the rules start arriving — and they get insane. The funniest thing on the internet this decade.", "u": "https://neal.fun/password-game/"},
    {"n": "Asteroid Launcher", "e": "☄️", "c": "fun", "d": "Drop an asteroid anywhere on Earth and watch the crater, fireball and shockwave hit your own city. Horrifyingly good.", "u": "https://neal.fun/asteroid-launcher/"},
    {"n": "Absurd Trolley Problems", "e": "🚋", "c": "fun", "d": "The trolley problem, escalated until your morals fall apart — then it shows you what everyone else chose.", "u": "https://neal.fun/absurd-trolley-problems/"},
    {"n": "Spend Bill Gates' Money", "e": "💸", "c": "fun", "d": "You have $100 billion. Buy Big Macs, private islands, or an NBA team — and discover you still can't spend it all.", "u": "https://neal.fun/spend/"},
    {"n": "Wonders of Street View", "e": "🛣️", "c": "fun", "d": "The strangest things Google's cameras ever caught, collected in one place. A man in a horse mask, every time.", "u": "https://neal.fun/wonders-of-street-view/"},

    # ── 🎪 fun · live windows onto the real world ──
    {"n": "Radiooooo", "e": "📼", "c": "fun", "d": "Pick a country, pick a decade, and hear what people were actually listening to. Radio Garden's time-travelling cousin.", "u": "https://radiooooo.com"},
    {"n": "MarineTraffic", "e": "🚢", "c": "fun", "d": "Every cargo ship on Earth, live, right now. Click any dot and see what it's carrying and where it's going.", "u": "https://www.marinetraffic.com"},
    {"n": "Ventusky", "e": "🌪️", "c": "fun", "d": "The planet's weather as flowing colour — wind, rain, temperature, swell — scrub forward in time and watch storms form.", "u": "https://www.ventusky.com"},
    {"n": "SkylineWebcams", "e": "📹", "c": "fun", "d": "Thousands of live cameras: a Roman piazza at dawn, a Tokyo crossing at midnight, a puffin colony in Iceland.", "u": "https://www.skylinewebcams.com"},

    # ── 🎪 fun · explorables (things that teach by letting you fiddle) ──
    {"n": "Bartosz Ciechanowski", "e": "⚙️", "c": "fun", "d": "How gears, lenses, GPS and engines actually work — every diagram draggable. Nothing else on the web looks this good.", "u": "https://ciechanow.ski"},
    {"n": "Parable of the Polygons", "e": "🔺", "c": "fun", "d": "A playable story about how tiny individual bias becomes massive collective segregation. You'll never unsee it.", "u": "https://ncase.me/polygons/"},
    {"n": "Loopy", "e": "🔁", "c": "fun", "d": "Draw a system — arrows, loops, feedback — hit play, and watch it run. A whiteboard that simulates itself.", "u": "https://ncase.me/loopy/"},
    {"n": "Crowds", "e": "👥", "c": "fun", "d": "A playable explanation of how riots, fads and revolutions actually spread. From the maker of Evolution of Trust.", "u": "https://ncase.me/crowds/"},
    {"n": "Explained Visually", "e": "📐", "c": "fun", "d": "Hard maths — eigenvectors, Markov chains, Pi — made obvious by letting you drag the numbers around.", "u": "https://setosa.io/ev/"},
    {"n": "Red Blob Games", "e": "🔷", "c": "fun", "d": "The clearest explanations of pathfinding, hexagons and noise ever written — every single one interactive.", "u": "https://www.redblobgames.com"},

    # ── 🎪 fun · maps and data made beautiful ──
    {"n": "City Roads", "e": "🗺️", "c": "fun", "d": "Type any city. It draws every single road in it and nothing else — your hometown rendered as a nervous system.", "u": "https://anvaka.github.io/city-roads/"},
    {"n": "Map of GitHub", "e": "🌌", "c": "fun", "d": "Every open-source project as a star, clustered into galaxies by what they're near. Fly through the whole sky.", "u": "https://anvaka.github.io/map-of-github/"},

    # ── 🎪 fun · sound ──
    {"n": "Museum of Endangered Sounds", "e": "📼", "c": "fun", "d": "Dial-up. The Nokia ringtone. A Windows 95 boot. Sounds that are already gone, kept alive in one room.", "u": "https://savethesounds.info"},
    {"n": "musicforprogramming", "e": "🎧", "c": "fun", "d": "One long mix, made for deep work, with zero lyrics and zero interruptions. Programmers have used it for 15 years.", "u": "https://musicforprogramming.net"},
    {"n": "Rainy Mood", "e": "🌧️", "c": "fun", "d": "Rain on a window, for as long as you need it. The oldest and still the best of its kind.", "u": "https://rainymood.com"},

    # ── 🎪 fun · sandboxes and rabbit holes ──
    {"n": "Shadertoy", "e": "🖼️", "c": "fun", "d": "Thousands of live shaders, running in your browser, with the code beside them. Edit one line and watch reality change.", "u": "https://www.shadertoy.com"},
    {"n": "OldWeb.today", "e": "🕸️", "c": "fun", "d": "Browse the 1997 internet inside a real 1997 browser. Netscape, dial-up rendering, the whole thing.", "u": "https://oldweb.today"},
    {"n": "WikiTrivia", "e": "🃏", "c": "fun", "d": "Place random Wikipedia events on a timeline. Sounds easy. It is not. You'll play it for an hour.", "u": "https://wikitrivia.tomjwatson.com"},
    {"n": "100,000 Stars", "e": "✨", "c": "fun", "d": "Fly out from the Sun through the actual mapped positions of 100,000 nearby stars. Then keep going.", "u": "https://stars.chromeexperiments.com"},
    {"n": "The Powder Toy", "e": "🧪", "c": "fun", "d": "A physics sandbox with real thermodynamics — build a nuclear reactor out of sand and set it on fire.", "u": "https://powdertoy.co.uk"},
    {"n": "Zoomquilt 2", "e": "🌀", "c": "fun", "d": "An infinitely zooming painting that never repeats. Fall into it and forget what you were doing.", "u": "https://www.zoomquilt2.com"},
    {"n": "Bongo Cat", "e": "🐱", "c": "fun", "d": "A cat plays your keyboard with you. That's it. That's the whole site. It's perfect.", "u": "https://www.bongo.cat"},
    {"n": "The Useless Web", "e": "🎲", "c": "fun", "d": "One button. It throws you at the most pointless site on the internet. Press it again immediately.", "u": "https://theuselessweb.com"},
    {"n": "Old Maps Online", "e": "🗞️", "c": "fun", "d": "Search any place and see how cartographers drew it across 500 years. Watch coastlines get slowly less wrong.", "u": "https://www.oldmapsonline.org"},

    # ── 🍬 candy · macOS gadgets ──
    {"n": "Stats", "e": "📊", "c": "candy", "d": "Your Mac's CPU, RAM, network and battery — live in the menu bar. You'll never open Activity Monitor again.", "u": "https://github.com/exelban/stats"},
    {"n": "MonitorControl", "e": "🖥️", "c": "candy", "d": "Change your external monitor's brightness and volume with the Mac keys that were never supposed to work. It just fixes it.", "u": "https://github.com/MonitorControl/MonitorControl"},
    {"n": "Ice", "e": "🧊", "c": "candy", "d": "Your menu bar is 30 icons of noise. Ice hides the junk and shows what matters — free, and better than the app that charges.", "u": "https://github.com/jordanbaird/Ice"},
    {"n": "xbar", "e": "🍫", "c": "candy", "d": "Put the output of ANY script into your menu bar. Bitcoin price, build status, whether the coffee's fresh — if you can print it, you can pin it.", "u": "https://xbarapp.com"},
    {"n": "AeroSpace", "e": "🪟", "c": "candy", "d": "i3-style tiling windows on macOS. Your windows snap into place and never overlap again. Keyboard only, no mercy.", "u": "https://github.com/nikitabobko/AeroSpace"},
    {"n": "whatcable", "e": "🔌", "c": "candy", "d": "That drawer of identical USB-C cables? This tells you which one actually charges fast — and which is a lying piece of string.", "u": "https://github.com/darrylmorley/whatcable"},
    {"n": "FineTune", "e": "🔊", "c": "candy", "d": "Per-app volume on your Mac. Turn Spotify down without touching the video you're watching — what macOS should have shipped with.", "u": "https://github.com/ronitsingh10/FineTune"},
    {"n": "KeepingYouAwake", "e": "☕", "c": "candy", "d": "One click and your Mac never sleeps. Stop jiggling the mouse during a long render.", "u": "https://github.com/newmarcel/KeepingYouAwake"},

    # ── 🪟 win · Windows gadgets ──
    {"n": "Sniffnet", "e": "🕵️", "c": "win", "d": "Watch every connection your PC makes, live, in a window that's genuinely beautiful. Network monitoring that doesn't look like 1998.", "u": "https://sniffnet.net"},
    {"n": "GlazeWM", "e": "🔲", "c": "win", "d": "Tiling window manager for Windows. Your windows arrange into a perfect grid and you drive the whole thing from the keyboard.", "u": "https://github.com/glzr-io/glazewm"},
    {"n": "CopyQ", "e": "📋", "c": "win", "d": "Every copy you've ever made — searchable, scriptable, forever. The clipboard manager Windows should have had.", "u": "https://hluk.github.io/CopyQ/"},
    {"n": "OpenTrace", "e": "🧭", "c": "win", "d": "Traceroute, but with a map. Watch your packets physically hop across the planet to reach a server.", "u": "https://github.com/Archeb/opentrace"},

    # ── 🤖 agent · AI ──
    {"n": "Continue", "e": "⌨️", "c": "agent", "d": "An open-source coding agent that lives in your editor and actually finishes the job. Bring your own model — no subscription.", "u": "https://continue.dev"},
    {"n": "CrewAI", "e": "🧑‍🚀", "c": "agent", "d": "Give a team of AI agents different roles — researcher, writer, critic — and let them argue their way to an answer. Weirdly effective.", "u": "https://www.crewai.com"},
    {"n": "Agent Zero", "e": "🕳️", "c": "agent", "d": "An AI agent that writes its own tools as it goes. Genuinely unsettling to watch it solve something you never taught it.", "u": "https://github.com/agent0ai/agent-zero"},
    {"n": "Eliza", "e": "🧬", "c": "agent", "d": "An operating system for AI agents. Build one that lives on Discord, posts to X, and keeps running while you sleep.", "u": "https://github.com/elizaOS/eliza"},

    # ── 🎨 creator · maker tools ──
    {"n": "Espanso", "e": "⚡", "c": "creator", "d": "Type ;addr and your full address appears. Anywhere, any app, instantly. Runs invisibly and quietly saves you hours a week.", "u": "https://espanso.org"},
    {"n": "Yazi", "e": "📁", "c": "creator", "d": "A terminal file manager faster than Finder, driven entirely by keyboard, that previews absolutely everything.", "u": "https://yazi-rs.github.io"},
    {"n": "Excalidraw", "e": "✏️", "c": "creator", "d": "A whiteboard that makes everything look hand-drawn. Open it, sketch the idea, send the link. No account, no friction.", "u": "https://excalidraw.com"},
    {"n": "Squoosh", "e": "🗜️", "c": "creator", "d": "Shrink any image to a fraction of its size with a live before/after slider — and it never leaves your browser.", "u": "https://squoosh.app"},
    {"n": "Carbon", "e": "🎞️", "c": "creator", "d": "Paste code, get a beautiful screenshot of it. Every dev on Twitter uses this and pretends they don't.", "u": "https://carbon.now.sh"},
    {"n": "regex101", "e": "🔍", "c": "creator", "d": "Write a regex and watch it explain itself, character by character, as you type. The tool that finally makes regex make sense.", "u": "https://regex101.com"},
    {"n": "Shotcut", "e": "🎬", "c": "creator", "d": "A real video editor — timeline, keyframes, 4K — free, on every platform, with no watermark and no account.", "u": "https://shotcut.org"},
    {"n": "Zettlr", "e": "📝", "c": "creator", "d": "Write, cite and publish from one Markdown workbench. Built for people who actually finish the thing.", "u": "https://zettlr.com"},
    {"n": "css-doodle", "e": "🌀", "c": "creator", "d": "One line of CSS becomes generative art. Paste it, nudge a number, lose an hour.", "u": "https://css-doodle.com"},
    {"n": "Plausible", "e": "📈", "c": "creator", "d": "Web analytics that fit on one screen, need no cookie banner, and don't sell your visitors. The anti-Google-Analytics.", "u": "https://plausible.io"},
    {"n": "ksnip", "e": "✂️", "c": "creator", "d": "Screenshot, annotate, arrow, blur, done — on Mac, Windows and Linux, with no subscription nagging you.", "u": "https://github.com/ksnip/ksnip"},
]


def find_array(html):
    r"""Locate the TOYS array by BRACKET MATCHING, not regex.

    `var TOYS=(\[.*?\]);` fails: the non-greedy match stops at the first `]` it sees, which
    lands inside the array, and json.loads then chokes on "Extra data". Count brackets — and
    ignore any that appear inside a JSON string (a blurb could contain one).
    """
    i = html.index("var TOYS=")
    j = html.index("[", i)
    depth, k, in_str, esc = 0, j, False, False
    while k < len(html):
        c = html[k]
        if in_str:
            if esc:      esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"':  in_str = True
            elif c == "[": depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return j, k + 1
        k += 1
    raise ValueError("unterminated TOYS array")


def norm(u):
    return u.rstrip("/").lower()


def main():
    # Candidates default to the NEW list above, but an optional JSON file path
    # (same object shape) can be passed to feed a batch without editing this file.
    candidates = NEW
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            candidates = json.load(f)
        print(f"  candidates: {len(candidates)} from {sys.argv[1]}")

    html = open(INDEX, encoding="utf-8").read()
    start, end = find_array(html)
    toys = json.loads(html[start:end])
    print(f"  existing: {len(toys)} tools")

    have_u = {norm(t["u"]) for t in toys}
    have_n = {t["n"].strip().lower() for t in toys}

    added, skipped = [], []
    for t in candidates:
        if norm(t["u"]) in have_u:
            skipped.append((t["n"], "url already listed")); continue
        if t["n"].strip().lower() in have_n:
            skipped.append((t["n"], "name already listed")); continue
        for k in ("n", "e", "c", "d", "u"):
            if not t.get(k):
                skipped.append((t.get("n", "?"), f"missing {k}")); break
        else:
            toys.append(t)
            have_u.add(norm(t["u"])); have_n.add(t["n"].strip().lower())
            added.append(t)

    for n, why in skipped:
        print(f"  ⊘ skipped  {n}  ({why})")
    print(f"\n  + added {len(added)}  ->  {len(toys)} total")

    # rebuild, preserving the single-line format the file already uses
    html = html[:start] + json.dumps(toys, ensure_ascii=False) + html[end:]
    open(INDEX, "w", encoding="utf-8").write(html)

    # VALIDATE: it must parse back, and every category must be one the UI knows
    h2 = open(INDEX, encoding="utf-8").read()
    s2, e2 = find_array(h2)
    check = json.loads(h2[s2:e2])
    cats = {t["c"] for t in check}
    print(f"  validated: {len(check)} entries parse · categories {sorted(cats)}")
    assert cats <= {"fun", "candy", "win", "agent", "creator"}, f"unknown category: {cats}"
    assert len({norm(t['u']) for t in check}) == len(check), "DUPLICATE URL SLIPPED THROUGH"
    print("  ✓ no duplicate urls · all categories valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
