import CoreGraphics
let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly], kCGNullWindowID) as! [[String: Any]]
let others = list.filter { ($0[kCGWindowLayer as String] as? Int) == 0 }
print("screen_capture_preflight=\(CGPreflightScreenCaptureAccess()) layer0=\(others.count) with_bounds=\(others.filter{$0[kCGWindowBounds as String] != nil}.count) with_owner=\(others.filter{$0[kCGWindowOwnerName as String] != nil}.count) with_name=\(others.filter{$0[kCGWindowName as String] != nil}.count)")
