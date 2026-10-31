// 開発版のボタンを、名前ではなく pid からたどって見つけ、本物のマウスのクリックを合成して押す。
// ⚠️ 2026-10-30 に JXA の windows() が同じ名前の O1 の窓を返し、O1 を押した（results.md の 1）。
//    ここでは AXUIElementCreateApplication(pid) で pid から直接たどり、押す直前に
//    その座標の一番上の窓が同じ pid のものかを CGWindowList で確かめる。違えば押さない（rc=4）。
// 使い方: axclick <pid> list            … ボタンの題名・押せるか・中心の座標を出す
//         axclick <pid> raise           … その pid の窓を一番上に上げ、前面にする
//         axclick <pid> click <題名>    … その題名のボタンの中心をクリックする
//         axclick <pid> texts           … 窓の中の文字（AXStaticText の値）を上から順に出す
// rc: 0 = 成功 / 2 = 引数の誤り / 3 = ボタンが無い / 4 = その座標の一番上が別のプロセスの窓
import ApplicationServices
import CoreGraphics
import Foundation

func attr(_ e: AXUIElement, _ name: String) -> AnyObject? {
    var v: AnyObject?
    return AXUIElementCopyAttributeValue(e, name as CFString, &v) == .success ? v : nil
}

struct Btn { let title: String; let enabled: Bool; let center: CGPoint }

func walk(_ e: AXUIElement, _ depth: Int, _ out: inout [Btn]) {
    if depth > 40 { return }
    if (attr(e, kAXRoleAttribute) as? String) == kAXButtonRole {
        let t = (attr(e, kAXTitleAttribute) as? String).flatMap { $0.isEmpty ? nil : $0 }
            ?? (attr(e, kAXDescriptionAttribute) as? String) ?? ""
        var p = CGPoint.zero, s = CGSize.zero
        if let pv = attr(e, kAXPositionAttribute) { AXValueGetValue(pv as! AXValue, .cgPoint, &p) }
        if let sv = attr(e, kAXSizeAttribute) { AXValueGetValue(sv as! AXValue, .cgSize, &s) }
        let en = (attr(e, kAXEnabledAttribute) as? Bool) ?? false
        out.append(Btn(title: t, enabled: en, center: CGPoint(x: p.x + s.width / 2, y: p.y + s.height / 2)))
    }
    if let kids = attr(e, kAXChildrenAttribute) as? [AXUIElement] {
        for k in kids { walk(k, depth + 1, &out) }
    }
}

/// 画面上の点で一番上にある、ふつうの層（layer 0）の窓の持ち主の pid。
func topOwner(at pt: CGPoint) -> pid_t? {
    guard let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as? [[String: Any]] else { return nil }
    for w in list {  // 前から順に並ぶ
        guard (w[kCGWindowLayer as String] as? Int) == 0,
              let b = w[kCGWindowBounds as String] as? [String: CGFloat],
              let alpha = w[kCGWindowAlpha as String] as? CGFloat, alpha > 0 else { continue }
        let r = CGRect(x: b["X"] ?? 0, y: b["Y"] ?? 0, width: b["Width"] ?? 0, height: b["Height"] ?? 0)
        if r.contains(pt) { return (w[kCGWindowOwnerPID as String] as? Int).map { pid_t($0) } }
    }
    return nil
}

let args = CommandLine.arguments
guard args.count >= 3, let pid = pid_t(args[1]) else {
    FileHandle.standardError.write("usage: axclick <pid> list | click <title>\n".data(using: .utf8)!); exit(2)
}
let app = AXUIElementCreateApplication(pid)
var btns: [Btn] = []
for w in (attr(app, kAXWindowsAttribute) as? [AXUIElement]) ?? [] { walk(w, 0, &btns) }

switch args[2] {
case "raise":
    // pid の要素に直接かける（名前で解決しない）。窓を一番上に上げ、アプリを前面にする。
    for w in (attr(app, kAXWindowsAttribute) as? [AXUIElement]) ?? [] {
        AXUIElementPerformAction(w, kAXRaiseAction as CFString)
    }
    let r = AXUIElementSetAttributeValue(app, kAXFrontmostAttribute as CFString, kCFBooleanTrue)
    print("raised pid=\(pid) frontmost_set=\(r == .success)")
case "texts":
    func texts(_ e: AXUIElement, _ depth: Int) {
        if depth > 40 { return }
        if (attr(e, kAXRoleAttribute) as? String) == kAXStaticTextRole,
           let v = attr(e, kAXValueAttribute) as? String, !v.isEmpty { print(v) }
        if let kids = attr(e, kAXChildrenAttribute) as? [AXUIElement] { for k in kids { texts(k, depth + 1) } }
    }
    for w in (attr(app, kAXWindowsAttribute) as? [AXUIElement]) ?? [] { texts(w, 0) }
case "list":
    for b in btns { print("\(b.title)\tenabled=\(b.enabled)\t(\(Int(b.center.x)),\(Int(b.center.y)))") }
case "click":
    guard args.count >= 4 else { exit(2) }
    let hits = btns.filter { $0.title == args[3] }
    guard hits.count == 1, let b = hits.first else {
        print("button not found or ambiguous: \(args[3]) count=\(hits.count)"); exit(3)
    }
    guard let owner = topOwner(at: b.center), owner == pid else {
        print("REFUSED: top window at \(b.center) belongs to pid \(String(describing: topOwner(at: b.center))), not \(pid)"); exit(4)
    }
    let src = CGEventSource(stateID: .hidSystemState)
    CGEvent(mouseEventSource: src, mouseType: .mouseMoved, mouseCursorPosition: b.center, mouseButton: .left)?.post(tap: .cghidEventTap)
    usleep(80_000)
    CGEvent(mouseEventSource: src, mouseType: .leftMouseDown, mouseCursorPosition: b.center, mouseButton: .left)?.post(tap: .cghidEventTap)
    usleep(60_000)
    CGEvent(mouseEventSource: src, mouseType: .leftMouseUp, mouseCursorPosition: b.center, mouseButton: .left)?.post(tap: .cghidEventTap)
    let ms = Int(Date().timeIntervalSince1970 * 1000)
    print("CLICKED \(b.title) at (\(Int(b.center.x)),\(Int(b.center.y))) enabled=\(b.enabled) t=\(ms)")
default:
    exit(2)
}
