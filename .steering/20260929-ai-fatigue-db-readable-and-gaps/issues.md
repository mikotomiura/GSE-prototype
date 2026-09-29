# AI 疲労 文献 DB：調査不足の issue 一覧（2026-09-29）

> ★ 生成物。`scripts/issues_data.py` から `scripts/build_readable.py` が書く（xlsx の『調査不足とissue』シートと同じデータ）。手で直さず、データを直して再生成する。
> ★ GitHub の issue は起票していない。著者への照会も送っていない（下書きのみ・付録 A）。
> ⚠️ 件数は『調べる価値』の目安で、PRISMA の件数ではない（付録 B）。

## 一覧

| 番号 | 種類 | 優先度 | 手間 | タイトル | 依存 |
|---|---|---|---|---|---|
| S-01 | サーヴェイ | 高 | 大 | 専門データベースで本検索を行う（英語） | N-05 |
| S-02 | サーヴェイ | 高 | 中 | 検索漏れ候補を抄録で判定する（まず ★ 印 8 件と AF017 の引用追跡 3 件） | —（N-05 の前でも、判定の記録を残せば進めてよい） |
| S-04 | サーヴェイ | 高 | 中 | 反対向き・中立の証拠を集める：AI は疲労・燃え尽きを減らすか（医療の AI 記録支援・下書き返信など） | N-05 |
| S-05 | サーヴェイ | 高 | 中 | 自動化を『見張る』疲労（受動的疲労・覚醒水準の低下・自動化への慢心）の研究を取り込む | N-05 |
| S-06 | サーヴェイ | 中 | 中 | 『警報疲れ（alert fatigue）』と AI の出力への反応（医療の意思決定支援）を調べる | N-05 |
| S-07 | サーヴェイ | 中 | 中 | 働く人・専門職の AI 疲労を狙って探す（開発者・医療者・AI の出力を評価する人） | S-01 |
| S-08 | サーヴェイ | 中 | 中 | AI 疲労の測定尺度を一覧にし、測定の質を COSMIN で評価する（翻訳版の有無を含む） | S-02 |
| S-09 | サーヴェイ | 中 | 小 | 『なぜ疲れるのか』の理論の節を作る（機会費用・補償的制御・能動／受動的疲労・自我消耗の再現性問題） | S-05（受動的疲労の部分） |
| S-10 | サーヴェイ | 中 | 小 | 強いデザイン（縦断・日誌法・実験）で AI と疲労を扱った研究を狙って探す | S-01 |
| S-12 | サーヴェイ | 中 | 小 | 日本語の文献・日本の対象者の研究を探す | — |
| S-03 | サーヴェイ | 低 | 小 | 引用追跡を行う（前方: AF001 を引く研究／後方: 既存レビューの採択研究） | N-08（AF014 を使う場合） |
| S-11 | サーヴェイ | 低 | 小 | 『AI 疲労』という語の使われ方を整理する（使っていて疲れる／AI の話題・導入に疲れる／AI による仕事の増加で燃え尽きる／プロンプト疲れ） | S-02 |
| I-01 | アイディア | 高 | 小 | 【GSE へ】この DB を、GSE のロードマップ最優先 5『AI 疲労を横断する scoping review』の AI 疲労の系統として扱うかを決める | — |
| I-02 | アイディア | 高 | 中 | 【GSE へ】検証負担・やり取りの負担（verification / interaction burden）の自己報告項目の候補を、EVAL-NCC の測定辞書に足すか検討する | N-07（AF001 の項目を参照するなら） |
| I-09 | アイディア | 高 | 中 | 【サーベイ論文へ】疲労の『源』で中心候補をコーディングする（プロンプトを作る負担／出力を確かめる負担／修正・やり直しの負担） | N-05・S-02 |
| I-03 | アイディア | 中 | 小 | 【GSE へ】『能動的な疲労／受動的な疲労』の区別を、生成的返権論の負荷逆説（§6.3）の境界条件として書き足すか検討する | S-05 |
| I-04 | アイディア | 中 | 大 | 【両方】AF001 の AI 疲労尺度の日本語版を作り、検証する計画を立てる（独立した研究になりうる） | N-07・S-08 |
| I-05 | アイディア | 中 | 小 | 【GSE へ】GR-H12 の反証表の交絡の欄に『睡眠』を足すか検討する（AF008 の所見から） | — |
| I-10 | アイディア | 中 | 小 | 【サーベイ論文へ】『誰が負担を負うか』の列を抽出フォームに足す（解釈・確認・修正・帰結） | N-05 |
| I-11 | アイディア | 中 | 小 | 【サーベイ論文へ】序論の枠組み: AI 疲労を『自動化が人に残す後始末の負担』の系譜に置く | S-05 |
| I-12 | アイディア | 中 | 小 | 【サーベイ論文へ】文献の質の問題そのものを所見として書く（報告値の食い違い・参考文献や DOI の誤り・媒体の偏り） | N-03 |
| I-06 | アイディア | 低 | 小 | 【GSE へ】研究ポジショニング §1『AI 時代の角度』を、DB の証拠の強さで点検する | N-01 |
| I-07 | アイディア | 低 | 小 | 【GSE へ】Nudge の『通知疲れ・慣れ』の文献を、介入設計の制約として取り込む | S-06 |
| I-08 | アイディア | 低 | 小 | 【GSE へ】【保留・記録のみ】GSE のデータで AI 利用の有無を区別したくなったときの前提を書き残す | — |
| N-01 | 通常 | 高 | 小 | 中心候補のうち本文未入手の 3 件（AF002・AF003・AF009）の全文を入手し、中心-A か B かを確定する | — |
| N-02 | 通常 | 高 | 中 | 人間 2 名の独立スクリーニングを行い、AI の予備判定と照らし合わせる（判定者用ファイルの仕上げ・AF024 の範囲判定を含む） | N-05 と同時に進めてよい（基準が変わるなら N-05 を先に） |
| N-05 | 通常 | 高 | 中 | スコーピングレビューのプロトコルを確定し、事前登録する（OSF など） | I-01 の決定（GSE のレビューと共有するか）があれば反映 |
| N-03 | 通常 | 中 | 小 | 報告値の食い違いを著者に照会するかを決め、送るなら送る（6 件・下書きあり） | — |
| N-04 | 通常 | 中 | 小 | 元 DB を v1.1 に更新する（書誌の補完・デザインや件数の修正を反映） | N-01 の結果も反映するなら N-01 の後 |
| N-06 | 通常 | 中 | 小 | IEEE DataPort の『AI 疲労』データセット 2 件が実測か合成かを確かめる | — |
| N-10 | 通常 | 中 | 小 | 【GSE】中央書誌 [P362]（AF001）の注記を一次に合わせる | — |
| N-07 | 通常 | 低 | 小 | AF001（AI 疲労尺度）の補足資料で全 15 項目・事前登録・データを確認する | — |
| N-08 | 通常 | 低 | 小 | AF014（包括的レビュー）の引用文献の実在を確かめる（引用追跡に使う場合のみ） | S-03 |
| N-09 | 通常 | 低 | 小 | Arun & Fischer 2026 の本文を読み、AF020 の『一部再現しなかった』報告を確かめる | — |

## おすすめの順番

1. **すぐにできる（数日）**: N-01 本文未入手の 3 件の全文入手／S-02 ★ 印など 11 件の抄録判定／N-06 データセット 2 件の確認／I-01 GSE との関係を決める
2. **サーベイの土台（1〜2 週）**: N-05 プロトコルの確定と事前登録（S-04・S-05・S-06 の範囲、I-09・I-10 の抽出フォームの列をここで決める）→ N-02 人間 2 名の独立判定（★ 判定者 1 は、判定が終わるまで AI のまとめを読まない）
3. **本検索（数週）**: S-01 専門データベースでの本検索（S-07 職種・S-10 強いデザイン・S-12 日本語の検索ブロックを含める）
4. **論文の中身を厚くする**: S-04 反対向きの証拠／S-08 尺度の一覧／S-09 理論の節／S-11 語の用法／I-11 序論の系譜／I-12 文献の質を所見に
5. **GSE への還元（研究者の判断）**: I-02 検証負担の項目案／N-10 [P362] の注記／I-05 GR-H12 の交絡／I-03・I-04・I-06・I-07

## サーヴェイ issue

### S-01（優先度 高・手間 大）専門データベースで本検索を行う（英語）

- **なぜ必要か**: 元 DB は公開 Web の 53 クエリ（ヒット件数なし）で集めた探索版。2026-09-28 に OpenAlex と Crossref で上位 50 件だけを点検しても、題名段で『含める』候補が 31 件見つかった ＝ DB が網羅できていない強い兆候。
- **根拠の場所**: はじめに A8〜A9／項目定義・採択基準 r23〜r24／検索漏れ候補（31 件が『含める』）
- **調べる価値の判断材料**: OpenAlex の自由語検索で『"AI fatigue"』158 件（2026-09-28 の点検と 2026-09-29 の再取得で同じ値）。
- **次の一手**: N-05 で決めた検索式を Scopus・Web of Science・APA PsycInfo・IEEE Xplore・ACM DL・PubMed（または Europe PMC）・ERIC で実行 → データベースごとのヒット数と実行日を記録 → 文献管理ソフトに書き出して重複を除く → 二重スクリーニング（N-02 と同じ手順）。
- **完了の条件**: PRISMA の流れ図が作れる件数（検索 → 重複除去 → TA 段 → 全文段）がそろう。
- **GSE との関係**: —
- **依存・順序**: N-05

### S-02（優先度 高・手間 中）検索漏れ候補を抄録で判定する（まず ★ 印 8 件と AF017 の引用追跡 3 件）

- **なぜ必要か**: 145 件は題名と機械抽出の語だけで予備判定しており、抄録は読んでいない。★ 印は査読誌の中心的な候補で、DB の結論（中心-A は 7 件）を変えうる。
- **根拠の場所**: 検索漏れ候補（H 列＝含める 31・保留 42・除外 72）
- **調べる価値の判断材料**: ★ 候補の実在は Crossref で確認済み: JEIM 2026（意思決定疲労・訂正あり）doi:10.1108/jeim-10-2025-1027／Scientific Reports 2026 doi:10.1038/s41598-026-45402-7／Acta Psychologica 2026 doi:10.1016/j.actpsy.2026.107396／AI & Society 2025 doi:10.1007/s00146-025-02764-2／Technology in Society 2026 doi:10.1016/j.techsoc.2026.103553／Education and Information Technologies 2025（プライバシー疲労）doi:10.1007/s10639-024-13198-6／Journal of Business Convergence 2025（AI 不安から疲労へ）doi:10.31152/jb.2025.12.10.6.297／Zenodo の AI 疲労の系統的レビュー（非査読・Nobles 2026・DataCite で確認）doi:10.5281/zenodo.22838191。★ Scientific Reports 2026 と Acta Psychologica 2026 は著者が共通（Honggang W・Khoso A）で題名も似る → AF006・AF007 と同じく、標本の重なりを先に確認する。
- **次の一手**: ★ 8 件（★ は 9 行あるが 1 行は Zenodo のレビューの版違い）と AF017 の引用追跡 3 件、計 11 件の抄録を読み TA 段で判定 → 含めるものは全文段へ → Zenodo のレビューは採択研究の一覧を DB と突き合わせる → 残りの『含める』『保留』も同様に。
- **完了の条件**: 11 件の TA 段と全文段の判定が記録され、中心-A / B の件数が更新される。
- **GSE との関係**: —
- **依存・順序**: —（N-05 の前でも、判定の記録を残せば進めてよい）

### S-04（優先度 高・手間 中）反対向き・中立の証拠を集める：AI は疲労・燃え尽きを減らすか（医療の AI 記録支援・下書き返信など）

- **なぜ必要か**: 元 DB の基準は『負担低下・群間差なしの結果も記録する』と定めるが、中心候補はすべて『AI で疲れる』向き。一方で医療では、AI の記録支援（ambient AI scribe）や患者メッセージの下書きが医療者の燃え尽き・ウェルビーイングを変えるかを、無作為化比較試験で調べた研究が既にある。DB の中心には実験が 1 本もないので、ここは一方向に偏って見える最大の穴。
- **根拠の場所**: 項目定義・採択基準 r8／検索漏れ候補 No.61・73・76・80・84・88・91・93（いずれも保留止まり）
- **調べる価値の判断材料**: Europe PMC（題名・抄録）で『AI 記録支援 × 燃え尽き・疲労・認知負荷』89 件、『AI の下書き返信 × 燃え尽き等』18 件（2026-09-29）。種文献（Crossref で確認）: Lukac et al. 2025 NEJM AI の RCT doi:10.1056/aioa2501000／Afshar et al. 2025 NEJM AI のプラグマティック RCT（ウェルビーイング）doi:10.1056/aioa2500945／Olson et al. 2025 JAMA Netw Open doi:10.1001/jamanetworkopen.2025.34976／Shah et al. JAMIA doi:10.1093/jamia/ocae295／Garcia et al. 2024 JAMA Netw Open doi:10.1001/jamanetworkopen.2024.3201／Tai-Seale et al. 2024 JAMA Netw Open（RCT）doi:10.1001/jamanetworkopen.2024.6565。
- **次の一手**: N-05 で『AI が疲労を減らす介入研究』の扱いを決める → 医療・教育・一般業務で、AI 導入の前後または群間で疲労・燃え尽き・負担を測った研究を検索 → 向き（減る／差なし／増える）と測定尺度を表にする。
- **完了の条件**: 向き別の件数と、測定尺度・デザインの表ができる。
- **GSE との関係**: ★ GR-H11（負荷の最小化を普遍的な善にしない）・roadmap §5.7『負担最小化を普遍善にできない』と対になる証拠。AI が負担を『減らす』研究も『移す』研究も、GSE では interaction burden / verification burden の区別で読む。
- **依存・順序**: N-05

### S-05（優先度 高・手間 中）自動化を『見張る』疲労（受動的疲労・覚醒水準の低下・自動化への慢心）の研究を取り込む

- **なぜ必要か**: 元 DB の対象は『AI を利用・監督・評価する人』だが、監督（見張り）による疲労の研究が 1 本もない。自動運転やヒューマンファクターでは、作業を自動化に任せて見張るだけになると『受動的疲労（passive fatigue）』が生じ、覚醒水準が下がることが長く研究されている。AF009 の因子名にも『Passive Fatigue』がある。
- **根拠の場所**: 項目定義・採択基準 r7（中心の対象）／Claude適格性評価 AF009／GSE の [P373]・[P375]（自動化の段階・制御の遷移）
- **調べる価値の判断材料**: Europe PMC（題名・抄録）で『passive fatigue』26 件、『automation complacency』25 件（2026-09-29）。Semantic Scholar（題名・抄録の一括検索）で『passive fatigue』87 件、うち自動化を含む 36 件。種文献（Crossref で確認）: Desmond & Hancock（能動的／受動的疲労の古典・書籍の章）doi:10.1201/b12791-3.1／Saxby et al. 2013 J Exp Psychol Appl doi:10.1037/a0034386／Körber et al. 2015 doi:10.1016/j.promfg.2015.07.499／Neubauer et al. Human Factors doi:10.1177/0018720811423261／Matthews et al. 2019 のレビュー doi:10.1016/j.aap.2018.04.004／Parasuraman & Manzey 2010 doi:10.1177/0018720810376055。
- **次の一手**: N-05 で自動運転などの自動化を『AI』に含めるか決める → 含めない場合も、理論節（S-09）の背景として能動的／受動的疲労の区別と測定法（課題負荷・覚醒の尺度）をまとめる。
- **完了の条件**: 能動的／受動的疲労の区別と、既存の測定法の表が理論節または隣接研究に入る。
- **GSE との関係**: I-03（生成的返権論の境界条件）の材料になる。
- **依存・順序**: N-05

### S-06（優先度 中・手間 中）『警報疲れ（alert fatigue）』と AI の出力への反応（医療の意思決定支援）を調べる

- **なぜ必要か**: AI・自動化の出力（警報・提案）を大量に受け取ると、無視や上書きが増える『警報疲れ』は医療情報学で確立した概念。AI の出力を確かめる負担（検証負担）と同じ構造だが、DB に入っていない。AI で警報を減らす研究もある（検索漏れ候補 No.42）。
- **根拠の場所**: 検索漏れ候補 No.42（AI Magazine 2026・保留）
- **調べる価値の判断材料**: Europe PMC（題名・抄録）で『alert fatigue』537 件、うち AI・機械学習を含む 80 件（2026-09-29）。種文献（Crossref で確認）: van der Sijs et al. 2006 JAMIA doi:10.1197/jamia.M1809／Ancker et al. 2017 doi:10.1186/s12911-017-0430-8／Graafsma et al. 2024 JAMIA のスコーピングレビュー doi:10.1093/jamia/ocae076。
- **次の一手**: N-05 でルールベースの警報を範囲に含めるか決める → 含めない場合も、概念の比較（警報疲れ・自動化バイアス・AI 疲労の違い）として背景に入れる。
- **完了の条件**: 警報疲れと AI 疲労の概念比較の表ができる。
- **GSE との関係**: I-07（Nudge の通知疲れ）の材料になる。
- **依存・順序**: N-05

### S-07（優先度 中・手間 中）働く人・専門職の AI 疲労を狙って探す（開発者・医療者・AI の出力を評価する人）

- **なぜ必要か**: 中心-A の 7 件に『働く人』の標本が 1 件もない（大学生 3・一般の利用者 4）。働く人は中心-B の AF019 だけ。検索漏れ候補には職場の燃え尽き研究が多い（No.62・74・79・83・87・89・97・103・105・139）。開発者の AI コーディング支援、AI の出力を評価する人（注釈者・評価者）はまったく手つかず。
- **根拠の場所**: 証拠の地図シート／検索漏れ候補（職場の候補）
- **調べる価値の判断材料**: Europe PMC（題名・抄録）で『生成 AI × 疲労・燃え尽き × 医師・看護師・放射線科医など』67 件（2026-09-29）。⚠️ 開発者（Copilot・AI コーディング支援）の件数は未計測: Semantic Scholar では Copilot が『副操縦士（co-pilot）』とも一致して意味のある件数にならず、OpenAlex は 2026-09-29 に匿名検索が回数制限で使えなかった。
- **次の一手**: 職種ごとの検索語（developer / programmer / Copilot、physician / nurse、annotator / rater / content moderator）で S-01 に追加の検索ブロックを作る。
- **完了の条件**: 職種別の件数と中心候補の一覧ができる。
- **GSE との関係**: GSE の Coding head（task_kind）と VibeCoding（AI 操作が主体で打鍵が薄いドメイン・G1 README）の文脈で、開発者の研究は参考になる。★ ただし GSE は打鍵から AI 疲労を推定しない（GR-H12）。
- **依存・順序**: S-01

### S-08（優先度 中・手間 中）AI 疲労の測定尺度を一覧にし、測定の質を COSMIN で評価する（翻訳版の有無を含む）

- **なぜ必要か**: DB で AI に向けた疲労を測る道具はばらばら: AF001 の 15 項目尺度（唯一まとまった検証）、AF009 の探索的な 25 項目、AF005 の既存尺度の書き換え、AF002・AF003 の書き換え項目、AF008 の非公開の項目。サーベイ論文で『何で測られてきたか』は中心的な問い。
- **根拠の場所**: Claude方法論評価（COSMIN）／Claude領域別評価（測定・構成概念）／AF032（COSMIN）
- **調べる価値の判断材料**: OpenAlex で『"AI fatigue scale"』6 件（2026-09-29）。J-STAGE・CiNii の題名段で、日本語の AI 利用者の疲労の尺度・研究は 0 件（2026-09-29・8 語・各上位 100 件）。
- **次の一手**: S-01・S-02 の含める研究から尺度を抜き出し、項目数・下位尺度・AI への向け方・信頼性・妥当性・翻訳版を表にする。COSMIN の測定特性ごとに評価（合計点は付けない）。
- **完了の条件**: 尺度の一覧表と、測定特性ごとの評価ができる。
- **GSE との関係**: ★ GSE は AI 疲労尺度を外部の自己報告（ベースライン・遅延追跡）にだけ使い、瞬間状態・介入の引き金・短縮版には使わない（roadmap §5.7・GR-H12）。I-04（日本語版）の前提。
- **依存・順序**: S-02

### S-09（優先度 中・手間 小）『なぜ疲れるのか』の理論の節を作る（機会費用・補償的制御・能動／受動的疲労・自我消耗の再現性問題）

- **なぜ必要か**: DB の『尺度・理論』は尺度の原著だけで、疲労が生じる仕組みの理論がない。AF004 は自我消耗理論に依拠しているが、その再現性には大規模な反証がある。
- **根拠の場所**: GSE照合 追加候補（[P205]・[P206]・[P209]）／Claude領域別評価 AF004
- **調べる価値の判断材料**: GSE に既に精読済みの文献がある: Kurzban et al. 2013 の機会費用モデル [P205]、Agrawal et al. 2022 の規範的説明 [P206]、Hopstaken et al. 2015 の離脱の可逆性 [P209]、自我消耗の多施設の追試とメタ分析 [P199]・[P200]・[P201]・[P204]、そのグルコース説への反証 [P207]・[P208]（★ 前回の GSE照合シートは再現性問題を [P207]・[P208] としたが、この 2 件はグルコース説への反証である）。GSE に無いもの（Crossref で確認）: Hockey 1997 の補償的制御の枠組み doi:10.1016/S0301-0511(96)05223-4、Saxby et al. 2013 の能動的／受動的疲労 doi:10.1037/a0034386。
- **次の一手**: GSE の精読カードから要点を移し、Hockey 1997 と能動／受動的疲労を足して 1〜2 頁の理論の節にする。
- **完了の条件**: 理論の節（出典つき）ができ、DB の『尺度・理論』に理論の文献が加わる。
- **GSE との関係**: GSE の既存カードを再利用できる（新しく引く文献は citation-ssot で登録）。
- **依存・順序**: S-05（受動的疲労の部分）

### S-10（優先度 中・手間 小）強いデザイン（縦断・日誌法・実験）で AI と疲労を扱った研究を狙って探す

- **なぜ必要か**: DB の一次研究は横断調査と質的研究がほとんどで、時間をずらして測ったのは AF019 と AF022 だけ（どちらも AI に向けた疲労ではない）。AI を操作して疲労を測った実験は 0。『AI を使うと疲れる』の因果には近づけていない。
- **根拠の場所**: 証拠の地図シート／Claude領域別評価（時間順序・因果）
- **調べる価値の判断材料**: Europe PMC（題名・抄録）で『生成 AI × 疲労・燃え尽き × 縦断・日誌・経験サンプリング・無作為化』24 件（2026-09-29）で、上位は医療の AI 記録支援の RCT（S-04 と重なる）。医療以外の強いデザインは見当たらない。
- **次の一手**: S-01 の検索式に設計のフィルタ（longitudinal / diary / experience sampling / randomized）を足した検索ブロックを作り、医療以外を重点的に見る。
- **完了の条件**: 強いデザインの研究の件数と一覧ができる（0 件ならそれ自体をサーベイの所見として書ける）。
- **GSE との関係**: GSE の O1（常時収集）は長期の自然作業を記録するが、AI 利用の有無は記録しない（I-08）。
- **依存・順序**: S-01

### S-12（優先度 中・手間 小）日本語の文献・日本の対象者の研究を探す

- **なぜ必要か**: 元 DB の日本語の探索（Q026・Q045〜Q053）は結論が出ていない。2026-09-29 に J-STAGE と CiNii Research を 8 語で調べたところ、題名に AI と疲労の語を含む上位の文献は『AI が人の疲労を測る』研究（E1）か、材料の疲労（アルミ合金の『Al』が『AI』と誤表記されたもの）ばかりで、AI 利用者の疲労の研究は 0 件だった。
- **根拠の場所**: 検索ログ Q026・Q045〜Q053／項目定義・採択基準 r25
- **調べる価値の判断材料**: J-STAGE:『AI 疲労』9,066 件・『生成AI 疲労』201 件・『AI疲れ』3 件、CiNii Research:『AI 疲労』157 件・『生成AI 疲労』2 件。いずれも上位 100 件の題名で該当なし（⚠️ 題名段・上位 100 件の点検で、不在の証明ではない）。
- **次の一手**: 医中誌 Web（医療者）、CiNii の抄録・本文、学会予稿（情報処理学会・人工知能学会・ヒューマンインタフェース学会・産業衛生学会）、『テクノストレス』『デジタル疲労』『生成 AI 負担』の語で探す。
- **完了の条件**: 日本語の候補の一覧（0 件ならその検索記録）ができる。
- **GSE との関係**: I-04（日本語版）の必要性の根拠になる。
- **依存・順序**: —

### S-03（優先度 低・手間 小）引用追跡を行う（前方: AF001 を引く研究／後方: 既存レビューの採択研究）

- **なぜ必要か**: AF001 は AI 疲労の定義と尺度の中核で、今後の AI 疲労研究はこれを引くはず。既存レビュー（AF013〜AF018・Zenodo のレビュー）の採択研究にも DB にない一次研究があり得る。
- **根拠の場所**: Claude適格性評価 AF001・AF013〜AF018／検索漏れ候補 No.15
- **調べる価値の判断材料**: 2026-09-29 時点で OpenAlex 上の AF001 の被引用は 2 件（AI への態度の潜在プロファイル・教育のデジタル成果物）で、どちらも AI 疲労の研究ではない → 前方追跡は数か月おいてから回すのが効率的。
- **次の一手**: 3 か月ごとに AF001 の被引用を確認 → 新しい AI 疲労研究を TA 段へ。後方追跡は既存レビューの参考文献を DB と突き合わせる。
- **完了の条件**: 追跡の実行日と追加候補が検索ログに記録される。
- **GSE との関係**: —
- **依存・順序**: N-08（AF014 を使う場合）

### S-11（優先度 低・手間 小）『AI 疲労』という語の使われ方を整理する（使っていて疲れる／AI の話題・導入に疲れる／AI による仕事の増加で燃え尽きる／プロンプト疲れ）

- **なぜ必要か**: DB の文献は『AI 疲労』を少なくとも 3〜4 通りの意味で使っている。AF013 は AI 導入や言説への疲れも含む。サーベイ論文の定義を決めるには、用法を分けておく必要がある。
- **根拠の場所**: Claude適格性評価 AF013（E 列）／検索漏れ候補 No.128・129（プロンプト疲れの概念分析の補足資料）
- **調べる価値の判断材料**: ⚠️ 件数は目安にならない: OpenAlex の初回点検（2026-09-29）で『"prompt fatigue"』139 件・『"AI hype" fatigue』124 件だったが、上位は『promptly fatigued』（語幹の一致）や AI 疲労と無関係の文献だった。Semantic Scholar の『"prompt fatigue"』9 件もすべて無関係。→ 用法の研究の量は件数では測れず、S-02 で含めた研究の定義文から整理する。
- **次の一手**: 含めた研究の定義文を抜き出し、上の 4 つの用法に振り分ける表を作る。プロンプト疲れの概念分析の本体論文を辿る。
- **完了の条件**: 用法ごとの定義の表ができ、サーベイの定義文が決まる。
- **GSE との関係**: GSE の interaction burden（プロンプトの作り直し）と verification burden（出力の確認）の区別に対応する（生成的返権論 §6.3）。
- **依存・順序**: S-02


## アイディア issue

### I-01（優先度 高・手間 小）【GSE へ】この DB を、GSE のロードマップ最優先 5『AI 疲労を横断する scoping review』の AI 疲労の系統として扱うかを決める

- **なぜ必要か**: GSE の理論ロードマップ §10 は最優先の 5 番目に『generative art / portrait / withdrawal / embodiment / AI fatigue を横断する scoping review』を挙げている。2026-09-19 の GSE の体系的レビューのプロトコル・検索ログには疲労の語が 1 つもなく（AI 疲労のデータセット 2 件が偶然ヒットしただけ）、AI 疲労の系統は手つかず。研究者が作った DB はまさにその系統を実行している。
- **根拠の場所**: docs/theory/theory-architecture-and-roadmap.md §10（最優先 5）／.steering/20260919-ssot-sr-systematic-review/（protocol.md・search-log.md に fatigue・疲労の語なし）
- **調べる価値の判断材料**: 2026-09-29 に grep で確認。
- **次の一手**: 研究者が選ぶ: (a) DB を GSE のレビューの AI 疲労の系統として参照する、(b) GSE 側で別に行う、(c) GSE では行わない。(a) なら、DB の採否基準は GSE に中立のまま保ち、GSE の文書からは DB の結論を引用する形にする。
- **完了の条件**: 選んだ案がロードマップの注記か steering の判断記録に残る。
- **GSE との関係**: ★ 前回の評価プロトコル §7『GSE にとって有用かどうかで採否を変えない』を守る（サーベイ論文の独立性）。
- **依存・順序**: —

### I-02（優先度 高・手間 中）【GSE へ】検証負担・やり取りの負担（verification / interaction burden）の自己報告項目の候補を、EVAL-NCC の測定辞書に足すか検討する

- **なぜ必要か**: GSE の理論ロードマップ §5.7 は『タスク固有の検証負担・義務感・不当な責任集中感を減らすか』を GSE が追加検証するものに挙げる。しかし EVAL-NCC の測定辞書 v0.1 の 8 構成概念（判断品質・誤採用・無検証依存・支援到達可能性・罪悪感・応答義務・不利益予期・放置不安）に、負担そのものの項目は無い（§4 の無検証依存は『必要以上の確認を増やす設計は verification burden で同時に罰する』と書くが、その項目がない）。
- **根拠の場所**: .steering/20260916-gse-theory-operationalization-review/measurement-dictionary.md（§1・§12）／roadmap §5.7
- **調べる価値の判断材料**: DB の一次資料に項目文の手がかりがある: AF005 の Table 2（『AI が作った情報の真偽を繰り返し確かめて感情的に消耗した』）、AF007 の指標（『大量の出力を確かめて精神的に消耗した』n=72）、AF001 の認知の下位尺度（N-07 の後）、GSE の [P398]（LLM 支援の文献レビューの verification burden）。
- **次の一手**: 上の文言を参考に、タスク固有の負担項目（7 件法・認知面接用の候補）を 4〜6 個起こし、測定辞書の構成概念として追加する案を書く。
- **完了の条件**: 測定辞書に追加する構成概念の案（定義・含めない近接概念・項目候補・判定）ができ、研究者が採否を決める。
- **GSE との関係**: ★ 禁止線（roadmap §5.7）: この項目を AI Fatigue Scale やその短縮版と呼ばない／AI を用いない条件には『AI 疲労』と呼ばず interaction burden / verification burden とする／瞬間状態や介入の引き金に使わない。項目は妥当化済み尺度ではない（測定辞書 §12 と同じ扱い）。
- **依存・順序**: N-07（AF001 の項目を参照するなら）

### I-09（優先度 高・手間 中）【サーベイ論文へ】疲労の『源』で中心候補をコーディングする（プロンプトを作る負担／出力を確かめる負担／修正・やり直しの負担）

- **なぜ必要か**: DB の中心候補は、疲労の源を暗に分けている: AF002・AF003 はプロンプトの不確実さと作り直し、AF005 と AF007 の指標は出力を確かめる負担、AF001 は認知の過負荷。GSE は生成的返権論 §6.3 で、負担を interaction burden（やり取り）と verification burden（確認）に分けて扱ってきた。この区別をサーベイの分析の軸にすると、『AI 疲労』の中身を具体的に整理できる。
- **根拠の場所**: Claude適格性評価 AF001〜AF012（E 列）／GSE の生成的返権論 §6.3・[P363]・[P364]・[P376]・[P398]
- **調べる価値の判断材料**: 前回のセッションのアイディア G01 と同じ着想（未コミットの data_d.py）。
- **次の一手**: 抽出フォーム（N-05）に『疲労の源』の列を足し、含めた研究を『プロンプト／確認／修正／利用量・時間／導入の圧力／その他』に振り分ける。
- **完了の条件**: 源ごとの研究数と、源ごとの測定の仕方の表ができる。
- **GSE との関係**: ★ 論文では GSE に言及せず、公開文献（Tankelevitch et al. 2024 [P364]・Simkute et al. 2024 [P376] など）を出典に軸を立てる（公開する成果物に GSE を書かない方針）。
- **依存・順序**: N-05・S-02

### I-03（優先度 中・手間 小）【GSE へ】『能動的な疲労／受動的な疲労』の区別を、生成的返権論の負荷逆説（§6.3）の境界条件として書き足すか検討する

- **なぜ必要か**: GSE の [P376]（生成 AI の皮肉）は『利用者の役割が出力を作ることから評価することへ移った』とする。ヒューマンファクター研究では、作業を任せて見張るだけになると受動的疲労と覚醒低下が生じる（S-05）。GSE が守る生産的苦闘は能動的な関与であり、『摩擦を取り除いても負荷は消えず、種類が能動から受動に変わりうる』と書ければ、返権の負荷逆説の記述が具体的になる。
- **根拠の場所**: docs/theory/generative-relinquishment-theory.md §6.3／docs/references.md [P368]・[P369]・[P376]
- **調べる価値の判断材料**: S-05 の種文献（Saxby et al. 2013 ほか）。
- **次の一手**: S-05 の結果を読んでから、§6.3 の注記の案（2〜3 文・出典つき）を書き、研究者が採否を決める。
- **完了の条件**: 注記の案と採否が記録される。
- **GSE との関係**: ★ docs/theory は理論の候補（EH0）で SSOT の主張ではない。新しい理論名は付けない（返権の負荷逆説と同じく、先行の一般形があることを明記する）。引用は citation-ssot で登録する。
- **依存・順序**: S-05

### I-04（優先度 中・手間 大）【両方】AF001 の AI 疲労尺度の日本語版を作り、検証する計画を立てる（独立した研究になりうる）

- **なぜ必要か**: 日本語の AI 利用者の疲労の研究・尺度は見つからなかった（S-12）。GSE の理論文書は、日本語版は『翻訳・逆翻訳、認知インタビュー、因子構造の確認を経るまで確立尺度として扱わない』と定める。日本語版の検証は、それ自体が小さな独立した研究として成立しうる。
- **根拠の場所**: docs/theory/theory-architecture-and-roadmap.md（§5.7 の後段・日本語版の条件）／Claude適格性評価 AF001（H 列）
- **調べる価値の判断材料**: 翻訳の手順の標準（Crossref で確認）: Beaton et al. 2000 doi:10.1097/00007632-200012150-00014、Wild et al. 2005（ISPOR）doi:10.1111/j.1524-4733.2005.04054.x。⚠️ AF001 の論文のライセンスは CC BY-NC-ND（2026-09-28 の抽出で Unpaywall の表示）で、翻訳は改変に当たりうる → 先に著者の許諾を取る。
- **次の一手**: 著者に許諾を依頼 → 順翻訳 2 名・逆翻訳 → 認知面接 → 確認的因子分析と原版との測定不変性 → 再検査。必要な標本数を見積もる。
- **完了の条件**: 許諾の有無と、手順・標本数・倫理審査の見込みを書いた計画ができる。
- **GSE との関係**: ★ GR-H12: 日本語版を作っても用途は外部の自己報告（ベースライン・遅延追跡）に限る。打鍵から推定しない・介入の引き金にしない。
- **依存・順序**: N-07・S-08

### I-05（優先度 中・手間 小）【GSE へ】GR-H12 の反証表の交絡の欄に『睡眠』を足すか検討する（AF008 の所見から）

- **なぜ必要か**: GSE の GR-H12 の反証表は、交絡の候補に『一般疲労、作業量、時間帯、AI 利用量、technostress』を挙げるが、睡眠は無い。AF008 では、学生のタイプを最も強く分けたのが睡眠の質だった（F(5,382)=44.69）。AF001 も一般・デジタル疲労との関連を報告し、中心-B の研究はすべて一般的な疲労を測っている。
- **根拠の場所**: .steering/20260916-gse-theory-operationalization-review/gr-h4-h9-h11-h12-falsification-table.md（GR-H12 の行）／GSE照合 AF008
- **調べる価値の判断材料**: ⚠️ AF008 自体は項目数の食い違いなどの問題がある（C04・C05）。睡眠を交絡の候補に挙げる根拠は AF008 だけに頼らず、一般的な疲労研究の知見でも補う。
- **次の一手**: GR-H12 の行の交絡の欄に睡眠（と、測るなら一般疲労の尺度 AF028 など）を足す案を書き、研究者が採否を決める。
- **完了の条件**: 反証表の更新案と採否が記録される。
- **GSE との関係**: ★ GR-H12 の結論（AI 疲労を行動痕跡から推定しない・外部自己報告に限る）は変えない。交絡の候補を増やすだけ。
- **依存・順序**: —

### I-10（優先度 中・手間 小）【サーベイ論文へ】『誰が負担を負うか』の列を抽出フォームに足す（解釈・確認・修正・帰結）

- **なぜ必要か**: AI 疲労の文献は、疲労を個人の状態として測るものが多く、組織や設計が負担をどう配っているかは別に書かれる（AF013・AF015・AF017）。GSE は『権限と負担の二重台帳』で、誰が解釈し・確認し・修正し・帰結を引き受けるかを分けて記述してきた。抽出の段階で負担の担い手を記録すれば、個人の疲労と配置の問題を分けて整理できる。
- **根拠の場所**: GSE の生成的返権論 §6.3（二重台帳）・[P370]・[P372]／Claude適格性評価 AF013・AF015・AF017
- **調べる価値の判断材料**: 前回のセッションのアイディア G02 と同じ着想。
- **次の一手**: 抽出フォームに『負担の担い手（本人／組織／設計者／明記なし）』と『負担の種類』の列を足す案を N-05 に入れる。
- **完了の条件**: 抽出フォームに列が入り、試しに 3〜5 件で記入できることを確かめる。
- **GSE との関係**: ★ 論文では GSE の用語（返権・二重台帳）を使わず、公開文献（Flemisch et al. 2012 の A2CR [P370]・Pritchett et al. 2014 [P372]）を出典にする。
- **依存・順序**: N-05

### I-11（優先度 中・手間 小）【サーベイ論文へ】序論の枠組み: AI 疲労を『自動化が人に残す後始末の負担』の系譜に置く

- **なぜ必要か**: 『自動化の皮肉』（Bainbridge 1983）・責任と権限の二重拘束（Woods 1985）・生成 AI の皮肉（Simkute et al. 2024）は、自動化が人に確認と後始末を残すことを 40 年にわたって論じてきた。AI 疲労を新しい現象としてだけ扱うより、この系譜の最新の形として置く方が、何が新しく何が既知かを示せる。GSE は 2026-09-19 のサーヴェイでこれらを全文照合している。
- **根拠の場所**: GSE の docs/references.md [P368]・[P369]・[P376]・[P367]／docs/literature/20260919-authority-return-burden-precedents.md
- **調べる価値の判断材料**: 前回のセッションのアイディア G06 と同じ着想。受動的疲労（S-05）とも接続する。
- **次の一手**: 序論の骨子（1 段落）と、系譜の年表（1983 → 1985 → 2012 → 2024 → AI 疲労）を書く。
- **完了の条件**: 序論の骨子と年表ができる。
- **GSE との関係**: ★ 論文では GSE に言及しない。出典は公開文献だけ。
- **依存・順序**: S-05

### I-12（優先度 中・手間 小）【サーベイ論文へ】文献の質の問題そのものを所見として書く（報告値の食い違い・参考文献や DOI の誤り・媒体の偏り）

- **なぜ必要か**: 今回の評価で、34 件の中から報告値の食い違い（AF004・AF006・AF008・AF011）、倫理の記載の矛盾（AF012）、参考文献・DOI の誤り（AF004・AF011・AF014）が一次で見つかった。新しい領域の文献の質は、サーベイ論文の限界と方法の節で正面から書くべき所見になる。GSE は citation-ssot で DOI と書誌を照合する規律を持ち、その実例になる。
- **根拠の場所**: Claude照合事項 C01〜C08・C18・R-I01・R-I03
- **調べる価値の判断材料**: 前回のセッションのアイディア G08 と同じ着想。
- **次の一手**: 誤りの種類（数値の不整合／倫理の記載／参考文献・DOI／件数の表記）× 研究の表を作る。査読の形態・媒体も列に入れる。
- **完了の条件**: 表と、限界の節の下書き（数段落）ができる。
- **GSE との関係**: ★ 不整合の指摘は研究不正の認定ではない。論文では個別の研究を責める書き方をせず、種類と頻度で書く。GSE には言及しない。
- **依存・順序**: N-03

### I-06（優先度 低・手間 小）【GSE へ】研究ポジショニング §1『AI 時代の角度』を、DB の証拠の強さで点検する

- **なぜ必要か**: RP §1 は『LLM が詰まりの解消を摩擦ゼロにしつつある』とする。DB と GSE の既存文献は『摩擦が消える』というより『負担が確認・監督へ移る』ことを示唆する（[P365]・[P376]・AF005・AF007）が、証拠の多くは横断・自己報告である。
- **根拠の場所**: docs/research-positioning.md §1（AI 時代の角度）
- **調べる価値の判断材料**: Claude領域別評価（中心候補の多くが横断）。
- **次の一手**: §1 に『負担は移る』という一文と証拠の強さの注記を足す案を書く。AF004（向きの矛盾）・AF011（分析単位）は引かない。
- **完了の条件**: 案と採否が記録される。
- **GSE との関係**: citation-ssot で登録してから引く。[P363] は全文確認（N-01）まで provisional のまま。
- **依存・順序**: N-01

### I-07（優先度 低・手間 小）【GSE へ】Nudge の『通知疲れ・慣れ』の文献を、介入設計の制約として取り込む

- **なぜ必要か**: GSE の現行の介入は Nudge のみ。警報疲れ（S-06）の文献は、繰り返される通知が無視・上書きされていく過程を扱っており、Nudge の cooldown・1 日の上限・dismiss 率（HIR）の読み方に直接関わる。GSE の中央書誌に『alert fatigue』は 0 件（慣れの文献は [V124]・[P87]・[P88] がある）。
- **根拠の場所**: docs/references.md（alert fatigue 0 件・2026-09-29 に grep）／intervention-design Skill
- **調べる価値の判断材料**: S-06 の種文献（Ancker et al. 2017 ほか）。
- **次の一手**: S-06 の結果から、Nudge の頻度・上限の設計に効く知見を抜き出して、介入設計の文書への注記案を書く。
- **完了の条件**: 注記の案と採否が記録される。
- **GSE との関係**: ★ 介入の発火・上限の変更は intervention-design Skill の対象で、実装は別タスク。ここでは文献の取り込みまで。
- **依存・順序**: S-06

### I-08（優先度 低・手間 小）【GSE へ】【保留・記録のみ】GSE のデータで AI 利用の有無を区別したくなったときの前提を書き残す

- **なぜ必要か**: GSE のアウトカム指標には『答えの受領』の代理（paste_after_stuck_rate など）があるが、貼り付けが AI からかどうかは区別できない。O1 はアプリの役割カテゴリを記録せず（ADR-014 D4）、クリップボードは文字数だけ。AI 疲労の文献と GSE のデータを結びつけたくなったときに、行動から AI 利用を推し量ってしまう危険がある。
- **根拠の場所**: docs/glossary.md（アウトカム指標・常時収集）／docs/agent-shared.md（clipboard.rs は文字数のみ）
- **調べる価値の判断材料**: —
- **次の一手**: 今は動かさない。もし必要になったら、セッション単位の自己申告（『このセッションで AI を使ったか』）を設ける案を、同意文書・ESM の契約変更として ADR で議論する（data-privacy Skill の対象）。
- **完了の条件**: この前提が記録されている（この issue 自体）。
- **GSE との関係**: ★ 行動痕跡から AI 利用や AI 疲労を推定しない（GR-H12）。自己申告の選択肢の追加は被験者向け文書の契約変更。
- **依存・順序**: —


## 通常 issue

### N-01（優先度 高・手間 小）中心候補のうち本文未入手の 3 件（AF002・AF003・AF009）の全文を入手し、中心-A か B かを確定する

- **なぜ必要か**: 中心候補 13 件のうち 3 件は抄録しか読めておらず、質問文が AI に向いているか（A か B か）が決まっていない。全文で確かめたら B だった先例（AF004・AF019）がある。AF002 と AF003 は同じ著者群で、標本が別かも未確認。
- **根拠の場所**: Claude適格性評価 AF002・AF003・AF009（K 列）／Claude照合事項 R-I14・C16
- **調べる価値の判断材料**: AF002・AF003 は ScienceDirect の購読制、AF009 は IEEE Xplore（2026-09-28 にスクリプトでもブラウザでも本文に届かなかった）。
- **次の一手**: 機関アクセス（大学図書館・ILL）か著者への依頼で PDF を入手 → 疲労の項目文・標本手続き・収集時期・プラットフォームを確認 → Claude適格性評価の K 列と方法論評価の JBI 項目を更新。
- **完了の条件**: 3 件の K 列が A か B に確定し、JBI 項目が U 以外で埋まる。AF002 と AF003 の標本の関係が記録される。
- **GSE との関係**: AF002 は GSE の [P363]（provisional）。全文で確かめたら references.md の状態を active にできるか判断する。
- **依存・順序**: —

### N-02（優先度 高・手間 中）人間 2 名の独立スクリーニングを行い、AI の予備判定と照らし合わせる（判定者用ファイルの仕上げ・AF024 の範囲判定を含む）

- **なぜ必要か**: 元ファイルの規則では、採否は人間 2 名の独立判定で決める（AI の予備整理は独立判定に数えない）。いま『スクリーニング』の判定者 1・2・最終判定は 34 件すべて『未判定』。前回のセッションの記録によれば、判定者 1 は研究者自身が務める（研究者の発言『独立判定のうちの一つは私が行う感じになります』）。AF024 は規則だけでは範囲が決まらず人間に委ねた。
- **根拠の場所**: スクリーニング!D5:F38（未判定）／AI判定比較／Claude適格性評価 AF024／Claude評価基準／前回の worktree の未コミットの judge_xlsx.py
- **調べる価値の判断材料**: 2026-09-28 に全件『未判定』のままであることを機械で確認済み。★ 前回のセッションが、AI の判定を 1 つも含まない『判定者用ファイル』を作るスクリプト（C:\GSE-ai-fatigue-appraisal の archive/scripts/judge_xlsx.py）を書きかけていたが、ファイルは出力されず、コミットもされていない（2026-09-29 に確認）。⚠️ 研究者はチャットの要約で Claude の判定の一部を既に見ており、今回の読みやすい版を読むとさらに独立性が下がる。
- **次の一手**: (1) 判定者用ファイルを仕上げる（AI の判定・懸念の語が入っていないことを機械で確かめる）→ (2) 判定者 1（研究者）は、判定が終わるまで『★まず読む』『論文ごとの要点』と Claude・GPT のシートを開かずに判定する → (3) 判定者 2 には AI の結果を見ていない人を当てる → (4) TA 段 → 全文段で判定し、最終判定と除外理由を記入 → (5) AI判定比較シートで照合し、人間同士の一致度（κ など）を計算。AF024 と『中心-B を AI 疲労と合算しない』規則の採否もここで決める。
- **完了の条件**: スクリーニング!F5:F38 が全件埋まり、不一致の調整の記録と、判定者 1 が AI の結果をどこまで見ていたかの記録が残る。
- **GSE との関係**: —
- **依存・順序**: N-05 と同時に進めてよい（基準が変わるなら N-05 を先に）

### N-05（優先度 高・手間 中）スコーピングレビューのプロトコルを確定し、事前登録する（OSF など）

- **なぜ必要か**: 元 DB は『探索版』で、専門データベースの本検索・独立判定・品質評価が未実施。Claude 評価の基準も抽出前に固定しただけで事前登録ではない。本検索（S-01）の前に、何を AI とみなすか・範囲の 2 段（中心-A / 中心-B）・除外理由コードを固めておかないと、後から基準を動かしたと見られる。
- **根拠の場所**: 項目定義・採択基準 r22〜r24／Claude評価基準（『事前登録済みのプロトコルではない』）／AF030・AF031・AF033
- **調べる価値の判断材料**: PRISMA-ScR（AF030）と JBI の方法論（AF031）が型を与える。AF033 によれば PRISMA-ScR は改訂作業中（2026-09-28 時点で正式版は未確認）。
- **次の一手**: PCC（対象・概念・文脈）と中心-A / B の規則、除外理由コード、情報源、検索式、二重スクリーニング、抽出フォーム、品質評価の扱い（合計点を付けない等）を 1 本の文書にする。★ 範囲の判断が要る論点: (1) ルールベースの警報・自動運転の自動化を『AI』に含めるか（S-05・S-06）、(2)『AI が疲労を減らす』介入研究を中心に入れるか（S-04）、(3) 学位論文・プレプリント・学会抄録を入れるか。
- **完了の条件**: 登録番号（DOI）が付き、以後の変更は逸脱として記録される。
- **GSE との関係**: 前回の評価プロトコル（.steering/20260928-ai-fatigue-db-appraisal/design.md）をひな形にできる。★ GSE 照合は採否に使わない方針を引き継ぐ。
- **依存・順序**: I-01 の決定（GSE のレビューと共有するか）があれば反映

### N-03（優先度 中・手間 小）報告値の食い違いを著者に照会するかを決め、送るなら送る（6 件・下書きあり）

- **なぜ必要か**: 引用できる範囲を狭めている食い違いが一次で確認された: AF006 の百分率の分母（1,054）と AF007 との標本の関係／AF004 の交互作用の向き／AF008 の項目数と推定の安定性／AF011 の分析単位／AF012 の倫理承認／AF014 の採択件数。
- **根拠の場所**: Claude照合事項 C01・C02・C04・C05・R-I01・R-I03・C07／照会の下書きシート
- **調べる価値の判断材料**: いずれもメインが一次（PDF・全文 HTML・Europe PMC）で確認し、算術で照合した。⚠️ 研究不正の認定ではない。
- **次の一手**: 下書きを読み、送る相手（責任著者か編集部か）と差出人名を決める → 送る場合は送付日と返答を Claude照合事項に追記。送らない場合も、DB の引用制限（数値を引かない等）はそのまま有効。
- **完了の条件**: 6 件それぞれに『送った／送らない』とその理由が記録される。
- **GSE との関係**: —
- **依存・順序**: —

### N-04（優先度 中・手間 小）元 DB を v1.1 に更新する（書誌の補完・デザインや件数の修正を反映）

- **なぜ必要か**: Claude 評価で見つけた修正案は、元シートを変えない方針のため未反映。元 DB だけを見る人には古い値が残る。
- **根拠の場所**: Claude照合事項 C19（書誌の補完）・R-I04（AF007 のデザイン）・R-I05（AF009 の N・項目・因子）・C08（AF018 の件数）・C15（AF020 の要約）／Claude×GPT比較 AF031（全著者 9 名）
- **調べる価値の判断材料**: いずれも一次資料または Crossref で確認済み。
- **次の一手**: 元 DB の複製に v1.1 として反映し、変更履歴のシートを足す。同梱の CSV・RIS・SQLite・JSON も同じ時点で書き出し直す（元の注意書き『Excel 編集後、他形式へは自動同期されません』）。
- **完了の条件**: v1.1 と変更履歴ができ、他形式も同じ時点にそろう。
- **GSE との関係**: —
- **依存・順序**: N-01 の結果も反映するなら N-01 の後

### N-06（優先度 中・手間 小）IEEE DataPort の『AI 疲労』データセット 2 件が実測か合成かを確かめる

- **なぜ必要か**: 題名に 6000・15000 件とあり、合成データの可能性があるが未確認。実測なら大規模な一次データ、合成なら証拠から外す必要がある。GSE の 2026-09-19 体系的レビューでも抄録段で記録だけした。
- **根拠の場所**: 検索漏れ候補 No.17・No.22（doi:10.21227/rz27-ze05・10.21227/94rd-ny74）／GSE照合 C2-0345・C2-0363
- **調べる価値の判断材料**: 2026-09-28 の API 検索と 2026-09-19 の GSE の体系的レビューの両方でヒット。
- **次の一手**: DataPort のページと付属文書で、生成方法・収集手続き・倫理の記載を確認。合成なら E4（一次研究でない）として除外し理由を記録。
- **完了の条件**: 2 件の判定（含める／除外 E4）が記録される。
- **GSE との関係**: GSE の SR（screening-C2.md）の記録も同じ結論で更新できる。
- **依存・順序**: —

### N-10（優先度 中・手間 小）【GSE】中央書誌 [P362]（AF001）の注記を一次に合わせる

- **なぜ必要か**: GSE の references.md は [P362] を『持続的 AI 利用への比較的安定した傾向尺度』と書くが、一次では 2 週間の再検査 ICC(2,1)=.65（著者は moderate）、下位尺度 .54〜.71。『中程度の時間的安定性をもつ自己報告尺度』の方が一次に近い。
- **根拠の場所**: GSE照合 AF001（F 列）／docs/references.md [P362]
- **調べる価値の判断材料**: 2026-09-28 にメインが出版社版 PDF で確認。
- **次の一手**: citation-ssot の規則（append-only・日付つき注記）で [P362] の注記に訂正を足す。理論文書（生成的返権論 §6.3 の表）で同じ言い回しがないかも確認。
- **完了の条件**: [P362] に日付つきの訂正注記が入り、同じ言い回しの残りが 0 になる。
- **GSE との関係**: ★ GR-H12（AI 疲労は外部の自己報告としてのみ使う）の結論は変わらない。安定性の表現だけを一次に合わせる。
- **依存・順序**: —

### N-07（優先度 低・手間 小）AF001（AI 疲労尺度）の補足資料で全 15 項目・事前登録・データを確認する

- **なぜ必要か**: AF001 は唯一まとまった検証のある AI 疲労尺度だが、補足資料の項目表（Table S6）は未照合。4 研究のうち事前登録が見えたのは 3 研究だけ。日本語版の検討（I-04）の前提になる。
- **根拠の場所**: Claude適格性評価 AF001（H 列）／Claude領域別評価 AF001（透明性）／抽出ノート G1
- **調べる価値の判断材料**: ResearchBox 6748 に Study 2〜4 の事前登録とデータがある（2026-09-28 のサブエージェント抽出）。
- **次の一手**: 補足資料と ResearchBox を読み、全項目・下位尺度・採点方法・事前登録の範囲を記録する。
- **完了の条件**: 全 15 項目の文言と下位尺度の対応、事前登録の有無が記録される。
- **GSE との関係**: GSE の [P362] の記述と照合できる（N-10）。
- **依存・順序**: —

### N-08（優先度 低・手間 小）AF014（包括的レビュー）の引用文献の実在を確かめる（引用追跡に使う場合のみ）

- **なぜ必要か**: AF014 は採択件数（22／30）と DOI の表記に食い違いがあり、GPT の照合事項でも参考文献の書誌に要確認点があった。引用追跡の出発点にするなら、先に実在を確かめる必要がある。
- **根拠の場所**: Claude照合事項 R-I10・C07・C18
- **調べる価値の判断材料**: AF004・AF011 では参考文献の誤りが訂正通知で直された先例がある（C18）。
- **次の一手**: 引用追跡（S-03）で AF014 を使うと決めたら、参考文献を Crossref で 1 件ずつ照合する。
- **完了の条件**: 照合結果（実在・書誌の誤り）が記録される。
- **GSE との関係**: —
- **依存・順序**: S-03

### N-09（優先度 低・手間 小）Arun & Fischer 2026 の本文を読み、AF020 の『一部再現しなかった』報告を確かめる

- **なぜ必要か**: AF020（考えさせる仕掛けは過信を減らすが使い勝手の評価が下がる）の関連報告として、2026 年の部分的な非再現が GSE の文献カードに挙がっているが、本文は未照合。
- **根拠の場所**: Claude照合事項 C15／GSE照合 AF020・追加候補 Arun & Fischer 2026
- **調べる価値の判断材料**: 書誌は Crossref で確認済み（doi:10.1145/3808045.3808049）。
- **次の一手**: 本文を読み、『選択的な摩擦で主観的な負荷だけが増えた』の中身（測定・標本・比較）を記録。DB に隣接研究として追加するか決める。
- **完了の条件**: DB への追加の可否と、AF020 の要約の精密化が決まる。
- **GSE との関係**: GSE の文献カード（docs/literature/20260724-friction-retention-and-overreliance-evidence.md）のやり残しも同時に閉じられる。⚠️ 摩擦の強さの実験（GR-H11）は GSE の計画外（2026-09-19 J-7 で保留）なので、GSE 側の実験案にはつなげない。
- **依存・順序**: —


## 付録 A：照会の下書き（未送信・送るかは研究者が決める）

### Q1. AF006（Parreño et al. 2026）の責任著者。AF007 の著者にも写し —— Table 3 の百分率の分母と、AF007 との標本の関係（N-03・C01・R-I07）

- 送る前に確かめること: AF007 の著者と重なる人を確認して宛先を決める。Table 3 と Table 5 の注を送る前にもう一度読む。

```text
Dear Dr. Parreño,

We are conducting a scoping review on fatigue related to AI use and are extracting data from your article "How do College Students Express AI Fatigue?" (IJLTER 25(3), doi:10.26803/ijlter.25.3.29). In Table 3, the percentages (e.g., 472 = 44.8%) correspond to a denominator of 1,054 rather than the 1,000 responses reported in the abstract, while the note to Table 5 (582 responses) is consistent with 1,000. Could you clarify (1) which denominator applies, (2) whether any responses were excluded and how many, and (3) whether the data overlap with the 1,054 responses analysed in Miranda et al. (IJLTER 25(5), doi:10.26803/ijlter.25.5.5)? This will help us avoid counting the same sample twice.

Thank you for your time.
Kind regards,
```

### Q2. AF004（Tian et al. 2025）の責任著者 —— 情報リテラシーの調整効果の向き（N-03・C02・C03）

- 送る前に確かめること: Acta Psychologica の訂正の手続き（編集部宛てにするか）を確認。§3.4・§4.1・§4.3 と Table 3 を送る前にもう一度読む。

```text
Dear Dr. Tian,

We are reviewing your article in Acta Psychologica (doi:10.1016/j.actpsy.2025.105725) for a scoping review on AI-related fatigue. We would appreciate clarification on the direction of the moderation by information literacy. The abstract and Section 4.3 state that literacy amplified cognitive fatigue when AI reliance was high, whereas Sections 3.4 and 4.1 state that higher literacy attenuates the positive relationship, which appears consistent with the negative interaction coefficient (β = −0.06, p = .025). We also noted that the reported indirect effect (−0.14) differs from the product of the path coefficients (0.51 × −0.33 ≈ −0.17). Could you confirm which interpretation is intended, and whether a correction is planned? We note that the published corrigendum (doi:10.1016/j.actpsy.2026.107179) concerns references only.

Kind regards,
```

### Q3. AF008（Soriano et al. 2026）の責任著者 —— 項目数（36 と 24）と、混合モデルの推定の安定性（N-03・C04・C05・R-I08）

- 送る前に確かめること: Table 3 の AIC・BIC から逆算した対数尤度の計算を送る前にもう一度確かめる。

```text
Dear Dr. Soriano,

We are extracting data from your article on AI-induced fatigue profiles (IAES IJ-AI, doi:10.11591/ijai.v15.i2.pp1963-1971). The text states that the instrument had 36 items, while the item counts in Table 1 sum to 24. Could you clarify the number of items per scale and whether reliability coefficients are available? In addition, the log-likelihoods implied by the AIC and BIC values in Table 3 appear to decrease when moving from k = 3 to k = 4 and from k = 8 to k = 9, which may indicate local optima. Could you tell us how many random initializations were used for the Gaussian mixture models?

Kind regards,
```

### Q4. AF011（Shalu et al. 2026）の責任著者 —— 相関の分析の単位（参加者か項目か）と検定の N（N-03・R-I01・C06）

- 送る前に確かめること: Figure 1 の注と Table 3 を送る前にもう一度読む。p 値の再計算（N=6 で .053）を確かめる。

```text
Dear Dr. Shalu,

We are reviewing your article "The Cognitive Cost of AI" (Annals of Neurosciences, doi:10.1177/09727531251359872) for a scoping review. The note to Figure 1 indicates that the points represent individual survey items, and the reported p-value for r = .806 (p = .053) matches a test with N = 6 rather than N = 500. Could you clarify whether the correlations in Tables 3–6 were computed across participants or across items, and which N was used for the significance tests? We would also be grateful for the sources and reliability of the decision-fatigue measure, and for the ethics approval details.

Kind regards,
```

### Q5. AF012（Khan et al. 2025）の責任著者 —— 倫理承認の記載と標本抽出（N-03・R-I03）

- 送る前に確かめること: MDPI の現行版で記載が直っていないかを先に確認（2026-09-28 は Wayback の保存版で確認）。

```text
Dear Dr. Khan,

We are extracting data from your article in Technologies (doi:10.3390/technologies13110486). Section 3.4 states that the study had ethical approval from an institutional review board, whereas the Institutional Review Board Statement and Informed Consent Statement at the end of the article read "Not applicable". Could you tell us which statement is correct and, if approval was obtained, the name of the committee and the approval number? We would also appreciate clarification of how the stratified random sampling was implemented, given that recruitment was through personal contacts on social media.

Kind regards,
```

### Q6. AF014（Sosiński et al. 2026）の責任著者 —— 採択件数（22 と 30）と DOI の表記（N-03・C07）

- 送る前に確かめること: 引用追跡に AF014 を使わないなら送らなくてよい（N-08）。

```text
Dear Dr. Sosiński,

We are reviewing your article "AI Fatigue and Mental Health Implications" (Quality in Sport, doi:10.12775/QS.2026.54.70890). The abstract states that the review summarizes 22 studies, while the main text refers to 30 reviewed studies in several places. Could you confirm the number of included studies? We also noticed that the DOI printed in the PDF (…55.70890) does not resolve, whereas …54.70890 does.

Kind regards,
```

## 付録 B：件数の目安

| issue | 情報源 | 検索式 | 件数 | 取得日 | 注記 |
|---|---|---|---|---|---|
| S-01 | OpenAlex（自由語） | `"AI fatigue"` | 158 | 2026-09-29 | 2026-09-28 の検索漏れ点検の記録と同じ値 |
| S-08 | OpenAlex（自由語） | `"AI fatigue scale"` | 6 | 2026-09-29 | この後 OpenAlex の匿名検索は回数制限で使えなくなった |
| S-03 | OpenAlex（被引用） | `cites: AF001（W7166304533）` | 2 | 2026-09-29 | 2 件とも AI 疲労の研究ではない |
| S-04 | Europe PMC（題名・抄録） | `TITLE_ABS:("ambient AI" OR "AI scribe" OR "ambient scribe" OR "ambient listening" OR "ambient artificial intelligence") AND TITLE_ABS:(burnout OR fatigue OR "cognitive load" OR exhaustion)` | 89 | 2026-09-29 | 上位に NEJM AI の RCT 2 本 |
| S-04 | Europe PMC（題名・抄録） | `TITLE_ABS:("large language model" OR "generative AI" OR "AI-generated" OR "artificial intelligence") AND TITLE_ABS:("draft replies" OR "draft responses" OR "in-basket" OR inbox) AND TITLE_ABS:(burnout OR fatigue OR "cognitive burden" OR "task load")` | 18 | 2026-09-29 |  |
| S-05 | Europe PMC（題名・抄録） | `TITLE_ABS:"passive fatigue"` | 26 | 2026-09-29 | Europe PMC は生命科学中心。工学系は OpenAlex の行を参照 |
| S-05 | Europe PMC（題名・抄録） | `TITLE_ABS:("automation complacency" OR "automation-induced complacency")` | 25 | 2026-09-29 |  |
| S-06 | Europe PMC（題名・抄録） | `TITLE_ABS:"alert fatigue"` | 537 | 2026-09-29 |  |
| S-06 | Europe PMC（題名・抄録） | `TITLE_ABS:"alert fatigue" AND TITLE_ABS:("artificial intelligence" OR "machine learning")` | 80 | 2026-09-29 |  |
| S-07 | Europe PMC（題名・抄録） | `TITLE_ABS:("generative AI" OR ChatGPT OR "large language model") AND TITLE_ABS:(fatigue OR exhaustion OR burnout) AND TITLE_ABS:(physician OR nurse OR clinician OR radiologist)` | 67 | 2026-09-29 |  |
| S-10 | Europe PMC（題名・抄録） | `TITLE_ABS:("generative AI" OR "generative artificial intelligence" OR ChatGPT OR "large language model") AND TITLE_ABS:(fatigue OR exhaustion OR burnout) AND TITLE_ABS:(longitudinal OR diary OR "experience sampling" OR randomized OR randomised OR "multi-wave" OR "time-lagged")` | 24 | 2026-09-29 | 上位は医療の AI 記録支援の RCT |
| S-05 | Semantic Scholar（一括検索） | `"passive fatigue"` | 87 | 2026-09-29 | 上位に Desmond & Hancock・Körber 2015・Saxby 2013 |
| S-05 | Semantic Scholar（一括検索） | `"passive fatigue" + (automated ¦ automation)` | 36 | 2026-09-29 |  |
| S-06 | Semantic Scholar（一括検索） | `"alert fatigue"` | 1,214 | 2026-09-29 | 工学・セキュリティの警報も含む |
| S-06 | Semantic Scholar（一括検索） | `"alert fatigue" + ("artificial intelligence" ¦ "machine learning")` | 251 | 2026-09-29 | サイバーセキュリティの警報疲れも混ざる |
| S-04 | Semantic Scholar（一括検索） | `("AI scribe" ¦ "ambient scribe" ¦ "ambient AI") + (burnout ¦ fatigue)` | 95 | 2026-09-29 |  |
| S-09 | Semantic Scholar（一括検索） | `"decision fatigue" + ("artificial intelligence" ¦ "generative AI")` | 39 | 2026-09-29 | AF011・検索漏れ候補 No.108 を含む |
| S-07 | OpenAlex（自由語） | `"content moderators" burnout` | 177 | 2026-09-29 | 人が投稿を審査する仕事の燃え尽き（AI に限らない）。AI の出力を評価する人の研究の周辺の量の目安 |
| S-11 | OpenAlex（自由語） | `"prompt fatigue"` | 139（目安にしない） | 2026-09-29 | 上位は『promptly fatigued』（語幹の一致）など無関係 |
| S-11 | OpenAlex（自由語） | `"AI hype" fatigue` | 124（目安にしない） | 2026-09-29 | 上位は AI 疲労と無関係 |
| S-07 | — | `開発者（Copilot・AI コーディング支援）× 疲労` | 未計測 | 2026-09-29 | Semantic Scholar では Copilot が co-pilot（副操縦士）とも一致して件数が意味を持たず、OpenAlex は回数制限で使えなかった |
| S-12 | J-STAGE | `AI 疲労` | 9,066 | 2026-09-29 | 上位 100 件の題名に該当なし（材料の疲労・AI が疲労を測る研究） |
| S-12 | J-STAGE | `生成AI 疲労` | 201 | 2026-09-29 | 上位 100 件の題名に該当なし |
| S-12 | J-STAGE | `AI疲れ` | 3 | 2026-09-29 | 該当なし（特集の序文など） |
| S-12 | CiNii Research | `AI 疲労` | 157 | 2026-09-29 | 上位 100 件のうち題名に AI 語と疲労語を含む 32 件はすべて該当なし（材料の疲労・AI が人の疲労を測る研究・実用書など） |
| S-12 | CiNii Research | `生成AI 疲労` | 2 | 2026-09-29 | 該当なし |

## 付録 C：種文献（2026-09-29 に Crossref・DataCite で実在を確認・本文は未読）

- [S-02] Asmi, Wong, Almugren ほか 2026. Dark side of generative AI: a stressor–strain outcome and cognitive load theory explanation on decision fatigue and cognitive overload. *Journal of Enterprise Information Management*. https://doi.org/10.1108/jeim-10-2025-1027
- [S-02] Honggang W, Khoso A, Althubyani A ほか 2026. Technostress, digital fatigue, and AI dependency as antecedents of burnout and SDG-4 achievement in EFL classrooms. *Scientific Reports*. https://doi.org/10.1038/s41598-026-45402-7
- [S-02] Khoso A, Honggang W ほか 2026. Technostress forecasting in EFL classrooms: How digital fatigue and perceived AI ethical concerns shape digital burnout and undermine SDG-4 achievement. *Acta Psychologica*. https://doi.org/10.1016/j.actpsy.2026.107396
- [S-02] Thorpe D, Bean C, Krieg J ほか 2025. Associations between generative artificial intelligence usage, Job Demands, Job Control and Burnout. *AI & Society*. https://doi.org/10.1007/s00146-025-02764-2
- [S-02] Kim B, Kim M 2026. Digital efficiency, human exhaustion: How human-centered AI buffers the impact of AI adoption on physical health via AI techarnostress（★ Crossref の題名の表記のまま）. *Technology in Society*. https://doi.org/10.1016/j.techsoc.2026.103553
- [S-02] Chung J, Kwon H 2025. Privacy fatigue and its effects on ChatGPT acceptance among undergraduate students: is privacy dead?. *Education and Information Technologies*. https://doi.org/10.1007/s10639-024-13198-6
- [S-02] Kang I, Li D 2025. AI Anxiety to Fatigue and Its Consequences: The Moderating Role of AI Usage Motivation. *Journal of Business Convergence*. https://doi.org/10.31152/jb.2025.12.10.6.297
- [S-02] Nobles C 2026（非査読・DataCite で確認）. AI Fatigue in Higher Education: A Systematic Review of Associated Conditions, Manifestations, and Lifelong Learning Implications. *Zenodo*. https://doi.org/10.5281/zenodo.22838191
- [S-02] Kim B, Lee J 2024（AF017 の引用追跡）. The mental health implications of artificial intelligence adoption: the crucial role of self-efficacy. *Humanities and Social Sciences Communications*. https://doi.org/10.1057/s41599-024-04018-w
- [S-02] Hur W, Shin Y 2024（AF017 の引用追跡）. Service employees' STARA awareness and proactive service performance. *Journal of Services Marketing*. https://doi.org/10.1108/JSM-03-2023-0115
- [S-02] Jeong J, Kim B, Lee J 2024（AF017 の引用追跡）. Navigating AI transitions: how coaching leadership buffers against job stress and protects employee physical health. *Frontiers in Public Health*. https://doi.org/10.3389/fpubh.2024.1343932
- [S-04] Lukac P, Turner W, Vangala S ほか 2025. Ambient AI Scribes in Clinical Practice: A Randomized Trial. *NEJM AI*. https://doi.org/10.1056/aioa2501000
- [S-04] Afshar M ほか 2025. A Pragmatic Randomized Controlled Trial of Ambient Artificial Intelligence to Improve Health Practitioner Well-Being. *NEJM AI*. https://doi.org/10.1056/aioa2500945
- [S-04] Olson K, Meeker D, Troup M ほか 2025. Use of Ambient AI Scribes to Reduce Administrative Burden and Professional Burnout. *JAMA Network Open*. https://doi.org/10.1001/jamanetworkopen.2025.34976
- [S-04] Shah S, Devon-Sand A, Ma S ほか 2024. Ambient artificial intelligence scribes: physician burnout and perspectives on usability and documentation burden. *Journal of the American Medical Informatics Association*. https://doi.org/10.1093/jamia/ocae295
- [S-04] Garcia P, Ma S, Shah S ほか 2024. Artificial Intelligence–Generated Draft Replies to Patient Inbox Messages. *JAMA Network Open*. https://doi.org/10.1001/jamanetworkopen.2024.3201
- [S-04] Tai-Seale M, Baxter S, Vaida F ほか 2024. AI-Generated Draft Replies Integrated Into Health Records and Physicians' Electronic Communication. *JAMA Network Open*. https://doi.org/10.1001/jamanetworkopen.2024.6565
- [S-05] Desmond P, Hancock P 2000（書籍の章）. Active and Passive Fatigue States. *Stress, Workload, and Fatigue*. https://doi.org/10.1201/b12791-3.1
- [S-05] Saxby D, Matthews G, Warm J ほか 2013. Active and passive fatigue in simulated driving: Discriminating styles of workload regulation and their safety impacts. *Journal of Experimental Psychology: Applied*. https://doi.org/10.1037/a0034386
- [S-05] Körber M, Cingel A, Zimmermann M ほか 2015. Vigilance Decrement and Passive Fatigue Caused by Monotony in Automated Driving. *Procedia Manufacturing*. https://doi.org/10.1016/j.promfg.2015.07.499
- [S-05] Neubauer C, Matthews G, Langheim L ほか 2011. Fatigue and Voluntary Utilization of Automation in Simulated Driving. *Human Factors*. https://doi.org/10.1177/0018720811423261
- [S-05] Matthews G, Neubauer C, Saxby D ほか 2019. Dangerous intersections? A review of studies of fatigue and distraction in the automated vehicle. *Accident Analysis & Prevention*. https://doi.org/10.1016/j.aap.2018.04.004
- [S-05] Parasuraman R, Manzey D 2010. Complacency and Bias in Human Use of Automation: An Attentional Integration. *Human Factors*. https://doi.org/10.1177/0018720810376055
- [S-06] van der Sijs H, Aarts J, Vulto A ほか 2006. Overriding of Drug Safety Alerts in Computerized Physician Order Entry. *Journal of the American Medical Informatics Association*. https://doi.org/10.1197/jamia.M1809
- [S-06] Ancker J, Edwards A ほか 2017. Effects of workload, work complexity, and repeated alerts on alert fatigue in a clinical decision support system. *BMC Medical Informatics and Decision Making*. https://doi.org/10.1186/s12911-017-0430-8
- [S-06] Graafsma J, Murphy R, van de Garde E ほか 2024. The use of artificial intelligence to optimize medication alerts generated by clinical decision support systems: a scoping review. *Journal of the American Medical Informatics Association*. https://doi.org/10.1093/jamia/ocae076
- [S-06] Goddard K, Roudsari A, Wyatt J 2012. Automation bias: a systematic review of frequency, effect mediators, and mitigators. *Journal of the American Medical Informatics Association*. https://doi.org/10.1136/amiajnl-2011-000089
- [S-09] Hockey G R J 1997. Compensatory control in the regulation of human performance under stress and high workload: A cognitive-energetical framework. *Biological Psychology*. https://doi.org/10.1016/S0301-0511(96)05223-4
- [I-04] Beaton D, Bombardier C, Guillemin F ほか 2000. Guidelines for the Process of Cross-Cultural Adaptation of Self-Report Measures. *Spine*. https://doi.org/10.1097/00007632-200012150-00014
- [I-04] Wild D, Grove A, Martin M ほか 2005. Principles of Good Practice for the Translation and Cultural Adaptation Process for Patient-Reported Outcomes (PRO) Measures. *Value in Health*. https://doi.org/10.1111/j.1524-4733.2005.04054.x
- [N-09] Arun S, Fischer J 2026. Encouraging Thought Before Completion: The Role of Task-Specific Selective Friction in AI-Assisted Knowledge Work. *Proc. 5th Annual Symposium on Human-Computer Interaction for Work*. https://doi.org/10.1145/3808045.3808049
