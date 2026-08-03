# 🎰 AI Slot Tool Finder

A free, open-source web app for discovering curated tools — pull a slot-machine lever, get a tool you'd probably never find yourself.

- **421 manually reviewed entries** across 5 categories — every link checked, zero duplicates
- **One self-contained HTML file** — no build step, no dependencies
- **No login, no backend, no analytics, no tracking**
- Works locally (download and double-click) or hosted via GitHub Pages
- **[🎰 Mac menu bar app](#-put-it-in-your-menu-bar-mac)** — 616 KB, native, works offline

Maintained by **YL MRKT**. AI research agents assisted with discovery; **every listed tool was manually reviewed before inclusion.**

![AI Slot Tool Finder](screenshots/main.png)

## Try it

**[▶ Play it here](https://cuttingthru18-cmd.github.io/ai-slot-tool-finder/)** — any browser, any device.

Or run it locally: download `index.html` and open it. That's the entire install.

## What's inside

| Category | Count | What it means |
|---|---|---|
| 🟣 **Fun** | 127 | Websites that exist to amaze — globes, games, art, sound. |
| 🟡 **Mac Candy** | 57 | Free apps that make a Mac prettier or smoother. |
| 🟢 **Agent Power** | 115 | AI tools, playgrounds, and installable skills/MCP servers you can try today. |
| 🔵 **Creator** | 67 | Editors, converters, audio fixers, screenshot tools. |
| 🪟 **Windows Candy** | 55 | Free apps that glow up a Windows PC. |

The machine deals without repeats — you'll see all 421 before any repeat. Prefer browsing? Click **"INSIDE THE MACHINE"** at the bottom of the page for the full list.

## Why trust this?

- **No account required** — nothing to sign up for, ever
- **No backend** — static HTML only; the page can't collect anything
- **No analytics or trackers** — verify it yourself: it's one readable file
- **Every link manually reviewed** before inclusion (free or real free tier · actively maintained · official source)
- **Automated weekly link checks** run every Monday via GitHub Actions — every tool URL is
  fetched, redirects followed, and parked/for-sale domains rejected even when they answer 200.
  Dead links open an issue automatically and get fixed or removed.
- Last full link review: **2026-08-03** — all 421 checked, 4 fixed, 1 removed

## The machine

**Tap the lever** — or hit Enter — and it fires straight away.

Or grab the red knob and **drag it down the track**: it resists, bottoms out, and springs back.
Once you start dragging you're committing to a pull, so the drag only engages if you take it past
halfway. Let go short of that and it springs back without firing, the way an abandoned pull should.

The reels are real strips: they blur, decelerate, and **sharpen just before they stop** — the
symbol comes into focus as it slows, the way a physical reel does. Then they overshoot the
payline and kick back. When all three land, everything fires at once — the rims throb gold,
the symbols pop, the payline blazes, and the background flares.

The background is three parallax layers whose hue shifts with the category you pick. It pauses
when the tab is hidden.

Everything respects `prefers-reduced-motion`.

## The AI assistant button

If you run an AI assistant like [Claude Code](https://claude.com/claude-code): when the machine picks an installable tool, **COPY FOR YOUR AI ASSISTANT** copies a ready-made install request to paste to it. No assistant? The tool's page opens either way — install it normally.

## 🎰 Put it in your menu bar (Mac)

The machine, one click away, from inside any app — no tab, no URL, no signup.

**Install it:**

1. Download **`AI-Slot-Tool-Finder-macOS.zip`** from the [latest release](../../releases/latest) and unzip it
2. Drag **AI Slot Tool Finder.app** to your **Applications** folder
3. **Right-click the app → Open**, then click **Open** in the dialog

> **Step 3 matters, and only the first time.** The app isn't signed with a paid Apple
> Developer ID ($99/year), so double-clicking it shows *"can't be opened because it is
> from an unidentified developer."* Right-click → Open is macOS's built-in way to say
> you trust it. After that it opens normally, forever.
>
> Prefer the terminal? `xattr -dr com.apple.quarantine "/Applications/AI Slot Tool Finder.app"`

Then click **🎰** in your menu bar and pull the lever. To have it there every morning:
**System Settings → General → Login Items → +** and add it.

**Or build it yourself** — it's one Swift file, no dependencies:

```sh
git clone https://github.com/cuttingthru18-cmd/ai-slot-tool-finder.git
cd ai-slot-tool-finder/menubar
./build.sh --install
```

(Needs Xcode command line tools: `xcode-select --install`.)

### What it does

Same machine as the site: pull the lever, the reels stop left to right, you get one
tool. Same no-repeat bag — you'll see all 421 before any repeat. Filter by category,
**Open** it, or **Copy for AI** to paste an install request to your assistant.

| | |
|---|---|
| **616 KB** | Native Swift. Not Electron — that would be ~200MB for the same thing |
| **Works offline** | The full shelf ships inside the app; the network is a refresh, never a dependency |
| **Never needs updating** | Tools are fetched from [`tools.json`](tools.json) once a day, so new tools just appear |
| **No account, no analytics** | Same posture as the site. Nothing is collected, nothing phones home except the tool list |

### Building on the tool list

`tools.json` is the same 421 entries the site uses, written from the identical array
so the two can't drift. It's served from GitHub Pages and free to use:

```
https://cuttingthru18-cmd.github.io/ai-slot-tool-finder/tools.json
```

```json
{"n": "Radio Garden", "e": "📻", "c": "fun",
 "d": "Spin a 3D globe and drop into any live radio station on Earth…",
 "u": "https://radio.garden"}
```

## Make it feel like an app (any platform)

- **Mac (Safari):** File → **Add to Dock**
- **iPhone/iPad:** Share → **Add to Home Screen**

## Contributing

Found a dead link or know a tool that belongs here? [Open an issue](../../issues/new/choose) — there are templates for dead links, tool suggestions, and bugs. See [CONTRIBUTING.md](CONTRIBUTING.md) for the quality bar.

## How it was made

The tool list was researched with AI agents across sources like [awesome-mac](https://github.com/jaywcjlove/awesome-mac), [tools.simonwillison.net](https://tools.simonwillison.net), [neal.fun](https://neal.fun), and the [Charm](https://github.com/charmbracelet) suite — then each entry was manually reviewed and quality-gated before inclusion. The app itself is one hand-written HTML file.

## License

MIT — see [LICENSE](LICENSE). The tools inside belong to their own creators; this machine just introduces you.
