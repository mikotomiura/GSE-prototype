# design — Epic 1 アプローチ

## 方針

改善設計書 v0.1 は「提案」ステータス。これを**そのままコピーせず**、Epic 0 で確定した現行コード実態を
反映した SSOT へ「昇格」する。すなわち設計書の思想（GSE v2）を保ちつつ、
「◎ 実装済み / ✗ 未実装 / 記録のみ」の実態と「エビデンスの温度」を各所に刻む。

## 成果物と配置

| ファイル | 内容 | 昇格元 |
|---|---|---|
| `docs/architecture/gse-v2-overview.md` | GSE v2 定義・7層構造・維持/廃棄する主張・HMM の位置づけ・エビデンス温度・現行実装状況表 | 設計書 §0/§2/§3.1/§5/§7.2/§7.3 |
| `docs/architecture/domain-adapter-boundary.md` | Layer 0-3（Session Context / Domain Adapter / Event Envelope / domain-local feature）の境界と trait 案・privacy 禁止事項 | 設計書 §3.2–3.5/§8.1/§8.2 |
| `docs/architecture/intervention-decision-engine.md` | Layer 5-7（Opportunity/Receptivity/Consent/Decision/Outcome）・decision ルール・pure function 化・現行 intervention.rs との対応 | 設計書 §3.6/§3.7/§8.3 |
| `docs/adr/README.md` | ADR 索引・ステータス凡例 | — |
| `docs/adr/ADR-001..007-*.md` | 7 本の ADR | 設計書 §7.1/§10・roadmap |

> `docs/schemas/` `docs/validation/` `docs/research/` 等（設計書 §7.1 の残り）は Epic 5/後続で扱う。Epic 1 は
> architecture ADR に集中する（roadmap Epic 1 の射程）。Gate D/S/H の schema 化は Epic 5。

## ADR 一覧と Epic 1 での決定深度

roadmap の ADR 候補表に対応。各 ADR は Context/Decision/Alternatives/Consequences/Migration を持つ。

| ADR | 主題 | Epic 1 での扱い |
|---|---|---|
| ADR-001 | HMM を Writing baseline へ降格 | **決定可**（設計書 §2.3/§3.3/§7.2 と一致・実装は Epic 2）。三状態表示の降格方針を記す |
| ADR-002 | domain-local inference / Adapter 境界 | 方向を**提案**（trait 案）・確定は Epic 2 の抽出で。Accepted(方向) / 実装は後続 |
| ADR-003 | Accountability を core 外へ分離 | **境界は決定・採否は保留**（エビデンス未確定・第4ラウンド待ち）。extensions/ 分離のみ確定 |
| ADR-004 | Decision Engine 境界（pure function 化） | **決定可**（Need/Opportunity 分離済・new_with_thresholds 実在）。Consent 軸新設は Epic 3 |
| ADR-005 | Event Envelope schema versioning | 方向を**提案**（additive・schemars 既存基盤）・確定は実装時 |
| ADR-006 | **task_kind → β 配線 or IME 代理を正とするか** | ★**最優先・最詳細**。現行=ime_open 切替・task_kind 非配線。Alternatives を尽くし推奨を出すが、**確定は研究者判断**（Phase1 交絡・凍結との関係） |
| ADR-007 | receptivity 統合スコア化 or 分解維持 | **決定可**（現状維持＝分解形を推奨・観測可能性の理由）。 |

## エビデンス温度の扱い（過大主張の防止・最重要）

research-positioning §8 / roadmap のエビデンス判定を各 docs に反映する。原則:

- **実証で支持**: `none`/`defer` 第一級化 [V43 系]、Motivation Generator を標準実装しない（実行意図 補正後 d≈.15 [P21]・ナッジ補正後 d≈0 [V40]）、Gate D は低継続率を桁の prior に [V41][V42]。
- **未検証（効果を主張しない）**: Session Context（WorkIntent/SupportConsent）・Accountability Extension・Agentic Coding 過信 proxy。→ covariate（交絡切り分け）／倫理・自律性ゲート／feasibility の枠に**留める**。
- 理論接地は**機会保存**（反射的オフロードを減らし自力解決の機会を保存＝行動指標で測定）。学習効果（[P12]Kapur）は「守るべき困難の存在根拠」に限定し「摩擦が学習を生む」には使わない [P27][P28]。
- 各 docs の該当箇所に「エビデンス状態」注記を置き、`docs/research-positioning.md §1/§8` を評価の SSOT として参照リンクする（引用は既存 [Pn]/[Vn] を指すのみ・新規登録しない）。

## 変更しないもの（凍結・不変条件の再掲）

migration-risk-register の Step 0 凍結対象に一切触れない。docs 追加のみ。既存 docs（architecture.md /
research-positioning.md / functional-design.md 等）は**書き換えず**、新規 `docs/architecture/` `docs/adr/` を
追加する（旧技術設計の置換は「方針」として ADR/overview に記し、本体書き換えは研究者承認後の別タスク）。

## テスト戦略

コード変更が無いため replay/cargo test は対象外。代わりに:
- `git diff --stat` に `src-tauri/` `src/` が現れないことを確認（コードゼロ変更の acceptance）。
- 相互参照リンクの妥当性（存在するファイル・見出しを指すか）を目視 + grep で確認。
- 引用 `[Pn]/[Vn]` が references.md に実在する番号のみを使っているか grep で確認。
- `/cross-review`（Codex 独立レビュー）で過大主張・事実誤り・現行実態との齟齬を点検。

## 進め方
1. overview → adapter-boundary → decision-engine の順で 3 本作成。
2. ADR README → ADR-006（最優先）→ 001/004/007（決定可）→ 002/003/005（方向提案）。
3. 相互リンク・引用チェック → `/finish-task` → `/cross-review`。
4. ADR-006 の推奨と研究者判断待ち点を完了報告で明示。
