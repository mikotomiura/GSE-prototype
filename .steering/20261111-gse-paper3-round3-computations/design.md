# 設計

## アプローチ
3 つの計算はどれも、前の試験のコードを写さずに SHA-256 で照らして読み込み、新しい部分（最頻値の評価・候補への追加・複製の追加）だけを書く。条件と読みの形をコードより前にコミットし、門（selftest・変異・再現の照らし）を本計算の前に通す。

| 計算 | ディレクトリ | 機械 | 新しく書くもの | 再現の照らし |
|---|---|---|---|---|
| 1 合成の分解 | `experiments/20261111-sensitivity-mode-decomposition/` | Mac | 作り直し（共通と w を除く共通）・最頻値の評価・a/b/c・形・読み | P-REPRO（pool と g が sens の JSON とビット一致）・P-SAME（2 段の c の中央値が sens の summary と同じ） |
| 2 CS1 の種 | `experiments/20261110-per-person-sensitivity/`（追記） | Mac | `run_add.py`・`run_add.sh`・`sens_report.py` の 2 群 | P-REREP（今のコードで複製 00 を回し直してビット一致）・足さないときの report がバイト同じ |
| 3 最頻値を候補と列に | `experiments/20261111-mode-in-selection/` | HP Z2 | 候補の並べ・選び・相手の列・形 M/S/N | P-REPRO（mode の pickle に mode の集計を当て直して summary と同じ） |

## 変更対象
- 新しいファイルだけ。`run_synth.py`・`synth.py`・`pinned.py`・`analysis.py`（sens）と mode・tau-extend の scripts は変えない（計算 1 と 3 がハッシュで照らす）。
- `sens_report.py` だけ直す（2 群の照らし）。

## テスト戦略
- 各計算の selftest と変異（名指しの門が赤）。計算 3 は Mac と HP Z2 の両方で selftest と変異を回す。
- 計算 1 は本計算の最初の複製で P-REPRO が通ることを試しに確かめてから全体を回す（値は見ない）。
- code-reviewer と /cross-review（Codex。合成のコードと条件だけを送り、実データ・書き手ごとの値は送らない）。
