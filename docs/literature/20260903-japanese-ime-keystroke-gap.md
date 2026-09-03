# 文献カード: 日本語 IME 打鍵の空白はどこにあるか

- **トピック**: japanese-ime-keystroke-gap
- **日付**: 2026-09-03
- **用途**: ★ **主張範囲の確定**（未踏提出文書の日本語 IME 主張が過大でないかを裁く）

## ★ 動機（★ どのやり残しを埋めるラウンドか）

`20260703-intervention-content-and-ml-grounding.md:184-185` 逐語:

> **やり残し**: 日本語 IME 込みの pause 位置分類は世界的に空白 (Hylog [V5] が唯一の隣接) —
> GSE が貢献可能な領域。

⚠️★★★ **その「唯一の隣接」に精読カードが無かった。**★ 存在否定を主張するのに、隣接 1 本を読んでいない状態だった。
★ かつ技術設計書 §8 が **無出典で「公開データセットは国際的に存在しない」と書いていた**（2026-09-03 に取り下げ済み）。

## ★ 検証状態

- 取得: **3 angle**（Hylog 一次全文 / CJK 打鍵ログの先行 / 公開データセット＋反証）
- **一次全文を自読したもの 2 本**: Hylog（21 p・`pypdf`）／ Uto et al. 2020（28 p・`pypdf`）
- ★ **反証 angle を含めた**（Q4: 空白は「未開拓」ではなく別理由ではないか）
- 否決: **2 件**（末尾）

## ★★★ gate 判定（要点先出し）

| 下位問い | 温度 |
|---|---|
| Q1 IME 経由入力を扱う打鍵ログ手法の先行 | ★ **確定・存在する**（中国語。Hylog / Inputlog 中国語版・韓国語版） |
| Q2 非アルファベットのポーズ位置 × 認知過程 | ★ **確定・存在する**（中国語のみ・実質 1 系統） |
| Q3 公開された日本語 IME 打鍵データセット | ⚠️ **二段に割れる**（カード5） |
| Q4（反証）空白の理由 | ★ **「未開拓」寄り。ただし主因の外挿は未証明** |

---

## 1. それはどんなもの?

**日本語 IME 環境の打鍵から執筆過程を推定する、という GSE の設定について、先行がどこまで来ているかを 3 angle で確かめたラウンド。**
★ 結論は **「打鍵 × HMM × 執筆過程」は既に取られており、空いているのは IME の側である**。

---

## 2. 先行研究と比べてどこがすごい? — ⚠️★★★ **本ラウンド最大の発見**

### ★★★ カード1: 日本語話者の打鍵ログを 30 秒窓 × HMM で執筆過程推定した先行が既にある **[検証済 3-0]** [P270]

**Uto, M., Miyazawa, Y., Kato, Y., Nakajima, K. & Kuwata, H. (2020) IJAIED 30(2):271–298.**
★ **一次全文 28 p を自読**（UEC リポジトリ submitted version）。

逐語（★ GSE と同型である決定的な箇所）:

> **frame width W = 30 s and step width H = 10 s**

- **N=72**（男 37 / 女 35・**16–23 歳**・中央値 19・高校生 34 ＋ 大学生 38）
- reading-to-write 課題・**45 分**固定・総打鍵 **184,916**
- 移動窓ごとに打鍵特徴量 → **HMM で潜在状態**（時間依存 ＋ 学習者依存パラメータ）
- 状態解釈（2018 年の日本語版 [P271]）: **待機 / 文章化（速筆型・遅筆型）/ 推敲（修正量多・少・全体・個別）**・最良 **S=9 状態**

⚠️★★★ **GSE の骨格（30 秒ローリングウィンドウ → 打鍵特徴量 → HMM → 潜在状態）とほぼ同型である。**
→ ★★★ **`research-positioning.md` にこれが無いまま「打鍵 × HMM で執筆過程」を新規性として書くと崩れる。**

### ⚠️★★★ ただし、この先行は IME を 1 語も扱っていない（★ 実測）

★ **全文の語数カウント（実測・`uto2020.txt` 65,208 字）**:

| 語 | 出現 |
|---|---|
| `japanese` | ⚠️ **0** |
| `japan` | 3（★ **すべて著者所属の住所**） |
| `input method` / `kana` / `kanji` / `conversion` | ⚠️ **すべて 0** |
| `english` | 0 |

→ ★★★ **論文は執筆言語を明記していない。** ⚠️ 被験者は日本の高校生・大学生で著者も日本の機関だが、
★ **「日本語で書いた」と論文が述べているわけではない**（★ 断定して引かないこと）。
★ ロガーは自作の**テキスト水準ロガー**（⟨文字列, カーソル位置, タイムスタンプ⟩）で、
**IME を扱ったのではなく、結果テキストだけを見ることで IME を迂回している。**

→ ★★★ **したがって差分は「打鍵 × HMM」ではなく「IME を正面から扱うこと」に移る。**

### ★ カード2: 唯一の隣接（Hylog）は日本語を扱わず、content-free 化の余地が構造的に無い **[検証済 3-0]** [V5]

**Crotti, R., Denaro, G., Du, Z. & Muñoz Martín, R. (2026)** — ★ **IEEE Access 14:117046–117067 に採録済み**
（doi:10.1109/ACCESS.2026.3718565）。⚠️ 現行 [V5] は arXiv 版で登録されており**書誌の格上げが要る**。
★ **一次全文 21 p を自読**。

⚠️★★★ **現行 [V5] の gloss「日本語 IME ログ健全性（本文非保存）」は二重に誤り**:

| gloss | 一次の事実 |
|---|---|
| 日本語 IME | ⚠️ **簡体字中国語 + pinyin のみ**（Microsoft Pinyin IME）。★ `Japanese` の出現は**全文で 1 回**、future work の一文だけ —— 逐語 *"**Japanese requires handling multiple scripts (hiragana, katakana, kanji) and input methods (romaji, kana input), necessitating additional pattern rules**"* |
| 本文非保存 | ⚠️★★★ **完全に content-full。** 逐語 *"make it possible to reconstruct the **full** state of the text at any given time"* |

★ **`privacy` / `GDPR` / `anonymi` の出現は全文で 0 回**（実測）。倫理の記述は
*"Approval from an ethics committee was not deemed necessary, as the study involved a non-invasive task,
collected no sensitive personal data, and posed no foreseeable risk"* の 1 文のみ。
⚠️ Chrome 拡張は *"scans accessed pages to detect input fields and capture snapshots of any text typed in"*
と書きながら、**パスワード欄の除外について記述が無い**。

★★★ **これが GSE の差分の実体である** —— 未確定文字列を IME API 抜きで取る唯一の経路が
「アプリの中に入って本文を読む」ことなので、**content-free 化の余地が構造的に無い**。
→ ★ **差分は「文献の不在」ではなく「設計上の排他性」**。

---

## 3. 技術や手法の肝はどこ?

### ★ カード3: ポーズ位置分類は言語体系に対して不変ではない **[検証済 3-0]** [P272]

**Lu, X. (2020) PhD thesis, UCL**（N=32 L2 中国語 ＋ 32 L1 中国語・Translog 2.0・**pause threshold 2 s**・刺激回想）。

★ アルファベット由来の 4 分類（語内 / 語間 / 節間 / 文間・Barkaoui 2019）を中国語へ移植したところ**足りず**、
⚠️★★★ **コーディング中に 2 分類が創発した** —— **`Bpc`（Pinyin と漢字の間＝IME 変換待ち）** と `Bcr`（文脈的修正の間）。

| 位置 | L2 中国語 | L1 中国語 |
|---|---|---|
| 語内 | translation 95% | translation 67% |
| ★ **Pinyin↔漢字（変換待ち）** | ★ **translation 97%** | ★ **translation 82%** |
| 語間 | translation 68% | translation 56% |
| 文間 | planning 49% | **planning 62%** |

逐語: *"writers **paused when they were selecting the Chinese characters from the list after finishing typing the Pinyin**. Such pauses were coded as **a pause between Pinyin and character(s)**"*

→ ★★★ **GSE への直撃**: `anonymize.rs` の `KeyCategory`（`SentencePunctuation` / `Space` / `Enter`）で境界を取る設計は
**ラテン系の前提**である。⚠️ 日本語では **(a) 語間に空白が無い (b) 変換確定が「見えない境界」を作る** の 2 点で崩れる。
★ Lu が中国語で `Bpc` を足さざるを得なかったのと同じ問題が日本語でも起きる。
★ これは **ADR-019 D6「段を上げる前に観測空間の穴（語・文境界のリズム特徴）を埋める」と同じ場所を指している。**

### ★ カード4: IME 確定の検出は「推論」であり、確実な信号ではない **[検証済 3-0]** [V5]

★ Hylog の IME 確定検出は **「SPACE を押したのに画面テキストに空白が出ない」というパターンマッチ**である。
逐語: *"The keystroke logger records a number key or SPACEBAR. **The character corresponding to that key does not appear in the text logged by Hylog at the expected position.**"*

| | John (L1) | Jane (L2) |
|---|---|---|
| precision | **98.4%** | **100%** |
| recall | **99.6%** | **95.6%** |

⚠️ GT は**画面録画からの人手カウント**・**N=2**。
→ ★ **IME イベントを「確実に取れる信号」と仮定してはいけない**ことの定量根拠。

★ 併せて **IME 確定前後の IKI だけが桁違いに長い**（外れ値除去後の平均 **635.05 / 1136.47 ms**、他階層は 123–320 ms）。
→ ★ GSE の実測「変換セッションが推定窓の 56–60%（IME 重量級 fixture で 94%）を覆う」と**独立に整合する**。

---

## 4. どうやって有効だと検証した?

★ 本ラウンドは**存在・不在の確定**が目的なので、下位問いごとに温度を分けた（上表）。

### ⚠️★★★ カード5: Q3 は二段に割れる —— 「日本語の打鍵ログ公開物」は在る。「IME 変換過程を含む公開データセット」は無い **[検証済 2-1]** [P273]

- ★ **在る側**: **ENJA15**（Carl, Aizawa & Yamada 2016・CRITT TPR-DB）。**EN→JA 翻訳・55 時間超**・
  Translog-II の打鍵＋視線・**CC ライセンスで公開**（★ 公開ページを直接確認）。
  ⚠️★★★ **ただし IME / かな漢字変換の扱いは 1 語も書かれていない**（★ 実測）。
  ★ かつ Hylog が一次で *"**none supports non-alphabetic writing, as they cannot identify logograms and symbols introduced by IMEs**"* と述べており、**Translog-II もその「既存ロガー」に含まれる**。
- ⚠️ **供給が止まっている側**: **NINJAL の W-CoLeJa** は打鍵記録ソフト（EssayLoggerTS・約 600 名 × 4 年）を
  **持ちながら、配布物に含めていない**（配布は作文本文・テスト結果・アンケートのみ）。
- ★ キーストロークダイナミクスの網羅サーヴェイ（Shadman et al. arXiv:2303.04605）の公開データセット表 **16 件に日本語は 0 件**。

→ ★★★ **主張は「日本語 IME の変換過程を含む公開データセットは確認できない」まで狭める。**
⚠️ **「日本語の打鍵ログはゼロ」は ENJA15 が反例なので言えない。**
★ **留保 1 票**: ENJA15 が IME 事象を記録しているか**未確認**（→ やり残し）。

### ⚠️★★★ カード6: 「本文を保存せず公開する」は GSE の独自性にならない **[検証済 3-0]** [P274]

★ 先例が **3 系統**確認できた:

| 先例 | 方式 |
|---|---|
| **Tappy**（PhysioNet・Adams 2017） | ★ 文字を記録せず**左右手 ＋ キー列**だけに落とす |
| **IKDD**（*Information* 2024, 15, 511） | ★ ダイグラフに集計し**順序を破棄**。復元不可能性を明示 |
| **Kaggle "Linking Writing Processes"**（KLICKE 由来・CC BY 4.0） | ★ 英数字キーを全部 `q` に置換した **"Q-type"** 形式 |

→ ★★★ **「本文非保存だから公開しやすい」を差分として書いてはならない。**
★ 差分は **「既存ロガーが構造的に扱えない日本語 IME という領域で content-free を成立させること」**に置く。
⚠️ Q-type の逐語は一次 PDF が 403 で未取得（**PLAUSIBLE**）。★ ただし**先例の存在自体は 3 系統あるので結論は動かない**。

---

## 5. 議論はあるか?

### ★ カード7: Q4（反証）—— 空白の理由は「未開拓」寄り。ただし主因は外挿 **[検証済 2-1]** [P275]

| 反証仮説 | 判定 |
|---|---|
| プライバシーで公開できない | ★ **確定**。逐語（EURASIP・doi:10.1186/s13635-020-0100-8）*"**not publicly available due to the sensitivity of biometric data**. Volunteers had privacy concerns and did not consent to wider data sharing (as is their right in **GDPR**)"*。⚠️ **ただし英語では大規模公開が繰り返し成立しており、日本語固有の空白は説明しない** |
| 既存資源で足りる | ⚠️ **成立しない**（Hylog が既存ツールの IME 非対応を一次で明示） |
| 需要がない | ⚠️ **成立しない**（NINJAL が実際に取り、Hylog が 2026 年に新規開発） |
| ツールの IME 非対応が主因 | ★ **PLAUSIBLE BUT UNPROVEN**（★ Hylog の一次は強いが、**中国語について書かれたものを日本語へ外挿している**） |

★ **厚さの順は 中国語 > 韓国語 > 日本語**（確定）:

| | 専用ツール | IME 過程を扱う実証 | ポーズ位置分類 |
|---|---|---|---|
| 中国語 | Hylog / Inputlog 中国語版 | Lu 2020, Lu & Révész 2021 | ★ 6 分類（`Bpc` 含む） |
| 韓国語 | Inputlog 韓国語版（音節 ＋ 選択字） | ⚠️ 無し | ⚠️ 無し |
| **日本語** | ⚠️★★★ **公式ツール無し** | ⚠️ **無し** | ⚠️ **無し** |

★ Hylog 自身の逐語: *"Studies of text-production processes in non-alphabetic scripts are **significantly fewer** than those on alphabetic languages. Furthermore, **very few employ keyloggers for quantitative analysis**."*
⚠️ Hylog が非アルファベットの先行として挙げたのは **4 件のみ**、★ **うち 2 件は Lu 単独の同一データ**。

⚠️★★★ **前ラウンド（`20260815`）の空白理由とは型が違う。** ★ あちらは逐語
「**分野は打鍵ログだけでは分からないと結論して、別モダリティへ行った**」＝ **見切られた空白**。
★ 本ラウンドは **供給側の空白**（需要も計測実績もあるのに公開・ツールが無い）。→ ★ **同じ「ゼロ」でも扱いが違う。**

---

## 6. 次に読むべき論文は?

1. ★★★ **Lu, X. (2020) PhD thesis 全文 490 p** — [P272]（★ 本ラウンドは該当章のみ）
2. ★★ **ENJA15 の生ログ**（SourceForge SVN）— ⚠️ **IME 事象を記録しているかの直接確認**（カード5 の留保 1 票）
3. ★★ **Inputlog 韓国語版の論文**（Kim, Doh, Min 2024・*Korean Language Education* 186）— ⚠️ DOI 未確認・本文未取得
4. ★ **Wang, Zhai & Su (2001) CHI** doi:10.1145/365024.365298 — CJK IME 入力を視線と併せて解剖した古典
5. ★ **Barkaoui (2019) SSLA** doi:10.1017/S027226311900010X — ポーズ位置 4 分類の出所

---

## ⚠️★★★ 否決リスト（★ 記録しないと同じ主張が再浮上する）

| 否決した主張 | 票 | 理由 |
|---|---|---|
| 「日本語 IME 環境の打鍵データセットは国際的に存在しない」 | **0-3** | ⚠️ **ENJA15 が反例**（EN→JA・Translog-II・CC 公開）。★ かつ網羅探索をしていない。→ **「IME 変換過程を含む公開データセットは確認できない」へ縮小** |
| 「本文を保存しない設計だから公開時のプライバシーリスクが構造的に小さい＝GSE の差分」 | **1-2** | ⚠️ **Tappy / IKDD / Q-type の 3 系統が先行**。★ 性質としては真だが**差分にはならない** |

---

## → GSE への含意

- **やり残し（1 行）**: ⚠️★★★ **ENJA15 が IME 事象を記録しているか未確認**。★ ここが埋まると Q3 の留保 1 票が外れる。
  ★ 併せて **日本語側は CiNii / J-STAGE / 国立国語研究所の全文検索を直接叩いていない**（WebSearch 経由の間接探索のみ）。
- **§4 差分との関係**: ★★★ **精緻化（主張範囲の縮小 ＋ 置き場所の移動）**。
  - ⚠️ **降ろす**: 「打鍵 × HMM で執筆過程を推定する」— [P270] が既にやっている（**30 秒窓まで同型**）
  - ⚠️ **降ろす**: 「本文非保存だから公開しやすい」— 3 系統の先例がある
  - ★ **残る差分（3 点）**: **(1) IME を正面から扱うこと**（[P270] は迂回・[V5] は中国語のみ）／
    **(2) content-free と IME 対応の両立**（★ [V5] は本文読み取りに全面依存＝構造的に排他）／
    **(3) リアルタイムの介入判断へ接続すること**（★ [P270] は事後の教育フィードバック）
- ★ **借りられる型**: [P271] は「専門家 2 名にリプレイを見せて作業内容分布を評定させ、**JS 擬距離で一様分布と比較**」
  （**0.695 / 0.796** vs 一様分布 **1.361**）。★ **一様分布ベースラインを置く**のは GSE の較正評価でも真似できる。
