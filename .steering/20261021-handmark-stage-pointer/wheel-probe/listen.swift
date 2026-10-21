// ホイールが聞くだけの CGEventTap に届くかを数える（ADR-040 D7 の確かめ・記録しない）。
// 使い方: listen <秒> <結果を書くファイル>。数と権限の状態だけを書く（位置も時刻も書かない）。
import CoreGraphics
import ApplicationServices
import Foundation

let seconds = Double(CommandLine.arguments[1]) ?? 15
let outPath = CommandLine.arguments[2]
var scrolls = 0
var leftDowns = 0

let mask = (CGEventMask(1) << CGEventType.scrollWheel.rawValue) | (CGEventMask(1) << CGEventType.leftMouseDown.rawValue)
let cb: CGEventTapCallBack = { _, type, event, _ in
    if type == .scrollWheel { scrolls += 1 }
    if type == .leftMouseDown { leftDowns += 1 }
    return Unmanaged.passUnretained(event)
}
let tap = CGEvent.tapCreate(tap: .cgSessionEventTap, place: .headInsertEventTap, options: .listenOnly,
                            eventsOfInterest: mask, callback: cb, userInfo: nil)
var line = "ax_trusted=\(AXIsProcessTrusted()) listen_access=\(CGPreflightListenEventAccess()) tap_created=\(tap != nil)"
if let tap = tap {
    let src = CFMachPortCreateRunLoopSource(nil, tap, 0)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), src, .commonModes)
    CGEvent.tapEnable(tap: tap, enable: true)
    CFRunLoopRunInMode(.defaultMode, seconds, false)
    line += " tap_enabled_at_end=\(CGEvent.tapIsEnabled(tap: tap))"
}
line += " scrolls=\(scrolls) left_downs=\(leftDowns)\n"
try? line.write(toFile: outPath, atomically: true, encoding: .utf8)
