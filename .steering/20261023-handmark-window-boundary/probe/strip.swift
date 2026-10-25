// 下の縁の帯の試し（判断 4・5）。
// 1) 下の縁に太さ 14 点の帯を出す（accessory・浮く層・クリック透過・全 Space）。打鍵は読まず、合成の風で線を揺らし続ける。
// 2) 1 秒ごとに、帯が画面上にあるか・普通の窓（層 0）のどれより前か・覆われていないか・自分の CPU を書く。
// 3) --hide-at N --restore-at M: N 秒目に「いま見えているアプリ」を覚えて隠し、M 秒目にそのアプリだけを戻す。
//    書くのは数だけ。アプリの名前は書かない。覚えた一覧は戻したら捨てる。
// 画面は撮らない。--duration 秒で自分で終わる。
import AppKit

func arg(_ name: String, _ def: Double) -> Double {
  let a = CommandLine.arguments
  if let i = a.firstIndex(of: name), i + 1 < a.count, let v = Double(a[i + 1]) { return v }
  return def
}
let duration = arg("--duration", 60)
let hideAt = arg("--hide-at", -1)
let restoreAt = arg("--restore-at", -1)
let thick = CGFloat(arg("--thick", 14))
let fps = arg("--fps", 60)

final class StripView: NSView {
  var t0 = Date()
  override var isOpaque: Bool { false }
  override func draw(_ dirty: NSRect) {
    let t = Date().timeIntervalSince(t0)
    let w = bounds.width, h = bounds.height
    // 合成の風: 8 秒周期で強弱をつける（打鍵は読まない）。
    let wind = 0.5 + 0.5 * sin(t * 2 * .pi / 8)
    let path = NSBezierPath()
    var x: CGFloat = 0
    while x <= w + 6 {
      let y = h / 2 + h * 0.34 * CGFloat(0.3 * sin(Double(x) / 420 + t * 0.35) + wind * sin(Double(x) / 110 - t * 3))
        .clamped(-1, 1)
      if x == 0 { path.move(to: NSPoint(x: x, y: y)) } else { path.line(to: NSPoint(x: x, y: y)) }
      x += 6
    }
    path.lineWidth = 2.75
    NSColor(white: 0.07, alpha: 0.22 * 0.7).setStroke(); path.stroke()
    path.lineWidth = 1.1
    NSColor(white: 1, alpha: 0.85 * 0.7).setStroke(); path.stroke()
  }
}
extension CGFloat { func clamped(_ a: CGFloat, _ b: CGFloat) -> CGFloat { Swift.min(b, Swift.max(a, self)) } }

func cpuSeconds() -> Double {
  var u = rusage(); getrusage(RUSAGE_SELF, &u)
  return Double(u.ru_utime.tv_sec + u.ru_stime.tv_sec) + Double(u.ru_utime.tv_usec + u.ru_stime.tv_usec) / 1e6
}

func visibleRegularApps() -> [NSRunningApplication] {
  let me = ProcessInfo.processInfo.processIdentifier
  return NSWorkspace.shared.runningApplications.filter { $0.activationPolicy == .regular && !$0.isHidden && $0.processIdentifier != me }
}

func hiddenRegularApps() -> Int {
  NSWorkspace.shared.runningApplications.filter { $0.activationPolicy == .regular && $0.isHidden }.count
}

final class D: NSObject, NSApplicationDelegate {
  var win: NSWindow!
  var view: StripView!
  let start = Date()
  var lastCpu = cpuSeconds(), lastWall = Date()
  var remembered: [NSRunningApplication] = []
  var hidDone = false, restoreDone = false

  func applicationDidFinishLaunching(_ n: Notification) {
    let s = NSScreen.main!.frame
    let r = NSRect(x: s.minX, y: s.minY, width: s.width, height: thick)
    win = NSWindow(contentRect: r, styleMask: .borderless, backing: .buffered, defer: false)
    win.isOpaque = false
    win.backgroundColor = .clear
    win.hasShadow = false
    win.level = .floating
    win.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle, .fullScreenAuxiliary]
    win.ignoresMouseEvents = true
    view = StripView(frame: NSRect(origin: .zero, size: r.size))
    win.contentView = view
    win.orderFrontRegardless()
    print("start screen=\(Int(s.width))x\(Int(s.height)) thick=\(Int(thick)) fps=\(Int(fps)) duration=\(Int(duration)) hide_at=\(hideAt) restore_at=\(restoreAt)")
    fflush(stdout)
    Timer.scheduledTimer(withTimeInterval: 1 / fps, repeats: true) { _ in self.view.needsDisplay = true }
    Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in self.second() }
  }

  func second() {
    let el = Date().timeIntervalSince(start)
    let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] ?? []
    var myRank = -1, firstLayer0 = -1, layer0Count = 0, fullLayer0 = 0
    let sf = NSScreen.main!.frame
    for (i, d) in list.enumerated() {
      let num = d[kCGWindowNumber as String] as? Int ?? -1
      let layer = d[kCGWindowLayer as String] as? Int ?? -1
      if num == win.windowNumber { myRank = i }
      if layer == 0 {
        layer0Count += 1
        if firstLayer0 < 0 { firstLayer0 = i }
        if let b = d[kCGWindowBounds as String] as? [String: Any],
           let w = b["Width"] as? Double, let h = b["Height"] as? Double,
           w >= Double(sf.width) - 1, h >= Double(sf.height) - 1 { fullLayer0 += 1 }
      }
    }
    let now = Date(), cpu = cpuSeconds()
    let pct = (cpu - lastCpu) / now.timeIntervalSince(lastWall) * 100
    lastCpu = cpu; lastWall = now
    let front = myRank >= 0 && (firstLayer0 < 0 || myRank < firstLayer0)
    let vis = win.occlusionState.contains(.visible)
    print(String(format: "t=%.0f onscreen=%@ front_of_layer0=%@ visible=%@ layer0=%d full_size_layer0=%d cpu_pct=%.1f visible_apps=%d hidden_apps=%d",
                 el, myRank >= 0 ? "1" : "0", front ? "1" : "0", vis ? "1" : "0", layer0Count, fullLayer0, pct, visibleRegularApps().count, hiddenRegularApps()))
    if hideAt >= 0, !hidDone, el >= hideAt {
      hidDone = true
      remembered = visibleRegularApps()
      // --activate-first: 先に自分を前面に出す（前面のアプリは外から隠せない見込みのため。メニューの「ほかを隠す」と同じ順）。
      if CommandLine.arguments.contains("--activate-first") { NSApp.activate(ignoringOtherApps: true) }
      let ok = remembered.map { $0.hide() }.filter { $0 }.count
      print("hide remembered=\(remembered.count) hide_true=\(ok)")
      // 戻り値は当てにならない（試し 2 で実際に隠れても false だった）ので、1 秒後に読み直す。
      let rem = remembered
      DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
        print("hide_check not_hidden_after_1s=\(rem.filter { !$0.isHidden }.count) active_not_hidden=\(rem.filter { !$0.isHidden && $0.isActive }.count)")
        fflush(stdout)
      }
    }
    if restoreAt >= 0, hidDone, !restoreDone, el >= restoreAt {
      restoreDone = true
      let ok = remembered.map { $0.unhide() }.filter { $0 }.count
      let stillHidden = remembered.filter { $0.isHidden }.count
      print("restore remembered=\(remembered.count) unhide_true=\(ok) still_hidden_immediately=\(stillHidden)")
      remembered = []
    }
    fflush(stdout)
    if el >= duration { NSApp.terminate(nil) }
  }
}
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let d = D(); app.delegate = d; app.run()
