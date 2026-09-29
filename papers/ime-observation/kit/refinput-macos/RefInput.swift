// Reference input field for macOS.
//
// A minimal Cocoa application whose only view implements NSTextInputClient. Every call the input method
// makes on that protocol is written as a content-free `gt/1` line (`src: "mac_nstic"`; the contract is
// specified in ../formats/FORMATS.md): the kind of call, lengths, ranges and times, and nothing else.
//
// The text itself is kept in memory only, because the input method has to be answered truthfully
// (marked range, selected range, substring queries). It is never written to the log.
//
// The recording function takes an enumeration and integers only. There is deliberately no overload that
// accepts a string, so a string cannot reach the log by construction.
//
// Nothing here interprets the calls: they are written in the order received. Assigning meaning to that
// order is left to downstream analysis.
//
//   RefInput --out <path>              open one window and record until it is closed
//   RefInput --selftest [--out <path>] no window; drive the protocol methods directly and read the log back

import AppKit
import Foundation

let appVersion = "0.1.0"

// MARK: - Log vocabulary

enum Ev: String {
    case setMarked = "set_marked"
    case insertText = "insert_text"
    case unmark = "unmark"
    case firstRect = "first_rect"
    case doCommand = "do_command"
    case keyDown = "key_down"
    case focusIn = "focus_in"
    case focusOut = "focus_out"
}

enum Cmd: String {
    case insertNewline = "insertNewline:"
    case cancelOperation = "cancelOperation:"
    case deleteBackward = "deleteBackward:"
    case deleteForward = "deleteForward:"
    case moveLeft = "moveLeft:"
    case moveRight = "moveRight:"
    case moveUp = "moveUp:"
    case moveDown = "moveDown:"
    case insertTab = "insertTab:"
    case insertBacktab = "insertBacktab:"
    case noop = "noop:"
    case other = "other"
}

// MARK: - Sink

var sink: FileHandle?
var writeFailed = false

func appendLine(_ text: String) {
    guard let handle = sink else {
        writeFailed = true
        return
    }
    do {
        // One write per line, unbuffered, so a record survives if the process is killed later.
        try handle.write(contentsOf: Data((text + "\n").utf8))
    } catch {
        writeFailed = true
    }
}

func openSink(path: String, replaceExisting: Bool) -> Bool {
    let fm = FileManager.default
    if fm.fileExists(atPath: path) {
        if !replaceExisting { return false }
        try? fm.removeItem(atPath: path)
    }
    guard fm.createFile(atPath: path, contents: nil), let handle = FileHandle(forWritingAtPath: path) else {
        return false
    }
    sink = handle
    appendLine("{\"kind\":\"header\",\"format\":\"gt/1\",\"src\":\"mac_nstic\",\"app_version\":\"\(appVersion)\",\"os\":\"macos\"}")
    return !writeFailed
}

func wallMs() -> Int64 {
    return Int64((Date().timeIntervalSince1970 * 1000).rounded(.down))
}

func monoNs() -> UInt64 {
    return clock_gettime_nsec_np(CLOCK_UPTIME_RAW)
}

// The recording function. Arguments are an enumeration and integers only; `cmd` is emitted from the
// enumeration's raw value.
func record(ev: Ev, cmd: Cmd? = nil, vk: Int? = nil, len: Int? = nil, selLoc: Int? = nil, selLen: Int? = nil,
            repLoc: Int? = nil, repLen: Int? = nil) {
    var line = "{\"kind\":\"ev\",\"t_wall_ms\":\(wallMs()),\"t_mono_ns\":\(monoNs()),\"ev\":\"\(ev.rawValue)\""
    if let cmd = cmd { line += ",\"cmd\":\"\(cmd.rawValue)\"" }
    if let vk = vk { line += ",\"vk\":\(vk)" }
    if let len = len { line += ",\"len\":\(len)" }
    if let selLoc = selLoc { line += ",\"sel_loc\":\(selLoc)" }
    if let selLen = selLen { line += ",\"sel_len\":\(selLen)" }
    // NSNotFound means "no replacement range was given"; the field is left out in that case.
    if let repLoc = repLoc, repLoc != NSNotFound, repLoc >= 0 {
        line += ",\"rep_loc\":\(repLoc)"
        if let repLen = repLen { line += ",\"rep_len\":\(repLen)" }
    }
    line += "}"
    appendLine(line)
}

// MARK: - The view

final class RefInputView: NSView, NSTextInputClient {
    // The text lives in memory only (UTF-16 units, as the protocol counts them).
    private let text = NSMutableString()
    private var marked = NSRange(location: NSNotFound, length: 0)
    private var selected = NSRange(location: 0, length: 0)

    override var acceptsFirstResponder: Bool { return true }

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        guard let win = window else { return }
        let center = NotificationCenter.default
        center.addObserver(forName: NSWindow.didBecomeKeyNotification, object: win, queue: nil) { _ in
            record(ev: .focusIn)
        }
        center.addObserver(forName: NSWindow.didResignKeyNotification, object: win, queue: nil) { _ in
            record(ev: .focusOut)
        }
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.white.setFill()
        bounds.fill()
        let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: 24), .foregroundColor: NSColor.black]
        text.draw(at: NSPoint(x: 12, y: bounds.height / 2), withAttributes: attrs)
    }

    override func keyDown(with event: NSEvent) {
        record(ev: .keyDown, vk: Int(event.keyCode))
        interpretKeyEvents([event])
    }

    // Range the next edit replaces: the explicit range if given, else the marked range, else the selection.
    private func target(_ replacement: NSRange) -> NSRange {
        var r = replacement
        if r.location == NSNotFound { r = (marked.location != NSNotFound) ? marked : selected }
        let end = min(max(r.location, 0) + max(r.length, 0), text.length)
        let start = min(max(r.location, 0), text.length)
        return NSRange(location: start, length: end - start)
    }

    private func plain(_ value: Any) -> NSString {
        if let a = value as? NSAttributedString { return a.string as NSString }
        if let s = value as? NSString { return s }
        return ""
    }

    // MARK: NSTextInputClient

    func insertText(_ string: Any, replacementRange: NSRange) {
        let s = plain(string)
        record(ev: .insertText, len: s.length, repLoc: replacementRange.location, repLen: replacementRange.length)
        let r = target(replacementRange)
        text.replaceCharacters(in: r, with: s as String)
        marked = NSRange(location: NSNotFound, length: 0)
        selected = NSRange(location: r.location + s.length, length: 0)
        needsDisplay = true
    }

    func setMarkedText(_ string: Any, selectedRange: NSRange, replacementRange: NSRange) {
        let s = plain(string)
        record(ev: .setMarked, len: s.length, selLoc: selectedRange.location, selLen: selectedRange.length,
               repLoc: replacementRange.location, repLen: replacementRange.length)
        let r = target(replacementRange)
        text.replaceCharacters(in: r, with: s as String)
        marked = s.length > 0 ? NSRange(location: r.location, length: s.length) : NSRange(location: NSNotFound, length: 0)
        selected = NSRange(location: r.location + max(selectedRange.location, 0), length: max(selectedRange.length, 0))
        needsDisplay = true
    }

    func unmarkText() {
        record(ev: .unmark)
        marked = NSRange(location: NSNotFound, length: 0)
        needsDisplay = true
    }

    func selectedRange() -> NSRange { return selected }

    func markedRange() -> NSRange { return marked }

    func hasMarkedText() -> Bool { return marked.location != NSNotFound }

    func attributedSubstring(forProposedRange range: NSRange, actualRange: NSRangePointer?) -> NSAttributedString? {
        let start = min(max(range.location, 0), text.length)
        let end = min(start + max(range.length, 0), text.length)
        let r = NSRange(location: start, length: end - start)
        actualRange?.pointee = r
        return NSAttributedString(string: text.substring(with: r))
    }

    func validAttributesForMarkedText() -> [NSAttributedString.Key] { return [] }

    func firstRect(forCharacterRange range: NSRange, actualRange: NSRangePointer?) -> NSRect {
        record(ev: .firstRect)
        actualRange?.pointee = range
        guard let win = window else { return .zero }
        let caret = NSRect(x: 12, y: bounds.height / 2 - 4, width: 1, height: 32)
        return win.convertToScreen(convert(caret, to: nil))
    }

    func characterIndex(for point: NSPoint) -> Int { return 0 }

    override func doCommand(by selector: Selector) {
        record(ev: .doCommand, cmd: Cmd(rawValue: NSStringFromSelector(selector)) ?? .other)
    }
}

// MARK: - Self-test

func selftestFailure(_ what: String) -> Int32 {
    FileHandle.standardError.write(Data("selftest failed: \(what)\n".utf8))
    return 1
}

func runSelftest(outPath: String?) -> Int32 {
    let path = outPath ?? (NSTemporaryDirectory() + "refinput-selftest-\(getpid()).jsonl")
    let removeAfter = (outPath == nil)
    defer { if removeAfter { try? FileManager.default.removeItem(atPath: path) } }
    guard openSink(path: path, replaceExisting: true) else { return selftestFailure("cannot open the output") }

    _ = NSApplication.shared
    let view = RefInputView(frame: NSRect(x: 0, y: 0, width: 400, height: 100))
    let none = NSRange(location: NSNotFound, length: 0)

    // Strings are built from code points so that the read-back check below has a fixed thing to look for.
    let reading = String(String.UnicodeScalarView([0x306B, 0x307B, 0x3093, 0x3054].compactMap(Unicode.Scalar.init)))
    let kanji = String(String.UnicodeScalarView([0x65E5, 0x672C, 0x8A9E].compactMap(Unicode.Scalar.init)))
    let astral = String(String.UnicodeScalarView([0x20BB7, 0x61].compactMap(Unicode.Scalar.init)))

    view.setMarkedText(reading, selectedRange: NSRange(location: 4, length: 0), replacementRange: none)
    view.insertText(kanji, replacementRange: NSRange(location: 0, length: 4))
    view.setMarkedText("", selectedRange: NSRange(location: 0, length: 0), replacementRange: none)
    view.setMarkedText(astral, selectedRange: NSRange(location: 3, length: 0), replacementRange: NSRange(location: 3, length: 0))
    view.setMarkedText(NSAttributedString(string: "\(kanji)"), selectedRange: NSRange(location: 0, length: 3), replacementRange: none)
    view.unmarkText()
    _ = view.firstRect(forCharacterRange: NSRange(location: 0, length: 0), actualRange: nil)
    view.doCommand(by: #selector(NSResponder.cancelOperation(_:)))
    view.doCommand(by: #selector(NSResponder.selectAll(_:)))
    record(ev: .keyDown, vk: 36)
    record(ev: .focusOut)
    record(ev: .focusIn)
    if writeFailed { return selftestFailure("a write failed") }
    try? sink?.close()
    sink = nil

    guard let data = FileManager.default.contents(atPath: path) else { return selftestFailure("cannot read the output back") }
    // (b) Nothing that was passed in may appear: the whole output must be plain ASCII.
    if data.contains(where: { $0 >= 0x80 }) { return selftestFailure("non-ASCII bytes in the output") }
    guard let body = String(data: data, encoding: .utf8) else { return selftestFailure("output is not UTF-8") }
    if body.contains(reading) || body.contains(kanji) || body.contains(astral) {
        return selftestFailure("a passed string appears in the output")
    }

    var rows: [[String: Any]] = []
    for line in body.split(separator: "\n") {
        guard let obj = (try? JSONSerialization.jsonObject(with: Data(line.utf8))) as? [String: Any] else {
            return selftestFailure("a line is not a JSON object")
        }
        rows.append(obj)
    }
    guard let header = rows.first, header["kind"] as? String == "header", header["src"] as? String == "mac_nstic",
          header["os"] as? String == "macos" else { return selftestFailure("bad header") }
    let events = rows.dropFirst()

    // (a) The recorded lengths equal the UTF-16 lengths of what was passed.
    let expectedLens = [reading.utf16.count, kanji.utf16.count, 0, astral.utf16.count, kanji.utf16.count]
    let lens = events.filter { $0["ev"] as? String == "set_marked" || $0["ev"] as? String == "insert_text" }
        .compactMap { $0["len"] as? Int }
    // Order of the calls above: set_marked, insert_text, set_marked, set_marked, set_marked.
    if lens != expectedLens { return selftestFailure("lengths \(lens) differ from \(expectedLens)") }
    if astral.utf16.count != 3 { return selftestFailure("a supplementary-plane character must count as 2 units") }
    let evNames = events.compactMap { $0["ev"] as? String }
    let expectedEv = ["set_marked", "insert_text", "set_marked", "set_marked", "set_marked", "unmark", "first_rect",
                      "do_command", "do_command", "key_down", "focus_out", "focus_in"]
    if evNames != expectedEv { return selftestFailure("event order \(evNames)") }
    // An absent replacement range leaves rep_* out; a given one records it.
    guard let firstSet = events.first, firstSet["rep_loc"] == nil, firstSet["rep_len"] == nil, firstSet["sel_loc"] as? Int == 4
    else { return selftestFailure("replacement range handling") }
    let insertRow = events[events.startIndex + 1]
    if insertRow["rep_loc"] as? Int != 0 || insertRow["rep_len"] as? Int != 4 {
        return selftestFailure("replacement range was not recorded")
    }
    // (c) A selector outside the enumeration is recorded as `other`.
    let cmds = events.filter { $0["ev"] as? String == "do_command" }.compactMap { $0["cmd"] as? String }
    if cmds != ["cancelOperation:", "other"] { return selftestFailure("commands \(cmds)") }
    return 0
}

// MARK: - Application

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { return true }
}

var delegate: AppDelegate?

func runApp() -> Int32 {
    let app = NSApplication.shared
    app.setActivationPolicy(.regular)
    let d = AppDelegate()
    delegate = d
    app.delegate = d
    let view = RefInputView(frame: NSRect(x: 0, y: 0, width: 640, height: 200))
    let win = NSWindow(contentRect: view.frame, styleMask: [.titled, .closable], backing: .buffered, defer: false)
    win.title = "Reference input field"
    win.contentView = view
    win.center()
    win.makeKeyAndOrderFront(nil)
    win.makeFirstResponder(view)
    app.activate(ignoringOtherApps: true)
    // The window may already be key before the observers were registered.
    if win.isKeyWindow { record(ev: .focusIn) }
    app.run()
    return writeFailed ? 1 : 0
}

// MARK: - Entry

func usage() -> Int32 {
    FileHandle.standardError.write(Data("usage: refinput-macos --out <path> | --selftest [--out <path>]\n".utf8))
    return 2
}

func main() -> Int32 {
    var outPath: String?
    var selftest = false
    var i = 1
    let args = CommandLine.arguments
    while i < args.count {
        switch args[i] {
        case "--selftest":
            selftest = true
        case "--out":
            i += 1
            if i >= args.count { return usage() }
            outPath = args[i]
        default:
            return usage()
        }
        i += 1
    }
    if selftest { return runSelftest(outPath: outPath) }
    guard let path = outPath else { return usage() }
    // A recording run never replaces an existing file, so that a raw log cannot be destroyed.
    guard openSink(path: path, replaceExisting: false) else {
        FileHandle.standardError.write(Data("cannot create the output (it may already exist)\n".utf8))
        return 1
    }
    return runApp()
}

exit(main())
