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
//   5. always restores the saved pictures and reads them back (Ctrl+C included), except while the
//      operator may be on the second Space of the manual check, where a restore would act on the wrong
//      Space; then it leaves the restore file and the placeholder images for a manual restore
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
    if pids.isEmpty { return ["cpu_s": NSNull(), "rss_mb": NSNull(), "n": 0, "pids": ""] }
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
    // the pid set lets delta() reject a span in which a process was restarted
    return ["cpu_s": ok ? (cpu as Any) : NSNull(), "rss_mb": rss, "n": pids.count, "pids": pids.sorted().joined(separator: ",")]
}

func selfSample() -> [String: Any] {
    var ru = rusage()
    getrusage(RUSAGE_SELF, &ru)
    let cpu = Double(ru.ru_utime.tv_sec) + Double(ru.ru_utime.tv_usec) / 1e6
        + Double(ru.ru_stime.tv_sec) + Double(ru.ru_stime.tv_usec) / 1e6
    let rssLine = run("/bin/ps", ["-o", "rss=", "-p", String(ProcessInfo.processInfo.processIdentifier)])
    let rss = (Double(rssLine.trimmingCharacters(in: .whitespacesAndNewlines)) ?? 0) / 1024
    return ["cpu_s": cpu, "rss_mb": rss, "n": 1, "pids": String(ProcessInfo.processInfo.processIdentifier)]
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
        let changed = (va["pids"] as? String) != (vb["pids"] as? String)
        if !changed, let x = va["cpu_s"] as? Double, let y = vb["cpu_s"] as? Double { d = ((y - x) * 1000).rounded() / 1000 }
        // the pids themselves do not go to the results
        out[k] = ["cpu_s": d, "pids_changed": changed, "rss_mb_start": orNull(va["rss_mb"]),
                  "rss_mb_end": orNull(vb["rss_mb"])] as [String: Any]
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
        guard let line = readLine() else { return "unknown" }  // end of input
        let r = line.trimmingCharacters(in: .whitespaces).lowercased()
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
    do {
        let data = try JSONSerialization.data(withJSONObject: res, options: [.prettyPrinted, .sortedKeys])
        try data.write(to: out)
        print("Results: \(out.path)")
    } catch {
        print("Could not write the results: \(error)")
    }
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
    let t0 = nowMs()
    Thread.sleep(forTimeInterval: 3)
    res["dryrun_cpu"] = delta(s0, samples())
    res["dryrun_elapsed_s"] = (nowMs() - t0) / 1000
    print("Dry run (the picture was not changed).")
    writeResults("-dryrun")
    try? FileManager.default.removeItem(at: work)
    exit(0)
}

if !force && exists.contains(false) {
    print("A screen's picture is not a readable file (for example a moving aerial wallpaper).")
    print("It cannot be restored through this API. Switch to a picture first, or pass --force.")
    res["aborted"] = "original_not_restorable"
    writeResults("-aborted")
    try? FileManager.default.removeItem(at: work)
    exit(3)
}

// The restore file is the only place that holds the original paths. It stays in the temporary folder.
// Nothing is changed unless it was written.
let restoreJSON: [[String: Any]] = orig.enumerated().map { i, o in ["index": i, "url": orNull(o.url?.path)] as [String: Any] }
do {
    let data = try JSONSerialization.data(withJSONObject: restoreJSON, options: [.prettyPrinted])
    try data.write(to: restoreFile)
} catch {
    print("Could not save the original pictures (\(error)). Nothing was changed.")
    res["aborted"] = "restore_file_not_written"
    writeResults("-aborted")
    try? FileManager.default.removeItem(at: work)
    exit(4)
}
print("Saved the original pictures to \(restoreFile.path)")

// ---------------------------------------------------------------------------
// Interruption: Ctrl+C or a termination request only raises a flag. The main flow stops at its next
// step and restores in one place. While the main flow waits for the operator (readLine) it cannot
// change the picture, so the handler restores itself in that case.
// ---------------------------------------------------------------------------
struct Interrupted: Error {}
let stateLock = NSLock()
var interrupted = false
var inPrompt = false
var onOtherSpace = false  // the operator was sent to the second Space and has not been confirmed back
var restoreTargetUnconfirmed = false
var restoredOnce = false

func isInterrupted() -> Bool {
    stateLock.lock()
    defer { stateLock.unlock() }
    return interrupted
}

func nap(_ seconds: Double) throws {
    let end = nowMs() + seconds * 1000
    while nowMs() < end {
        if isInterrupted() { throw Interrupted() }
        Thread.sleep(forTimeInterval: min(0.1, max(0, (end - nowMs()) / 1000)))
    }
    if isInterrupted() { throw Interrupted() }
}

func setPicture(_ u: URL, _ s: NSScreen, _ o: [NSWorkspace.DesktopImageOptionKey: Any]) throws {
    if isInterrupted() { throw Interrupted() }
    try ws.setDesktopImageURL(u, for: s, options: o)
}

// sendsAway: this prompt sends the operator to another Space (or may find them there). The flag is
// raised in the same critical section that checks for an interruption, so an interruption that came
// before the prompt was shown still restores normally.
func guarded<T>(sendsAway: Bool = false, _ f: () -> T) throws -> T {
    stateLock.lock()
    inPrompt = true
    let before = interrupted
    if !before && sendsAway { onOtherSpace = true }
    stateLock.unlock()
    if before {
        stateLock.lock(); inPrompt = false; stateLock.unlock()
        throw Interrupted()
    }
    let v = f()
    stateLock.lock(); inPrompt = false; stateLock.unlock()
    if isInterrupted() { throw Interrupted() }
    return v
}

func restore() {
    stateLock.lock()
    if restoredOnce { stateLock.unlock(); return }
    restoredOnce = true
    let other = onOtherSpace
    stateLock.unlock()
    if other {
        // restoring now would act on the second Space and leave the first one with the placeholder
        res["restored"] = "not_attempted_on_other_space"
        res["restore_target_unconfirmed"] = true
        print("Not restored: this may be the second Space. Go back to the first Space and pick your picture again")
        print("(the original paths are in \(restoreFile.path), the placeholder images in \(work.path); see README).")
        return
    }
    var restored: [Any] = []
    for o in orig {
        guard let u = o.url else { restored.append("original_missing"); continue }
        do {
            try ws.setDesktopImageURL(u, for: o.screen, options: o.options)
            restored.append(samePath(ws.desktopImageURL(for: o.screen), u) && fileHash(u) == o.sha256)
        } catch { restored.append(false) }
    }
    res["restored"] = restored
    res["restore_target_unconfirmed"] = restoreTargetUnconfirmed
    let allOk = restored.allSatisfy { ($0 as? Bool) == true }
    print("Restored: \(restored)")
    if allOk && !restoreTargetUnconfirmed {
        try? FileManager.default.removeItem(at: restoreFile)
        try? FileManager.default.removeItem(at: work)
    } else {
        // keep the placeholder images too: a picture may still point at them
        print("Restore was not confirmed. The original paths are kept in \(restoreFile.path) and the placeholder images in \(work.path) (see README).")
    }
}

// One exit path: whoever comes second (the handler or the main flow) waits here until the first one
// has restored, written the results and exited. The lock is never released on purpose.
let finishLock = NSLock()

func finish(_ code: Int32, interruptedRun: Bool = false) -> Never {
    finishLock.lock()
    if interruptedRun { res["interrupted"] = true }
    restore()
    writeResults("")
    exit(code)
}

signal(SIGINT, SIG_IGN)
signal(SIGTERM, SIG_IGN)
var signalSources: [DispatchSourceSignal] = []
for sig in [SIGINT, SIGTERM] {
    let src = DispatchSource.makeSignalSource(signal: sig, queue: DispatchQueue.global())
    src.setEventHandler {
        stateLock.lock()
        interrupted = true
        let waiting = inPrompt
        stateLock.unlock()
        print("\nInterrupted: restoring the original pictures.")
        if waiting { finish(130, interruptedRun: true) }
    }
    src.resume()
    signalSources.append(src)
}

var exitCode: Int32 = 0
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
            try setPicture(u, o.screen, opts)
            lat.append(nowMs() - t0)
            tot += 1
            if samePath(ws.desktopImageURL(for: o.screen), u) { okN += 1 }
        }
        try nap(0.3)
    }
    res["per_screen"] = ["calls": tot, "readback_ok": okN, "latency_ms_median": orNull(median(lat)),
                         "latency_ms_p95": orNull(pct(lat, 95)), "latency_ms_max": orNull(lat.max())] as [String: Any]

    // 2. Distinct pictures per screen
    if orig.count >= 2 {
        for (i, o) in orig.enumerated() { try setPicture(imgs[i][i % 2], o.screen, opts) }
        res["distinct_per_screen_readback_ok"] = orig.enumerated().allSatisfy { i, o in samePath(ws.desktopImageURL(for: o.screen), imgs[i][i % 2]) }
    } else {
        res["distinct_per_screen_readback_ok"] = "single_screen"
    }

    // 3. CPU and memory: idle, then updating (elapsed times are measured, not assumed)
    let s0 = samples()
    let tIdle = nowMs()
    try nap(Double(idleS))
    let s1 = samples()
    let idleElapsed = (nowMs() - tIdle) / 1000
    var updates = 0
    let tStart = nowMs()
    while nowMs() - tStart < Double(busyS) * 1000 {
        for (i, o) in orig.enumerated() { try setPicture(imgs[i][updates % 2], o.screen, opts) }
        updates += 1
        try nap(Double(busyEvery))
    }
    let s2 = samples()
    let lastSetFirst = imgs[0][(updates - 1) % 2]  // what the first screen of this Space shows now
    res["cpu"] = ["idle_s": idleS, "busy_s": busyS, "busy_every_s": busyEvery, "busy_updates": updates,
                  "idle_elapsed_s": idleElapsed, "busy_elapsed_s": (nowMs() - tStart) / 1000,
                  "idle": delta(s0, s1), "busy": delta(s1, s2)] as [String: Any]

    // 4. Optional manual checks
    if manual {
        let o0 = orig[0]
        // Back on the first Space = the readback shows what this script set there AND the operator says so
        // (the readback alone cannot tell Spaces apart if the getter ignores them).
        func confirmFirstSpace(expect: URL) throws -> Bool {
            while true {
                if samePath(ws.desktopImageURL(for: o0.screen), expect) {
                    let yes = try guarded { askYesNo("Are you on the first Space (the one you started on) now?") }
                    if yes == "yes" { return true }
                }
                let ans = try guarded { () -> String in
                    print("Switch to the first Space and press Enter, or type skip: ", terminator: "")
                    return (readLine() ?? "skip").trimmingCharacters(in: .whitespaces).lowercased()
                }
                if ans == "skip" { return false }
            }
        }
        // From the first prompt on, the operator may be on another Space until confirmed back.
        try guarded(sendsAway: true) { waitEnter("\nManual check A: Spaces. Open Mission Control, add a second Space, come back to the first one, then press Enter.") }
        let startOk = try confirmFirstSpace(expect: lastSetFirst)
        if !startOk {
            res["manual_spaces"] = "skipped_not_on_first_space"
            res["manual_screen_share"] = "skipped_not_on_first_space"
            restoreTargetUnconfirmed = true
            finish(0)
        }
        stateLock.lock(); onOtherSpace = false; stateLock.unlock()
        try setPicture(imgs[0][0], o0.screen, opts)
        try guarded(sendsAway: true) { waitEnter("The striped image is now set on this Space. Switch to the second Space (Ctrl+Right) and press Enter.") }
        let readbackOther = samePath(ws.desktopImageURL(for: o0.screen), imgs[0][0])
        let visibleOther = try guarded { askYesNo("Do you see the striped image on the second Space?") }
        res["manual_spaces"] = ["readback_matches_on_other_space": readbackOther,
                                "striped_image_visible_on_other_space": visibleOther] as [String: Any]
        try guarded { waitEnter("Switch back to the first Space, then press Enter.") }
        // Everything after this (the share check and the restore) acts on the current Space.
        let back = try confirmFirstSpace(expect: imgs[0][0])
        res["manual_back_on_first_space_confirmed"] = back
        if back {
            stateLock.lock(); onOtherSpace = false; stateLock.unlock()
            try guarded { waitEnter("\nManual check B: start a screen share or a screen recording that shows the desktop, then press Enter. Three updates follow, 5 s apart.") }
            for k in 0..<3 {
                try setPicture(imgs[0][(k + 1) % 2], o0.screen, opts)
                try nap(5)
            }
            let shareVisible = try guarded { askYesNo("Was the change of picture visible in the share or recording?") }
            let flicker = try guarded { askYesNo("Was there a flicker or a flash on the screen when the picture changed?") }
            res["manual_screen_share"] = ["change_visible_in_share": shareVisible, "flicker_or_flash": flicker] as [String: Any]
        } else {
            // not confirmed on the first Space: no further change, and the automatic restore is not trusted
            res["manual_screen_share"] = "skipped_not_on_first_space"
            restoreTargetUnconfirmed = true
        }
    }
} catch is Interrupted {
    finish(130, interruptedRun: true)
} catch {
    // only the domain and code go to the results: the description can carry file paths
    let ns = error as NSError
    res["error"] = ["domain": ns.domain, "code": ns.code] as [String: Any]
    print("Error: \(error)")
    exitCode = 1
}
finish(exitCode)
