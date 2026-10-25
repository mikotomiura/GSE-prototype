# 引き継ぎ: C（TRACE）—— 較正の 2 回目（12 月）と一致の出し方

作成 2026-10-25（Mac）。前提は判断 107（`.steering/20261017-ai-fatigue-c-outline/decisions.md`）。始める前に、1 回目の冊が戻っていること（研究者に聞く）と、1 回目の終わりから 4 週間以上たっていることを確かめる。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。決めてほしいことは AskUserQuestion で推奨と理由を添えて聞く。
- 一次資料は TRACE の `registration-en.md` の GSRR-44（2 較正・5 AI の下書き）・GSRR-46・GSRR-65 と `codebook-c2b-en.md`。登録と添付は書き換えない。
- 符号化するのは研究者。私は 1 回目の値を見ない・研究者に見せない（2 回目は 1 回目を見ずに）。一致を出すまで 1 回目の冊は開かず、構造と SHA-256 だけを扱う。

## 1. 1 回目が戻ったら（11 月中）

1. Drive の `TRACE/TRACE_calibration/pass1/` の 2 冊（符号化の冊・案内と ZEF の冊）の SHA-256 と大きさを記録し、手元 `~/Documents/TRACE/calibration/pass1-returned/` に読み取り専用で写す。値は開かない。
2. 符号化の冊を `c_coding_book.py export <写し> --out ~/Documents/TRACE/calibration/codes/` で書き出す（`*_coder1.csv`）。止まったら、どの欄かだけを研究者に伝える（値は読まない）。書き出した CSV の SHA-256 を記録し、ここで 1 回目を閉じる。
3. ZEF の表は冊の外なので、A〜J 列だけを `zef_coder1.csv` に書き出す小さな脚本を作る（値を表示しない）。

## 2. 2 回目の冊（12 月・1 回目から 4 週間以上後）

- `c_coding_book.py make --coder coder2 --ids <並べ替えた 11 件> --out ~/Documents/TRACE/calibration/pass2` → 名の頭に『較正2回目』を付ける。1 回目の値は入らない（道具の決まり）。
- 順: 本番（GSRR-44 の 3）は seed 20261020 の `random.shuffle` で並べ替える。較正の順は登録に決まりが無いので、本番と同じやり方にするか研究者に聞く（推奨: 同じやり方で、seed は本番と別の値を記録して使う。本番の seed を較正で使うと本番の順が前もって知れる）。
- 案内の冊: `make_calibration_guide.py --pass 2 --coder coder2 ...`（ZEF の表は空・項目の順は変えない）。
- Drive の `TRACE_calibration/pass2/` に置く。

## 3. 一致の出し方（2 回目が戻った後）

1. 2 回目も 1 と同じく書き出す（`*_coder2.csv`）。
2. `uv run --with openpyxl python c_synthesis.py --agreement ~/Documents/TRACE/calibration/codes`（既定の組は coder1 と coder2。集合は exploration）。
3. 登録の単位ごとに、比べる数が 5 以上で 80% に届かない単位を並べる。比べる数が 5 未満の単位は一覧にする（較正されない・GSRR-65）。ZEF の 15 項目は表の一致を別に出し、コードブックの例と重なる項目を注記する。kappa は報告するが基準ではない。
4. 改訂の候補は 2 回の食い違いだけから作り、拠った記録の ID を添える。例題の 17 点（`worked-examples/findings.md`）と主の尺度の `instrument_id` の決まり（判断 107）は、食い違いに現れたものだけを根拠にできる。主の尺度の決まりは列の辞書への追記として研究者に聞く。
5. ここで初めて C5 の AI の照合（`~/TRACE-calibration-c5/out/matches.csv`）を開いてよい。開く前に SHA-256 が `0aba2d0a78609e060b8b871274b8fbdda942b2993b7c54adf7008a400d71507d` であることを確かめる。人と AI の一致は報告だけで、較正の基準ではない。C4f の AI の下書きは較正では作っていない。

## 4. 並行して残っていること（このタスクの外）

- 例題 W01〜W04 は判断 110 で確定した。改訂の候補（本番の前）: 主の尺度の `instrument_id` = main（判断 107）、language は ISO 639-1 の 2 文字（判断 110）。
- h2 の取り込みは済み（判断 106）。b23〜b39 の 2 人で決める記録を `next-session-ai-fatigue-c-stage2-close-b01-b22.md` と同じ手順で出す。
