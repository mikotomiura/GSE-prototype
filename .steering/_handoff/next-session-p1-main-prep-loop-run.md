# 次セッション — D. P1 本体の準備: Loop の実行（issue 001〜010）

> 作成: 2026-09-26（分解セッション・Opus）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260926-p1-main-prep/` の issue ファイルと `_issue-plan.md`。
> ★ 分解と実行は別セッション（`docs/loop-engineering.md`）。**issue ファイルだけを読んで実行が成立すること**が契約 —— 成立しなければ分解の失敗として記録し、推測で埋めない。

## §0 打ち込む用（★ `/clear` の後、`/model sonnet` にしてから貼る）

```
.steering/_handoff/next-session-p1-main-prep-loop-run.md を読んで、D（P1 本体の準備）の Loop を実行してください。

ブランチ: feat/p1-main-prep（分解はコミット済み）。モード C:
  bash scripts/loop-run.sh .steering/20260926-p1-main-prep
★ 初回は安い issue 1 本を parallel=1 で回して基盤を確かめる（例: --issues 009）。その後、残りを回す。
★ ウェーブと並列の根拠は .steering/20260926-p1-main-prep/_issue-plan.md §2 / §3。

⚠️ 実データ（NDJSON・metrics・--features の出力）を開かない・集計しない・試しに 1 本回さない。入力は repo の合成 fixture だけ。
⚠️ docs/preregistration-p1-episode.md（v1.1）と src-tauri/prereg/p1-episode.json を書き換えない。PG-1 の値を決めない。
⚠️ worker が done と言っても信じない。merge 前にメインが clean な checkout で acceptance 10 本（issues/00X-acceptance.sh）と、
   過去の acceptance 3 本（20260921-p1-prereg-cli-poles/issues/003・008、20260914-mhd-feature-offline-tiers/issues/003）を正しい終了コードで回す（起票 P1-H 未是正）。
⚠️ issue が Stop Condition に当たったら、Allowed Files を広げて通さない。止めて研究者に戻す（特に 008 の「O1 の実ログが feat 行を持たない経路」）。
★ 完了時は /finish-task（code-reviewer ＋ security-checker を並列・model 明示・範囲/禁止/締切つき → /cross-review 2 巡・パス限定・Codex gpt-6-astra）
  → git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 確認）を自動で。
⚠️ git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/（別トラック）は触らない・コミットしない。
⚠️ .codex/budget.json は台帳（git checkout -- で戻さない・記帳はコミットに含める）。
応答は日本語。
```

## §1 状態（2026-09-26・分解セッション終了時）

- ブランチ `feat/p1-main-prep`（main = `9803b3e7` から）。分解の成果（requirement / design / decisions / tasklist / `_issue-plan.md` / `_loop-config.json` / `issues/001〜010` ＋ acceptance）と `docs/glossary.md` の 5 語をコミット済み。**未 push**。
- 研究者裁定: `decisions.md` 判断 1〜15・18（＋ #8 の再確認）。分解時の Opus 判断: 16・17・19・20。
- 前提の実測: 004 / 008 が呼ぶ過去 acceptance 3 本は分解時点で緑（`tasklist.md`）。

## §2 ⚠️ 見落としやすい点（issue に書いてあることの再掲）

- Python の issue（001〜006）は `ci.yml` の同じ step にモジュール名を足すので**直列**。Rust（007 → 008 → 010、009 は独立）と並列にできる。
- 003 のテストは duckdb が要る。CI では `Install duckdb` より後で走ること（前にあると全件 skip の緑）。
- 008 は fixture 19 本中 11 本（`feat` 行 0 本）の `T1a` を `null` に変える。過去 acceptance 2 本は「一時コピーに 1Hz の `feat` 行を足す」形に張り直す（緩めない）。
- 選択器（005）は **metric 表まで**。集約・同点の崩し・最終選択は実装しない（判断 18・v1.2 で宣言してから）。

## §3 やらないこと

- 実データに触れる・PG-1 を通す・凍結物を変える・転帰を定義する・`experiments/<日付>-…/` を作る・C トラック
