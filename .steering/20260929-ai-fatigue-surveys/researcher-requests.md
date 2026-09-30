# [研究者] への依頼の一覧（本文の入手・有料データベースの検索）

> スクリプトやこちらの環境では届かないもの。★ 判定の結論は書かない（どの文献の何を確かめたいかだけ）。
> 本文・PDF を入手したら repo には置かず、置き場所を知らせてください（こちらで読み、要点だけを記録します）。
> ★★ **2026-09-30 の研究者の決定: 有料のデータベースと有料の本文は使わない**（「有料のやつは行わない形にしましょ。お金だせない」）。無料の版の有無は OpenAlex の `open_access`（DOI で 1 件ずつ・連絡先を送らない・2026-09-30）で確かめた。下の「状態」の列がその結果。記録は `../20260930-ai-fatigue-judge-file/decisions.md` 判断 3。

## A. 有料・自動取得できないデータベースの検索（S-12）

| # | データベース | 検索したいこと | 検索式の案 | 理由 | 状態（2026-09-30） |
|---|---|---|---|---|---|
| A1 | 医中誌 Web | 日本の医療者で、AI（生成 AI・AI 記録支援・画像診断 AI 等）の利用と疲労・燃え尽き・負担を扱った研究 | `(人工知能/TH or AI/AL or 生成AI/AL or ChatGPT/AL or 大規模言語モデル/AL) and (疲労/TH or 燃え尽き症候群/TH or バーンアウト/AL or 疲弊/AL or 負担/AL)`（シソーラス語は医中誌の画面で確かめてください） | S-12 の検索範囲に医療の日本語文献が入っていない | **行わない**（有料）。日本語の医療の文献は、無料の J-STAGE（S-12 で検索済み）の範囲に限られる |
| A2 | Google Scholar（手で） | 日本語の「AI疲れ」「生成AI 疲労」「AI 疲弊」「精査疲れ」 | 上位 50 件の題名と件数 | 学会の予稿・紀要・学位論文の拾い漏れを見る（自動取得は利用規約で禁止） | 研究者が手で行う（無料・題名と件数だけ） |
| A3 | 情報処理学会 電子図書館（情報学広場） | 研究会・全国大会の予稿で、生成 AI の利用と疲労・負担を扱うもの | `生成AI 疲労`・`LLM 負担`・`AI 疲れ` | スクリプトで検索する口が無い | Claude がブラウザで検索する（無料の検索だけ・題名と件数だけ） |

## B. 本文の入手（機関アクセス・著者への依頼）

| # | 文献 | 確かめたいこと | 関係する issue |
|---|---|---|---|
| B1 | AF002（ScienceDirect） | 疲労の項目文・標本・収集時期。★ 2026-09-30: 経路の強さ（応答の不確実さ → 認知的疲労 と プロンプトの不確実さ → 感情的疲労）と交差の経路 | N-01・N-14 |
| B2 | AF003（ScienceDirect） | 同上。AF002 と標本が別か。★ 2026-09-30: 人数 1,045 の本文での確認 | N-01・N-14 |
| B3 | AF009（IEEE Xplore） | 同上 | N-01 |
| B4 | Asmi ほか 2026（JEIM, doi:10.1108/jeim-10-2025-1027）と訂正通知（doi:10.1108/jeim-08-2026-1628） | 意思決定疲労の尺度の出典・項目が AI に向くか・標本の国。訂正の中身 | S-02 |
| B5 | Khoso ほか 2026（Acta Psychologica, doi:10.1016/j.actpsy.2026.107396）★ CC BY の表示あり。スクリプトでは出版社のページに届かない（ブラウザで読む許可があれば、こちらで読める） | データの出どころ・収集時期・Scientific Reports 2026（同じ著者・N=545）への言及 | S-02 |
| B6 | Thorpe ほか 2025（AI & Society, doi:10.1007/s00146-025-02764-2） | 燃え尽きの尺度・デザイン | S-02 |
| B7 | Kim & Kim 2026（Technology in Society, doi:10.1016/j.techsoc.2026.103553） | 抄録すら取れていない。疲労（消耗）の測定・標本 | S-02 |
| B8 | Kang & Li 2025（Journal of Business Convergence, doi:10.31152/jb.2025.12.10.6.297・DBpia） | AI 疲労の尺度の出典・項目数・項目文（S-08 の一覧に入れるため） | S-02・S-08 |
| B9 | Nobles 2026（Zenodo, doi:10.5281/zenodo.22838191） | 公開のファイルだが、2026-09-29 に Zenodo が 403（大量アクセスの制限）を返した。日をおいてこちらで再取得する（ブラウザで手で落とせるなら、その方が早い） | S-02 |
| B10 | Ambient Artificial Intelligence Use and Clinician Documentation Burden, Productivity, and Efficiency（*JAMA Netw Open* 2026, doi:10.1001/jamanetworkopen.2026.15762） | 抄録が取れず、S-04 の機械のふるいを題名だけで受けた。比較の有無・燃え尽きや疲労の測定 | S-04 |
| B11 | Reimagining Surgical Documentation: Implementing Ambient Artificial Intelligence…（*Plast Reconstr Surg* 2025, doi:10.1097/prs.0000000000012725） | 同上（題名に燃え尽きの語） | S-04 |
| B12 | Impact of Ambient Artificial Intelligence Documentation on Cognitive Load（*Mayo Clin Proc Digit Health* 2025, doi:10.1016/j.mcpdig.2024.100193） | 同上 | S-04 |

★ 2026-09-30 の状態（OpenAlex の `open_access`）: **無料の版が無い 8 件**（B1・B2・B3・B4・B6・B7・B8・B11）は「入手不可（費用）」。★ **無料の版がある 4 件**は Claude が読む: B5（gold・ScienceDirect の PDF。スクリプトでは届かないのでブラウザで）・B9（green・Zenodo）・B10（gold・PubMed Central に投稿版）・B12（gold・PubMed Central に投稿版）。著者に本文を頼むのは無料だが外部に出る操作なので、送るかは研究者が決める（N-03 と同じ扱い）。

★ 2026-09-30（後）: 無料の 4 件を読んだ。B5 → `survey-S-02.md` #3・§3（出版社のページをブラウザで読んだ）。B9 → 同 #8（Zenodo のファイルが今回は取れた。原稿の写しと表で、採択 32 件と DB・追加候補を DOI で突き合わせた）。B10・B12 → `survey-S-04.md` §1・§3（Europe PMC の全文。どちらも疲労・燃え尽きの尺度は無い）。★ 上の「PubMed Central に投稿版」は取り違えで、B10・B12 とも PubMed Central にあるのは出版社の版だった。残る依頼は、入手不可（費用）の 8 件（B1〜B4・B6〜B8・B11）と A 群。

（S-08 以降で見つかったものは、このあとに足す。）
