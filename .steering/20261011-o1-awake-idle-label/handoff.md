# 引き継ぎ: O1 の「起きたまま作業していない区間」に宣言ラベルが付いたまま残る問題

作成: 2026-10-11（Surface・研究者が自分で O1 を実走している途中の会話から）

## 次のセッションへのプロンプト（そのまま貼る）

```
.steering/20261011-o1-awake-idle-label/handoff.md を読んで、O1 の「機械は起きているが作業していない区間」に
宣言ラベルが付いたまま記録が進む問題を解決する。issue #330（idle trim・.steering/20261008-p1-sleep-trim/）
の前処理に足す形で設計し、研究者の実走データ（O1 を実走中）と「作業していなかった時間」のメモを突き合わせながら作る。
CLAUDE.md の手順に従う: /start-task が先・docs を先読み（下の「先に読む」）・必須 Skill を Read・
レビューは code-reviewer + security-checker を並列・完了時に /cross-review・応答は日本語。
```

## 背景（2026-10-11 に一次で確かめたこと）

- アプリは宣言したタスクのラベルを自分では外さない。日次ローテートでも今の宣言をそのまま次のファイルへ書き直す
  （`src-tauri/src/lib.rs` の `O1Declaration::KeepCurrent`、コメント「宣言を捏造しない」）。
  そのため、席を外していても PC が起きていれば、宣言ラベル付きの `feat` 行が 1 秒ごとに続く。
- 既存の前処理 idle trim（事前宣言 v1.2 §6・issue #330・`gse-replay --features`）が落とすのは、
  `feat` 行の間隔が `idle_trim_min_gap_ms`（60 秒）以上空いた穴の直前と、ファイルの最後だけ。
  スリープで行が途切れた場合が対象で、**行が途切れない「起きたままの放置」は拾わない**。
- 後から切り分ける材料は記録にある: `key` 行・`pointer_bin` 行・フォーカス遷移（`observe*.rs`）。

## 研究者の方針（2026-10-11）

- 記録の時点では直せない課題として扱い、集計の後の前処理で対処する。
- issue #330 で入れた前処理に足す形にし、実走データで回して確かめる。

## 研究者が決めること（Claude は決めない）

1. 「作業していない」とみなす無入力の長さの閾値。読む・考える時間も入力なしの作業なので、短くすると P1 が見たい停滞そのものを削る。
2. 区間を落とすのか、ラベルだけ無効にするのか。
3. 事前宣言 p1-episode は凍結済み（v1.2・`src-tauri/prereg/p1-episode.json` は `frozen`）。足すなら改訂か逸脱の記録か。
   idle trim と同じく、前処理なしと並べて報告する形にするか。

## 先に読む

- `.steering/20261008-p1-sleep-trim/`（requirement / design / decisions / verification）
- `docs/preregistration-p1-episode.md` §6（idle trim）と代償の表
- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` 補訂 4
- `docs/glossary.md` の「無入力の末尾の前処理」
- Skill: `verify-before-claiming`・`reproducibility-discipline`・`data-privacy`（実走データを扱う）・`subagent-delegation`

## 実走データを見ながら作る（研究者は O1 を実走中・2026-10-11）

研究者自身が O1 を回し続けているので、前処理は実データで作りながら確かめる。

- データ: `~/Documents/GSE-sessions/gse_o1_*.ndjson`（2026-10-09 14:20 JST から記録中）。
  記録中のファイルは書き込まれ続けるので、閉じたファイル（`session_end` のあるもの）を使う。
  使うファイルは名前と SHA-256 を記録に残す（先例: `.steering/20261008-p1-sleep-trim/verification.md`）。
- 正解の手がかり: 研究者が「作業していなかった時間」のメモを残す（下の形式）。
  前処理が落とした区間と突き合わせて、取りこぼし（離れていたのに残った）と削りすぎ（読む・考えるのに落とした）を数える。
  ```
  2026-10-11 19:10–19:45 離席（食事）
  2026-10-11 21:00–21:30 PC の前だが別のこと（動画）
  2026-10-11 22:05–22:20 資料を読んでいた（入力なしだが作業中）
  ```
  「入力なしだが作業中」の区間が、閾値を決めるうえでいちばん効く。思い出せる範囲でよく、全部でなくてよい。
- 手順の案: (1) 閉じたファイルで、入力（`key` 行・`pointer_bin` 行）の間隔の分布と、フォーカス遷移の有無を数える。
  (2) 研究者のメモの区間と重ねる。(3) 閾値の候補ごとに、落とす量とメモとの一致を表にする。(4) 研究者が閾値を決める。
- 読み方の制約（idle trim の先例どおり）: 読むのは `gse-replay` の出力（封筒の `provenance` / `config`・onset 行の時刻）と、
  自分で数えた集計値だけ。比較用のスクリプトは repo の外（scratchpad）に置く。
  NDJSON は外部 LLM（Codex を含む）に渡さない。repo にもコミットしない。

## 同じ会話で見つかった別件（このタスクの範囲外・扱いは研究者が決める）

- O1 では送信できたことの知らせが被験者に出ない。提出レシート（`src/App.tsx` の「記録を送信しました」）は
  `g1Mode` のときだけ出し、`get_submission_status` も G1 の参加者 ID で数える。届いたかを見るのは、研究者側の
  O1 受領台帳（`Form_O1/GSE_O1_Ledger.gs`）と `gse-app.log` の `O1 auto-submit` の行だけ。
- 実走中の `gse-app.log` に `keyboard hook may be dead` / `keyboard hook is NOT delivering events` が
  10/10 夜〜10/11 に繰り返し出ている（その間は打鍵が記録されていない）。
