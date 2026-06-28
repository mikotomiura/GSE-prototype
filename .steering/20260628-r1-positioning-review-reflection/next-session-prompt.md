# 次セッション用 開始プロンプト（R1 研究ポジショニングへレビュー指摘を反映）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> **docs のみの編集**。Phase 1 のセッション収集コード・NDJSON schema は変更しない。
> **Physical Anchor の指摘 C は除外**（PA は実装予定のため §9 等の PA 記述はいじらない）。

## 0. 一言ゴール
2026-06-28 に後付け生成した研究トラック docs（Phase R1・未コミット）へ、Codex+Claude 二重レビューの
指摘 **A・B・D・E・F・G・H・I・J・K・L**（C 除く）を反映し、研究主張の妥当性・整合・非 overclaim を満たす。

## 1. 最初にやること（必須）
1. `.steering/20260628-r1-positioning-review-reflection/` の requirement.md / design.md / decisions.md / tasklist.md を読む。
2. **decisions.md「未決 A-1」**（p_stuck の正当化方針: (a) 象限 high-Q1×low-Q2 を stuck 相当とみなす / (b) 補助 self-marker / (c) X1 は X/Y 二軸妥当性に限定）を**ユーザーに 1 問だけ確認**してから編集に着手。
3. `/start-task` 不要（本 steering が既にある）。実装着手前に design.md の変更対象を再確認。

## 2. 確定済み前提（触らない・decisions.md 参照）
- headline は **B「Stuck 検出 × 介入タイミング」主役**、A(System)/C(Vision) 入れ子。
- GSE は F/I/S を 3 値で実用分類**しない**。Need=p_stuck の 1 次元 Stuck 検出、Opportunity=介入タイミング。
- MhD=検出モデル総称、Stage1=ルールベース HMM。references は P/V 名前空間（renumber 禁止）。
- **A は「取った後の測り方/解釈」の問題で収集不変**（schema_dto.rs:82 で p_stuck はログ済、calibration_eval は X/Y のみ集約）。

## 3. 反映する指摘（design.md の表が一次・C は除外）
A-1 X1 の橋渡し（C-index は X/Y 二軸を検証・p_stuck は別）/ A-2 criterion label 限界＋軽減 / B H-X2 を探索的へ /
D H-Y 交絡＋追加アウトカム / E §4 に「本文非保存制約下の統合プロトタイプ＋前向き較正」を新規性核 /
F glossary に MhD 登録 / G GATE1 延期の整合 / H C-index 0.65 根拠 / I §1 から [P11] 除外 /
J [P15] 測定点のみ / K 真の null/abandon 条件 / L 参照記号訂正＋GATE↔PreReg を glossary。

## 4. ground truth（突合先）
docs/functional-design.md・glossary.md / Form_Phase1/ユーザー検証_codex-review_v0.4.docx.md /
docs/wbs_検証用docs/*.docx（textutil 変換）/ docs/[提案プロジェクト補足資料]GSE_proposal_参考文献.md /
docs/preregistration-v0.3.md。

## 5. 完了基準
- 全 inline [Pn]/[Vn] が references.md に実在（grep 集合比較）／overclaim 語ゼロ（grep）。
- code-reviewer + `/cross-review`（Codex・`bash scripts/run-codex-*.sh`。+x 欠落のため bash 経由。必要なら先に `chmod +x scripts/*.sh`）。
- `docs(research): R1 ポジショニングへレビュー指摘を反映 (Physical Anchor 除く)` でコミット → `/finish-task`。

> 注: 別タスク `.steering/20260628-probe-scheduling-and-interruptibility/` の落合サーベイが
> research-positioning §3/§4・references(V) に追記する。**本タスク（R1 反映）を先に**完了させてから
> 走らせると衝突しない。
