# Step 1 結果 — correction_after_pause の FP/TP 特徴量診断 (P000 13 session)

実行: `gse-replay <13 sessions> --nudge-diag`（production 不変・既定 thresholds）。日付: 2026-06-18。

## 診断結果

ACT=34 全件 `correction_after_pause`。GT 群別の決定時特徴量 (min / median / max):

| group | n | p_stuck | f3 | f4 | f6 | idle_ms |
|---|---:|---|---|---|---|---|
| **protect (FP=有害)** | 22 | 0.65/**0.78**/0.88 | 0.33/0.37/0.46 | 1.00/2.71/4.94 | **0.00**/0.55/0.67 | **12503**/24606/28216 |
| **stall (TP=有益)** | 12 | 0.62/**0.85**/0.92 | 0.23/0.36/0.49 | **2.38**/3.45/3.45 | **0.37**/0.55/0.73 | **2781**/24302/29797 |

## 分離可能性の判定: クリーンな単一カットは無い（中心質量が重なる）

- **p_stuck**: TP median (0.85) > FP median (0.78) だが range は全面オーバーラップ (FP 0.65–0.88 / TP 0.62–0.92)。
  → nudge_need を上げると FP も TP も同時に削る（Phase 0 sweep の挙動と一致）。クリーンには切れない。
- **f3**: 中央値ほぼ同一 (0.37 vs 0.36)、全面オーバーラップ。分離力なし。
- **idle_ms**: 中央値ほぼ同一 (~24.5k vs ~24.3k)。**FP は全件 idle≥12.5s**(短 pause の FP は無い) だが、
  大半の TP も同じ medium 帯に居る → idle で切ると TP も大量に巻き込む。クリーンに切れない。

### 唯一の「TP ゼロコスト」レバー候補 = FP のみの低裾 (f4 / f6)
- **f4 (burst length)**: TP の下限 = **2.38**。FP は下限 1.00 まで伸びる。
  → 「f4 ≥ 2.38 を要求」すれば **TP は 1 件も落とさず**、f4<2.38 の FP だけ落とせる。
- **f6 (pause-after-delete)**: TP の下限 = **0.37**。FP は下限 0.00 (= delete 後 pause 無し)。
  → 「f6 ≥ 0.37 を要求」すれば **TP ゼロコスト**で f6<0.37 の FP だけ落とせる。

ただし両特徴とも中央値は群で同一 (f4≈median 重なり / f6 median 0.55 共通) なので、
落とせるのは **FP の低裾の数件のみ**。劇的な HIR 改善ではなく、限定的な削減。
**正確な削減量 (HIR/recall) は counterfactual で測る必要がある (Step 2)**。

## 結論と申し送り

1. **keystroke 特徴量 (decision 時) では FP と TP を劇的には分離できない。** 中心質量
   (p_stuck≈0.8 / f3≈0.37 / f4≈3 / f6≈0.55 / idle≈24s) が両群で重なる。これは
   「keystroke-only がこの識別で天井に当たっている」ことの定量的裏付けであり、
   improvement-plan §3 の主張と整合する。
2. **限定的だがゼロコストの候補**: `f4 ≥ ~2.4` と `f6 ≥ ~0.37` は TP を落とさず FP 低裾を切れる
   → Step 2 で counterfactual 試算する価値あり (production 変更候補)。
3. **GT の留保が効く**: FP 22 件は全て idle 12.5–28s の **長い correction pause** を Flow と
   ラベルした区間。forward-fill GT では「30–60 秒前の Flow 申告が延伸され、実際は stall へ
   ドリフトしていた」可能性が高く、**FP の一部は真の害でなく GT アーティファクト**。
   → 回復窓 W・GT 精緻化で像が変わりうる (screening であり verdict ではない、§9)。
4. **カメラ提案との関係**: 提案の抑制ルール (reading_like=低 correction / off_screen / face_absent) は
   この FP 母集団 (高 correction・on-screen・長 pause) に当たらない。カメラを足しても
   この 22 FP は減らせない見込み。カメラの主目的は別 (離席/読書の FP) に絞るべき。

## 次の選択肢
- **(a) Step 2**: f4/f6 floor を injectable 化し counterfactual で HIR/recall を試算 (production 変更候補 ≤3)。
- **(b)** blunt な nudge_need=0.80 を採用 (Phase 0 で HIR 0.647→0.357 と既測、recall 0.073→0.055)。
- **(c)** GT/回復窓を見直し「FP がどれだけ真の害か」を再評価してから判断。

---

# Step 2 結果 — correction_after_pause veto floor の counterfactual

`gse-replay <13 sessions> --corr-floor`（production 不変・veto を注入 thresholds で評価）。

veto = `correction_after_pause` の nudge を `f4 < floor` または `f6 < floor` で defer に落とす。
floor 候補は診断の TP 下限 (f4=2.38 / f6=0.37)。

| candidate | nudge | fp | tp | HIR | Prec | Recall | DC | Burden/min |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| baseline | 34 | 22 | 12 | 0.647 | 0.353 | 0.073 | 0.933 | 0.520 |
| **f4≥2.38** | 25 | **13** | **12** | **0.520** | 0.480 | **0.073** | 0.933 | 0.383 |
| f6≥0.37 | 24 | 13 | 11 | 0.542 | 0.458 | 0.067 | 0.933 | 0.367 |
| f4≥2.38 OR f6≥0.37 | 24 | 13 | 11 | 0.542 | 0.458 | 0.067 | 0.933 | 0.367 |

## 結論: f4≥2.38 が Pareto 最適

- **f4≥2.38**: 22 FP のうち **9 件を除去 (→13)、TP は 12 のまま維持 (recall 不変 0.073)**。
  HIR 0.647→**0.520**、burden 0.520→0.383、DC 0.933 維持。**TP ゼロコストの予測が実証された。**
- f6≥0.37 / both は **TP を 1 件落とす** (12→11, recall 0.073→0.067)。診断の TP f6 下限「0.37」は
  2 桁丸めで、実値が 0.37 をわずかに下回る TP が 1 件あり veto に掛かった。FP 除去数は f4 と同じ
  9 件なので、f6/both は **f4 に対し純粋に劣る**（同じ FP を切り TP を 1 余分に失う）。
- both が f6 と同値 = f4<2.38 の FP は f6<0.37 の部分集合。

## 閾値変更候補 (Step 2 成果、≤3)

1. **【推奨】correction_after_pause に `f4 ≥ 2.38` ゲートを追加**: HIR 0.647→0.520・burden -26%・
   **recall/TP/DC 全て不変**。keystroke 側で唯一見つかった「害だけを減らす」レバー。
2. 候補 1 + nudge_need 微増 (例 0.65): さらに HIR を削るが recall が落ち始める (Phase 0 sweep 参照)。段階適用。
3. （却下）f6 floor / both: f4 単独に劣後 (TP を無駄に失う)。

## 重要な留保 (production 採用前に必須認識)
- **過学習リスク**: floor 2.38 は P000 の **TP 最小値そのもの**で、この 13 session に最大限フィット。
  新データで f4<2.38 の TP が出れば recall を削る。production 採用時は (a) やや保守的な floor
  (例 2.0) にする、(b) ラベル付き session 増加後に再校正、のいずれかを推奨。
- 残る 13 FP は f4/f6 では切れない真の overlap 領域。screening であり verdict ではない (forward-fill GT,
  単一被験者, n 小)。FP の一部は GT ドリフト由来の可能性 (§ Step1 留保)。
- **production 採用は別ステップ**: floor を既定に入れる = 挙動変更 → policy/HMM_VERSION 検討 +
  golden snapshot 再生成 + decisions.md 記録が必要。本タスクは counterfactual の試算までで、採用は承認後。

## 生成物
- `--nudge-diag` モード (reason×GT 特徴量診断)。
- `--corr-floor` モード (veto floor counterfactual、baseline/f4/f6/both 比較)。
- `InterventionThresholds.correction_f4_floor / correction_f6_floor` (既定 None = production 不変、採用時の注入口)。
- 本 results.md。
