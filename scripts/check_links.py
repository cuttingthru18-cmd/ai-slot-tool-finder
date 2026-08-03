#!/usr/bin/env python3
"""Check every tool URL in tools.json. The real gate.

The GitHub workflow used to point lychee at index.html — but every tool URL lives inside a
JS array, not an <a href>, so lychee found TWO links and reported green. This reads the
actual data.

Exit 1 if any URL is dead. Writes dead-links.md for the issue body.
"""
import json, os, sys, time, urllib.request, urllib.error, ssl, socket
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


def parked(url):
    """Return a reason string if this URL is a parked/for-sale page rather than a site."""
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            final = r.geturl()
            body = r.read(6000).decode("utf-8", "replace")
    except Exception:
        return None

    for h in PARKED_HOSTS:
        if h in final.lower():
            return f"redirects to parking host {h}"

    low = body.lower()
    # A real site is not 1.5KB of nothing. Require BOTH a tiny body and a parking tell,
    # so a legitimate page that merely says "for sale" somewhere isn't condemned.
    if len(body) < 1500:
        for m in PARKED_MARKERS:
            if m in low:
                return f"parked page ({m!r} in a {len(body)}-byte body)"
    for m in ("this domain is for sale", "buy this domain", "the domain name is for sale"):
        if m in low:
            return f"parked page ({m!r})"
    return None


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
    if alive:
        p = parked(url)
        if p:
            return {"name": tool["n"], "cat": tool["c"], "url": url,
                    "code": code, "err": f"PARKED — {p}", "alive": False}
    return {"name": tool["n"], "cat": tool["c"], "url": url,
            "code": code, "err": err, "alive": alive}


def main():
    tools = json.load(open(TOOLS))
    print(f"Checking {len(tools)} URLs…", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(check, tools))

    dead = [r for r in results if not r["alive"]]
    infra = [r for r in results if r.get("infra")]
    for r in dead:
        print(f"  DEAD  {r['code'] or r['err']}  {r['name']}  {r['url']}", flush=True)
    for r in infra:
        print(f"  SKIP  {r['err']}  {r['name']}  {r['url']}", flush=True)

    print(f"\n{len(results) - len(dead)}/{len(results)} alive · {len(dead)} dead"
          + (f" · {len(infra)} unreachable from this runner (not counted)" if infra else ""))

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
