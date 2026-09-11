# タスクリスト

## 準備（2026-09-11 完了）
- [x] `.idea/` 17 本の棚卸し（サブエージェント 6 本で分担調査）
- [x] `docs/` 既存 SSOT の棚卸し（ADR-001〜022・未確定マーカー・禁止用語 15 件）
- [x] ⚠️★★★ **ADR-023〜028 が未マージブランチに既存**であることを発見
- [x] ⚠️★★★ **転帰定義が 3 つ並立**していることを発見
- [x] O1 配布前に手遅れになる観測の特定（P1〜P4）
- [x] `docs/loop-engineering.md` を読み、適用範囲を判断（`decisions.md` 判断 1）
- [x] grill（判断分岐を閉じる）→ `decisions.md` に判断 1〜6 を記録
- [x] issue 分解（001〜009）＋ `_issue-plan.md`（DAG・交差表・verify_level 割当）

## Wave 0 — 取り込み（案 C）
- [ ] **001** アウトカム系（ADR-023/024 + `metrics.rs` +909 + 実験）★ 単独ウェーブ
- [ ] **002** 表現層 ADR（ADR-025〜028 + `expression-channel.md` + `glossary.md` + README）
- [ ] **003** サーヴェイ（`references.md` +112 + `literature/` 3 本）
- [ ] **004** ツール（`secrets-filter.sh` 穴 4 件 + `md2pptx.py` + `svg2png.py`）
- [ ] **005** 提出文書図版（`mitou_submission/`）
- [ ] **006** 残り docs（`agent-shared` / `research-positioning` / `wbs` ほか 7 本）

## Wave 1 — 新規裁定・実装
- [ ] **007** ★最優先 転帰定義の一本化（ADR-009 と ADR-024 の関係を確定）
      ⚠️ `/reimagine` を設計段階で起動する
- [ ] **008** macOS IME の確定 / 放棄判別（P1・O1 配布前に手遅れ）★ 単独ウェーブ
- [ ] **009** 修飾キー同時押下フラグ（P3・O1 配布前に手遅れ）
      ⚠️ 007 の裁定結果を確認してから着手（不要になる可能性がある）

## 各 issue 共通の作業
- [ ] ⚠️ **`acceptance.sh` を書く**（`_issue-plan.md` の自己検査で未実施と判明）
      002 / 003 / 005 / 006 は「取り込まなくても lint が緑」になりうる
- [ ] `code-reviewer` + `security-checker` を**並列**起動（009 は `security-checker` 必須）
- [ ] `/cross-review`（Codex + Claude の独立レビュー）— **各タスク完了時に必須**

## Wave 0 完了後
- [ ] `issue-slicing` を再度回して 010 以降を分解（`_issue-plan.md` の「未分解の残り」を参照）
- [ ] `blockers.md` の起票 2 件を処理

## 完了処理
- [ ] `design.md` の最終化
- [ ] `/finish-task`
- [ ] git commit（⚠️ `git add -A` / `git add <dir>` **禁止**。パスを明示して staging する）
