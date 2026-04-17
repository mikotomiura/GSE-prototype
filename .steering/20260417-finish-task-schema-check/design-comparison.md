# 設計案比較 (v1 vs v2)

## v1 の要旨

- **新設 Step 2.5** を `.claude/commands/finish-task.md` に追加する
- 検出は **2 段**: `git diff HEAD` (未コミット) + `git log --grep="Refs:"`
  (タスク関連コミット)
- DATASET_ROOT resolution を finish-task 側で 4 段 fallback 実装
- HELPER_EXITCODE 0/1/2/3/4 ごとの Claude 応答を明示
- 失敗時は Claude が helper 出力を **要約 + 修復手順を再提示**
- tier-3 という独立概念で workflow guard を導入
- 追加行数: ~40 行

## v2 の要旨

- **既存 Step 3 (レビュー+テスト) に統合** し、新 Step 番号を作らない
- 検出は **1 段**: `git diff $(merge-base HEAD origin/main)` のみ
  (コミット規約への依存を排除)
- DATASET_ROOT resolution を helper に全移譲 (単一の真実の源)
- 失敗時は helper の **生出力をユーザーに見せる** (tier-2 と UX 統一)
- Step 3 内「並列に走る検査」の 1 つとして扱う (review-changes / test-runner
  と同列)
- 追加行数: ~20 行

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| アプローチ | 新設 Step 2.5 + tier-3 として独立 | 既存 Step 3 に統合・検査並列実行の一員 |
| 検出ロジック | 2 段 (git diff + git log --grep Refs:) | 1 段 (merge-base 基点の git diff) |
| コミット規約依存 | あり (`Refs: .steering/<taskdir>/` に依存) | なし (git tree 直接) |
| DATASET_ROOT resolve | finish-task.md 側で 4 段 fallback 実装 | helper に移譲 (env + 既定の 1 段簡易) |
| 失敗時提示 | Claude が helper 出力を要約 + 再提示 | helper 出力を生表示 (tier-2 と同 UX) |
| Step 番号 | Step 2.5 (小数) を導入 | 既存 Step 1-5 を維持 |
| 並列実行 | 独立 Step ゆえ直列で Step 3 手前に入る | Step 3 の parallel pipeline に合流 |
| 追加行数 | ~40 行 | ~20 行 |
| 変更規模 | 中 (frontmatter + 新 Step + 4 fallback + 要約テキスト) | 小 (frontmatter + Step 3 内 1 ブロック) |
| テスト戦略 | 6 ケース手動回帰 + dogfood | 3 ケース手動回帰 + dogfood |
| リスク | Refs: 規約違反で検出漏れ・小数 Step の可読性低下・4 fallback ロジック重複 | Step 3 肥大化・並列 pipeline への馴染み (検証要)・UX が生出力依存 (helper メッセージ品質に直結) |

## 決定的な分岐点

### 1. 検出の堅牢性

v1 は `git log --grep="Refs: <taskdir>"` に依存する。これは CLAUDE.md の
コミット規約が守られた場合のみ当たる。規約違反 / 緊急 hotfix / rebase で
message が消えた場合などに **false negative (drift を見逃す)** が発生する。

v2 は git tree そのものを見るため規約違反耐性がある。ただし
`origin/main` が不在の環境 (shallow clone, offline) では fallback として
`HEAD` を使うため、unpushed な複数 commit の累積は見逃す可能性がある。
→ この場合は未コミット diff のみ検出するので「直前の finish で触ってれば
catch する」縮退動作になる。実用上は十分。

**v2 が上**: 縮退動作は安全側、v1 の規約依存は安全側ではない。

### 2. ロジックの重複排除

v1 は DATASET_ROOT を finish-task.md と helper の **両方で解決** する
(二重実装)。どちらかが更新されると片方が drift する古典的アンチパターン
(前タスクで ps1/sh の 2 言語同期問題を避けたのと同じ構造)。

v2 は helper 一元化。finish-task 側は env の優先順位を 1 行書くだけ。

**v2 が上**: DRY 原則に忠実・保守しやすい。

### 3. ワークフロー可読性

v1 は Step 2.5 という小数 Step 番号を導入する。初見の人が「なぜ 2.5?」と
つまずく可能性がある。Step 番号体系が綺麗に揃っていた既存フロー
(1/2/3/4/5) を壊す。

v2 は既存 Step を維持したまま Step 3 内部に追加する。ただし Step 3 が
肥大化するため、サブ見出し (`### 3.1 schema-parity-check` 等) の導入で
視認性を補う必要がある。

**引き分け〜僅かに v2 有利**: v1 の小数 Step は目を引くが、Step 3 の
サブ見出し運用が可能なら v2 の方が構造整合的。

### 4. 失敗時の UX

v1 は Claude が helper 出力を「要約して親切に再構成」する。情報伝達の
丁寧さでは良いが、**Claude が helper エラーメッセージの細部を省略する
リスク**がある (variant 名の欠落、cp の正確なパス忘れなど)。

v2 は helper 生出力を出す。tier-2 と完全一致した UX になる。ユーザーが
sync-all の Step 0 で見たのと同じメッセージが finish でも出る → メンタル
モデルが一貫する。

**v2 が上**: 情報保全と UX 統一の両面で優位。

### 5. tier 階層化の妥当性

v1 は明示的に「tier-3」という概念を導入する。設計ドキュメント
(development-guidelines.md) でも tier-1/2/3 表を書くことになる。
この階層化は drift 検出の多段防御を可視化でき、教育的価値が高い。

v2 は「Step 3 並列検査の 1 つ」として位置付ける。tier 概念は
development-guidelines.md に記載するが、finish-task.md 自体は独立
Step を切らない。階層化は docs 内で行い、workflow ファイルは最小化する。

**引き分け**: 設計思想の違い。tier 可視化重視なら v1・workflow 簡潔さ
重視なら v2。

## 推奨案

**v2 を推奨** — 理由:

1. **検出ロジックの堅牢性**: v2 は git tree 直接参照でコミット規約違反に
   耐性がある。v1 の Refs: grep 依存は、本タスクが防ごうとしている
   "運用ミスで drift が素通りする" 問題と**同型の再帰**を生む
   (前タスクの reimagine でも同じ理屈で v2 が選ばれた経緯と一貫)
2. **DRY**: DATASET_ROOT resolution の二重実装を避けられる
3. **UX 統一**: tier-2 / tier-3 で失敗時表示が同一になり、学習コスト低い
4. **変更規模**: 追加行数が半分程度 (~20 行 vs ~40 行)・レビュー負荷軽い

v1 を採る場合の条件:
- Step 番号の明示的可視化が運用上必要だと判断する
- tier-3 概念を docs 以外 (workflow ファイル自体) にも焼き付けたい
- 検出 2 段の冗長性を「保険」として価値と見る

## ハイブリッド案 (参考)

「Step 2.5 は作らないが Step 3 内のサブ見出しで目立たせる」方向性。
具体的には:

- Step 3 の本文を `### 3.1 Review & Test (並列)` と `### 3.2 Schema
  parity check (並列)` に分ける
- v2 の検出ロジック・helper 直接呼出し・生出力方針はそのまま採用
- tier 対応表は docs/development-guidelines.md に追記

hybrid は **v2 の実質 + v1 の可視化要素** を合成する。
実装コストは v2 と同等・workflow 可読性は v1 に近付く。
