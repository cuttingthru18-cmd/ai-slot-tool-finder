// AI Slot Tool Finder — the lever, in your menu bar.
//
// The site's whole trick is that pulling makes you want to pull again. That does not
// survive being turned into a list of links, so this is not a list of links: it is the
// machine, one click away, from inside any app.
//
// Deliberately native and tiny. An Electron build of this would be ~200MB and would ship
// an auto-updater that breaks itself the moment it downloads an unsigned build. All the
// content lives remotely instead, so the app almost never needs updating at all — adding
// 50 tools is one `git push` and every installed copy has them the next morning.

import AppKit
import SwiftUI

// MARK: - Model

/// Field names are the site's, not prettier ones. index.html is the single source of
/// truth and this decodes its array verbatim, so the two can never drift apart.
struct Tool: Codable, Hashable {
    let n: String   // name
    let e: String   // emoji
    let c: String   // category
    let d: String   // description
    let u: String   // url
}

let FEED_URL = URL(string: "https://cuttingthru18-cmd.github.io/ai-slot-tool-finder/tools.json")!
let CATEGORIES = ["all", "fun", "agent", "creator", "candy", "win"]

// MARK: - Shelf

final class Shelf: ObservableObject {
    @Published var tools: [Tool] = []
    @Published var current: Tool?
    @Published var reels: [String] = ["🎰", "🎰", "🎰"]
    @Published var spinning = false
    @Published var copied = false
    @Published var category = "all" { didSet { refillBag() } }

    /// Names already drawn this cycle. The site's no-repeat bag: you see all 379 before
    /// you see any of them twice, which is the difference between discovery and a
    /// random-link button.
    private var drawn: Set<String> = []
    private var bag: [Tool] = []

    private let cacheURL: URL = {
        let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("AI Slot Tool Finder", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir.appendingPathComponent("tools.json")
    }()

    var pool: [Tool] { category == "all" ? tools : tools.filter { $0.c == category } }

    init() {
        drawn = Set(UserDefaults.standard.stringArray(forKey: "drawn") ?? [])
        load()
        refresh()
    }

    // MARK: Loading

    /// Cache first, then the copy that shipped inside the app. Something is always on
    /// screen instantly — the network is a refresh, never a dependency.
    private func load() {
        if let d = try? Data(contentsOf: cacheURL), let t = try? JSONDecoder().decode([Tool].self, from: d), !t.isEmpty {
            tools = t
        } else if let bundled = Bundle.main.url(forResource: "tools", withExtension: "json"),
                  let d = try? Data(contentsOf: bundled),
                  let t = try? JSONDecoder().decode([Tool].self, from: d) {
            tools = t
        }
        refillBag()
    }

    /// Pull the shelf once a day. Failure is silent and harmless: the cached copy is
    /// already loaded, so a plane, a captive wifi portal, or a dead site all just mean
    /// you keep the tools you had.
    func refresh() {
        let last = UserDefaults.standard.double(forKey: "lastFetch")
        guard Date().timeIntervalSince1970 - last > 86_400 || tools.isEmpty else { return }
        URLSession.shared.dataTask(with: FEED_URL) { [weak self] data, _, _ in
            guard let self, let data, let fresh = try? JSONDecoder().decode([Tool].self, from: data), !fresh.isEmpty
            else { return }
            try? data.write(to: self.cacheURL)
            UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "lastFetch")
            DispatchQueue.main.async {
                self.tools = fresh
                self.refillBag()
            }
        }.resume()
    }

    // MARK: The bag

    private func refillBag() {
        bag = pool.filter { !drawn.contains($0.n) }
        if bag.isEmpty {                       // whole shelf seen — reshuffle and go again
            drawn.removeAll()
            bag = pool
        }
        bag.shuffle()
    }

    private func draw() -> Tool? {
        if bag.isEmpty { refillBag() }
        guard let t = bag.popLast() else { return nil }
        drawn.insert(t.n)
        UserDefaults.standard.set(Array(drawn), forKey: "drawn")
        return t
    }

    var seenCount: Int { drawn.count }

    // MARK: The pull

    /// Reels stop LEFT to RIGHT, not together. Three things landing at once reads as a
    /// loading spinner finishing; three things landing in sequence reads as a slot
    /// machine, and the last reel is the only one anybody is actually watching.
    func pull() {
        guard !spinning, !pool.isEmpty, let target = draw() else { return }
        spinning = true
        copied = false
        current = nil

        let stops = [14, 19, 25]            // per-reel stop tick
        let total = stops.max()!
        var t = 0.0
        var gap = 0.035

        for tick in 0...total {
            let now = t
            DispatchQueue.main.asyncAfter(deadline: .now() + now) { [weak self] in
                guard let self else { return }
                self.reels = (0..<3).map { i in
                    tick >= stops[i] ? target.e : (self.pool.randomElement()?.e ?? "🎰")
                }
                if tick == total {
                    self.current = target
                    self.spinning = false
                }
            }
            t += gap
            gap *= 1.13                     // decelerate, then overshoot into the stop
        }
    }

    func copyForAI() {
        guard let t = current else { return }
        let msg = "Please vet and install \(t.n) for me: \(t.u)"
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(msg, forType: .string)
        copied = true
    }

    func open() {
        guard let t = current, let url = URL(string: t.u) else { return }
        NSWorkspace.shared.open(url)
    }
}

// MARK: - View

struct SlotView: View {
    @ObservedObject var shelf: Shelf

    var body: some View {
        VStack(spacing: 0) {
            header
            Divider().overlay(Color(hex: 0x3a3222))
            machine
            categoryPicker
            if let t = shelf.current { card(t) } else { placeholder }
            Divider().overlay(Color(hex: 0x3a3222))
            footer
        }
        .frame(width: 340)
        .background(Color(hex: 0x0e0d0b))
    }

    private var header: some View {
        HStack {
            Text("🎰").font(.system(size: 13))
            Text("AI SLOT TOOL FINDER")
                .font(.system(size: 11, weight: .bold, design: .monospaced))
                .foregroundColor(Color(hex: 0xFFD700))
            Spacer()
            Text("\(shelf.seenCount)/\(shelf.pool.count)")
                .font(.system(size: 10, design: .monospaced))
                .foregroundColor(Color(hex: 0x8a8478))
        }
        .padding(.horizontal, 14)
        .padding(.top, 14).padding(.bottom, 10)   // the popover crowds its own top edge
    }

    private var machine: some View {
        HStack(spacing: 12) {
            ZStack {
                HStack(spacing: 6) {
                    ForEach(0..<3, id: \.self) { i in
                        Text(shelf.reels[i].isEmpty ? "🎰" : shelf.reels[i])
                            .font(.system(size: 32))
                            .frame(width: 62, height: 78)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(LinearGradient(
                                        colors: [Color(hex: 0x0b0a09), Color(hex: 0x211d17), Color(hex: 0x0b0a09)],
                                        startPoint: .top, endPoint: .bottom))
                            )
                            .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color(hex: 0x3a3222), lineWidth: 1))
                    }
                }
                // The payline. Without it the three cells read as three icons in boxes
                // rather than one machine that has landed on something.
                Rectangle()
                    .fill(Color(hex: 0xFFD700).opacity(shelf.spinning ? 0.10 : 0.30))
                    .frame(height: 1)
                    .padding(.horizontal, 4)
                    .animation(.easeOut(duration: 0.25), value: shelf.spinning)
            }
            lever
        }
        .padding(.top, 6)
        .padding(.bottom, 14)
    }

    /// A ball riding ON a rod, starting at the top and dropping while the reels run.
    ///
    /// The first version stacked the ball ABOVE the rod in a VStack and then offset it
    /// downward, so it rendered as a glowing bead impaled through the middle of a stick —
    /// not a lever, and the first thing YL pointed at. A ZStack puts the ball on the rod
    /// where a lever's ball actually lives, and the travel stays inside the housing.
    private var lever: some View {
        ZStack(alignment: .top) {
            Capsule()
                .fill(Color(hex: 0x2a2419))
                .overlay(Capsule().stroke(Color(hex: 0x3a3222), lineWidth: 1))
                .frame(width: 6, height: 78)

            Circle()
                .fill(RadialGradient(colors: [Color(hex: 0xFFE873), Color(hex: 0xC9A227)],
                                     center: .topLeading, startRadius: 1, endRadius: 24))
                .overlay(Circle().stroke(Color(hex: 0x8a6a00), lineWidth: 0.5))
                .frame(width: 22, height: 22)
                .shadow(color: Color(hex: 0xFFD700).opacity(0.35), radius: 4)
                .offset(y: shelf.spinning ? 56 : 0)
                .animation(.spring(response: 0.30, dampingFraction: 0.6), value: shelf.spinning)
        }
        .frame(width: 24, height: 78)
        .contentShape(Rectangle())
        .onTapGesture { shelf.pull() }
        .help("Pull")
    }

    private var categoryPicker: some View {
        HStack(spacing: 4) {
            ForEach(CATEGORIES, id: \.self) { c in
                Text(c)
                    .font(.system(size: 9, weight: shelf.category == c ? .bold : .regular, design: .monospaced))
                    .foregroundColor(shelf.category == c ? Color(hex: 0x0e0d0b) : Color(hex: 0x8a8478))
                    .padding(.horizontal, 7).padding(.vertical, 3)
                    .background(
                        Capsule().fill(shelf.category == c ? Color(hex: 0xFFD700) : Color.clear)
                    )
                    .onTapGesture { shelf.category = c }
            }
        }
        .padding(.bottom, 12)
    }

    private var placeholder: some View {
        Text("pull the lever")
            .font(.system(size: 11, design: .monospaced))
            .foregroundColor(Color(hex: 0x8a8478))
            .frame(maxWidth: .infinity)
            .padding(.vertical, 26)
    }

    private func card(_ t: Tool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text(t.e).font(.system(size: 20))
                Text(t.n).font(.system(size: 14, weight: .bold)).foregroundColor(Color(hex: 0xe8e3d6))
                Spacer()
                Text(t.c)
                    .font(.system(size: 9, design: .monospaced))
                    .foregroundColor(Color(hex: 0x8a6a00))
            }
            Text(t.d)
                .font(.system(size: 11))
                .foregroundColor(Color(hex: 0x8a8478))
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: 6) {
                btn("Open", filled: true) { shelf.open() }
                btn(shelf.copied ? "COPIED — PASTE TO YOUR AI" : "Copy for AI") { shelf.copyForAI() }
            }
            .padding(.top, 2)
        }
        .padding(.horizontal, 14).padding(.bottom, 14)
    }

    private func btn(_ label: String, filled: Bool = false, _ action: @escaping () -> Void) -> some View {
        Text(label)
            .font(.system(size: 10, weight: .semibold, design: .monospaced))
            .foregroundColor(filled ? Color(hex: 0x0e0d0b) : Color(hex: 0xFFD700))
            .padding(.horizontal, 10).padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 6)
                    .fill(filled ? Color(hex: 0xFFD700) : Color.clear)
                    .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color(hex: 0x8a6a00), lineWidth: filled ? 0 : 1))
            )
            .onTapGesture(perform: action)
    }

    private var footer: some View {
        HStack {
            Text("browse all \(shelf.tools.count)")
                .font(.system(size: 9, design: .monospaced))
                .foregroundColor(Color(hex: 0x8a8478))
                .onTapGesture {
                    NSWorkspace.shared.open(URL(string: "https://cuttingthru18-cmd.github.io/ai-slot-tool-finder/")!)
                }
            Spacer()
            Text("quit")
                .font(.system(size: 9, design: .monospaced))
                .foregroundColor(Color(hex: 0x8a8478))
                .onTapGesture { NSApp.terminate(nil) }
        }
        .padding(.horizontal, 14).padding(.vertical, 8)
    }
}

extension Color {
    init(hex: UInt32) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xff) / 255,
                  green: Double((hex >> 8) & 0xff) / 255,
                  blue: Double(hex & 0xff) / 255,
                  opacity: 1)
    }
}

// MARK: - App

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private let popover = NSPopover()
    private let shelf = Shelf()

    func applicationDidFinishLaunching(_ n: Notification) {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.title = "🎰"
        statusItem.button?.action = #selector(toggle)
        statusItem.button?.target = self

        popover.behavior = .transient          // click away and it closes, like a menu
        popover.contentViewController = NSHostingController(rootView: SlotView(shelf: shelf))
    }

    @objc private func toggle() {
        guard let button = statusItem.button else { return }
        if popover.isShown {
            popover.performClose(nil)
        } else {
            shelf.refresh()
            popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
            popover.contentViewController?.view.window?.makeKey()
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory)            // menu bar only — no Dock icon, no window
app.run()
