# IME 変換状態の content-free 観測 — 国際誌投稿のための評価設計と論文の外枠

## 背景

2026-09-27 の論文化可能性調査（本セッション）で、現状の実装・検証から書ける論文を洗った結果:

- ⚠️ 研究の headline（Stuck 検出 × 介入機会の前向き検証）は**未検証**。Phase1 は GATE3 = `DataInsufficient`
  （`experiments/20260731-phase1-calibration-analysis/notes.md:99-105,160-165`）。
- ⚠️ 人を対象とするデータは**倫理審査を経ていない**（`.steering/20260804-g1-pilot-execution/decisions.md` D-3・
  `docs/adr/ADR-014` 判断 3）→ 国際誌の倫理声明で詰まる。
- ★ 人を対象としない形で成立する最有力候補が **「日本語 IME の変換状態を本文を取らずに観測する技術」**:
  - TSF で他プロセスの composition を観測できないことの論証（`.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §7）
  - Windows = 窓イベント（`EVENT_OBJECT_IME_*` / DWM cloak）、macOS = 打鍵推論の状態機械（`src-tauri/src/input/ime_compose.rs`）
  - 実行コスト実測（CPU 平均 0.98% / 最大 4.30%・RSS 27MB・NDJSON 11.05MB/日・バッテリー欠測。`experiments/20260903-o1-runtime-cost/results/_summary.txt`）
  - 先行との差分は `docs/research-positioning.md:805-821`（[P270] は IME を迂回、[V5] は本文読み取りに依存）
- ⚠️ ただし **検出精度の評価が一度も行われていない**（grep で 0 件）。これが投稿の律速。

## ゴール

**Behavior Research Methods (BRM) に 2026 年内に投稿できる状態**（余裕があれば同じ結果を CHI 2027 Posters〔2027-01-21 締切・非アーカイブ〕にも出す。decisions.md 判断 8）へ向け、本タスクでは
**評価設計（凍結可能なプロトコル）と論文の外枠**を確定する。実装・計測・執筆本体は後続タスク（issue）に分ける。

## スコープ

### 含むもの
- 評価プロトコル（シナリオ目録・正解の取り方・指標・解析計画・OS × IME 行列）の設計と、`experiments/` への事前凍結文書
- 本文再構成不能性（content-free 主張）の評価設計（攻撃者モデル・コーパス・指標）
- 実行コスト（バッテリー再計測を含む）の扱いの確定
- 論文の外枠（構成・貢献の主張・各節の根拠資料の対応表・関連研究の骨子）
- 公開用の評価一式（別 repo）の切り出し範囲の設計
- 後続の実装・計測・執筆の issue 分解

### 含まないもの
- ⚠️ **人を対象とする打鍵データの収集**（著者本人の打鍵も含めない・合成入力のみ）
- ⚠️ **既存の Phase1 / G1 / O1 データの使用**
- `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED (0x8030)` の実装（survey §7.7 で研究者判断へ送り済み・本論文は実装済みの経路のみを記述する）
- ATOK など有償 IME
- [P321] 再解析の同梱
- GSE 本体の OSS 公開・JOSS 投稿（未踏採択後の方針）
- 国内学会への投稿

## 受け入れ条件

- [ ] `experiments/<date>-ime-observation-accuracy/` に評価プロトコル（シナリオ目録・正解の定義・指標・OS × IME 行列・解析計画）が書かれ、**実測前に凍結**されている
- [ ] 本文再構成不能性の評価設計（攻撃者モデル・コーパス・指標）が同プロトコルに含まれている
- [ ] 論文の外枠（節構成・貢献の主張・各主張 ↔ 根拠資料の対応表）が書かれている
- [ ] 公開用評価一式の切り出し範囲が決まっている
- [ ] 後続 issue が `.steering/.../issues/` に分解されている（Done が test 名 / exit code / 観測可能条件で言える形）
- [ ] 下した判断が `decisions.md` に記録されている

## 関連ドキュメント

- `docs/research-positioning.md` §4（L805-821: 日本語 IME の差分）
- `.steering/20260821-workspace-behavior-triage/survey-input-channels.md` §3.2 / §7
- `src-tauri/src/input/ime_compose.rs`（冒頭の OS 非対称表）/ `hook_macos.rs` / `hook_windows.rs` / `ime_windows.rs`
- `src-tauri/src/analysis/anonymize.rs`（`KeyCategory`）
- `experiments/20260903-o1-runtime-cost/`
- `docs/experiment-tracking.md`（再現性規約）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 正解の取り方・再構成攻撃の設計など、最良案が自明でない評価設計であり、やり直しが効かない（凍結後に変えると逸脱になる）。design.md の初版承認後に実行する。
