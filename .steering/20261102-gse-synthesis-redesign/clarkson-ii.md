# Clarkson II の入手の条件（2026-11-02・判断 1 の並行の確認）

サブエージェント（Sonnet）が調べ、要の逐語はメインが配布元のページを curl で取って照合した。データ本体・申請フォームには触れていない。

## 確かめたこと

- 配布元: CITeR（Clarkson University）の https://citer.clarkson.edu/clarkson-university-keystroke-dataset-ii/
  - 逐語（メインが照合）: "This Clarkson II keystroke dataset was recorded in a user's natural setting, thus is completely uncontrolled." / "there are 101 data files one for each user. Each data file has three columns, from left to right: timestamp when a key is pressed or released, indicator of key press/release (1/0), and a key code." / "the timestamp is measured in a unit of 100 nanosecond"
  - このページには、ダウンロードのリンク・請求の手順・ライセンスの記載が無い（メインが request・download・license の語を探して 0 件）。
- 同じ配布元の Clarkson I のページ（サブエージェントの抜粋・メインは照合していない）: "To request this dataset, please contact citer@clarkson.edu and indicate the specific dataset."
- 元論文: Murphy, Huang, Hou, Schuckers. "Shared dataset on natural human-computer interaction to support continuous authentication research". IJCB 2017, pp. 525–530. DOI 10.1109/BTAS.2017.8272738（サブエージェントの報告。doi.org が IEEE の 8272738 へ転送することを確認したと報告）。Vural ら 2014 は Clarkson I（実験室・39 人）の論文。
- 二次の論文（arXiv 2501.07600・サブエージェントが pdftotext で読んだ・メインは照合していない）は「2.5-year period」「103 subjects」・平均約 12.5 万打鍵・打鍵とマウスと書く。配布は 101 ファイルで、マウスは配布の説明に出てこない。

## 確かめられなかったこと

- 実際の入手の経路（請求か、会員向けの SharePoint か）・ライセンス・再配布の可否。
- 1 人あたりの記録の日数と時間、セッションの境目、記録の止まりと無活動の区別。キーの符号が仮想キーコードか。
- Murphy 2017 の本文（clarkson.edu の PDF は curl でボット対策のページが返り、取れなかった。サブエージェントは User-Agent を変えて取り直そうとして自動の判定に止められ、回避しなかった）。

## 次の一手（研究者）

- ブラウザで Murphy 2017 の PDF を開いて利用の条件を見る。請求するなら `citer@clarkson.edu` に Clarkson II と明記して送る（送るのは研究者）。返事の前にデータを取らない。
