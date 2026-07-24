# Epic 1 — Architecture ADR + 改善設計書の SSOT 昇格

## 背景

Post-Phase1 の再設計を実装フェーズへ進めるにあたり、Epic 0（`.steering/20260724-epic0-repo-reality-check/`、
PR #70 で main 済み）が現行コードの実態と改善設計書 v0.1 の差分を確定した。次段の Epic 1 は
**コード変更ゼロ**で、(1) 改善設計書（`~/Downloads/GSE_Post_Phase1_Improvement_Design_v0.1.md`・docs 未昇格の提案）を
`docs/` 配下の SSOT へ昇格し、(2) アーキテクチャ判断を ADR として起票する。特に **ADR-006（task_kind→β 配線
vs IME 状態を代理とする）** は Phase2 マルチタスク化・Adapter 抽象化の分岐点であり最優先で決める。

Phase1 はデータ収集が未完（pilot GATE2 大幅 FAIL・リマインド Web アプリ未デプロイ）。ロードマップは Epic 1 に
「Phase1 完了 + 研究者承認」を課すが、Epic 1 は docs のみで**凍結対象に一切触れず**データ収集と物理干渉しない。
研究者（ユーザー）が Epic 1 着手を承認済み（2026-07-24）。

## ゴール

改善設計書の中核思想（GSE v2）を `docs/` の一次資料として確立し、ADR-001〜007 を Context/Decision/
Alternatives/Consequences/Migration の形式で起票する。以後の Epic 2 以降（コード変更）が参照できる
「動く前に決めておくべき設計判断」を文書として固める。エビデンスの温度を過大主張せず正直に刻む。

## スコープ

### 含むもの
- 改善設計書を `docs/architecture/gse-v2-overview.md`（＋必要なら domain-adapter-boundary / intervention-decision-engine）へ SSOT 昇格（設計書 §7.1）。
- ADR-001〜007 を `docs/adr/` に起票。**ADR-006 を最優先・最詳細**。
- 旧技術設計主張の置換表（設計書 §7.2）・README 修正方針（§7.3）を docs 側に反映（README 本体の書き換えは提案として明記、実施は研究者承認後）。
- エビデンス温度の明記（research-positioning §8 に接地）: Session Context は「効果」主張せず covariate/倫理ゲートに留める、Motivation Generator 非標準実装、Gate D は prior 扱い。

### 含まないもの
- **一切のコード変更**（`src-tauri/src/**`・`src/**`）。Epic 2 以降。
- 凍結対象への接触: `schema_dto.rs` / `schema/current.json` / `engine.rs` の HMM_VERSION / `intervention.rs` 閾値定数 / `probe_scheduler.rs` / `App.tsx` argumentative lock / `preregistration-v0.3.md`。
- ADR-006 以外の ADR の「決定」を確定すること（枠と Epic0 実態の反映まで。難所は研究者判断を仰ぐ）。
- 新規 [Pn]/[Vn] 文献の登録（Epic 1 は architecture タスク。エビデンスは既存引用を参照）。
- WBS の期間再配分・preregistration の改訂（研究者判断）。

## 受け入れ条件

- [ ] `docs/architecture/gse-v2-overview.md` が存在し、GSE v2 定義・7層構造・維持/廃棄する主張・エビデンス温度を含む。
- [ ] `docs/adr/` に ADR-001〜007 が存在し、各 ADR に Context/Decision/Alternatives/Consequences/Migration がある。
- [ ] ADR-006 が現行実態（β は ime_open 切替・task_kind 非配線）を正確に反映し、選択肢と推奨・研究者判断待ち点を明示。
- [ ] 過大主張なし: 未検証項目（Session Context 効果・Accountability・Agentic 過信 proxy）は「効くはず」で採用せず、covariate/倫理/feasibility 枠に留めることが文書に明記されている。
- [ ] コード差分ゼロ（`git diff` に `src-tauri/` `src/` の変更が無い）。
- [ ] `/finish-task` + `/cross-review` を通す。

## 関連ドキュメント

- `.steering/20260724-epic0-repo-reality-check/`（repo-inventory / design-vs-code-gap / migration-risk-register / adr-and-issue-roadmap）— 現行実態の真実源。
- `~/Downloads/GSE_Post_Phase1_Improvement_Design_v0.1.md` — 昇格元。
- `docs/research-positioning.md` §1/§8/§9 — 理論接地（機会保存）・エビデンス温度・スコープ。
- `docs/wbs-verification-halfyear.md` §改訂予定 — Phase 1.5 挿入・Gate D/S/H。
- `docs/references.md` — 引用 SSOT（append-only）。

## 運用メモ
- /reimagine 適用: No
- 理由: docs のみ・改善設計書 §7.1/§10 と Epic0 ロードマップで成果物構成が既に明示されており実装案の分岐は小さい。個別の難所（ADR-006 の task_kind→β 配線判断）は本文内で Alternatives として展開し、確定は研究者判断に委ねる。
