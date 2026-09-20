# 設計

## 実施アプローチ

- **移設**: `.idea/` の 3 本を `docs/theory/` へ写した（ファイル名から日付を外した。元の名前と日付は冒頭に書いた）。スクリプト（`$CLAUDE_JOB_DIR/tmp/move_theory.py`）で機械的に行った:
  - リンク: `../.steering/` → `../../.steering/`、`../docs/X` → `../X`、移した 3 本の相互参照は新しい名前へ、移さない `.idea/` の草案は `../../.idea/…`（追跡外）へ。
  - 改名（件数）: 「非支配的協調」→「関係的自律を支える協調」（A 6 / B 4）、「Lv1 Nudge」→「Nudge」（A 1 / B 1）。MTP は 0 件。⚠️ 草案の「計測なき身体回帰」→「自ら選んだ間と再開の機会」（A 10）も当てたが、**段 3 判断 3 #1 で戻した**（decisions.md 判断 2）。
- **注記**（本文の該当箇所に日付つきで足した。本文の既存の文は消していない）:
  - B: J-3（停止対象）・返権の負荷逆説の先行と差分（判断 2 #1）と J-17（負担台帳の射程）・J-9（終端の表現）・J-4（非再捕捉の射程）・J-7（GR-H11）・J-6（BRIDGE-DN）・改名した語の S2 の依拠と差分。
  - A: 論文計画の記号の規則・J-6・J-7・J-14（§4 の見出し）・J-4 / J-3（CORE-CS）・改名した語の S2 の依拠と差分。
- **当てなかったもの**: 批判的レビューの判定（例: A §0「概念的成立: 高い」の縮小案）は研究者の採否が未了なので、本文に当てず冒頭で併読を促した。
- `.idea/` の元の 3 本の冒頭に「移した・以後は編集しない」を 1 行足した（★ 追跡外なのでコミットには入らない）。

## 変更対象

### 新規作成するファイル
- `docs/theory/README.md` / `theory-architecture-and-roadmap.md` / `generative-relinquishment-theory.md` / `measurement-terminating-practice-portraiture.md`

### 修正するファイル
- `docs/agent-shared.md`（主要ディレクトリ・リンクハブ）・`docs/repository-structure.md`（docs の木）

## 影響範囲

- `docs/` の直下の本数は 21 のまま（★ `agent-shared.md` の「20」が古い値だった）。`theory/` ディレクトリが増える。`check_citations.py` の走査対象に入る（★ 違反なし）。

## テスト戦略

- リンクの存在確認（壊れたリンク 0 件）・`check_citations.py` 違反なし・禁止用語の規則（ヒットは改名を説明する注記と否定形の行だけ）・`/cross-review` 2 巡。

## ロールバック計画

- コミットを `git revert` する（`.idea/` の元ファイルは残っている）。
