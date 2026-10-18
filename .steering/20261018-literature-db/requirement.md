# literature-db（文献 DB を 1 つの仕組みにする）

## 背景

2026-10-18、研究者の依頼で、これまでのサーヴェイの書誌（6 枝の `docs/references.md`・906 件）を Google スプレッドシートの DB・検索のページ・書誌のファイル（BibLaTeX / BibTeX / CSL-JSON）にした。675 件には要約と特徴も付けた。ただし作り方は作業用の一時ディレクトリでその場で書いたコードで、3 つがばらばらに作られている（手順は `scripts/refdb/draft/STEPS.md`）。研究者の言葉: 「スプレッドシート基本の上で一つに繋げておくとより楽かも。今後の研究を行う上でもこの仕組みを入れると楽かもね」。

## ゴール

スプレッドシートを中心に、`docs/references.md` を正本とした文献 DB を 1 つのコマンドで作り直せるようにし、`/literature-review` の最後の段に組み込む。

## スコープ

### 含むもの
- `scripts/refdb/`: 書誌と引用の収集・カードでの記述・抄録と書誌の取得（キャッシュつき）・CSV・検索のページ・BibLaTeX / BibTeX / CSL-JSON を 1 本のコマンドで作る
- 読んだ・メモ（シートが正本）を key で結び直して、作り直しで消さない
- 要約・特徴を `docs/literature/refdb/summaries.json` で持ち、無い文献を一覧にする。要約を書く依頼文を `scripts/refdb/summary_prompt.md` に起こす
- `/literature-review` に、新しい書誌の要約を書き DB を作り直してシートとページへ反映する段を足す
- シートとページへ反映する手順（Drive for desktop・Chrome での変換・Sheets の API）を文書にする

### 含まないもの
- 書誌の正本をシートに移すこと（判断 1: 正本は references.md のまま）
- 番号の衝突（48 個）の解消（別タスク）
- 抄録を repo に入れること（著作物。手元のキャッシュだけ）
- Google の API キーやサービスアカウントを作ること

## 受け入れ条件

- [ ] 1 つのコマンドで、2026-10-18 に作ったものと同じ件数（906 件・要約 675 件・カードでの記述 576 件）の CSV・ページ・.bib 2 本・CSL-JSON ができる
- [ ] 読んだ・メモを入れた CSV を渡すと、作り直した後も key で同じ行に残る（テストで確かめる）
- [ ] 7 列の行・配列の題・null の年（2026-10-18 に踏んだ形）をテストで扱う
- [ ] 要約が無い文献の一覧が出る
- [ ] `/literature-review` に DB を作り直す段がある（`empirical-prompt-tuning` で確かめる）
- [ ] `/cross-review` を通す

## 関連ドキュメント

- `scripts/refdb/draft/STEPS.md`（2026-10-18 の手順）
- `.claude/commands/literature-review.md`・`.claude/skills/citation-ssot/SKILL.md`
- memory `abstract-sources-and-drive-ids`（大きな表をシートにする経路）

## 運用メモ
- /reimagine 適用: No
- 理由: 2026-10-18 に一度作って動いた手順を 1 本にまとめる作業で、主な判断（判断 1〜4）は研究者が決めた
