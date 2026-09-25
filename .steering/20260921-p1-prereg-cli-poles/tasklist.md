# タスクリスト

> ★ 実行の形は **混合**（判断 12）—— 【1】は本セッションの対話、【2】以降は **新セッションで Loop**。

## 準備（★ 本セッション・2026-09-21・Opus）

- [x] ハンドオフ `.steering/_handoff/next-session-step6-prereg-cli-poles.md` を読む
- [x] ⚠️ **PR #221 の merge を確認**（★ `6a70f5b`・merge 済み）
- [x] ⚠️ **004 / 006 が既に merge 済みであることを確認**（★ `6f5bb9f`〜`9eb539d`・2026-09-20/21）
      → ★ ハンドオフ §1 の「⑥ と ④ のどちらを先にするか」は**消滅**（⚠️ `tasklist.md` の `[!]` は更新漏れ）
- [x] 一次を読む: `decisions.md` 判断 25 #13 ／ `blockers.md` 起票 7 / 11 / 12 / 13 / 14 / 15 / 16 / 20 / 21 ／
      ADR-030 D2 / D3 / D4 / D8 / D10 ＋ **補訂 1** ／ `preregistration-v0.3.md` ／ roadmap §3
- [x] ⚠️ **一次の食い違いを 1 件発見**（「P1 *前*」 vs 「P1 の実データで」）→ 判断 1 で閉じた
- [x] **grill**（★ 判断分岐 12 件を研究者が裁定 → `decisions.md` 判断 1〜12）
- [x] ⚠️ **一次で確かめた事実**: `key.mod` 未実装 ／ `meta` に `os` が無い ／
      `capabilities` に修飾キー項目が無い ／ **`collect_key_events` が release を捨てている** ／
      `delete_time_range` の検査は `from_ms > to_ms` だけ ／ `RecordingControls.tsx` は `datetime-local`
- [x] `docs/glossary.md` に確定用語 5 件（観測区間 / 極 / 極の適用可否 / 事前宣言文書 / 凍結 JSON）
- [x] `requirement.md` / `design.md` / `decisions.md`

## 【1】事前宣言文書 ＋ 凍結 JSON（★ 本セッションの対話・⚠️ 凍結は不可逆）

- [x] `src-tauri/prereg/p1-episode.json`（★ 運用値 8 項目 ＋ 探索空間 ＋ 役割 ＋ 手続き）
- [x] `docs/preregistration-p1-episode.md`（§0 位置づけ / §1 運用値 / §2 探索空間 / §3 読み方 / §4 代償 / §5 主張しないこと）
- [x] ⚠️★★★ **§2 探索空間を研究者へ提示し、承認を取った**（★ 判断 15 → 4 点とも草案どおり承認）
- [x] `scripts/check_prereg_parity.py`（★ **陽性対照つき** —— 変異 7 件すべてが赤）
- [x] ⚠️ 検査を**実ファイルで通しで回した** —— ★ **自分の穴を 2 件掘り出した**
      （従属マーカーの部分一致 ／ 子プロセス stderr の cp932 デコード失敗）→ `decisions.md` 末尾に記録
- [x] `docs/preregistration-v0.3.md` にリンク 1 行 ／ `docs/agent-shared.md` のリンクハブに 1 行
- [x] `docs/glossary.md` に確定用語 5 件
- [x] コミット（⚠️ `git add -A` / `git add <dir>` は**使わない** —— ファイル名を明示） ★ `1cd25ce`
- [x] ⚠️★★★ **`status` は `draft` のまま**（★ 2026-09-25 `f5163a6` で frozen）（★ 判断 16）—— 【2】が end-to-end で通った時点で `frozen` に上げる。
      ★ **それは【2】の issue の最後の AC である**

## 分解（★ 本セッション・Opus）

- [x] `to-issues`（`issue-slicing` Skill）で【2】〜【7】を縦切り issue に分解
      → `issues/00X.md`（テンプレ `.steering/_template/loop-issue.md`）
- [x] `_issue-plan.md`（★ DAG / Allowed Files 交差表 / 自己検査）
- [x] `_loop-config.json`（⚠️ **`base_branch` を本タスクの作業ブランチに pin** ——
      ★ 規則は `.steering/_template/loop-config.README.md`）
- [x] ⚠️ **`--dry-run` で config / DAG / acceptance の検出を確認**
      ⚠️★★★ **2026-09-25 実行セッションで発見**: 初回の dry-run は **全 issue が `deps=[]`** だった —— ★ `- **001**（…）` の太字が `loop-run.sh` `issue_deps_raw` の正規表現（行頭 `- 001`）に当たらず、**依存が黙って全部落ちていた**（⚠️ `parallel: 2` なら 003 が 001 と同時に走る）。→ ★ 003〜009 の箇条書きを `- 001 （…）` に直し、DAG が §2 と一致することを再 dry-run で確かめた
- [ ] ⚠️★★★ **issue ファイルだけを読んで実行が成立するか**を自分で確かめる（★ 成立しないなら分解が失敗）

## ⚠️ 分解セッションはここで終わる

- [x] `/clear` する
- [x] **新セッション**で Loop を始める
      （★ C: `bash scripts/loop-run.sh .steering/20260921-p1-prereg-cli-poles` ／
       B: `/model sonnet` → `/loop-orchestrate` ／
       A: `bash scripts/loop-spawn.sh --task <task> <id> [short]`
       ⚠️★★★ **`--task` を落とすと fail-closed で止まる**）
- [ ] ⚠️ **解決した base の provenance を読む** —— ★ 「既定ブランチからの乖離コミット数」が
      0 でないときは**意図した pin か確かめる**（★ 2026-09-21 に 38 コミット前から切られた実測がある）

## 実行（★ 別セッション・Sonnet）

- [x] 【2】CLI 注入（凍結 JSON を既定 ＋ `--feature-config` ＋ `--set`・封筒 `config` の拡張）
- [x] 【3a】`T1a` の 30 秒窓（★ `features.rs` の `pub const` 化が**先**・⚠️ 振る舞いを変えない）
      ＋ `003-acceptance.sh` の「3 値が同値」検査の**置き換え** ＋ 起票 11 を閉じる
- [x] 【3b】極の器（`--pole` ＋ `Pole` enum ＋ `pole_applicable` ＋ `theta_sample_n`）
- [x] 【3c】極 B（`collect_pointer_bin_timestamps` ＋ 抑制区間 ＋ 評価区間の合成）
- [x] 【3d】極 M+（`collect_modifier_intervals` ＋ カウント方式 ＋ 挿入系の写像
      ⚠️ **`−1` は外さない** —— `Ctrl+Backspace` の陰性対照）
- [x] 【4】削除幅の制約（`MIN_REDACTION_WIDTH_MS` ＋ 広げて消す ＋ **陽性対照** ＋ UI 文言 ＋ 削除台帳）
- [x] 【5】IME 変換中の onset 頻度カウンタ（★ 抑制はしない。数えるだけ）
- [x] 【6】起票 21（多 onset の計算量の門・⚠️ 1 極あたりで置く）
- [x] `scripts/run-features-all-poles.sh`（★ 3 極の実行漏れを防ぐ）

## テスト

- [x] 各 issue の AC に 1 対 1 の test（★ `cargo test --workspace` は **`src-tauri/` から**）
- [x] ⚠️ ゴールデン（★ snapshot ファイル 6 本・`minimal.json` 内 15 snapshot）が **byte-equal**（★ `--snapshot`。動いたらリファクタが失敗している）
- [x] `check` / `clippy` / `fmt` / schema parity が exit 0
- [x] ⚠️★★★ **「検査の検査」5 点**（★ `design.md` §テスト戦略。⚠️ 省略しない）

## ドキュメント

- [x] 【7】`docs/adr/ADR-030-...md` に **補訂 2**（⚠️ **本文は 1 文字も書き換えない**）
- [x] `docs/verification-runbook.md` に 3 極を回す手順
- [x] `.steering/20260914-mhd-feature-offline-tiers/blockers.md` の
      起票 7 / 11 / 12 / 13 / 14 / 15 / 16 / 21 に **✅ 是正済み**を追記（⚠️ 起票本文は書き換えない）
- [x] 同 `tasklist.md` の `[!] 004` / `[!] 006` の**更新漏れ**を直す（★ 2026-09-21 に merge 済み）

## レビュー

- [x] `code-reviewer` ＋ `security-checker` を**並列**（⚠️ `model` を毎回明示・入れ子禁止・範囲と禁止事項・締切）
- [x] HIGH / MEDIUM への対応
- [x] ⚠️★★★ **`/cross-review`（Codex）を 2 巡**（★ 2026-09-25 実施・gpt-6-astra・パス限定 3 回〔1 巡目 A/B・2 巡目〕・146699 tokens。指摘 12 件 → 研究者裁定 3 件〔判断 27〜29〕・是正 6 件・偽陽性 1 件）
      （1 巡目 = 自文書・他文書の矛盾 ／ 2 巡目 = 自分が足した規則の境界条件）
      ⚠️ **「規則」と「その実装」を同じ diff 範囲に入れる**（★ 2026-09-21 の偽陽性の原因）
      ⚠️ **Codex 予算**: `.codex/budget.json` の上限は **300000**。`today.tokens_used` が 432937 のままなので
      **日付が変わるまで予算ガードで止まる**（★ それが意図どおり）。⚠️ **上限を勝手に引き上げない**
- [x] ⚠️ ブロックされた場合は **skip 理由を完了報告に明記**する

## 完了処理

- [ ] `_loop-retrospective.md`
- [ ] `design.md` / `decisions.md` の最終化（`/finish-task`）
- [ ] ⚠️ **main へのマージは研究者判断**
