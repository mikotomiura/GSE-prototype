# 分量の記録（paper-write Step 5）

| 日付 | 版（commit） | 対象 | 本文の語数 | 予算 | 測り方 | 備考 |
|---|---|---|---|---|---|---|
| 2026-11-07 | （外枠のみ） | 予算を決めた | — | 7,000 語・図表 4 | — | UMUAI に上限の規定なし。最近の 3 本は本文 約 9.8k〜13.3k 語（venue-umuai-ijhcs.md）。主張に要る仕組みが少ないので paper-write の目安の上の端に置いた。節ごとの予算は outline.md の「Structure and placement」 |
| 2026-11-11 | （本文の草稿 1 版・コミット前） | 本文 main.tex | 序論〜結論 約 4,400 語（texcount の Words in text 4,399・見出し 175・キャプション 194。要旨と Statements を含む合計 4,885） | 6,800 語・図表 4 | `texcount -inc -sum -total main.tex`（節ごとは `-sub=section`: 序論 599・関連 427・方法 983・結果 947・考察 491・限界 502・結論 95） | 予算の内。結果（予算 2,500）と考察（1,000）は薄い。7 語以上の繰り返しは 31 件（`ngram_repeats.py`）で、持ち帰りと推奨を序論・考察・結論でそろえたものが大半。但し書きの重複は「基の平滑は固定」1 件（方法で定義・限界で但し書き） |
| 2026-11-12 | （manuscript round 1 の直し・コミット前） | 本文 main.tex | 序論〜結論 5,086 語（texcount の節ごとの text+headers+captions の和: 序論 537・関連 481・方法 1,500・結果 1,247・考察 581・限界 607・結論 133）。要旨 245 語 | 6,800 語・図表 4 | `texcount -inc -sub=section main.tex`・要旨は `texcount -1` | attack-me round 1 の直し（感度の方法の小節・選びの目的・式・考察の位置づけを足し、Scale の段落と記号化の副の値を外した） |
