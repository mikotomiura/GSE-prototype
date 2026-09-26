# 次セッション — B. P1 事前宣言の新版 v1.1（`docs/preregistration-p1-episode.md`）

> 作成: 2026-09-26。⚠️★★★ **このメモを一次資料にしない。** 下の「一次」を開いて状態を確かめ直すこと。
> ★ 研究者と合意した順番（2026-09-26）: A（Loop 基盤・**完了** PR #224 / #225）→ **B（本メモ）** → D（P1 本体の準備）→ O1 / G1 の収集中に C ＋ 研究案。
> ★ **B は実データを 1 件も見る前に凍結し終える**（forking paths 排除）。D はこれを待っている。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-prereg-p1-episode-v1-1.md を読んで、B（P1 事前宣言の新版 v1.1）を実施してください。

中身: 凍結済みの docs/preregistration-p1-episode.md（v1.0.0・frozen）の新版を切るか、切るなら何を入れて再凍結するかを決め、実データを見る前に凍結し終える。
  出発点: 「併せて出力に載せるもの」表に ime_overlap が無い（ADR-030 補訂 2 項目 9 が規範上の置き場・新版を切るかは研究者判断）。
  ほかの候補は引き継ぎメモ §2 の表（★ 入れるかどうか自体を grill で決める）。

⚠️ /start-task が先（grill は Opus・判断分岐が閉じるまで）。文書のタスクだが Loop には分解しない（小さい）。
⚠️ 凍結文書（v1.0）を書き換えない。新版は §0 の凍結規約どおり「変更点と理由を明記して再凍結」。
⚠️ 長い一次資料（ADR-030 補訂 2・事前宣言 §2）を 1 節だけ読んで代表させない（verify-before-claiming ルール 7 / 8）。
⚠️ 実データ（NDJSON・metrics）を開かない・集計しない（PG-1 は WP1 の yield が出てから。本タスクの範囲外）。
★ 完了時は /finish-task → git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 確認）を自動で。
⚠️ git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/（別トラック）は触らない・コミットしない。
⚠️ .codex/budget.json は台帳（git checkout -- で戻さない・記帳はコミットに含める）。/cross-review は Codex gpt-6-astra。
応答は日本語。
```

## §1 状態（★ 2026-09-26 実測）

- main = `6aaa45f1`（PR #225 merge・CI 発火確認済み）。作業ツリーの未追跡は別トラックの `.steering/20260921-media-expression-theory-audit/` だけ。
- 凍結の対象:
  - 文書 `docs/preregistration-p1-episode.md` —— ステータス行「凍結 (frozen)（2026-09-25）」。§0 の凍結規約「凍結後の本書の変更は禁止…変更が必要なら**新バージョンを切り**、変更点と理由を明記して再凍結する」
  - 値の SSOT `src-tauri/prereg/p1-episode.json` —— `"version": "1.0.0"`・`"status": "frozen"`・`"document"` が上の文書を指す。`gse-replay --features` がこれを既定として読む
  - 一致検査 `scripts/check_prereg_parity.py`（文書と JSON の値の一致。★ 新版の置き方次第でこの検査の対象も変わる）
- ⚠️ 凍結文書の中でも **§2（探索空間・選択手続き）の見出しは「草案 —— 研究者の承認待ち」**のまま（★ 一次で確かめること）。

## §2 ★ v1.1 に入れる候補（⚠️ 入れるか・どう書くかは grill で決める。ここは材料の列挙だけ）

| # | 候補 | 一次 |
|---|---|---|
| 1 | **「併せて出力に載せるもの」表に `ime_overlap`（IME 変換中の onset 頻度）** —— 出発点 | ADR-030 補訂 2 項目 9（1318 行付近）／ `.steering/20260921-p1-prereg-cli-poles/issues/009.md` 158・173 行 |
| 2 | `ime_overlap` は「下限」ではなく**両方向の誤差がある観測値**（Windows は下限として読める） | 前タスク decisions.md 判断 29 ／ 補訂 2 |
| 3 | 極 B / 極 M+ の onset は baseline の部分集合 / 上位集合を**保証しない** → 上下界は両極の G2 の min / max | 判断 25・28 ／ 補訂 2 |
| 4 | §2（探索空間・選択手続き）の「草案」表記の扱い（承認して凍結するか・草案のまま残すか） | 事前宣言 §2 見出し |
| 5 | P1-A: 凍結既定 config（`warmup_count=100`）では restart の非退化検査が走らない —— 事前宣言に書くことか、コード / fixture 側の宿題か | 判断 19・起票 P1-A |
| 6 | P1-F: `--set q=…` が従属変数 `warmup_count` を連動させない —— 探索プロトコルの記述に関わるか | 起票 P1-F ／ 001.md「未解決 4」 |

★ grill で閉じるべき分岐の例（固定リストではない）:
- そもそも新版を切るか（切らずに ADR 補訂 2 の置き場で足りるとするか）
- 新版の置き方: 同じファイルに版を重ねるか・別ファイル（例 `…-v1.1.md`）か／ JSON の `version` を上げるか・値が変わらないなら JSON は据え置くか／ `document` の指す先と parity 検査の対象
- 表への追加は「値」ではなく「出力」なので、凍結規約上 v1.1（小）で足りるか

## §3 ⚠️ やらないこと

- 凍結文書 v1.0 の本文を書き換える（新版で上書きを明記する）
- 実データを見る・PG-1（一人あたり episode 数の下限）の値を決める（★ WP1 の yield が出た直後の別ゲート）
- D（P1 本体の解析の段取り）に踏み込む
- コード（`gse-replay` の出力列など）を変える —— ★ もし grill で必要と分かったら、本タスクの範囲かを研究者に確認する（★ `ime_overlap` は issue 007 で**既に出力されている** —— `src-tauri/src/analysis/feat_offline/mod.rs:1006` 付近で `stall_onset.ime_overlap` へ配線・2026-09-26 確認。⚠️ retrospective（`t0` より後の `ime_shadow` 行に依存しうる）である点は同 169 行）
