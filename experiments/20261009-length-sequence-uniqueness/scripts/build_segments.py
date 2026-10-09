"""Preprocess Aozora Bunko texts into segment sequences (design.md sections 4 and 5).

  build_segments.py --manifest results/corpus_manifest.json --zips raw/zips --config config.json
                    --out-dir raw/derived --stats results/corpus_stats.json

For each work and each segmentation (B0..B3) a list of segments is built; a segment is
(attacker_keys, attacker_units, writer_units, valid). It is stored compactly (see pack) in
<out-dir>/<corpus|reference>_<B0..B3>.pkl:
  attacker_keys   standard key count of the attacker's reading (SudachiPy on the text without ruby)
  attacker_units  that reading as a string of hiragana, `ー` and `#` (one key for a digit, letter or symbol)
  writer_units    the reading with ruby substituted (the writer of the noisy conditions)
  valid           False when the segment holds a character whose typing is not determined (design.md 4.3)

Only SudachiPy is used besides the standard library. The tokenizer is created once per process.
"""
import argparse
import hashlib
import json
import os
import pickle
import re
import sys
import unicodedata
import zipfile
import zlib
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from romaji_table import KANA_CHARS, count_keys, unit_keys  # noqa: E402

# ---------------------------------------------------------------- text body (same rules as the IME kit's body_lines)
DASH_RE = re.compile(r"-{10,}")
HEAD_SCAN = 40
HEAD_SPAN = 60
FOOT_RE = re.compile(r"底本[：:]")
ANNOT_RE = re.compile(r"［＃[^］]*］")

COMMA_CHARS = frozenset("、，,")
PERIOD_CHARS = frozenset("。．.")
BOUNDARY_CHARS = COMMA_CHARS | PERIOD_CHARS
CLOSERS = frozenset("」』）)〕］]】〉｝}")
SYMBOL_ONE_KEY = frozenset(
    "「」『』〔〕［］【】〈〉｛｝{}[]（）()！!？?・／/―─—－‐-ー〜～：:；;＝=＋+＊*＃#＆&＠@％%＿_＾^＼\\｜|\"“”'‘’"
)
WHITESPACE = frozenset(" 　\t")
KANJI_EXTRA = frozenset("々〆〇ヶ仝")


def is_digit_or_latin(ch):
    return ("0" <= ch <= "9") or ("０" <= ch <= "９") or ("a" <= ch <= "z") or ("A" <= ch <= "Z") \
        or ("ａ" <= ch <= "ｚ") or ("Ａ" <= ch <= "Ｚ")


def char_level_ok(ch):
    return ch in BOUNDARY_CHARS or ch in SYMBOL_ONE_KEY or ch in WHITESPACE or is_digit_or_latin(ch)


def kata_to_hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def is_kana_reading(s):
    if not s:
        return False
    h = kata_to_hira(s)
    return all(c in KANA_CHARS for c in h)


def is_kanji(ch):
    if ch in KANJI_EXTRA:
        return True
    o = ord(ch)
    return 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0xF900 <= o <= 0xFAFF or 0x20000 <= o <= 0x2FFFF


def body_lines(text):
    """Body lines after stripping the title and author lines, the frame of two dashed rules, the colophon
    and the annotation markers. Lines that held only annotations are dropped (the writer types nothing
    there); lines that were blank stay (a typed newline). Ruby is kept for parse_ruby."""
    lines = re.split(r"\r\n|\r|\n", text)
    first = next((i for i, ln in enumerate(lines[:HEAD_SCAN]) if DASH_RE.fullmatch(ln.strip())), None)
    second = None
    if first is not None:
        second = next((i for i in range(first + 1, min(len(lines), first + 1 + HEAD_SPAN))
                       if DASH_RE.fullmatch(lines[i].strip())), None)
    no_dash = second is None
    if second is not None:
        lines = lines[second + 1:]
    else:
        blank = next((i for i, ln in enumerate(lines[:HEAD_SCAN]) if ln.strip() == ""), None)
        if blank is not None and any(ln.strip() for ln in lines[blank + 1:]):
            lines = lines[blank + 1:]
    for i, ln in enumerate(lines):
        if FOOT_RE.match(ln):
            lines = lines[:i]
            break
    out = []
    for ln in lines:
        stripped = ANNOT_RE.sub("", ln)
        if ln.strip() and not stripped.strip():
            continue
        out.append(stripped)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out, no_dash


# ---------------------------------------------------------------- ruby
def parse_ruby(line):
    """Returns (plain, writer, cut_map, n_ruby, n_substituted).

    plain   the line without ruby (the base characters kept)
    writer  the line with each ruby base replaced by its reading in hiragana when the reading is kana only
    cut_map list of len(plain)+1: the position in `writer` of each cut position of `plain`; a cut inside a
            replaced base maps to the proportional position inside the replacement (rounded half up)
    """
    plain, writer = [], []
    p2w = []
    inner = []  # (start, end) of replaced bases in plain
    bar = None
    n_ruby = n_sub = 0
    i = 0
    while i < len(line):
        c = line[i]
        if c == "｜":
            bar = len(plain)
            i += 1
            continue
        if c == "《":
            j = line.find("》", i)
            if j < 0:
                i += 1
                continue
            reading = line[i + 1:j]
            i = j + 1
            n_ruby += 1
            be = len(plain)
            if bar is not None:
                bs = bar
            else:
                bs = be
                while bs > 0 and is_kanji(plain[bs - 1]):
                    bs -= 1
            bar = None
            if bs < be and is_kana_reading(reading):
                ws = p2w[bs]
                del writer[ws:]
                writer.extend(kata_to_hira(reading))
                for p in range(bs, be):
                    p2w[p] = ws
                inner.append((bs, be, ws, len(writer) - ws))
                n_sub += 1
            continue
        p2w.append(len(writer))
        plain.append(c)
        writer.append(c)
        i += 1
    cut_map = p2w + [len(writer)]
    for bs, be, ws, wlen in inner:
        for p in range(bs + 1, be):
            cut_map[p] = ws + (2 * (p - bs) * wlen + (be - bs)) // (2 * (be - bs))  # proportional, rounded half up
    return "".join(plain), "".join(writer), cut_map, n_ruby, n_sub


# ---------------------------------------------------------------- tokenizer
class Tokenizer(object):
    def __init__(self, max_bytes):
        from sudachipy import Dictionary, SplitMode  # imported here so that the selftest can run parts without it
        self._tok = Dictionary(dict="core").create()
        self._mode = SplitMode.C
        self._max = max_bytes

    def chunks(self, line):
        """Split a line longer than max_bytes after a 。 (or, failing that, at a fixed length). A chunk of
        max_bytes // 4 characters never exceeds max_bytes (a character is at most 4 bytes in UTF-8)."""
        if len(line.encode("utf-8")) <= self._max:
            return [(0, line)]
        out, start = [], 0
        step = self._max // 4
        while start < len(line):
            hard = min(len(line), start + step)
            cut = line.rfind("。", start, hard) if hard < len(line) else -1
            end = cut + 1 if cut >= start else hard
            out.append((start, line[start:end]))
            start = end
        return out

    def tokens(self, line):
        """[(begin, end, surface, reading, pos)] with character offsets in `line`."""
        out = []
        for off, chunk in self.chunks(line):
            for m in self._tok.tokenize(chunk, self._mode):
                out.append((off + m.begin(), off + m.end(), m.surface(), m.reading_form(), m.part_of_speech()))
        return out


# ---------------------------------------------------------------- units
def is_word_char(ch):
    """A character that may be read through the dictionary: a letter (kanji, kana, the iteration marks,
    the long-vowel mark) or the ideographic zero. Digits, Latin letters, symbols and anything else are not."""
    if is_digit_or_latin(ch):
        return False
    return unicodedata.category(ch).startswith("L") or ch == "〇"


def token_units(begin, surface, reading):
    """[(position, kind, payload)]: kind 'U' (payload = unit string), 'B' (payload = 'comma' or 'period'),
    'X' (a character whose typing is not determined).

    Order (design.md section 4.3): whitespace -> nothing; every character typed one by one (table, digits,
    Latin letters, boundaries) -> one unit or boundary per character; every character a word character and
    the reading kana only -> the reading; anything else (a symbol outside the table such as … or ※, a
    replacement character, a token mixing digits or Latin letters with kanji or kana) -> invalid."""
    if surface == "" or all(ch in WHITESPACE for ch in surface):
        return []
    if all(char_level_ok(ch) for ch in surface):
        out = []
        for i, ch in enumerate(surface):
            if ch in WHITESPACE:
                continue
            if ch in COMMA_CHARS:
                out.append((begin + i, "B", "comma"))
            elif ch in PERIOD_CHARS:
                out.append((begin + i, "B", "period"))
            else:
                out.append((begin + i, "U", "#"))
        return out
    if all(is_word_char(ch) for ch in surface) and is_kana_reading(reading):
        return [(begin, "U", kata_to_hira(reading))]
    return [(begin, "X", surface)]


CONTENT_POS = frozenset(["名詞", "代名詞", "動詞", "形容詞", "形状詞", "副詞", "連体詞", "接続詞", "感動詞", "接頭辞"])
NOUNISH = frozenset(["名詞", "形状詞", "接尾辞"])


def bunsetsu_starts(tokens):
    """Character positions where an approximate bunsetsu starts (design.md section 5)."""
    starts = []
    prev = None
    for begin, end, surface, reading, pos in tokens:
        if surface == "" or all(ch in WHITESPACE for ch in surface):
            continue
        p0, p1 = pos[0], pos[1]
        start = False
        if p0 == "補助記号" and p1 == "括弧開":
            start = True
        elif p0 in CONTENT_POS:
            start = True
            if prev is not None:
                q0, q1 = prev[0], prev[1]
                if q0 == "接頭辞" or (q0 == "補助記号" and q1 == "括弧開"):
                    start = False
                elif p0 in NOUNISH and q0 == "名詞":
                    start = False
            if p1 == "非自立可能":
                start = False
        if start:
            starts.append(begin)
        prev = pos
    return starts


# ---------------------------------------------------------------- cuts and segments
def line_cuts(plain, att_items, starts, mode):
    """Cuts of one line in plain coordinates: [(position, rank, kind)], kind 'SP' (the boundary character at
    `position`), 'CF' (a confirm Enter just before `position`), 'NL' (the newline at the end).

    mode 'none' (B0, B3), 'sentence' (B1) or 'bunsetsu' (B2)."""
    cuts = [(pos, 1, "SP") for pos, kind, _ in att_items if kind == "B"]
    cf = set()
    if mode == "sentence":
        for pos, kind, payload in att_items:
            if kind == "B" and payload == "period":
                q = pos + 1
                while q < len(plain) and plain[q] in CLOSERS:
                    q += 1
                cf.add(q)
    elif mode == "bunsetsu":
        # punctuation and closing brackets never start a bunsetsu, so they stay with the one before them
        cf.update(s for s in starts if s > 0)
    if mode != "none":
        typed = sorted(pos for pos, kind, _ in att_items)
        last_cf = max([c for c in cf if c <= len(plain)] or [0])
        if any(p >= last_cf for p in typed):
            cf.add(len(plain))
        cf = {c for c in cf if c > 0}
    cuts += [(c, 0, "CF") for c in cf]
    cuts.append((len(plain), 2, "NL"))
    cuts.sort()
    return cuts


def merge(items, cuts):
    """Walk units and cuts in order; yields ('U', payload) / ('X', payload) / ('CUT', kind)."""
    seq = [(pos, 1, 0, kind, payload) for pos, kind, payload in items if kind != "B"]
    seq += [(pos, rank, 1, "CUT", kind) for pos, rank, kind in cuts]
    seq.sort(key=lambda t: (t[0], t[1], t[2]))
    for pos, rank, _, kind, payload in seq:
        yield kind, payload


def map_cuts(cuts, cut_map):
    return [(cut_map[pos], rank, kind) for pos, rank, kind in cuts]


DEFINITIONS = {
    "B0": ("none", frozenset(["SP", "NL"])),
    "B1": ("sentence", frozenset(["SP", "NL", "CF"])),
    "B2": ("bunsetsu", frozenset(["SP", "NL", "CF"])),
    "B3": ("none", frozenset(["SP"])),
}


class SegmentBuilder(object):
    def __init__(self):
        self.segs = []
        self.units = []
        self.invalid = False

    def add(self, kind, payload):
        if kind == "U":
            self.units.append(payload)
        elif kind == "X":
            self.invalid = True

    def close(self):
        self.segs.append(("".join(self.units), self.invalid))
        self.units, self.invalid = [], False


def segments_of_work(lines, tok):
    """Returns ({definition: [(att_keys, att_units, wr_units, valid)]}, stats)."""
    stats = {"lines": len(lines), "ruby": 0, "ruby_substituted": 0, "x_tokens": 0, "x_examples": {}}
    per_line = []
    for ln in lines:
        plain, writer, cut_map, n_ruby, n_sub = parse_ruby(ln)
        stats["ruby"] += n_ruby
        stats["ruby_substituted"] += n_sub
        ptoks = tok.tokens(plain)
        wtoks = tok.tokens(writer) if writer != plain else None
        att = [u for t in ptoks for u in token_units(t[0], t[2], t[3])]
        wr = att if wtoks is None else [u for t in wtoks for u in token_units(t[0], t[2], t[3])]
        for _, kind, payload in att:
            if kind == "X":
                stats["x_tokens"] += 1
                key = payload[:4]
                stats["x_examples"][key] = stats["x_examples"].get(key, 0) + 1
        per_line.append((plain, att, wr, cut_map, bunsetsu_starts(ptoks)))

    out = {}
    for name, (mode, kinds) in DEFINITIONS.items():
        a_b, w_b = SegmentBuilder(), SegmentBuilder()
        for plain, att, wr, cut_map, starts in per_line:
            cuts = [c for c in line_cuts(plain, att, starts, mode) if c[2] in kinds]
            for kind, payload in merge(att, cuts):
                if kind == "CUT":
                    a_b.close()
                else:
                    a_b.add(kind, payload)
            for kind, payload in merge(wr, map_cuts(cuts, cut_map)):
                if kind == "CUT":
                    w_b.close()
                else:
                    w_b.add(kind, payload)
        a_b.close()
        w_b.close()
        if len(a_b.segs) != len(w_b.segs):
            raise RuntimeError("segment counts differ between the attacker and the writer (%s)" % name)
        segs = []
        for (au, ainv), (wu, winv) in zip(a_b.segs, w_b.segs):
            segs.append((count_keys(au) if not ainv else -1, au, wu, not (ainv or winv)))
        # the segment opened after the last cut of the work is empty when the work ends with a cut; it is not typed
        if segs and segs[-1][1] == "" and segs[-1][2] == "" and segs[-1][3]:
            segs.pop()
        out[name] = segs
    return out, stats


# ---------------------------------------------------------------- corpus
SEP = chr(0x1F)


def read_zip_text(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".txt")]
        if len(names) != 1:
            raise ValueError("expected one .txt in %s, found %r" % (os.path.basename(path), names))
        data = z.read(names[0])
    text = data.decode("cp932", errors="replace")
    return text, text.count(chr(0xFFFD))


def window_hashes(keys, k):
    """Hashes of the windows of k consecutive valid segments (keys < 0 marks an invalid segment)."""
    out = set()
    run = 0
    for i, v in enumerate(keys):
        if v >= 0:
            run += 1
            if run >= k:
                out.add(hash(tuple(keys[i - k + 1:i + 1])))
        else:
            run = 0
    return out


def pack(segs):
    """(keys, blob): keys is an array of the attacker's key counts (-1 for an invalid segment); blob holds
    the attacker's unit strings and the writer's where they differ, compressed (the matching step only
    unpacks the works it needs)."""
    keys = array("i", [s[0] if s[3] else -1 for s in segs])
    au = SEP.join(s[1] for s in segs)
    diffs = [(i, s[2]) for i, s in enumerate(segs) if s[2] != s[1]]
    blob = zlib.compress(pickle.dumps((len(segs), au, diffs), protocol=4), 6)
    return keys, blob


def unpack(blob):
    """blob -> (attacker unit strings, writer unit strings), one per segment."""
    n, au, diffs = pickle.loads(zlib.decompress(blob))
    a = au.split(SEP) if n else []
    w = list(a)
    for i, s in diffs:
        w[i] = s
    return a, w


class Tally(object):
    """Per-definition counts for corpus_stats.json (computed before any matching)."""

    def __init__(self):
        self.d = {"segments": 0, "valid": 0, "zero_length_valid": 0, "keys_valid": 0,
                  "writer_reading_differs_valid": 0, "writer_units_valid": 0, "writer_unit_keys_valid": 0}

    def add(self, segs):
        d = self.d
        for keys_s, au, wu, valid in segs:
            d["segments"] += 1
            if not valid:
                continue
            d["valid"] += 1
            d["zero_length_valid"] += int(keys_s == 0)
            d["keys_valid"] += keys_s
            d["writer_reading_differs_valid"] += int(wu != au)
            if wu:
                parts = unit_keys(wu)
                d["writer_units_valid"] += len(parts)
                d["writer_unit_keys_valid"] += sum(len(p) for p in parts)

    def result(self):
        d = dict(self.d)
        v = d["valid"]
        d["valid_fraction"] = v / d["segments"] if d["segments"] else None
        d["mean_keys_valid"] = d["keys_valid"] / v if v else None
        d["writer_reading_differs_fraction_valid"] = d["writer_reading_differs_valid"] / v if v else None
        d["mean_keys_per_writer_unit"] = (d["writer_unit_keys_valid"] / d["writer_units_valid"]
                                          if d["writer_units_valid"] else None)
        return d


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--zips", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--stats", required=True)
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config, encoding="utf-8"))
    scfg = cfg["selection"]
    manifest = json.load(open(a.manifest, encoding="utf-8"))
    tok = Tokenizer(cfg["segmentation"]["max_line_bytes"])

    store = {role: {"work_ids": [], "sha256": [], "keys": {n: [] for n in DEFINITIONS},
                    "units": {n: [] for n in DEFINITIONS}} for role in ("corpus", "reference")}
    tallies = {role: {n: Tally() for n in DEFINITIONS} for role in ("corpus", "reference")}
    dropped = []
    seen_windows = set()
    agg = {"ruby": 0, "ruby_substituted": 0, "x_tokens": 0, "no_frame": 0, "replacement_chars": 0}
    x_examples = {}
    for e in manifest["works"]:
        role = e["role"]
        if role == "corpus" and len(store["corpus"]["work_ids"]) >= scfg["n_works"]:
            continue
        if "sha256" not in e:
            dropped.append({"work_id": e["work_id"], "role": role, "reason": "not fetched"})
            continue
        path = os.path.join(a.zips, e["work_id"] + ".zip")
        if sha256_file(path) != e["sha256"]:
            print("build_segments: %s does not match the manifest" % path, file=sys.stderr)
            return 1
        try:
            text, n_repl = read_zip_text(path)
        except Exception as ex:
            dropped.append({"work_id": e["work_id"], "role": role, "reason": "unreadable: %s" % ex})
            continue
        lines, no_dash = body_lines(text)
        segs, st = segments_of_work(lines, tok)
        if not any(s[3] for s in segs["B0"]):
            dropped.append({"work_id": e["work_id"], "role": role, "reason": "no valid segment"})
            continue
        packed = {n: pack(segs[n]) for n in DEFINITIONS}
        if role == "corpus":
            wins = window_hashes(packed["B0"][0], scfg["duplicate_window_k"])
            if wins and len(wins & seen_windows) >= scfg["duplicate_overlap"] * len(wins):
                dropped.append({"work_id": e["work_id"], "role": role, "reason": "content duplicate"})
                continue
            seen_windows |= wins
            agg["no_frame"] += int(no_dash)
            agg["replacement_chars"] += n_repl
            for k in ("ruby", "ruby_substituted", "x_tokens"):
                agg[k] += st[k]
            for k, v in st["x_examples"].items():
                x_examples[k] = x_examples.get(k, 0) + v
        s = store[role]
        s["work_ids"].append(e["work_id"])
        s["sha256"].append(e["sha256"])
        for n in DEFINITIONS:
            s["keys"][n].append(packed[n][0])
            s["units"][n].append(packed[n][1])
            tallies[role][n].add(segs[n])
        if role == "corpus" and len(s["work_ids"]) % 100 == 0:
            print("build_segments: %d works" % len(s["work_ids"]), flush=True)

    n_corpus = len(store["corpus"]["work_ids"])
    if n_corpus < scfg["n_works"]:
        print("build_segments: only %d usable works (need %d); raise fetch_count" % (n_corpus, scfg["n_works"]),
              file=sys.stderr)
        return 1

    os.makedirs(a.out_dir, exist_ok=True)
    files = {}
    for role in ("corpus", "reference"):
        s = store[role]
        for n in DEFINITIONS:
            path = os.path.join(a.out_dir, "%s_%s.pkl" % (role, n))
            with open(path, "wb") as f:
                pickle.dump({"work_ids": s["work_ids"], "sha256": s["sha256"], "keys": s["keys"][n],
                             "units": s["units"][n]}, f, protocol=4)
            files[os.path.basename(path)] = sha256_file(path)

    stats = {
        "format": "corpus-stats/1",
        "n_corpus": n_corpus,
        "n_reference": len(store["reference"]["work_ids"]),
        "corpus_work_ids": store["corpus"]["work_ids"],
        "reference_work_ids": store["reference"]["work_ids"],
        "dropped": dropped,
        "aggregate_corpus": agg,
        "invalid_token_examples_top": sorted(x_examples.items(), key=lambda kv: -kv[1])[:40],
        "corpus_by_definition": {n: tallies["corpus"][n].result() for n in DEFINITIONS},
        "reference_by_definition": {n: tallies["reference"][n].result() for n in DEFINITIONS},
        "derived_files_sha256": files,
    }
    stats["r_bar"] = stats["corpus_by_definition"]["B0"]["mean_keys_per_writer_unit"]
    with open(a.stats, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("build_segments: %d corpus works, %d reference works, %d dropped, r_bar %.4f"
          % (n_corpus, stats["n_reference"], len(dropped), stats["r_bar"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
