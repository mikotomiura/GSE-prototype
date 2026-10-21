# verdict（stage: outline・round 2・2026-10-20）

## 1. 判定: minor revision（ただし 1 頁目の害の置き方は研究者の判断が要る）
有効な査読 3 本（R1 major・R2 minor・R3 minor）＋監査役。round 1 の major の多く（場面と向き・閉じた世界の列・Edwards の位置づけ・偏りの節・上限を主張しないこと）は解消と判定された。残る芯は 1 つ。

## 2. 一致した指摘（分母 3）
| # | 指摘 | R1 | R2 | R3 | 監査 | 裏取り |
|---|---|---|---|---|---|---|
| 1 | 場面 1（公開コーパス）は閉じた世界が成り立つときほど新しく知られることが無い（隠された作文がコーパスにあれば本文・記録・得点は公開済み・書き手は匿名）。害 (b) が生じる場面（教室・公開された作文）と、評価の閉じた世界が当たる場面が重ならない。1 頁目を (b) で書くと主張と根拠がずれる | ○ | ○ | ○ | — | 真（Table 1 の行と KLiCKe の公開の形） |
| 2 | 翻訳の保持者は集めた研究者（公開する側）で external と合わず、Table 1 に行も無い。評価の候補の作り方として扱う | ○ | ○(nit) | ○ | ○(B-1,B-2) | 真 |
| 3 | 一様の囮（似通い方）の偏りが §3.5 の一覧に無い | ○ | ○ | ○ | ○(B-7) | 真 |
| 4 | "Parts of logs" に実例・根拠が無い。公開する側の選択肢として言い直すか、例を知らないと書く。対応表に行 | ○ | ○ | ○ | ○(1-1) | 真 |
| 5 | 教室の場面の道具は教員が既に過程を見られることを示し、害の根拠と逆を向く。保持者を「本文と名前を持つが公開された過程を持たない者」に。教員が公開する側なら external でない | ○ | ○(external) | ○ | ○(B-1) | 真 |
| 6 | 1 頁目の計画が評価の当たらない保持者を限定なしに並べる | ○ | — | ○ | — | 真 |
| 7 | "withstands"（ethics・outline）が §3.5 の "do not recommend a form" と事前登録 "does not say that a processing step works" に反する強さ | — | ○ | — | ○(B-4) | 真 |
| 8 | Hanisch は出版版で逐語を確かめて引く | ○(nit) | ○(nit) | — | — | 真（arXiv 版しか読んでいない。ACM はボットに閉じる→研究者に取得を頼むか arXiv 版で引き続ける） |

1 人だけ（真）: 偽の一致の率が出ないこと（攻撃者は棄権しない・AUC は率を与えない）を限界に（R1）／事前登録の raters・platforms と「同じ作文が本文つきで公開」の場面が落ちている（R1・事前登録 l.39 で確認）／書き手ごとの分位点は 90 までで上側の尾が見えない（R1・事前登録 l.203 で確認）／「common choice」の一般化（R1）／有用性の軸（process measures）を §3.5 と 1 頁目に（R2）／Hanisch の基準（手順を知る攻撃者・小さな集団）に設計が応えていることを 1 文（R2）／二重盲検の手がかり（所属が無い・日付つきの personal communication）（R2）／倫理節に資産・敵が現れる場合・義務の側の理由・コード公開の範囲（R3）／To our knowledge の検索の範囲を書く計画（R3）／見出し "Logs are released with the text hidden." は 1 例からの一般化（R3）。
監査役だけ（真）: "the attackers do not use language models" と KeyTAR の記述の矛盾（B-5）／"useful for research on writing" の根拠が競技の得点予測だけ（B-3）／outline の Section 3 の対応表に行が無い主張（B-6）／Kaggle と KLiCKe の組み合わせを名指すことの害を倫理で量る（B-8）／ENJA15 の同意の引用元は LREC の論文で、outline の「the corpus paper」は不正確（B-9。data.md の記録では LREC 2016 §2 の逐語）／KeyTAR のモデルの利用条件を倫理に（B-10）／1 頁目に持ち帰り 3（B-11）。

偽陽性・確かめられない: 監査 3-3（論文用 repo の preregistration.md）は round 1 で確認済み。R2 の round 1 の 6（規約・合意）は保留のまま（考察で扱う予定を outline に書く）。

## 3. 直す順（研究者の判断の後）
major: 1 頁目と Goals and harms の害の置き方（研究者の判断）→ 場面 1 の書き直し（候補集合の大きさの代理）→ Table 1 の Newly learned を直す → 教室の保持者の定義。
minor: 翻訳を候補の作り方へ／§3.5 に一様の囮・偽の一致の率・上側の尾／Parts of logs を公開する側の選択肢として／withstands を外す／raters を戻す／common choice を弱める／LM の文を「脅威モデルの中の攻撃者は」に／有用性の軸／Hanisch の基準への応答／useful for research の根拠を弱める／outline の対応表と倫理の計画（資産・敵が現れる場合・義務の側・コード公開・組み合わせを名指す害・KeyTAR の利用条件）・同意の引用元の名前／To our knowledge の検索の範囲の計画／見出し。
二重盲検の手がかり: 投稿版で personal communication の日付を外すかは、二重盲検の扱い（引き継ぎ 7）と一緒に研究者に問う。

## 4. 注入・逸脱
注入の疑い無し（4 本）。逸脱なし。接地の引用を 8 件追加で照合し、すべて本文に在った。

## 5. 研究者に問うこと
- 1 頁目と Goals and harms でどちらの害を主にするか（下の問い）
- 直す一覧（3 の minor）の承認

## 6. 研究者の決定と対応（2026-10-20・判断 62）
- 主の害は (a)。1 頁目の計画・"Goals and harms"・Table 1 の第 1 行を (a) に合わせ、(b) は教室と公開された作文の場面での条件つきの帰結とした。
- minor を全部承認し、直した: 翻訳を候補の作り方へ／§3.5 に一様の囮（向き不明）・棄権しないこと・偽の一致の率が出ないこと・分位点が 90 まで／Parts of logs を公開する側の選択肢として（例を知らない）／withstands を外した（ethics・outline）／採点者と収集した側を第 1 行の保持者に戻した／common choice → used in at least one other release／LM の文を「within the threat model」に／有用性の軸を §3.5 と outline に／Hanisch の勧め（手順と引数を知る攻撃者）に沿うことを 1 文／useful for research → useful for predicting the quality of writing／見出し "A release may hide the text."／教室の保持者を「本文と名前を持つが公開された過程を持たない者」に、記録を公開した教員は攻撃者でないと明記／倫理: 利害関係者ごとの失うもの（悪用がある場合とない場合）・組み合わせを名指す害・義務の側の理由・KeyTAR の利用条件・コード公開の範囲（未決の印）／outline の対応表に行を足し、To our knowledge の検索の範囲を書く計画、合意（再識別を試みない約束）は考察で扱う計画。
- 残し: Hanisch の出版版での逐語の照合（ACM の PDF はボットに閉じる。arXiv 版で引き、出版版を note に記した）。二重盲検の手がかり（所属・日付）は二重盲検の扱いと一緒に研究者に問う。
- attack-me（stage: outline）はここで閉じる。投稿前の通しの attack-me（stage: manuscript）で確かめる。tmp/ は投稿前の通しの後に消す（同じ文献を使うため）。
