---
name: literature-card
description: >
  先行研究・論文・技術ブログを読んでまとめる時に必須参照。落合フォーマットの 6 項目
  (1.どんなもの 2.先行研究と比べてどこがすごい 3.技術・手法の肝 4.どう有効と検証したか
  5.議論はあるか 6.次に読むべき論文) でカードを docs/literature/<YYYYMMDD>-<topic-slug>.md に
  書き、docs/literature/_index.md に追記し、出典を docs/references.md に append-only で登録する。
  「論文を読む」「文献をまとめる」「先行研究を調べる」「サーベイする」「関連研究を整理する」時に起動する。
  カード/索引の SSOT は docs/literature/_index.md、出典 SSOT は docs/references.md。
allowed-tools: Read, Write, Edit, Grep, WebSearch, WebFetch
---

# Literature Card Discipline

## このスキルの目的
文献の精読を、再利用可能な構造化カードに落とす。「やり残し」の抽出を毎回強制し、
research-positioning.md §3（ランドスケープ）/ §4（差分）に還元できる形にする。
本 skill は規約を再定義せず、`_index.md` の出力契約と `references.md` の登録を発火させる。

## カードの必須 6 項目（落合フォーマット）
1. それはどんなもの?
2. 先行研究と比べてどこがすごい?
3. 技術や手法の肝はどこ?
4. どうやって有効だと検証した?
5. 議論はあるか?
6. 次に読むべき論文は?
+ メタ: 出典 [n]（references.md に登録）、トピック、日付。

## 主要なルール
### ルール 1: 1 文献 = 1 カード、6 項目すべて埋める
「やり残し」（項目 2/5 から導く）を必ず 1 行で書く。これが §4 差分の素材になる。
### ルール 2: ファイルと索引
docs/literature/<YYYYMMDD>-<topic-slug>.md に保存し、_index.md の表に 1 行追記。
### ルール 3: 出典は citation-ssot 経由
各カードの文献を references.md に append-only 登録し、カードに [n] を付ける（書誌未確定は provisional）。
### ルール 4: GSE 文脈への還元
カードの「やり残し」が research-positioning.md §4（差分）の主張を補強/反証するかを 1 行で述べる。

## チェックリスト
- [ ] 6 項目すべて埋めたか
- [ ] 「やり残し」を 1 行で抽出したか
- [ ] _index.md に追記したか
- [ ] 出典を references.md に登録し [n] を付けたか（捏造書誌は provisional）
- [ ] GSE の §4 差分との関係を 1 行で述べたか

## 補足資料
- `card-template.md` — 6 項目カードの空テンプレ

## 関連する他の Skill
- citation-ssot — 出典登録で必ず併用
- `/literature-review` — サーヴェイ 1 ラウンド全体の実行コマンド（探索→敵対的 3 票検証→
  複数カード一括生成→references 登録→_index 追記→positioning 還元）。本 skill のカード契約を踏襲する。
  カード 1 枚を書くだけなら本 skill 単体でよい。
