# GSE のプロジェクト概要のスライド

誰にでも分かるように、手書き風の図で GSE の概要を説明する 19 枚のデッキ。2026-11-15 に作った。

| ファイル | 中身 |
|---|---|
| `GSE_project_overview.pptx` | できあがったデッキ（話す原稿は各スライドのノート） |
| `tpl.pptx` | 元のテンプレート（`deck_temp_template-original.pptx` の写し）。背景画像・地の色・配色はここから取る |
| `sketch.py` | 手描き風のイラスト（`img/*.png`）を描く。ラフな線のライブラリと図の一式 |
| `build.py` | テンプレートの上にスライドを組む（文字・図の配置・ノート） |
| `img/` | `sketch.py` が描いたイラスト（乱数の種を固定してあるので、同じ環境なら同じ絵になる） |

## 作り直し方

```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx Pillow lxml
.venv/bin/python sketch.py   # img/ を描き直す（図を変えたときだけ）
.venv/bin/python build.py    # GSE_project_overview.pptx を組み直す
```

- フォントは手書き風の **Klee One**（SIL OFL）。`sketch.py` は `~/Library/Fonts/KleeOne-SemiBold.ttf` を読む（別の場所なら環境変数 `GSE_DECK_FONT`）。
- Klee One が入っていない PC では別のフォントで表示される。他の人に渡すときは PDF に書き出す。
- 確かめるときの描画: LibreOffice（この Mac の headless の版）は Klee One を拾えず日本語が □ になる。Keynote で PDF に書き出して見る。

## 中身の出どころ

- 位置づけ・問い・設計: `docs/research-positioning.md`（2026-11-15 の現行版）と ADR-043〜053。
- 数字（AUC 0.49〜0.52・1 時間に 124〜182 回・6.3〜9.1%・2.2%〜26%）: ADR-047 Context と `research-positioning.md` §1.4。
- 外に見せる前提で、論文の投稿先と状態・未踏の不採択・参加者のデータは入れていない。

## 更新するとき

位置づけ（headline・一言・新規性の書き方）が変わったら、`build.py` の表紙のサブタイトル・11 枚目「だから、問いを変えた」・17 枚目「大切にしていること」・19 枚目「まとめ」を見直す。研究の決定はスライドで下さず、ADR と `research-positioning.md` を先に直す。
