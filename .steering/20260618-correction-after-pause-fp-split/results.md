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

## 生成物
- `--nudge-diag` モード (reason×GT 特徴量診断、production 不変、reusable)。
- 本 results.md。
