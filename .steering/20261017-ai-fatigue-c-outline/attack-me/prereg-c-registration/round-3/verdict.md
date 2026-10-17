# verdict（prereg・round 3・2026-10-17）

対象物: `registration-en.md` 草稿 0.3（コミット b94d9bd4）と `codebook-c2b-en.md` 版 2（コミット 9cf22180）。

## 1. 編集者の判定

**minor revision（直してから凍結）**。有効な査読 3 本とも minor。round 2 の指摘は 3 本とも全件解消と判定。残る major（R1 3 件・R2 2 件・R3 3 件）は、どれも規則の文を足せば消え、再査読は要らないと 3 本とも書いた。ただし主な数え方の入口（語の族・C1 の範囲・審査の範囲）は、直した文をメインが目で確かめてから凍結する。

## 2. 裏取り

- 接地: R1（Elson 1・Lintner 1）・R2（Perrig 2）・R3（Nuijten 1・GSRR 1）を照合し、すべて在った（Perrig の "scale-based" は pdftotext で "scalebased" になっていた）。
- 監査役 D-1 の「Jonaid は完了したレビューか」: DataCite の型は **Pre-registration**。→ 真。草稿 0.3 の "evaluate measurement properties with COSMIN; one example covers" は言い過ぎだった。0.4 で「registered review」と直し、参考文献に [Preregistration] と書いた。
- 偽陽性: 無し。

## 3. 2 人以上が一致した指摘（分母 3）と対応（草稿 0.4）

| 指摘 | 誰 | 対応 |
|---|---|---|
| 語の族の境界（2 族にまたがる名・族の外の語・結論に語が無い・語形） | R1・R2・R3 | 構成概念の語＝族の語（活用・複合を含む）・1 つでも共有すれば same・「instrument name has no family term」の値・(iii) は語が無ければ成立しない |
| 項目が載っていない尺度（原典から補う条件・部分開示の分母・origin の値・限界） | R1・R2 | 「変更なしで使った」と書かれていれば原典から補い印を付ける・部分開示は載った項目数を分母に全数を併記・origin に「wording not verifiable」・「items unavailable」の数を常に併記・限界に開示の偏り |
| 較正と小さい集合（15 件＋最小 10 件・探索の記録の seed・較正に使った探索の記録） | R1・R2・R3・監査 | 閾値を 25 件に・探索から seed 20261019 で最大 2 回・使った記録に印を付けて分けて示す |
| target の kappa の重複・止め方の単位 | R1・R2・R3・監査 | target は「no target」を含む全項目の 1 つに・止め方は GSRR-47 の単位（導出値を除く）・boundary と secondary の kappa を足す |
| codebook の mismatch の食い違い | R1・R3・監査 | 探索の記録だけと揃えた |
| late stratum の締めと手順 | R2・R3 | stage 5 の開始まで・2 人でコード |

## 4. 1 人だけの指摘（すべて採った）

- R1: C1 の AI の語の一覧・L1a は 1 項目以上（割合を記録）／L3 を C7 (ii) に入れる／設計の残余（other・unclear・diary・case）／C3 は複数可／群を交互に進める順（巡回）／C2b は COSMIN の内容的妥当性ではないと書く。
- R2: C1 は疲労の尺度を対象に、RQ1 と C7 は主な尺度の代表値／保留の 3 件の行き先（探索の集合へ）／AI と無関係な介入は操作なし・数える関係は AI 側の変数と疲労／抄録の results を文で定義／C2d の理由の基準／最小の尺度の数は項目のある尺度だけ。
- R3: 審査の対象＝登録の日に 2 人の最終判定が無いすべての候補（71 件・43 件を含む）・順の一覧と SHA-256 と Python の版を添付／AI の下書きは両方が値を固定するまで開けない・SHA-256 を記録／7 つの論点と問題の型の対応表／E5 の数え分けは C5 と RQ4 だけ／statcheck の規則への参照と片側の検出。
- 監査: 草稿に無いものを数える位置づけ（対応表に「In the narrative review?」の列）／分析の単位が複数あること（GSRR-5）／C1 を問題の型から外す（適格の定義と同じ理屈。問題は C7 (ii) が捉える）／43 件を「additional candidates」に含める（264 件）／本検索が 12-31 より前に走った場合／SQ1 に SQ2 を入れる／disengagement と `MOT` の対応／GSRR-34 の時制（8 件は除外）。
- 監査 C-4（decisions.md の判断 9 の「未対応」）は判断 10 で閉じる。C-10（骨子の古い記述）は判断 8 の「登録版が優先」のまま、骨子は直さない。

## 5. 逸脱

- 監査役は outline.md を全文読んだ（round 1・2 と同じ）。
- メインは round 3 の起動の間に `scripts/`（集計の脚本とダミーの表）を作った（対象物には触れていない）。

## 6. 研究者に問うこと

- 凍結してよいか（登録の前に埋める [at registration] の欄: 著者の名前・ORCID、著者 2 の全文の既読、検索の文字列、審査の順の一覧、脚本の SHA-256、コーディングの書式）。
