# タスクリスト

## 準備
- [x] 引き継ぎ (`.steering/_handoff/next-session-design-slides.md`) を読む
- [x] `/start-task` で grill（スコープ / デッキ構成 / 図の分量を研究者に確定）
- [x] docs の先読みをサブエージェント 4 本に並列で投げる
- [x] 一次資料メモを `.steering/` に残す（`facts-inference` / `facts-model-promotion` /
      `facts-architecture` / `facts-claims`）
- [x] テンプレートの仕様を**自分で実測**する（★ 引き継ぎの数値を鵜呑みにしない）

## 段 1: 変換器 `scripts/md2pptx.py`
- [x] `--template <path>` を足す
- [x] テンプレート指定時にスライドサイズを代入しない
- [x] テンプレート同梱の見本スライドを全削除する（`drop_rel` と `sldIdLst.remove` を対で）
- [x] `![alt](path)` の図を埋め込む（相対解決 / repo 外拒否 / PNG・JPEG のみ）
- [x] 表を**本物の `a:tbl`** にする（★ 列幅は中身で比例配分・font は列幅と行高から決める）
- [x] スライドごとにレイアウトを選ぶ（`<!-- layout: ... -->` ＋ 自動判定）
- [x] 版面を比で持つ `Geometry` を入れる（★ 継承座標は本文 1.60 inch で使えない）
- [x] テンプレートの「地」を複製する（背景 ＋ 左端の帯・`showMasterSp="0"` を揃える）
- [x] 欠けている `docProps/app.xml` を出力側で補う（★ 検査は緩めない）
- [x] `verify()` の検査 (7) の偽陽性を直す（`ctrTitle`/`subTitle` は master の `title`/`body` を継承する）
- [x] selftest に**変異体検査 10 本**を足す
- [x] `PYTHONUTF8=1 python scripts/md2pptx.py --selftest` が緑

## 段 2: 図
- [x] PNG 書き出し手順を**実測で復元**する（★ md5 一致で確認）
- [x] `scripts/svg2png.py` を新規作成（viewBox から寸法を読む / `--check` / 倍率違いは skip）
- [x] 新規図 6 枚を作る（層の地図 / データの形 / 量子化と遷移 / ドメインヘッド / 介入の決定 /
      段と昇格 / 候補モデルの比較 ＝ 7 枚になった）
- [x] 全図を書き出し、`.png` と `.svg` の縦横比一致を確認
- [x] ⚠️ 誤って 1 倍で上書きした `gse-workflow.png` を `git checkout` で戻す
- [x] レンダリングして**実際に目視**し、文字のはみ出し・線の重なりを直す

## 段 3: デッキ
- [x] 技術主軸で再構成（34 枚）
- [x] 降ろしてはいけない節を残す（主張の層構造 / 確証するのは L0 だけ / 較正前後 / 未実装の明示）
- [x] 図 7 枚を配置（★ 図スライドは全幅。半幅だと文字が 6pt になって読めない）
- [x] 図の内部タイトルとスライドタイトルの重複を解消
- [x] `check_doc_lexicon.py` が緑
- [x] `check_citations.py` が「違反なし」
- [x] LibreOffice → PDF → PyMuPDF で**各ページを目視**

## レビュー
- [x] 一次資料との突き合わせを別エージェントへ（★ 機械検査は事実誤りを検出しない）
- [x] `code-reviewer`
- [x] `security-checker`
- [x] HIGH 指摘への対応
  - [x] security H-1: **第三者テンプレートを取り込まない**方針へ転換し、自前生成器を作る（D11）
  - [x] review H-1: `verify()` に検査 (8)「宙吊りの関係参照」を足す（D12）
  - [x] review H-2: selftest が chrome の rId 張り替えを通るようにする
  - [x] review H-3: CI に `md2pptx.py --selftest` を足す
  - [x] fact C1/C2/H1-H4 と MEDIUM/LOW 計 21 件をスライドへ反映
  - [x] fact M4/L5/L6 ほか計 9 件を図へ反映
- [x] `/cross-review`（★ 結果と対応は `cross-review-codex.md`。5 件中 3 件を反映・1 件は既対応・1 件は見送り）

## ドキュメント
- [x] `docs/mitou_submission/README.md` を更新（再生成コマンド / 枚数 / 変換器の能力 / 図の書き出し）
- [x] `decisions.md` を書く

## 完了処理
- [x] `design.md` の最終化
- [x] git commit（`9b706d3`）
