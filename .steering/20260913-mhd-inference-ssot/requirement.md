# `stall onset` / `Decision Episode` の操作的定義（T3 トラック タスク 1）

## 背景

`ADR-029 D2` は **`t0 = stall onset` を予測トラックの時間原点として確定**したが、
★ **その実装定義を持っていない**。引いているのは概念定義 1 行だけである
（`docs/architecture/personalization-and-online-learning.md:336-337` 逐語）:

> **stall onset** = 個人×task_kind×phase 基準を下回る産出が、個人基準の pause 閾値を超えて
> 継続し始めた時点。（絶対秒数で固定しない。）

⚠️ この文には **3 つの未定義語**が入っている —— 「個人基準」「phase」「task_kind 基準」。
★ `.idea/20260910-...criterion...md:329` が §9「ADR 化前に閉じる必要がある問い」の
**筆頭**に本項を置いている。

⚠️★★★ **依存の根である**: これが無いと
- T1d（restart shape）の特徴群が定義できない（`pause 後` の起点が無い）
- person-period 表現の標本（期 k = 1, 2, …）が生成できない
- `Decision Episode` を標本単位にする既決（ADR-010 D4）が実体を持たない

## ゴール

**`stall onset` と `Decision Episode` の操作的定義を、
新しい観測ゼロ・`HMM_VERSION` 不変で確定する新規 ADR（ADR-030）を書く。**

★ あわせて「特徴量再設計を大まかに accept」の **accept の対象**
（Tier 枠 ／ 投資順序 ／ ablation 規律 ／ 計器を変える範囲の仕切り）を確定する。

⚠️★★★ **決められないなら「決められない理由」を書いて止める。**

## スコープ

### 含むもの
- `stall onset` の操作的定義（★ コードに落ちる形）
- 「個人基準の pause 閾値」の算出規則（⚠️ 絶対秒数で固定しない）
- `phase` / `task_kind` への依存の裁定
- `Decision Episode` の操作的定義（⚠️ **新設せず既存の受け皿に載せる**）
- 特徴量再設計の **accept 対象**（Tier 枠・投資順序・ablation 規律）
- ★ **計器を変えない範囲 / 変える範囲の仕切り**

### 含まないもの
- ⚠️ `features.rs` / `engine.rs` への実装（→ タスク 2・別セッション・Loop モード C）
- ⚠️ 期の幅 **Δ** の値の確定（★ ADR-009 §Accepted 条件 B で **P1 のデータ待ち**）
- ⚠️ T1c / T2 / T3 の採否（★ 計器変更を伴う → §8 タスク 4 で一括裁定）
- ⚠️ `ADR-009` の Accepted 化（★ G1 が `n = 0/3`）
- ⚠️ `metrics.rs` / prereg / 既存 ADR 本文の変更

## 受け入れ条件

- [ ] AC1: `stall onset` の操作的定義が**コードに落ちる形**で書かれている（「個人基準」「phase」が未定義のまま残っていない）
- [ ] AC2: `Decision Episode` との関係が明記され、**新設していない**（ADR-008 D2 / ADR-010 D4 / ADR-014 D6 を引く）
- [ ] AC3: 特徴量の **Tier 枠 ＋ 投資順序 ＋ ablation 規律**が確定している
- [ ] AC4: **「計器を変えない範囲」と「変える範囲」の仕切り**が明記されている
- [ ] AC5: 却下案が `Alternatives` に理由付きで残っている
- [ ] AC6: `check_doc_lexicon.py` が exit 0
- [ ] AC7: `check_citations.py` が exit 0（★ 「違反なし」まで反復）
- [ ] AC8: `docs/adr/README.md` に行があり、ファイルが実在する
- [ ] AC9: ヘッダに `昇格元: .idea/...` がある
- [ ] AC10: `/cross-review` ＋ `code-reviewer` ＋ `security-checker` を **3 つとも**通している

## 関連ドキュメント

- `docs/adr/ADR-029-outcome-role-arbitration.md`（⚠️ **未マージ**・ブランチ `docs/adr-029-outcome-role-arbitration`）
- `docs/adr/ADR-008 / ADR-009 / ADR-010 / ADR-014 / ADR-016 / ADR-020`
- `docs/architecture/personalization-and-online-learning.md` §3.1 / §3.3 / §11-1 / §11-7
- `docs/architecture/task-adaptation-and-scope-gating.md` §3.6
- `.idea/20260910-mhd-criterion-practice-trace-and-g-o-validation.md` §1.3 / §2.1 / §9
- `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md` §6.1

## 運用メモ
- /reimagine 適用: **Yes**（★ 引き継ぎ §0 が明示。ADR-029 で初回案が `ADR-014 D1` と衝突した先例）
- 理由: 設計判断・裁定であり、切り方を誤ると T0/T1 の実装が全部無駄になる
