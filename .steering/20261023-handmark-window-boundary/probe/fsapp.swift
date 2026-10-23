// 全画面役。普通の窓を出し、0.5s 後に画面いっぱいに広げ（最大化の代わり）、
// 4s 後に全画面（緑のボタンと同じ toggleFullScreen）、10s 後に戻し、14s 後に終わる。
import AppKit
class D: NSObject, NSApplicationDelegate {
  var w: NSWindow!
  func log(_ s: String) { print("fsapp \(String(format: "%.1f", Date().timeIntervalSince1970.truncatingRemainder(dividingBy: 1000))) \(s)"); fflush(stdout) }
  func applicationDidFinishLaunching(_ n: Notification) {
    w = NSWindow(contentRect: NSRect(x: 100, y: 100, width: 300, height: 200), styleMask: [.titled, .resizable, .closable], backing: .buffered, defer: false)
    w.collectionBehavior = [.fullScreenPrimary]
    w.backgroundColor = .windowBackgroundColor
    w.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true); log("normal_small")
    DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self.w.setFrame(NSScreen.main!.visibleFrame, display: true); self.log("covering_visibleFrame") }
    DispatchQueue.main.asyncAfter(deadline: .now() + 5) { self.w.toggleFullScreen(nil); self.log("toggle_fullscreen_on") }
    DispatchQueue.main.asyncAfter(deadline: .now() + 11) { self.w.toggleFullScreen(nil); self.log("toggle_fullscreen_off") }
    DispatchQueue.main.asyncAfter(deadline: .now() + 15) { self.log("quit"); NSApp.terminate(nil) }
  }
}
let app = NSApplication.shared
app.setActivationPolicy(.regular)
let d = D(); app.delegate = d; app.run()
