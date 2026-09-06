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
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を「違反なし」まで回す
- [x] ★ 「研究名・著者名・年が本文に出ているのに `[Pn]` が無い箇所」を目視で洗う（★ 該当 0）

## レビュー
- [x] `code-reviewer` + `security-checker` を**並列**起動
- [x] `/cross-review`（★ コミット後にパス限定で回した・指摘 5 件）
- [x] HIGH 指摘への対応（⚠️★★★ backlog へ punt しない）

## 完了
- [x] `/finish-task`

## レビュー結果の消化（★ 全件この タスク内で消化した）

| 出所 | 件数 | 消化 |
|---|---|---|
| `code-reviewer` | HIGH **2** / MEDIUM **7** / LOW 8 | ★ HIGH・MEDIUM **全件**。LOW は 2 件（絶対パス / gloss の留保） |
| `security-checker` | HIGH **2** / LOW 1 | ★ **全件** |
| `/cross-review`（Codex） | 中 **3** / 低 1 / テスト不足 1 | ★ **全件** |

### ⚠️★★★ 系統を分けた意味があった（★ 3 系統が別々の型を見つけた）

- **`code-reviewer` だけが見つけた**: `set -e` 下で `RC=$?` に到達しない silent failure ／
  検算が赤のとき `metrics.json` を黙って上書きする ／ `AWAY_IDLE_MS` の手写しに検査が無い
- **`security-checker` だけが見つけた**: ⚠️★★★ **`file_id` は不可逆ではない**
  （`sha256(ファイル名)[:8]` を **76/76 総当たりで復元された**）／実セッションファイル名の混入
- **Codex だけが見つけた**: ⚠️ **ソートが元順の異常を隠す** ／ p90 の定義 ／
  畳み込みの**時間的**不変条件が無い

★ 前セッションの教訓「独立レビューは系統を分ける意味がある」が、本タスクでも再現した。

## ⚠️ 本タスクの範囲外として残したこと（★ 研究者へ申し送り）

1. ⚠️★★★ **`scripts/capabilities_gate.py` の `file_id` は不可逆ではない。**
   ★ `experiments/_template/README.md:57-61` は逐語で「**不可逆な `file_id`**」と約束しているが、
   **32bit 切り詰め ＋ ソルト無し ＋ 低エントロピー入力**（擬似 ID ＋ 秒単位の日時）なので
   **総当たりで戻る**（★ レビューが 76/76 を数分で復元した）。
   → ★ 本タスクでは **自分の `results/capabilities.json` から `files[]` を落とす**ことで塞いだ。
   ⚠️ **repo 全体の是正（ソルト付きハッシュにする / 約束の文言を直す）は別タスク**である。
   ★ 幸い **`capabilities.json` を既にコミットしている実験は 1 つも無い**（★ 実測）。
2. ⚠️ **M1 の Step 2b（アウトカム本解析）は未実装**（★ `arm1/notes.md` §7 の限界を読んでから）。
