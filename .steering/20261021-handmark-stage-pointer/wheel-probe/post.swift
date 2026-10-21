// 合成のスクロールを n 回送る（ホイールの確かめの入力・人の手の入力の代わり）。
import CoreGraphics
import Foundation
let n = Int(CommandLine.arguments[1]) ?? 10
for _ in 0..<n {
    CGEvent(scrollWheelEvent2Source: nil, units: .line, wheelCount: 1, wheel1: -1, wheel2: 0, wheel3: 0)?.post(tap: .cghidEventTap)
    usleep(200_000)
}
