#!/usr/bin/env python3
"""Check every tool URL in tools.json. The real gate.

The GitHub workflow used to point lychee at index.html — but every tool URL lives inside a
JS array, not an <a href>, so lychee found TWO links and reported green. This reads the
actual data.

Exit 1 if any URL is dead. Writes dead-links.md for the issue body.
"""
import json, os, re, sys, time, urllib.request, urllib.error, ssl, socket
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools.json")
OUT = os.path.join(ROOT, "dead-links.md")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

# GitHub runners have no IPv6 route. Python happily picks a host's AAAA record, gets
# "[Errno 101] Network is unreachable", and the site looks dead — Townscaper and
# asciinema were both reported dead by CI while returning 200 everywhere else. Pin
# resolution to IPv4 so the runner's network shape can't be mistaken for a dead link.
_getaddrinfo = socket.getaddrinfo


def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _ipv4_only

# Errors that mean "this runner cannot reach the network", never "this site is gone".
# Condemning a link on one of these is how a checker starts lying in the other direction.
INFRA_ERRORS = ("network is unreachable", "temporary failure in name resolution",
                "no route to host", "errno 101", "errno -3")

# A timeout is not proof of death and not proof of life. asciinema.org answers 200 from a
# laptop and times out from a GitHub runner — datacenter ranges get throttled. Counting
# that as dead opens a bogus issue every Monday; counting it as fine hides real outages.
# So it gets its own verdict: reported loudly, every week, but it does not fail the run.
TIMEOUT_ERRORS = ("timed out", "timeout")

# Codes that mean "alive, just defensive": bot walls, rate limits, auth gates.
OK = set(range(200, 400)) | {401, 403, 429, 405, 406, 999}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


# A squatted domain answers 200 all day. It is WORSE than a 404: the machine sends
# someone to an ad page still wearing the tool's name. driveandlisten.com went this way —
# the parking page returned 200 and sailed through the first version of this check.
PARKED_HOSTS = (
    "forsale.godaddy.com", "sedo.com", "sedoparking.com", "afternic.com",
    "dan.com", "undeveloped.com", "bodis.com", "parkingcrew.net",
    "hugedomains.com", "buydomains.com", "domainmarket.com", "squadhelp.com",
    "atom.com", "namecheap.com/domains/registration",
)


# Squatters rarely bother with an HTTP redirect. driveandlisten.com serves a 113-byte page
# whose entire content is `window.location.href="/lander"` — urllib does not run JS, so
# following redirects sees a clean 200 and nothing else. The body is the only tell.
PARKED_MARKERS = (
    "/lander", "this domain is for sale", "buy this domain", "domain is for sale",
    "the domain name is for sale", "parkingcrew", "sedoparking", "afternic",
    "hugedomains", "domain for sale", "inquire about this domain",
)


# A parked domain is the LOUD failure. The quiet one is a page that is perfectly alive and
# simply is not the tool any more: screely.com now serves a sports-betting site, and the URL
# once listed for CheatSheet serves invoicing software. Both return a clean 200 with a real,
# substantial body and no parking marker anywhere — every liveness check on earth passes them.
#
# Comparing the title to the TOOL NAME does not work: plenty of good entries never matched
# (Subtitle Edit's page is titled "Nikse.dk"), so that flags dozens of healthy links and the
# whole check gets ignored. What is diagnostic is CHANGE. The title recorded while a link was
# known-good is the baseline; a title that moves away from it is the thing worth a human
# glance. This is a WARNING and never fails the run — a gate that cries wolf gets ignored,
# and that is the same failure in a different coat.
SHUTDOWN_MARKERS = (
    "has shut down", "has shut down.", "is shutting down", "we're shutting down",
    "no longer available", "no longer maintained", "has been discontinued",
    "service has ended", "this project is archived", "is sunsetting",
    "this site is no longer", "development has stopped", "project has ended",
)

TITLES = os.path.join(ROOT, "link-titles.json")


def _title_of(body):
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    if not m:
        return ""
    t = re.sub(r"<[^>]+>", " ", m.group(1))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:120]


def inspect(url):
    """One GET, three questions: is it parked, has it announced a shutdown, what is its title?

    Folded into a single fetch because the parked check already paid for the body; a second
    request per URL would double a 541-link run for nothing.
    """
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            final = r.geturl()
            body = r.read(60000).decode("utf-8", "replace")
    except Exception:
        return None, None, None

    low = body.lower()
    title = _title_of(body)

    for h in PARKED_HOSTS:
        if h in final.lower():
            return f"redirects to parking host {h}", None, title

    # A real site is not 1.5KB of nothing. Require BOTH a tiny body and a parking tell,
    # so a legitimate page that merely says "for sale" somewhere isn't condemned.
    if len(body) < 1500:
        for m in PARKED_MARKERS:
            if m in low:
                return f"parked page ({m!r} in a {len(body)}-byte body)", None, title
    for m in ("this domain is for sale", "buy this domain", "the domain name is for sale"):
        if m in low:
            return f"parked page ({m!r})", None, title

    # Only trust a shutdown notice near the top of the page. The phrase appears in plenty of
    # changelogs and blog archives further down, and condemning those is how this starts lying.
    head = low[:6000]
    for m in SHUTDOWN_MARKERS:
        if m in head:
            return None, f"shutdown notice on the page ({m!r})", title

    return None, None, title


def probe(url, method="HEAD", timeout=20):
    req = urllib.request.Request(url, method=method, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError) as e:
        return None, str(getattr(e, "reason", e))[:120]
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"[:120]


def attempt(url):
    code, err = probe(url, "HEAD")
    # Plenty of servers refuse HEAD but serve GET fine.
    if code is None or code not in OK:
        code2, err2 = probe(url, "GET")
        if code2 is not None:
            code, err = code2, err2
        elif err is None:
            err = err2
    return code, err


def check(tool):
    url = tool["u"]
    # Retry before condemning. The first version of this script called The Book of Shaders
    # dead on a one-off SSL handshake timeout; the site returns 200. A checker that
    # invents dead links gets ignored exactly like one that never finds any.
    for i in range(3):
        code, err = attempt(url)
        if code is not None and code in OK:
            break
        if i < 2:
            time.sleep(2 * (i + 1))
    alive = code in OK if code is not None else False
    if not alive and err and any(m in err.lower() for m in INFRA_ERRORS):
        return {"name": tool["n"], "cat": tool["c"], "url": url, "code": code,
                "err": f"INFRA (not counted as dead) — {err}", "alive": True,
                "infra": True}
    if not alive and code is None and err and any(m in err.lower() for m in TIMEOUT_ERRORS):
        return {"name": tool["n"], "cat": tool["c"], "url": url, "code": code,
                "err": f"UNVERIFIED — {err} after 3 tries", "alive": True,
                "unverified": True}
    if alive:
        p, shut, title = inspect(url)
        if p:
            return {"name": tool["n"], "cat": tool["c"], "url": url,
                    "code": code, "err": f"PARKED — {p}", "alive": False}
        return {"name": tool["n"], "cat": tool["c"], "url": url,
                "code": code, "err": err, "alive": True,
                "title": title, "shutdown": shut}
    return {"name": tool["n"], "cat": tool["c"], "url": url,
            "code": code, "err": err, "alive": alive}


def main():
    tools = json.load(open(TOOLS))
    print(f"Checking {len(tools)} URLs…", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(check, tools))

    dead = [r for r in results if not r["alive"]]
    infra = [r for r in results if r.get("infra")]
    unver = [r for r in results if r.get("unverified")]
    for r in dead:
        print(f"  DEAD  {r['code'] or r['err']}  {r['name']}  {r['url']}", flush=True)
    # Never silent. A check that quietly drops entries reads as "everything passed".
    for r in infra + unver:
        print(f"  SKIP  {r['err']}  {r['name']}  {r['url']}", flush=True)

    # ── has the page stopped being the tool? ──
    try:
        base = json.load(open(TITLES))
    except Exception:
        base = {}
    drift, seeded = [], 0
    for r in results:
        if not r.get("alive") or r.get("infra") or r.get("unverified"):
            continue
        if r.get("shutdown"):
            drift.append((r, r["shutdown"]))
            continue
        t, was = r.get("title"), base.get(r["url"])
        if not t:
            continue
        if was is None:
            base[r["url"]] = t
            seeded += 1
        elif was != t:
            drift.append((r, f"title changed: {was!r} → {t!r}"))
            base[r["url"]] = t          # record the new one, so it reports once, not forever
    # forget URLs that are no longer listed, so the baseline can't grow forever
    base = {k: v for k, v in base.items() if k in {r["url"] for r in results}}
    try:
        json.dump(base, open(TITLES, "w"), indent=0, sort_keys=True, ensure_ascii=False)
    except Exception as e:
        print(f"  (could not write {os.path.basename(TITLES)}: {e})")

    for r, why in drift:
        print(f"  DRIFT {r['name']}  —  {why}\n        {r['url']}", flush=True)

    print(f"\n{len(results) - len(dead)}/{len(results)} alive · {len(dead)} dead"
          + (f" · {len(infra)} unreachable from this runner" if infra else "")
          + (f" · {len(unver)} timed out, unverified — check these by hand" if unver else "")
          + (f" · {len(drift)} changed — review by hand, NOT failures" if drift else "")
          + (f" · {seeded} new baselines recorded" if seeded else ""))

    if dead:
        with open(OUT, "w") as f:
            f.write("Automated check found URLs that no longer resolve.\n\n")
            f.write("| Tool | Category | Status | URL |\n|---|---|---|---|\n")
            for r in dead:
                f.write(f"| {r['name']} | {r['cat']} | {r['code'] or r['err']} | {r['url']} |\n")
        return 1
    if os.path.exists(OUT):
        os.remove(OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
