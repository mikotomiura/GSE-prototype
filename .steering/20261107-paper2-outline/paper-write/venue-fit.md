# 投稿先の適合（paper-write Step 0・論文 2）

- 日付: 2026-11-07
- 土台: 論文 1 の `.steering/20261105-public-data-findings-paper/paper-write/venue-fit.md`（2026-11-05・JEDM・JLA・IEEE は一次で照合済み、UMUAI・BRM・IJHCS は未照合）。ここには論文 2 で変わる点だけを書く。規程の文は写し直していない（変わっていれば投稿の前に一次で取り直す）。
- 目的（論文 1 の判断 5 と同じ・判断 9）: 読者は行動のログから状態を推す研究者。読んだ人に変えてほしいのは評価の設計（停滞のラベルの定義を 1 つに決めて率や比べを報告する前に、定義の幅で結論が動くかを見て報告する）。
- 制約: 独立の研究者・掲載料は払わない（memory「無料で済ませる」）・プレプリントを併せて出す。

## 論文 2 で変わる点

| | JEDM | BRM | UMUAI | JLA |
|---|---|---|---|---|
| 論文 2 との合い | 合う（教育データ・方法と比較）。論文 1（1484）が査読中で、同じ誌に B0 の定義を共有する 2 本目を出すことになる | 合う（方法の誌・休止の時間の一般化の先例 [V425] が同誌）。目的の読者（学習分析）とはずれる。IME の論文（BR-Org-26-1306）が査読中 | 合う（利用者の状態のモデルの評価） | 読者は最もよく合い、先例 [V468]・[V471] が同誌。機関のメールの要件で出せない（論文 1 の照合） |
| 掲載料 | なし | 購読型で無料（未照合） | 購読型で無料（未照合） | なし |
| 分量 | 上限の記載なし・最近の論文の中央値 約 10,200 語 | 上限なし（未照合） | 未照合 | 8,000 語（込み） |

## 結論（3 行・仮）

- 種類: 評価の設計への方法の貢献（定義の選択に対する感度の記述・multiverse）。比較・一般化の系統に近い。
- 読者: 行動のログから状態を推す研究者（学習分析・教育データ）。方法の誌（BRM）は読者が心理学の打鍵の研究者に寄る。
- 分量の仮の予算: 本文 6,500 語（上限 8,000）。投稿先は attack-me の後に研究者に聞く（引き継ぎ §3 の 5）。その時に候補の規程を一次で取り直す。

## 追記（2026-11-07）: 3 誌の規程を一次で取り直した（Sonnet のサブエージェント・curl と Chrome）

照合の格: [curl] は原文を grep で確認、[Chrome] は Chrome の本文から写した、[OpenAlex] は API の返り値。保存は scratchpad の `venue2/`（repo の外）。UMUAI の Aims & Scope の末尾と倫理の節は読めていない。

| | JEDM | BRM | UMUAI |
|---|---|---|---|
| 範囲 | [curl] "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." 主題は教育の場のデータ（4 つのうち CS1 の 2 つと KLiCKe は教育、CoAuthor は違う） | [Chrome] "methods, techniques, and instrumentation of research in experimental psychology" | [Chrome] 利用者に適応する系と利用者のモデルの評価。方法論の感度の分析を名指しする文は読めた範囲に無い |
| 分量 | 記載なし（論文 1 の照合と同じ） | 要旨 250 語以内・本文の上限なし [Chrome] | 要旨 150〜250 語・本文の上限なし [Chrome] |
| 掲載料 | [curl] "There are no charges for published papers." | OA は APC $4,090。購読型の道はあるが、無料の明言は見つからない [Chrome] | Open Choice（購読型の道あり）[Chrome] |
| 重なりの規程 | [curl] "no submission, or substantially overlapping submission, be published or be under review elsewhere"。同じ誌の中の関連の投稿の規定は無い | 投稿案内に duplicate・redundant・concurrent の語は 0 件。Springer 共通の方針は未取得 | [Chrome] "A single study should not be split up into several parts to increase the quantity of submissions and submitted to various journals or to one journal over time (i.e. 'salami-slicing/publishing')." |
| 倫理 | 公開データの二次分析の規定なし | [Chrome] 人のデータは承認か免除の声明と免除の理由。"retrospective ethics approval usually cannot be obtained" | 未取得 |
| 近い論文（2023〜2026） | multiverse は 0 件 [OpenAlex] | multiverse が複数: 読みの眼球運動のデータの清掃と分析の手順の multiverse（2025・doi:10.3758/s13428-025-02689-0）ほか [OpenAlex] | multiverse は 0 件 [OpenAlex] |

### 結論（3 行・更新）

- 第一候補は JEDM。理由: 範囲の文が「一般化できる方法論・比べの分析」を求め、読者（論文 1 の判断 5）が合い、掲載料なし。論文 1（1484）との関係は、重なりの規程が「他所」での審査を禁じる文なので抵触しないと読めるが、B0 の定義とデータの共有を送付状に明記する。
- 第二候補は BRM。multiverse の先例が同誌にあり方法の論文として最も通りやすい形だが、読者が心理学に寄り、所属のない著者の倫理の免除の書き方に不確かさがあり、無料で出せることの明言が見つからない。
- UMUAI は salami-slicing の明文があり、論文 1 と同じデータの研究を分けて出す形が最も慎重を要する。
- 誌によらない新しい事実: 同じ型（行動のデータの清掃と分析の手順の multiverse）の先例が BRM に既にある（2025）。新しさの文と関連研究の柱 1 に入れる必要がある（文献の追いかけ・citation-ssot で登録）。
