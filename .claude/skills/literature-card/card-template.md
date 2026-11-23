# 文献カード テンプレ（落合フォーマット）

新規カードは `docs/literature/<YYYYMMDD>-<topic-slug>.md` にコピーして埋める。
出典は `docs/references.md` に append-only 登録（citation-ssot skill）。

```markdown
# 文献カード: <短いタイトル> [n]

- **トピック**: <topic-slug>
- **日付**: <YYYY-MM-DD>
- **出典 [n]**: docs/references.md の [n]（key: DOI/arXiv/URL）

## 1. それはどんなもの?
（1–3 行で要約）

## 2. 先行研究と比べてどこがすごい?
（既存との差分・新規性）

## 3. 技術や手法の肝はどこ?
（中心アイデア・キーメカニズム）

## 4. どうやって有効だと検証した?
（実験設計・データ・指標・主要結果）

## 5. 議論はあるか?
（限界・反論・再現性・スコープ）

## 6. 次に読むべき論文は?
（引用先・関連研究。references.md へ追加候補なら [n] 予約メモ）

## → GSE への含意
- **やり残し（1 行）**: この文献が残した空白＝
- **§8 新規性の範囲との関係**: research-positioning.md §8 を（補強 / 反証 / 精緻化）する。具体的には…
```

## 記入のコツ

- 項目 2 と 5 から「やり残し」を 1 行で必ず抽出する（これが research-positioning §8 の素材）。
- 6 項目を埋められないほど読めていないなら、カードを「draft」とマークして _index.md には載せない。
- 出典の DOI/URL が確認できなければ references.md に `provisional` で登録（捏造しない）。
- 索引追記を忘れない: `docs/literature/_index.md` の表に 1 行（日付 / トピック / ファイル / カード数 / やり残し要約）。
