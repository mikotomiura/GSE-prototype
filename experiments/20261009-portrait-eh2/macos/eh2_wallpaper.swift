// EH2 of the portrait (macOS): machine checks of the desktop picture API (NSWorkspace).
//
// What it does, with placeholder images only:
//   1. saves the current desktop picture of every screen (the paths to a temporary file, the options
//      in memory; neither goes to the results) and refuses to run when a screen's picture is not a
//      readable file (for example a moving aerial wallpaper, which this API cannot restore) unless
//      --force is given
//   2. sets the picture per screen, reads it back and times each call
//   3. measures the CPU time and resident memory of this process and of WallpaperAgent (or Dock)
//      while idle and while updating every few seconds
//   4. optionally (--manual) asks the operator to check Spaces and a screen share
//   5. always restores the saved pictures and reads them back
//
// NSWorkspace sets the picture of the current Space only. The script therefore changes and restores
// the current Space of each screen; other Spaces are not touched (except during the manual check,
// where the operator moves between Spaces and the script reads them).
//
// The results file holds no machine name, user name or file path: only screen sizes, timings,
// booleans and counts.
//
// Usage (needs the Xcode command line tools):
//   swift eh2_wallpaper.swift [--quick] [--manual] [--force] [--dry-run]
//     --quick    3 updates, 10 s idle, 10 s updating (smoke test, about 1 minute)
//     --dry-run  never sets the picture: lists the screens, makes the images, reads the current
//                pictures, samples CPU for a few seconds and writes the results
//     default    30 updates, 300 s idle, 300 s updating every 10 s (about 12 minutes)
//
// Do not run it on a machine that is running a measurement: the CPU figures would disturb each other.

import AppKit
import CryptoKit
import Foundation
import ImageIO

let args = Set(CommandLine.arguments.dropFirst())
let quick = args.contains("--quick")
let manual = args.contains("--manual")
let force = args.contains("--force")
let dryRun = args.contains("--dry-run")
let nUpdates = quick ? 3 : 30
let idleS = quick ? 10 : 300
let busyS = quick ? 10 : 300
let busyEvery = quick ? 3 : 10

let here = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
let resultsDir = here.deletingLastPathComponent().appendingPathComponent("results")
try? FileManager.default.createDirectory(at: resultsDir, withIntermediateDirectories: true)
let stampFmt = DateFormatter()
stampFmt.dateFormat = "yyyyMMdd-HHmmss"
let stamp = stampFmt.string(from: Date())
let isoFmt = ISO8601DateFormatter()
let work = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("gse-eh2-\(stamp)")
try FileManager.default.createDirectory(at: work, withIntermediateDirectories: true)
let restoreFile = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("gse-eh2-restore-\(stamp).json")

var res: [String: Any] = [
    "os": "macos",
    "os_version": ProcessInfo.processInfo.operatingSystemVersionString,
    "mode": dryRun ? "dryrun" : (quick ? "quick" : "full"),
    "started": isoFmt.string(from: Date()),
]

// "x ?? NSNull()" does not type-check when x is Double? or String?; this does.
func orNull(_ x: Any?) -> Any { x ?? NSNull() }

// /var and /private/var name the same folder; compare resolved paths.
func samePath(_ a: URL?, _ b: URL?) -> Bool {
    guard let a = a, let b = b else { return false }
    return a.resolvingSymlinksInPath().standardizedFileURL.path == b.resolvingSymlinksInPath().standardizedFileURL.path
}

func median(_ xs: [Double]) -> Double? {
    if xs.isEmpty { return nil }
    let s = xs.sorted()
    return s.count % 2 == 1 ? s[s.count / 2] : (s[s.count / 2 - 1] + s[s.count / 2]) / 2
}

func pct(_ xs: [Double], _ p: Double) -> Double? {
    if xs.isEmpty { return nil }
    let s = xs.sorted()
    let i = min(s.count - 1, max(0, Int((p / 100.0 * Double(s.count)).rounded(.up)) - 1))
    return s[i]
}

func nowMs() -> Double { Double(DispatchTime.now().uptimeNanoseconds) / 1e6 }

func run(_ path: String, _ arguments: [String]) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: path)
    p.arguments = arguments
    let pipe = Pipe()
    p.standardOutput = pipe
    p.standardError = Pipe()
    do { try p.run() } catch { return "" }
    p.waitUntilExit()
    return String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
}

// "[[dd-]hh:]mm:ss.ss" -> seconds
func parseCpuTime(_ s: String) -> Double? {
    var rest = s.trimmingCharacters(in: .whitespaces)
    var days = 0.0
    if let dash = rest.firstIndex(of: "-") {
        days = Double(rest[..<dash]) ?? 0
        rest = String(rest[rest.index(after: dash)...])
    }
    let parts = rest.split(separator: ":").map { Double($0) }
    if parts.contains(where: { $0 == nil }) || parts.isEmpty { return nil }
    var total = 0.0
    for v in parts { total = total * 60 + v! }
    return total + days * 86400
}

func procSample(_ name: String) -> [String: Any] {
    let pids = run("/usr/bin/pgrep", ["-x", name]).split(separator: "\n").map(String.init)
    if pids.isEmpty { return ["cpu_s": NSNull(), "rss_mb": NSNull(), "n": 0] }
    var cpu = 0.0
    var rss = 0.0
    var ok = true
    for pid in pids {
        let line = run("/bin/ps", ["-o", "time=,rss=", "-p", pid]).trimmingCharacters(in: .whitespacesAndNewlines)
        let f = line.split(separator: " ", omittingEmptySubsequences: true)
        if f.count >= 2, let t = parseCpuTime(String(f[0])), let r = Double(f[1]) {
            cpu += t
            rss += r / 1024
        } else { ok = false }
    }
    return ["cpu_s": ok ? (cpu as Any) : NSNull(), "rss_mb": rss, "n": pids.count]
}

func selfSample() -> [String: Any] {
    var ru = rusage()
    getrusage(RUSAGE_SELF, &ru)
    let cpu = Double(ru.ru_utime.tv_sec) + Double(ru.ru_utime.tv_usec) / 1e6
        + Double(ru.ru_stime.tv_sec) + Double(ru.ru_stime.tv_usec) / 1e6
    let rssLine = run("/bin/ps", ["-o", "rss=", "-p", String(ProcessInfo.processInfo.processIdentifier)])
    let rss = (Double(rssLine.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0) / 1024
    return ["cpu_s": cpu, "rss_mb": rss, "n": 1]
}

let agentName = run("/usr/bin/pgrep", ["-x", "WallpaperAgent"]).isEmpty ? "Dock" : "WallpaperAgent"

func samples() -> [String: [String: Any]] {
    ["self": selfSample(), agentName: procSample(agentName)]
}

func delta(_ a: [String: [String: Any]], _ b: [String: [String: Any]]) -> [String: Any] {
    var out: [String: Any] = [:]
    for (k, va) in a {
        let vb = b[k] ?? [:]
        var d: Any = NSNull()
        if let x = va["cpu_s"] as? Double, let y = vb["cpu_s"] as? Double { d = ((y - x) * 1000).rounded() / 1000 }
        out[k] = ["cpu_s": d, "rss_mb_start": orNull(va["rss_mb"]), "rss_mb_end": orNull(vb["rss_mb"])] as [String: Any]
    }
    return out
}

func makeImage(_ url: URL, _ w: Int, _ h: Int, _ variant: Int) throws {
    let cs = CGColorSpaceCreateDeviceRGB()
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0, space: cs,
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
        throw NSError(domain: "eh2", code: 1)
    }
    ctx.setFillColor(CGColor(red: 235 / 255, green: 232 / 255, blue: 225 / 255, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    let step = max(8, w / 24)
    if variant == 0 {
        ctx.setFillColor(CGColor(red: 120 / 255, green: 150 / 255, blue: 190 / 255, alpha: 1))
    } else {
        ctx.setFillColor(CGColor(red: 200 / 255, green: 140 / 255, blue: 170 / 255, alpha: 1))
    }
    var x = 0
    while x < w {
        if variant == 0 {
            ctx.fill(CGRect(x: x, y: 0, width: step, height: h))
        } else {
            ctx.fillEllipse(in: CGRect(x: x, y: h / 3, width: step, height: step))
        }
        x += step * 2
    }
    guard let img = ctx.makeImage(),
          let dest = CGImageDestinationCreateWithURL(url as CFURL, "public.png" as CFString, 1, nil) else {
        throw NSError(domain: "eh2", code: 2)
    }
    CGImageDestinationAddImage(dest, img, nil)
    if !CGImageDestinationFinalize(dest) { throw NSError(domain: "eh2", code: 3) }
}

func askYesNo(_ prompt: String) -> String {
    while true {
        print("\(prompt) [y/n/u(unknown)] ", terminator: "")
        let r = (readLine() ?? "").trimmingCharacters(in: .whitespaces).lowercased()
        switch r {
        case "y": return "yes"
        case "n": return "no"
        case "u": return "unknown"
        default: continue
        }
    }
}

func waitEnter(_ prompt: String) {
    print(prompt)
    _ = readLine()
}

let ws = NSWorkspace.shared
let screens = NSScreen.screens
struct Orig { let screen: NSScreen; let url: URL?; let options: [NSWorkspace.DesktopImageOptionKey: Any]; let w: Int; let h: Int; let sha256: String? }

// the hash confirms after the restore that the original file itself was not overwritten
func fileHash(_ url: URL?) -> String? {
    guard let u = url, let data = try? Data(contentsOf: u) else { return nil }
    return SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}
var orig: [Orig] = []
var screenInfo: [[String: Any]] = []
for (i, s) in screens.enumerated() {
    let scale = s.backingScaleFactor
    let w = Int(s.frame.width * scale)
    let h = Int(s.frame.height * scale)
    let u = ws.desktopImageURL(for: s)
    orig.append(Orig(screen: s, url: u, options: ws.desktopImageOptions(for: s) ?? [:], w: w, h: h, sha256: fileHash(u)))
    screenInfo.append(["index": i, "width_px": w, "height_px": h, "scale": Double(scale)])
}
res["screens"] = screenInfo as [[String: Any]]
res["wallpaper_process"] = agentName
let exists = orig.map { o -> Bool in
    guard let u = o.url, u.isFileURL else { return false }
    return FileManager.default.isReadableFile(atPath: u.path)
}
res["original_readable_file"] = exists

func writeResults(_ suffix: String) {
    res["finished"] = isoFmt.string(from: Date())
    let out = resultsDir.appendingPathComponent("eh2-macos-\(stamp)\(suffix).json")
    if let data = try? JSONSerialization.data(withJSONObject: res, options: [.prettyPrinted, .sortedKeys]) {
        try? data.write(to: out)
    }
    try? FileManager.default.removeItem(at: work)
    print("Results: \(out.path)")
}

if dryRun {
    var lat: [Double] = []
    for (i, o) in orig.enumerated() {
        let u = work.appendingPathComponent("s\(i)-a.png")
        try makeImage(u, o.w, o.h, 0)
        let attrs = try? FileManager.default.attributesOfItem(atPath: u.path)
        res["dryrun_image_bytes"] = orNull(attrs?[.size])
        let t0 = nowMs()
        _ = ws.desktopImageURL(for: o.screen)
        lat.append(nowMs() - t0)
    }
    res["dryrun_get_latency_ms_median"] = orNull(median(lat))
    let s0 = samples()
    Thread.sleep(forTimeInterval: 3)
    res["dryrun_cpu"] = delta(s0, samples())
    print("Dry run (the picture was not changed).")
    writeResults("-dryrun")
    exit(0)
}

if !force && exists.contains(false) {
    print("A screen's picture is not a readable file (for example a moving aerial wallpaper).")
    print("It cannot be restored through this API. Switch to a picture first, or pass --force.")
    exit(3)
}

// The restore file is the only place that holds the original paths. It stays in the temporary folder.
let restoreJSON: [[String: Any]] = orig.enumerated().map { i, o in ["index": i, "url": orNull(o.url?.path)] as [String: Any] }
if let data = try? JSONSerialization.data(withJSONObject: restoreJSON, options: [.prettyPrinted]) {
    try? data.write(to: restoreFile)
}
print("Saved the original pictures to \(restoreFile.path)")

var restoredOnce = false

func restore() {
    if restoredOnce { return }
    restoredOnce = true
    var restored: [Any] = []
    for o in orig {
        guard let u = o.url else { restored.append("original_missing"); continue }
        do {
            try ws.setDesktopImageURL(u, for: o.screen, options: o.options)
            restored.append(samePath(ws.desktopImageURL(for: o.screen), u) && fileHash(u) == o.sha256)
        } catch { restored.append(false) }
    }
    res["restored"] = restored
    let allOk = restored.allSatisfy { ($0 as? Bool) == true }
    print("Restored: \(restored)")
    if allOk {
        try? FileManager.default.removeItem(at: restoreFile)
    } else {
        print("Restore was not confirmed. The original paths are kept in \(restoreFile.path) (see README).")
    }
}

// Ctrl+C or a termination request still restores the pictures and writes the results.
signal(SIGINT, SIG_IGN)
signal(SIGTERM, SIG_IGN)
var signalSources: [DispatchSourceSignal] = []
for sig in [SIGINT, SIGTERM] {
    let src = DispatchSource.makeSignalSource(signal: sig, queue: DispatchQueue.global())
    src.setEventHandler {
        print("\nInterrupted: restoring the original pictures.")
        res["interrupted"] = true
        restore()
        writeResults("")
        exit(130)
    }
    src.resume()
    signalSources.append(src)
}

do {
    var imgs: [[URL]] = []
    for (i, o) in orig.enumerated() {
        let a = work.appendingPathComponent("s\(i)-a.png")
        let b = work.appendingPathComponent("s\(i)-b.png")
        try makeImage(a, o.w, o.h, 0)
        try makeImage(b, o.w, o.h, 1)
        imgs.append([a, b])
    }
    let opts: [NSWorkspace.DesktopImageOptionKey: Any] = [.imageScaling: NSNumber(value: NSImageScaling.scaleProportionallyUpOrDown.rawValue), .allowClipping: true]

    // 1. Per-screen set and read back
    var lat: [Double] = []
    var okN = 0
    var tot = 0
    for k in 0..<nUpdates {
        for (i, o) in orig.enumerated() {
            let u = imgs[i][k % 2]
            let t0 = nowMs()
            try ws.setDesktopImageURL(u, for: o.screen, options: opts)
            lat.append(nowMs() - t0)
            tot += 1
            if samePath(ws.desktopImageURL(for: o.screen), u) { okN += 1 }
        }
        Thread.sleep(forTimeInterval: 0.3)
    }
    res["per_screen"] = ["calls": tot, "readback_ok": okN, "latency_ms_median": orNull(median(lat)),
                         "latency_ms_p95": orNull(pct(lat, 95)), "latency_ms_max": orNull(lat.max())] as [String: Any]

    // 2. Distinct pictures per screen
    if orig.count >= 2 {
        for (i, o) in orig.enumerated() { try ws.setDesktopImageURL(imgs[i][i % 2], for: o.screen, options: opts) }
        res["distinct_per_screen_readback_ok"] = orig.enumerated().allSatisfy { i, o in samePath(ws.desktopImageURL(for: o.screen), imgs[i][i % 2]) }
    } else {
        res["distinct_per_screen_readback_ok"] = "single_screen"
    }

    // 3. CPU and memory: idle, then updating
    let s0 = samples()
    Thread.sleep(forTimeInterval: TimeInterval(idleS))
    let s1 = samples()
    var updates = 0
    let tStart = nowMs()
    while nowMs() - tStart < Double(busyS) * 1000 {
        for (i, o) in orig.enumerated() { try ws.setDesktopImageURL(imgs[i][updates % 2], for: o.screen, options: opts) }
        updates += 1
        Thread.sleep(forTimeInterval: TimeInterval(busyEvery))
    }
    let s2 = samples()
    res["cpu"] = ["idle_s": idleS, "busy_s": busyS, "busy_every_s": busyEvery, "busy_updates": updates,
                  "idle": delta(s0, s1), "busy": delta(s1, s2)] as [String: Any]

    // 4. Optional manual checks
    if manual {
        waitEnter("\nManual check A: Spaces. Open Mission Control, add a second Space, come back to the first one, then press Enter.")
        let o0 = orig[0]
        try ws.setDesktopImageURL(imgs[0][0], for: o0.screen, options: opts)
        waitEnter("The striped image is now set on this Space. Switch to the second Space (Ctrl+Right) and press Enter.")
        res["manual_spaces"] = [
            "readback_matches_on_other_space": samePath(ws.desktopImageURL(for: o0.screen), imgs[0][0]),
            "striped_image_visible_on_other_space": askYesNo("Do you see the striped image on the second Space?"),
        ] as [String: Any]
        waitEnter("Switch back to the first Space, then press Enter.")
        // Everything after this (the share check and the restore) acts on the current Space.
        var back = true
        while !samePath(ws.desktopImageURL(for: o0.screen), imgs[0][0]) {
            print("The picture here is not the striped image, so this may not be the first Space. Switch back and press Enter, or type skip: ", terminator: "")
            if (readLine() ?? "").trimmingCharacters(in: .whitespaces).lowercased() == "skip" { back = false; break }
        }
        res["manual_back_on_first_space_confirmed"] = back
        waitEnter("\nManual check B: start a screen share or a screen recording that shows the desktop, then press Enter. Three updates follow, 5 s apart.")
        for k in 0..<3 {
            try ws.setDesktopImageURL(imgs[0][(k + 1) % 2], for: o0.screen, options: opts)
            Thread.sleep(forTimeInterval: 5)
        }
        res["manual_screen_share"] = [
            "change_visible_in_share": askYesNo("Was the change of picture visible in the share or recording?"),
            "flicker_or_flash": askYesNo("Was there a flicker or a flash on the screen when the picture changed?"),
        ] as [String: Any]
    }
} catch {
    // only the domain and code go to the results: the description can carry file paths
    let ns = error as NSError
    res["error"] = ["domain": ns.domain, "code": ns.code] as [String: Any]
    print("Error: \(error)")
}
restore()
writeResults("")
