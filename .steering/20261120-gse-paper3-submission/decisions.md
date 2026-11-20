# 重要な設計判断

## 判断 1: 規程の読み直し（2026-11-20）
- Chrome で https://link.springer.com/journal/11257/submission-guidelines を読んだ。判断 46 の要点（LaTeX は SN の template・source と PDF・要旨 150〜250 語で未定義の略語なし・キーワード 4〜6・補足は "Online Resource"・ESM_n の連番・各ファイルに題/誌名/著者/連絡先・LLM の利用は Methods）は変わっていない。
- 新しく拾った点: 見出しは "Statements and Declarations"（同じ頁の Summary of requirements と SN の template は 'Declarations'）／Author Contribution と Competing Interest は投稿画面から入れたものだけが使われる／所属のない著者は市と国だけ／謝辞は title page に（謝辞なし）／参照の DOI は完全なリンクで（bib に doi あり）／責任著者は未公刊の資料をカバーレターで明かす。
- 見出しは 'Declarations' のまま（template と同じ頁の Summary of requirements に合い、公開した原稿の写しとも揃う）。

## 判断 2: 要旨の語数（2026-11-20・研究者の選択・推奨案）
- 空白区切りで 253 語（数式 4 個を 1 語ずつ）、texcount で 249 語（以前の記録 248 語はこの数え方の近い版）。投稿画面の数えを考え、意味を変えずに 2 か所を削った: "depends on what it is compared with" → "depends on the comparison"、"When the smoothing chosen for the shared model is applied" → "When the shared model's chosen smoothing is applied"。
- 結果: 空白区切り 248 語（AskUserQuestion では 247 と見込んだが、前者は −4 ではなく −3 だった）。投稿画面に貼る形（数式を "5×10^-4" と空白なし）でも 248 語。"5 × 10^-4" と空白を入れると 256 語になるので空白なしで貼る。
- Zenodo v1.0.0 の原稿の写しとは要旨の 2 か所だけ違う（版は上げない）。

## 判断 3: 組み直しと zip（2026-11-20）
- 空のディレクトリで組み直し: 本文 21 頁・補足 16 頁、誤り 0・overfull 0・未定義の参照 0。underfull は \raggedbottom による頁ごとの vbox と Code availability の URL の行（badness ≦ 3803）だけ。要旨を直す前の版は、コミット済みの PDF と pdftotext の文字が完全に一致した。
- zip（main.tex・main.bbl・references.bib・sn-jnl.cls・sn-basic.bst・figdata/ の 5 CSV）だけから組んで、文字が manuscript.pdf と一致。references.bib を抜いて bbl だけでも一致。

## 判断 4: カバーレター（2026-11-20・関連する原稿の段は研究者の選択・推奨案）
- 一次で確かめた重なり: JEDM 1484（推定器の 30 秒の信号・プレプリント 10.5281/zenodo.24026330 の題を Zenodo の API で照合）は、論文 3 の記号化と同じ前段（直前 30 秒の 5 特徴量・合成・平滑）の推定器を扱い、CS1 と探索で CoAuthor を使う。JEDM 1486（multiverse）は CoAuthor と CS1 2021 を含む 4 データ。どちらも系列モデルを当てはめない。PoPETs #55（照合）は KLiCKe だけで重ならない。
- 形は論文 2 の送付状に合わせた。AI の利用は Section 3.4（main.aux で照合）、分析の順は S8。

## 判断 5: CS1 の公開の範囲（2026-11-20）
- 食い違い: CS1 の問い合わせ（2026-11-02）で「公開は集計値だけ・再配布しない」と約束していた（main の .steering/20261104-cs1-landscape 判断 1）が、公開 repo は CS1 2021 の課題ごとの記号列の SHA-256（177 件・学生 ID と課題 ID が鍵）を出している。
- 研究者が CS1 の著者の返信を会話に貼った。要点の逐語: "Doing a release as you describe would be perfectly fine. Please just make sure credit can be traced back to the original dataset." → 了解を得たものとして扱う。
- 条件の確認: 公開 repo の README.md（l.147・l.191）と README.ja.md に Edwards, Hart and Shrestha と Harvard Dataverse doi:10.7910/DVN/BVOF7S（version 7.0）がある（GitHub の main を clone して確かめた）。本文は Edwards2023 を引き、補足 S3 に DOI と版がある。直すところは無い。
