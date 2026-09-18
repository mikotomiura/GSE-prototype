# 本文・位置を使わない「修正（revision）」の指標 —— `T1c` の算出式と名前の接地

> 2026-09-19 / `/literature-review` 1 ラウンド（S7）/ **設計根拠の補強**（★ issue 004 の算出式と**フィールド名**を決めるため）
> 名前空間: `V`（測定方法論）。登録 **[V151]–[V160]**（`provisional` 1 件 = [V159]）。

## 動機（★ なぜこのラウンドを回したか）

★ `.steering/20260914-mhd-feature-offline-tiers/blockers.md` **起票 9**: issue 004（`T1c` revision topology）の
`rewrite_count` / `redelete_count` / `loop_depth_max` / `local_recurrence` の**演算的定義がどこにも無い**
（★ 出典とされた `.idea/survey:189` は名前の一覧だけ）。worker は推測実装で 3 attempt を失って停止した。
★ 研究者判断（2026-09-18・`.steering/20260918-theory-critical-review/decisions.md` 判断 1 #8）:
**サーヴェイ S7 の後に算出式とフィールド名を確定する**。
⚠️ 懸念は「名前」にあった —— ADR-030 D10 の証拠列が逐語「**先行研究は本文・カーソル位置を持っている**」と書くとおり、
**`rewrite` / `loop depth` は本文・位置を前提にした構成概念を指している可能性**がある。

★ 下位問い（★ 自動再開の無人実行のため、分解は事前合意なしで記録した）:
- **S7-a** 書字過程研究の修正の構成概念は、本文か位置を**必要とする**か
- **S7-b** キー種別と時刻だけで定義された修正の指標は既にあるか。名前は何か
- **S7-c** 「入れ子の深さ」「局所的な反復」に当たる位置なしの指標はあるか
- **S7-d**（反証）位置なしの削除の計数は、誤打の訂正と内容の修正を分けられないのではないか

## 検証状態

- **探索**: サブエージェント 3 本（Opus・分野を変えた angle: 書字過程研究 / 教育測定・学習分析 / RQA・プログラミングの編集ログ）
- **取得ソース**: 約 30 件（★ 全文到達 22 件前後 ／ abstract のみ・未取得は各表に明記）
- **claim 抽出**: 18 件 → **検証 18 件**
- **confirmed 12**（3-0 が 8 / 2-1 が 4）／**否決 4**／**判定不能 2**（該当ゼロ）
  ⚠️ 初稿は 17 / 11 と書いていた —— 台帳で数え直して訂正した（★ 前ラウンドと同じ誤りを繰り返さないため台帳を置く）
- ★ **メインが保存本文（pypdf 抽出）で逐語を照合した**: [V151] p.6 / p.11 / p.12 ・[V152] p.5 / p.13 ・[V153] p.39 ・[V154] p.485 / p.487 / p.492 ・[V155] p.102 / p.111 / p.113 / p.118 ・[V156] p.88 ・[V157] p.28 ・[V158] p.406 ・[V159] p.25 ・[V160] p.249 / p.257
  （⚠️ [V154] の「93%」はサブエージェントが p.493 と報告したが、抽出本文の頁対応で **p.492** に訂正した）

### claim 台帳

| # | claim | 出典 | 票 | 温度 |
|---|---|---|---|---|
| 1 | 書字過程研究の修正の構成概念（pre / contextual・leading edge・embedded・repetitive・S-notation の入れ子・substitution）は**位置か本文を要する** | [V155] [V154] [V160] | **3-0** | 確定 |
| 2 | 「depth」は修正の**向き**（表層 / 深層・Faigley & Witte）の意味で既に使われている | [V155] | **3-0** | 確定 |
| 3 | 同一箇所の再修正（repetitive）は位置で定義され、典型例は**誤打の連鎖** | [V155] | **3-0** | 確定 |
| 4 | 位置なしで「入れ子の深さ」「rewrite」「redelete」「loop depth」を定義した先行 | — | — | **判定不能（0 件）** |
| 5 | キー種別と時刻だけで修正特徴を作り**人手注釈と照合**した研究 | — | — | **判定不能（0 件）** |
| 6 | 位置・内容を使わない Insert/Delete 列でも得点群は分かれたが、判別的だったのは**交替ではなく長い連続** | [V151] | **2-1** | 確定（留保あり） |
| 7 | 位置なしの削除 ÷ 挿入の比（DIRatio）は得点群間で差がない | [V151] | **3-0** | 確定 |
| 8 | 編集事象数と得点の関係は**文書長で正規化すると大部分消える**（量の交絡） | [V153] | **2-1** | 確定（留保あり） |
| 9 | 削除系の特徴は**課題を変えると最も一貫しない**。過程特徴は本質的に流暢さの尺度（著者の留保） | [V152] | **3-0** | 確定 |
| 10 | 自然課題では文字 bigram と打鍵間隔を使っても、誤打訂正の判別は**多数派基準 +1 ポイント**。誤打の時点までの特徴だけでは基準を下回る | [V156] | **3-0** | 確定 |
| 11 | 修正の 92% は表層で、backspace の計数は**粗い代理** | [V155] | **3-0** | 確定 |
| 12 | 位置で jump と局所編集を分けたモデルが有意に良い（位置が情報を持つ） | [V157] | **2-1** | 確定（留保あり） |
| 13 | 打鍵の RQA は**打鍵間隔**を入力にし、速度と強く相関する。**global** な打鍵パターンの分析と位置づけられる | [V158] | **2-1** | 確定（留保あり） |
| 14 | 「Average Recurrence」（Allen 2016）は RQA ではなく**時間窓どうしの距離**（ポーズの指標） | [V159] | **3-0** | 確定 |
| 15–18 | ⚠️ 否決 4 件 → §否決リスト | — | **1-2 が 1 / 0-3 が 3** | — |

### ★ 3 票の視点

① **内的妥当性**（定義・測定が主張と一致するか）② **GSE への外挿**（キー種別 14 カテゴリ・時刻・押下/解放だけで成り立つか）③ **頑健性**（小標本・二次引用・解釈の混入）。

## gate 判定（要点先出し）

| 下位問い | 温度 | 一言 |
|---|---|---|
| **S7-a** 修正の構成概念は本文・位置を要するか | **確定（要する）** | pre / contextual・embedded・repetitive・S-notation の入れ子・「depth」はすべて位置か本文で定義されている |
| **S7-b** キー種別と時刻だけの修正指標 | **部分的に既出 ／ 妥当性は判定不能** | 使えるのは削除の回数・連の長さ・直前ポーズ・Insert/Delete 列・修正間の時間まで。⚠️ 人手注釈と照合した研究は **0 件** |
| **S7-c** 入れ子・反復の位置なし指標 | **判定不能（0 件）＋名前の衝突は確定** | `loop depth` の用例 0 件。`local_recurrence` は既存の 2 用法（global RQA・時間窓間距離）と衝突 |
| **S7-d**（反証）誤打訂正と内容修正を分けられるか | **確定（分けられない）** | 文字 bigram があっても自然課題で基準 +1 ポイント。GSE は bigram すら持たない |

★ **issue 004 への判定**: **de-risk 先行** —— 算出式は新しい定数ゼロで閉じられる（`.steering/20260918-theory-critical-review/definitions-restop-t1d-t1c.md` §6）が、
⚠️ **フィールド名を既存の構成概念（位置・本文で定義）から切り離す改名**を先に決める必要がある（→ 研究者判断）。

---

### カード 1: 修正の構成概念はすべて位置か本文で定義されている —— `rewrite` / `redelete` / `loop depth` を GSE が名乗ると別物を指す **[検証済 3-0]** [V155] [V154] [V160]

1. **どんなもの?** 書字過程研究の修正の分類・命名（Conijn et al. の tagset [V155]、修正事象の自動抽出 [V154]、打鍵分析の方法論 [V160]）。
2. **先行研究と比べてどこがすごい?** tagset [V155] は 7,120 件の修正を人手注釈し、**同一箇所の再修正（repetitive）・入れ子（embedded）・向き（depth）**に操作的定義を与えた。
3. **技術や手法の肝は?** ★ どの定義も**文書中の文字位置**か**本文**に依存する:
   - repetitive —— 逐語 *"revisions which start (in the writing product) within two characters from the start (in the writing product) of the previous revision. This could, for example, happen when a typo is incorrectly revised"*（[V155] p.111）
   - depth —— 逐語 *"the orientation or the depth of the revision (Faigley & Witte, 1981)"*（[V155] p.102）＝ **表層か意味か**の区別
   - S-notation の入れ子 —— 逐語 *"S-notation can break with long texts, when the hierarchy becomes too complicated (e.g., revisions embedded within revisions, embedded within revisions, etc.)"*（[V154] p.487）
   - 公開コードの前提 —— 逐語 *"key type, position in the document and current document length"*（[V154] p.489）
   - typo の除外 —— 逐語 *"corrections of errors within a word, which leave the word otherwise unchanged and which do not result in a break of more than two seconds before the next keystroke"*（[V160] p.257）＝ **語（本文）が要る**
4. **どうやって有効だと検証した?** [V155] は二重注釈と一致度。★ repetitive の典型が「誤打を誤って直し、また直す」連鎖であることを著者自身が例示している。
5. **議論はあるか?** ⚠️ **位置なしで同じ語を使うと、先行研究が位置で定義した構成概念を *名乗る* ことになる**。GSE の「削除の走りの直後に挿入が来た」は**先端での訂正か遡った書き直しかを区別できない**ので、`rewrite` とは呼べない。「depth」は入れ子とも向きとも読まれる。
6. **次に読むべき論文は?** Lindgren & Sullivan (2006) の revision taxonomy 原典（未取得・abstract のみ）／ Kollberg & Severinson Eklundh の S-notation 原典（未取得）。

★ **判定**: **確定**。★ **GSE への帰結**: `rewrite_count` / `redelete_count` / `loop_depth_max` は**改名すべき**（例: `del_to_ins_transitions` / `delete_runs_after_first_in_burst` / `di_alternations_max`）。⚠️ 改名は issue 004 AC1 の改訂なので研究者判断。

### カード 2: 位置も内容も使わない Insert/Delete 列 —— 判別的なのは「交替」ではなく「長い連続」 **[検証済 2-1]** [V151]

1. **どんなもの?** ETS の中学生 761 名の論述ログを、**内容と間隔を捨てた操作列**（insert / delete / cut / paste / replace）で系列マイニングした研究。逐語 *"we purposely ignored the linguistic content"*（p.4）。
2. **先行研究と比べてどこがすごい?** ★ **GSE の `T1c` に最も近い入力**で書字過程を比べた、今回見つかった唯一の先行。
3. **技術や手法の肝は?** 長さ 10 以下の部分系列を support ≥ 0.1 で列挙し、得点群で χ² 比較（逐語 *"we only consider the actions, while ignoring the lengths of the pauses"*・p.9）。
4. **どうやって有効だと検証した?** ⚠️★★★ 逐語 *"the most discriminating subsequences featured longer sequences (more than an average word length of 4.5 characters in this dataset) of delete or insert actions rather than local editing featuring alternating deletes and inserts"*（p.11）。★ 比は効かない: 逐語 *"The difference on DIRatio was not significant"*（p.6）。
5. **議論はあるか?** ⚠️ **留保（1 票）**: Insert/Delete の判定は ETS の**位置つき差分ロガー**が行っている／予測対象は得点でありプロセス内状態ではない／短い往復を「誤打の素早い修正」とするのは逐語 *"not minor edits, which tend to be quick fixes to one or two characters"*（p.12）の**著者の解釈で検定なし**。
6. **次に読むべき論文は?** 同じデータで位置つき特徴と位置なし特徴を正面比較した研究（★ **0 件** —— [V157] が間接）。

★ **GSE への帰結**: 交替回数（`loop_depth_max` の候補 A）を主にせず、**連続長（`delete_run_max` は既に一意）と交替回数の両方を ablation にかける**（ADR-030 D10 の block ablation）。

### カード 3: 位置なしの削除の計数は「量」と「流暢さ」に交絡し、課題を変えると安定しない **[検証済 3-0 / 2-1]** [V152] [V153]

1. **どんなもの?** ETS の大規模な打鍵過程特徴の研究 2 本。
2. **先行研究と比べてどこがすごい?** 6 フォーム・2,500 名超で**課題間の一貫性**を見た（[V152]）。
3. **技術や手法の肝は?** 特徴ごとのフォーム間相関と、文書長での正規化。
4. **どうやって有効だと検証した?**
   - [V152] 逐語 *"the features most likely to link with editing and planning behaviors (pauses between sentences, cut/paste/jump events, and backspaces) show the least consistency across tasks"*（p.13）＋ 著者の留保 *"the features remain, essentially, measures of fluency"*（p.5）
   - [V153] 逐語 *"The strong relationships between the number of editing events and the scores have largely disappeared."*（p.39・文書長で正規化した後）
5. **議論はあるか?** ⚠️ [V153] は小標本のパイロット（2-1）。★ [P36]（Conijn 2019・既登録）も削除数は打鍵効率のような低次の要因と交絡すると述べる（サブエージェント報告）。
6. **次に読むべき論文は?** 位置なしの修正特徴を**打鍵数・中央値 IKI で統制した後**に残る情報を測った研究（0 件）。

★ **GSE への帰結**: `T1c` の各量は **`T0`（打鍵数・純産出）と速度で統制した増分**でしか評価しない（ADR-030 D10 の block ablation と calibration contribution）。

### カード 4: 誤打の訂正と内容の修正は、文字があっても自然課題ではほぼ分けられない **[検証済 3-0]** [V156] [V155]

1. **どんなもの?** 誤打訂正（typographic error revision）を過程データから判別するモデル。copy task と source-based の自然課題。
2. **先行研究と比べてどこがすごい?** 自然課題での**性能天井**を示した。
3. **技術や手法の肝は?** 文字 bigram・打鍵間隔などの過程特徴で random forest。
4. **どうやって有効だと検証した?** ⚠️★★★ 逐語 *"All models which only included the features up to the typographic error did not outperform the lower baseline"*・*"The accuracy, with 59%, only outperformed the lower baseline with 1%."*（[V156] p.88）。★ 基準率: 逐語 *"most revisions were surface revisions (92%)"*（[V155] p.113）・backspace 計数は *"a raw proxy of revisions … it ignores a wide range of revision events"*（[V155] p.118）。
5. **議論はあるか?** ★ **GSE は文字 bigram すら持たない**。→ キー種別と時刻だけで「内容の修正」を測ったと主張する根拠は無い。⚠️ 逆に、GSE の削除系の量は**ほぼ表層（誤打訂正）を数えている**と読むのが自然。
6. **次に読むべき論文は?** 日本語 IME 下の backspace と修正分類（★ **0 件**）。

★ **GSE への帰結**: `T1c` を「修正の位相」と呼ばず、**「削除と挿入の遷移の形」**という観測の名前で呼ぶ（★ glossary の方針「量が観測方法に紐づいた指標のままである間だけ守れる」と同じ）。

### カード 5: 「局所的な反復」は既存の 2 用法と衝突する **[検証済 3-0 / 2-1]** [V158] [V159]

1. **どんなもの?** 打鍵に再帰量化解析（RQA）をかけた研究と、"recurrence" を名に含む打鍵指標。
2. **先行研究と比べてどこがすごい?** RQA は時系列の再帰構造を扱う確立した枠組み。
3. **技術や手法の肝は?** ★ 入力は**打鍵間隔**（逐語 *"The pause time between each keystroke served as the target event for RQA"*・[V158] p.402）。⚠️ **キー種別の系列に RQA をかけた研究は 0 件**。
4. **どうやって有効だと検証した?** ⚠️ 速度の交絡: 逐語 *"shorter IKIs (thus faster typing) also corresponded to higher values of RQA"*（[V158] p.406）。★ Allen 2016 の "Average Recurrence" は逐語 *"This recurrence is expressed as the distances between time windows that contain at least one keystroke event. This measure is useful for identifying writing pauses"*（[V159] p.25）。
5. **議論はあるか?** ⚠️ [V158] は題名どおり **global** な打鍵パターンの分析。→ **`local_recurrence` は「global RQA」とも「時間窓間距離の recurrence」とも衝突する**。
6. **次に読むべき論文は?** Wallot & Grabowski (2019) の打鍵 RQA チュートリアル（未取得）。

★ **GSE への帰結**: `local_recurrence` は**改名**する（例: `category_bigram_repeat_rate`）。RQA を名乗るなら「閾値 0・埋め込み 1 のカテゴリ RQA」と明示し、打鍵数と中央値 IKI を共変量にする。

---

## 否決リスト（★ カード本体に書かない）

| # | 主張 | 票 | 否決理由 |
|---|---|---|---|
| 1 | 「単発の backspace は綴りの訂正、連続は編集を表す」 | **1-2** | 出典（Chanquoy 2009）を二次引用した学習分析論文（Malekian 2019）の記述で、**原典未確認・当該研究でも検証なし** |
| 2 | 「backspace 連が 5 打鍵を超えたら誤打ではない」 | **0-3** | [V156] p.83 の**著者自身が検証していない規則**（注釈作業の便宜） |
| 3 | 「多重 backspace 特徴の課題間相関は最低 .09」 | **0-3** | メインが表を照合したところ、該当の数値が**課題間相関か人手得点との相関か**を確定できなかった（[V152] の表の読み違いの疑い） |
| 4 | 「`Conijn et al. (2021)` という revision detection の独立した論文がある」 | **0-3** | 実体は [V154]（*Reading and Writing* 2024 年号・2021 online）。本文中の "Conijn et al., 2021" は [V155] を指す ＝ **`.idea/survey §13` の書誌の取り違え** |

## GSE への還元

- ★ **issue 004（`T1c`）**: 算出式は `definitions-restop-t1d-t1c.md` §6 の推奨候補（新しい定数ゼロ）で閉じられる。⚠️ ただし**名前を観測の名前へ改める**（カード 1 / 5）。→ `decisions.md` に判断 2 の候補として記録し、研究者に改名の可否を仰ぐ。
- ★ **ADR-030 D10 の `T1c` 行**「★ 中〜強（Tier 中で最も強い）」は、**本文・位置を持つ先行研究の強さ**であり、GSE の位置なし版には移らない（カード 4）。→ 段 3（ADR-030 補訂）で証拠列の注記候補。
- ⚠️ `research-positioning.md` §3 / §4 への還元は **段 3 へ送る**（研究者判断 1 #1 の反映と同時）。★ 還元の要点: 「content-free で修正を測った先行が 0 件」は**空白**であると同時に**警告**である（誤打訂正と内容修正を分けられない・量と速度に交絡）。

## やり残し

- ⚠️ **キー種別と時刻だけの修正特徴を人手注釈と照合した研究が 0 件** —— GSE の `T1c` は妥当性の証拠を持たないまま特徴になる（★ ablation と calibration でしか正当化しない）
- 原典未取得: Kaufer, Hayes & Flower 1986（R-burst）・Lindgren & Sullivan 2006・Kollberg / Severinson Eklundh の S-notation・Wallot & Grabowski 2019
- 日本語 IME 下の backspace（未確定文字列の削除）と修正分類: **0 件**
- `navigation` キーを「遡った修正」の位置の代理に使えるか（★ 本ラウンドの提案・未検証）
