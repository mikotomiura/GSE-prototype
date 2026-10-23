// 置き場所の試し: 窓の層と collectionBehavior を変えた小さな窓を出し、
// 別プロセスの窓が最大化・全画面になったときに、画面上にあるか・覆われているかを数値で書く。
// 画面は撮らない。描くのは色のついた四角だけ。
import AppKit

struct Conf { let name: String; let level: Int; let behavior: NSWindow.CollectionBehavior }
let desk = Int(CGWindowLevelForKey(.desktopWindow))
let confs: [Conf] = [
  Conf(name: "A_desktop_now", level: desk, behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle]),
  Conf(name: "B_desktop_aux", level: desk, behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle, .fullScreenAuxiliary]),
  Conf(name: "C_floating", level: Int(CGWindowLevelForKey(.floatingWindow)), behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle]),
  Conf(name: "D_floating_aux", level: Int(CGWindowLevelForKey(.floatingWindow)), behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle, .fullScreenAuxiliary]),
  Conf(name: "E_status_aux", level: Int(CGWindowLevelForKey(.statusWindow)), behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle, .fullScreenAuxiliary]),
  Conf(name: "G_floating_joinApps", level: Int(CGWindowLevelForKey(.floatingWindow)), behavior: [.canJoinAllApplications, .stationary, .ignoresCycle]),
  Conf(name: "H_floating_plain", level: Int(CGWindowLevelForKey(.floatingWindow)), behavior: []),
  Conf(name: "F_saver_aux", level: Int(CGWindowLevelForKey(.screenSaverWindow)), behavior: [.canJoinAllSpaces, .stationary, .ignoresCycle, .fullScreenAuxiliary]),
]

class D: NSObject, NSApplicationDelegate {
  var wins: [(String, NSWindow)] = []
  func applicationDidFinishLaunching(_ n: Notification) {
    let s = NSScreen.main!.frame
    for (i, c) in confs.enumerated() {
      // 画面の中央付近に 60x60 を横に並べる（全画面の窓に必ず重なる位置）
      let r = NSRect(x: s.midX - 270 + CGFloat(i) * 70, y: s.midY, width: 60, height: 60)
      let w = NSWindow(contentRect: r, styleMask: .borderless, backing: .buffered, defer: false)
      w.isOpaque = false
      w.backgroundColor = NSColor.systemTeal.withAlphaComponent(0.35)
      w.level = NSWindow.Level(rawValue: c.level)
      w.collectionBehavior = c.behavior
      w.ignoresMouseEvents = true
      w.title = c.name
      w.orderFrontRegardless()
      wins.append((c.name, w))
    }
    Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in self.dump() }
  }
  func dump() {
    let t = String(format: "%.1f", Date().timeIntervalSince1970.truncatingRemainder(dividingBy: 1000))
    let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as! [[String: Any]]
    // 前から後ろの順。自分の窓と全画面役の窓の順位だけ拾う。
    var rank: [Int: Int] = [:]; var fsRank = -1
    for (i, d) in list.enumerated() {
      let num = d[kCGWindowNumber as String] as! Int
      rank[num] = i
      if (d[kCGWindowOwnerName as String] as? String) == "fsapp", (d[kCGWindowLayer as String] as? Int) == 0 { if fsRank < 0 { fsRank = i } }
    }
    var parts: [String] = ["t=\(t)", "fsapp_rank=\(fsRank)"]
    for (name, w) in wins {
      let vis = w.occlusionState.contains(.visible) ? "vis" : "occ"
      let r = rank[w.windowNumber].map(String.init) ?? "off"
      parts.append("\(name):\(vis):\(r)")
    }
    print(parts.joined(separator: " ")); fflush(stdout)
  }
}
let app = NSApplication.shared
app.setActivationPolicy(CommandLine.arguments.contains("--regular") ? .regular : .accessory)
let d = D(); app.delegate = d; app.run()
