"""Text -> segments under the G1 rule (preregistration.md, "原文とおとりの区間").

The G1 app (v0.1.29 and older) records every punctuation and symbol key as `other`, so the boundaries are the
characters typed with those keys: 、，,。．. , the one-key symbols of the earlier experiment except the ones typed
with Shift and a digit key (config.json text_rule.counted_symbols), and the long-vowel mark ー inside a reading.
A newline is not a boundary (Enter is pressed to confirm conversions too). Digits, Latin letters and the counted
symbols are one key each. The reading, the ruby handling, the body lines and the key table are the earlier
experiment's (build_segments.py, romaji_table.py), imported after a SHA-256 check.
"""
from common import prior_module


class G1Rule(object):
    def __init__(self, cfg):
        self.bs = prior_module("build_segments", cfg)
        self.rt = prior_module("romaji_table", cfg)
        bs = self.bs
        counted = frozenset(cfg["text_rule"]["counted_symbols"])
        unknown = counted - bs.SYMBOL_ONE_KEY
        if unknown:
            raise SystemExit("g1rule: counted_symbols outside the one-key symbols: %r" % sorted(unknown))
        self.boundary = frozenset(bs.COMMA_CHARS | bs.PERIOD_CHARS | (bs.SYMBOL_ONE_KEY - counted))
        self.max_line_bytes = cfg["text_rule"]["max_line_bytes"]
        self._tok = None

    @property
    def tok(self):
        if self._tok is None:
            self._tok = self.bs.Tokenizer(self.max_line_bytes)
        return self._tok

    def token_items(self, surface, reading):
        """[('U', units) | ('B', None) | ('X', None)] for one token, in order."""
        bs = self.bs
        if surface == "" or all(ch in bs.WHITESPACE for ch in surface):
            return []
        if all(bs.char_level_ok(ch) for ch in surface):
            out = []
            for ch in surface:
                if ch in bs.WHITESPACE:
                    continue
                out.append(("B", None) if ch in self.boundary else ("U", "#"))
            return out
        if all(bs.is_word_char(ch) for ch in surface) and bs.is_kana_reading(reading):
            out = []
            for i, piece in enumerate(bs.kata_to_hira(reading).split("ー")):
                if i:
                    out.append(("B", None))
                if piece:
                    out.append(("U", piece))
            return out
        return [("X", None)]

    def items_of_lines(self, lines):
        """Items of the body lines (ruby removed: the attacker's plain text), the lines joined without a boundary."""
        for ln in lines:
            plain = self.bs.parse_ruby(ln)[0]
            for begin, end, surface, reading, pos in self.tok.tokens(plain):
                for it in self.token_items(surface, reading):
                    yield it

    def segments(self, items):
        """[(keys or -1, units)] from items. A segment holding an X item is invalid (-1). The segment opened
        after the last boundary is dropped when it is empty (nothing is typed there)."""
        segs = []
        units, invalid = [], False
        for kind, payload in items:
            if kind == "B":
                segs.append((units, invalid))
                units, invalid = [], False
            elif kind == "U":
                units.append(payload)
            else:
                invalid = True
        segs.append((units, invalid))
        if not segs[-1][0] and not segs[-1][1]:
            segs.pop()
        out = []
        for units, invalid in segs:
            s = "".join(units)
            out.append((-1 if invalid else self.rt.count_keys(s), s))
        return out

    def segments_of_lines(self, lines):
        return self.segments(self.items_of_lines(lines))


def copy_lines(path):
    """The 20 lines under '## 原文' of copy.md."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    body = text.split("## 原文", 1)[1]
    return [ln for ln in body.strip().splitlines() if ln.strip()]
