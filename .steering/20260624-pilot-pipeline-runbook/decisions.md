# 設計判断 (pilot-pipeline-runbook)

## D-PP1: decrypt は Rust `gse-unpack` bin (age crate) — shell+age CLI ラッパではない
- 選択肢: (A) `scripts/unpack-session.{sh,ps1}` が `age -d` CLI を呼ぶ / (B) Rust `gse-unpack` bin が
  age crate で復号。
- **採用 = (B)**。理由:
  1. **検証ゲートがローカルで回る**: end-to-end smoke は必須受け入れ条件。本機に **age CLI が未導入**
     (`command -v age` 空) のため、(A) だと smoke の decrypt 段が回らず gate が空振りする。(B) は
     cargo + python + duckdb (全て導入済) だけで全段通る。
  2. **transfer-pipeline D1 と対称**: 暗号化側 gse-package が「被験者に外部 CLI を要求しない自己完結
     Rust bin」を選んだ。復号側も同じ思想で揃える方が一貫。
  3. **回帰保護**: `cargo test --features package` で keygen→encrypt→decrypt 往復をテストできる。
- 鍵生成も `gse-unpack --keygen` で内蔵し、研究者が age CLI を別途入れなくても鍵ペアを作れる
  (age crate と age CLI は同一フォーマットなので相互運用可能。将来 age CLI 運用に切替も可)。

## D-PP2: 新タスクは PR #30 (feature/duckdb-join-harness) を基点にスタック
- handoff は「main 基点」を指示するが、依存する `build_analysis_db.py` (#6) は **PR #30 が未マージ**で
  origin/main に存在しない (`git ls-tree origin/main` で不在を確認)。main 基点だと smoke が依存物を
  欠く。
- **採用**: `feature/pilot-pipeline-runbook` を現 HEAD (8d0423b = PR #30 head) から作成しスタック PR 化。
  PR base は #30 マージ後に main へ向ける (または #30 ブランチ宛の stacked PR)。
- 作業ツリーには本タスクと無関係の未コミット変更 (budget.json / 旧 PDF 削除 / tmp_codex_*.txt 等) が
  あるが、これらは触らず、本タスクの新規ファイルのみを stage する。

## D-PP3: sessions.csv は「生成 + 手記入 phase」のハイブリッド
- どの session が pre/post かは研究設計依存で全自動化不能。`gen_sessions_manifest.py` が metrics/ を
  走査して `participant_id,session_id,os,phase` 行を吐き、**phase 列は空**で出す。研究者が pre/post を
  手記入。再生成時は既存の手記入 phase を **保全マージ** (上書きしない) する。
- session_id 規約は build_analysis_db.py と厳密一致: `filename[:-len(".metrics.json")]`、`.range` 除外。

## D-PP4: survey 配置規約 = `survey/*.csv` (P###.csv 推奨)、D8 WoZ 列を最小スキーマに追加
- build_analysis_db は `survey/*.csv` を `union_by_name` で結合し (participant_id, phase) 一意を要求。
  1 ファイル束ね・参加者別 `P###.csv` のどちらでも可。runbook は **参加者別 `survey/P###.csv`** を推奨
  (受領単位と一致、追記が楽)。
- **D8 散歩受容 (WoZ)**: post survey に数値自己申告列を追加 — `walk_done` (0/1)、
  `returned_to_work` (1-5 Likert)、`inconvenience_benefit_accepted` (1-5 Likert)。全て数値で PII 列
  ガード (exit 6) に抵触しない。build_analysis_db は任意 survey 列に対応済 (改修不要)。
- 計測コード (歩数/移動) は作らない (D8: Phase 1 は WoZ + 自己申告で受容性のみ)。

## D-PP6: /cross-review の Codex 系統は縮退 (skip 理由明記)
- `scripts/run-codex-review.sh` が入力を `git diff` (未ステージ working tree) 固定で取得するため、
  本タスクの **staged diff** (`git diff --cached`) をレビューできず、無関係な未ステージ変更
  (旧 PDF 削除・budci 等、`*.docx` 混入) を Codex が参照した。CLAUDE.md の安全ゲート方針
  (proprietary 混入・対象差分不一致) に従い **Claude 単独へ縮退**し本完了報告に skip 理由を明記。
- run-codex-review.sh の `--cached` 対応は **本タスク範囲外** (pipeline 結線が主眼) の tooling 課題。
  code-reviewer + security-checker + cross-reviewer(Claude 側) は完走し CRITICAL 0。

## D-PP5: smoke は bash 単独 (git-bash 前提)、ps1 は作らない
- pilot-smoke.sh は検証/開発ツール。orchestration の実体は cargo (cross) + python (cross) + Rust bin
  (cross) で、bash は薄い糊。Hook 群も全て bash 前提 (Windows=git-bash 必須) の方針に揃え、bash 単独。
- 一時資材 (鍵/平文/age/metrics) は `mktemp -d` 配下で完結し trap で必ず後始末 (data-privacy)。
