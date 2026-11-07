# 投稿の準備（JEDM・論文 1）

- 日付: 2026-11-07
- 研究者の判断（AskUserQuestion）: CS1 の著者の返事はまだ届いていない。匿名版にしない（単盲で出す）。今回はカバーレターと項目の一覧まで進め、版を上げることと公開 repo の写し直しは投稿する版が決まってから。
- 規程の出どころ: JEDM の頁を curl で取り、本文を抜き出して読んだ（scratchpad の `jedm-submit/`・repo の外）。Submissions・Information For Authors・About the Journal・Author Competing Interest Guidelines・Authorship Guidelines の 5 頁。サイトは Open Journal Systems 3.5.0.5（頁の generator の meta）。
- カバーレター: `papers/public-data-findings/submission/cover-letter.md`（英語・pandoc で組むと 1 頁・約 450 語）。

## 規程が求めることと、原稿の状態

| 規程（逐語の要点） | 出どころ | 原稿の状態 |
|---|---|---|
| 他誌に投稿中でない・既発表でない。会議論文の拡張なら 1/3 の新しい内容と、カバーレターに新しい貢献 | Submissions のチェックリスト | 該当しない（拡張でない）。カバーレターに書いた |
| 匿名版は任意。出せば双盲 | 同 | 匿名にしない（研究者の判断） |
| 倫理の基準に従う（COPE の著者向けの国際基準へのリンク） | 同 | 新しいデータの収集なし。Data and code availability に書いてある |
| 書式は JEDM のテンプレート（zip） | 同・Author Guidelines | `jedm` クラスで組んでいる（BUILD.md） |
| 利益相反をすべて申告。申告はカバーレターで | 同・Competing Interest Guidelines | カバーレターに書いた（推定器を著者が設計した・資金なし・編集者との関係なし）。下の未決 1 |
| 著者資格は ICMJE の 3 条件 | Authorship Guidelines | 単著。カバーレターに 1 文 |
| 投稿のファイルは PDF | Submissions のチェックリスト | 組んだ PDF を上げる |
| カバーレター（任意）を追加のファイルとして上げ、下の欄に貼る | 同 | ファイルと貼り付けの両方に使う。本文は同じもの |
| 生成 AI の利用を、参考文献の前の節「Declaration of Generative AI Software tools in the writing process」に決まった文で書く | 同・About の方針 | `sections/declarations.tex` にある（参考文献の直前）。方針の文は「使った部分を正確に」とあり、原稿は「all sections and in the supplementary material」と書いている |
| APA を参考に・投稿前の校正（Grammarly を勧める） | Author Guidelines | Grammarly は使わない（外部へ本文を送る）。組んだ誤り 0・overfull 1 は判断 41 の時点の数 |
| コードの共有を勧める。リポジトリをアーカイブして引用可能に | Author Guidelines・About | Zenodo の DOI（0.2.1）で示している |
| 査読者 3 名・3 か月を目指す。プレプリントは投稿の前と最中に可。受理・公開の後に DOI を足す | About・Copyright Notice | プレプリントは未決 2 |
| 掲載料なし。著作権は著者に残り、CC BY-NC-ND 4.0 で公開 | Information For Authors・Copyright Notice | 研究者が承知しておくこと（公開 repo のライセンスとは別） |

## 投稿の画面の項目（OJS 3.5）

ログインしないと画面は見えない。私はアカウントの作成とログインをしないので、下は OJS 3.5 の投稿の手順の一般の形と、JEDM の頁から読めることを合わせたもの。研究者が画面を開いたら、ここと違う項目を私が照合する（画面の文を読むのは私が Chrome でしてよいが、入力と Submit は研究者）。

| 段 | 項目 | 入れるもの |
|---|---|---|
| 登録 | 役割 | 「Register as Author」に印を付ける（付けないと Reader になり投稿できない・Information For Authors の逐語） |
| 1 開始 | 節（section） | 画面で選ぶ。research article に当たるもの |
| 1 開始 | チェックリスト | 上の表の 9 項目。匿名版の項目は「選ばない」で通る形か画面で確かめる |
| 1 開始 | 編集者への欄 | カバーレターの本文を貼る |
| 2 ファイル | 本文 | 組んだ PDF（補足は付録として同じ PDF に入っている） |
| 2 ファイル | 追加のファイル | カバーレターの PDF。CSV などの機械向けのファイルは上げない（memory の校正刷りの件） |
| 3 詳細 | 題 | 原稿の題をそのまま |
| 3 詳細 | 要旨 | `sections/abstract.tex` の本文を LaTeX の記号を外して貼る（`$[0.45, 0.55]$`・`--`・`\%`・`\url{}`）。貼る文は私が作る |
| 3 詳細 | キーワード | keystroke logging / stalls / equivalence testing / preregistration / introductory programming |
| 3 詳細 | 参考文献 | 欄があれば、組んだ PDF の参考文献を貼る |
| 4 寄与者 | 著者 | Mikoto Miura・Independent Researcher・ORCID 0009-0000-4196-0508・研究用のメール。国は研究者が入れる |
| 5 編集者へ | 資金・データ | 資金なし。データは原稿の Data and code availability と同じ |
| 6 確認 | 校正刷り | Submit の前に、システムが作った版の全頁を研究者が見る |

## 研究者の判断（AskUserQuestion・2026-11-07・判断 42）

1. 推定器を著者が設計したことを原稿にも書く → `sections/data.tex` の「The designer named the states」を「The author designed the estimator before this study and named its states」に（草稿 v8）。組むと誤り 0・未定義の参照と引用 0・overfull 1（v7 と同じ）。本文 7,463 語（+7）。
2. プレプリントは Zenodo で投稿の前に出す（公開は押す前に研究者に確かめる）。DOI が付いたらカバーレターの PREPRINT の行を埋める。
3. 投稿する版は v8（v7＋上の直し）。公開 repo の `paper/` を v8 に写し直して版を上げる（push と release の前に確かめる）。

## プレプリントの下書き（Zenodo・2026-11-07）

- 下書き 24026330（`unsubmitted`・予約の DOI 10.5281/zenodo.24026330）。PDF は Chrome の投稿の画面から上げ（Miura-2026-stall-runup-equivalence-preprint.pdf・323,529 バイト・md5 cc6cff37…が手元と一致・SHA-256 452f77ae…）、メタデータは deposit API で入れた（token はプロセスの中で読むだけ）。未公開の下書きはこの 1 件だけ。
- メタデータ: publication / preprint・CC BY 4.0・著者 Miura, Mikoto（Independent Researcher・ORCID）・題は原稿のまま・要旨は原稿の要旨から LaTeX の記号を外した文・版「v1 (manuscript before peer review)」・注記「Preprint; not peer reviewed.」・キーワード 5 つ・関連の識別子 9 件（公開 repo 0.2.2 の DOI と GitHub を isSupplementedBy、OSF の登録 5 件と CS1 の Dataverse 2 件を references。すべて解決を確かめた）。形は KeepCount のプレプリント（23858734）に揃えた。投稿先の誌名は書いていない（公開の時点では未投稿のため）。
- カバーレター: PREPRINT の行を予約の DOI で埋め、「既発表でない」に「プレプリントを除き」を足した（1 頁・約 470 語）。
- 公開（研究者の採否・AskUserQuestion）: 1 回目の publish は 400（`pids.doi` が空）。Chrome の画面で作った下書きは RDM の側の DOI が未設定で、deposit API の `prereserve_doi` は表示だけだった。RDM の API で `POST /api/records/24026330/draft/pids/doi` を呼んで同じ番号を予約し、2 回目で公開（`done`）。外から（token なし）`/api/records/24026330` で open・2026-11-07・preprint・CC BY 4.0・ファイル 1 つ（md5 一致）、取った PDF は手元と SHA-256 が同じ、`https://doi.org/10.5281/zenodo.24026330` は Zenodo に解決（302）。
- 次から: Zenodo の下書きは API だけで作る（画面で作ると DOI の欄が空のまま残る）。

## 投稿（2026-11-07・Claude in Chrome）

- 受付: JEDM の投稿番号 1484。受付の画面は「Submission complete」（確認のメールを送ったとの文）。API で status Queued・stage 1（submission）・節 Articles・dateSubmitted 2026-11-07 03:21:40（サイトの時刻。日本時間の 12:21 に押した）。
- ログインは研究者が先にしていた（私はパスワードを入れていない）。研究者の判断（AskUserQuestion）: 節は Articles、チェックリストとプライバシーの同意の印は私が付けてよい、全頁を見たうえで著作権の同意をして投稿する。
- 組んだもの（scratchpad・repo の外）: テンプレートは著者の頁のリンク（Google Drive）から 2024_08_02_jedm-latex.zip を取り直した。`build.sh` で誤り 0・未定義 0・overfull 1・32 頁。カバーレターは `pandoc cover-letter.md`（YAML の余白 22mm をそのまま使う。`-V geometry` で上書きすると URL がはみ出す）で 1 頁。
- 上げたファイル: 本文の PDF（Article Text・323,529 バイト・SHA-256 5eab8d6f…）とカバーレターの PDF（Letter to Editor・40,571 バイト・SHA-256 6e0f4dce…）。システムから取り直した 2 つが手元と SHA-256 で一致。OJS は校正刷りを作らない（編集者が見るのは上げた PDF そのもの）。
- 詳細: 題は原稿のまま。キーワード 5 つ。要旨は `abstract-plain.txt`（1,759 文字・一致）。参考文献の欄は main.bbl から 1 行 1 件の素の文 66 件。1 回目は変換が足りず（`{\O}`・`\v{s}` など）「Nielsen, M. .」になっていたので、9 か所を直して貼り直し、保存後に読み直した。編集者への欄はカバーレターの本文（pandoc の HTML）。
- 寄与者: 国 Japan・メールは登録のまま。所属にプロフィール由来の壊れた表記（PHP の serialize の文字列）が入っていたので「Independent Researcher」に直した（API で ror なしの 1 件を確認）。所属の候補を選ぶ途中で一覧が入れ替わり別の機関が選ばれたが、Add の前に外した。ORCID の欄は ORCID 側の確認が要るため空（原稿とカバーレターに番号がある）。
- 研究者のクリップボードは退避して戻した。
