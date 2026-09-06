# タスクリスト

## 準備
- [x] `CLAUDE.md` / `docs/agent-shared.md`（セッション開始時に自動読込）
- [x] `/start-task` で `.steering/20260906-resumption-baseline/` を作成
- [x] `.claude/skills/reproducibility-discipline/SKILL.md` を読む
- [x] `docs/experiment-tracking.md` を読む
- [x] `.claude/skills/verify-before-claiming/SKILL.md` を読む
- [x] ADR-023 の D6 / D7 / D8 ＋ §Migration を読む
- [x] `.claude/skills/browser-verification/SKILL.md` を読む（★ Chrome を使う前に）

## B1 — [P321] から再開ベースラインを実測する
- [x] A-0 到達性の確認（fail fast）
  - [x] figshare API（articles / account / search）→ ⚠️ 全滅（private のため）
  - [x] private-link ページ → ⚠️ curl は HTTP 202/0 バイト・ndownloader は 403
  - [x] 論文本体（arXiv:2105.02162）の Data Availability を一次で確認
  - [x] ⚠️★★★ `observe-dev.online` は **NXDOMAIN**（★ ローカル resolver ＋ Cloudflare DoH）
  - [x] ★ **実ブラウザ（Chrome）で取得成功** → `replication_package_FSE2021.zip`（182,303 B）
- [x] A-2-1 **検算 A**（★ 12 項目すべて緑）
- [x] ★ 活動の対応づけ（`Seeking information` == `Consulting External Resources`）を
      論文 Table 4/5 の**独立 3 統計**で検算
- [x] A-2-2 **R₀ / R₁ を算出**し、差を「放棄の混入量」として報告
- [x] ★ 感度分析（strict/broad × DF1/DF1+DF2 の 4 通り）
- [x] A-2-3 `notes.md` に**外挿の限界**を書く
- [x] A-5 `experiments/` 規約の**読み替え**を明記
- [x] ★ `run.sh` を実行して **exit 0** を確認
- [x] ★ 漏洩検査（`results/*.json` に URL / 動画 ID なし）

## M1 — 「中断 → 再開」の観測を設計する
- [x] ★ 3 粒度の一次を再確認（`features.rs:276` / `loop_step.rs:24` / `intervention.rs:10`）
- [x] ⚠️★★★ アーム分離の**機械的根拠**を取る（`capabilities_gate.py` → `INSTRUMENT_ABSENT` exit 4）
- [x] ★ 計器の実装日（2026-08-24）と収集日（2026-04〜07）を git / ファイル名で確認
- [x] ★ 実行可能性プローブ（125 事象 / 6 名 / 偏り 1〜42）
- [x] ★ 設計に **ADR-023 の 7 制約 ＋ B1 由来の 8 番目**を入れる
- [x] ★ `run.sh` を実行して **exit 0** を確認
- [x] ⚠️ 被験者 ID 抽出の取りこぼし（P000 が `UNKNOWN` に落ちた）を修正して再実行

## 検証
- [x] `--selftest` を 3 状態（正常 / 不在 / 壊れている）で通す
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` を「違反なし」まで回す
- [ ] ★ 「研究名・著者名・年が本文に出ているのに `[Pn]` が無い箇所」を目視で洗う

## レビュー
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] `/cross-review`（★ **コミット後**にパス限定で回す）
- [ ] HIGH 指摘への対応（⚠️★★★ backlog へ punt しない）

## 完了
- [ ] `/finish-task`
