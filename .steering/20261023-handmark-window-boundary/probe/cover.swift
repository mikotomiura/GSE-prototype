// 基準の確かめ: probe の窓の帯（画面中央）に重なる、層 0 以上の他の窓を数える。名前は読まない。
import AppKit
let s = NSScreen.main!.frame
// CG の座標は左上原点。probe の帯: x = midX-200 .. midX+220, AppKit の y = midY..midY+60 → CG の y = s.height - midY - 60 .. s.height - midY
let band = CGRect(x: s.midX - 200, y: s.height - s.midY - 60, width: 420, height: 60)
let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as! [[String: Any]]
var n = 0
for d in list {
  let layer = d[kCGWindowLayer as String] as! Int
  guard let b = d[kCGWindowBounds as String] as? NSDictionary, let r = CGRect(dictionaryRepresentation: b) else { continue }
  let alpha = d[kCGWindowAlpha as String] as? Double ?? -1
  if r.intersects(band) { n += 1; print("layer=\(layer) alpha=\(alpha) bounds=\(Int(r.minX)),\(Int(r.minY)),\(Int(r.width))x\(Int(r.height))") }
}
print("overlapping=\(n) screen=\(Int(s.width))x\(Int(s.height))")
