# resumption-baseline（B1 → M1）

## 背景

★ **ADR-023 は 2026-09-06 に Accepted で起票済み**（`docs/adr/ADR-023-coupling-as-primary-outcome.md`）。
★ 本タスクはその §Migration の前段 2 件を片づける。

⚠️★★★ ADR-023 **D7** が記録に固定した「計器の問題」は 6 つあり、そのうち **2 番目**
（**「解決」と「放棄」が content-free では区別できない**）だけは **実データで測れる**。
★ [P321] Alaboudi & LaToza (2021) の公開データは、**人手でビデオと発話を見て**なお
episode の終端を逐語 *"fixes the defect **or decides to stop**"* と置いており、
★ **「放棄がどれだけ混ざるか」を実測できる唯一の手がかり**である。

★ 研究者判断（2026-09-06）: ⚠️★★★ **アート（表現の形）の議論の前に B1 を片づける。**

## ゴール

- **B1**: [P321] の公開データから **R₀ / R₁** を実測する。
  ⚠️★★★ **先に検算 A（論文の既報値との突き合わせ）を通す。合わなければ止まる。**
- **M1**: 「中断 → 再開」の観測を `experiments/` として **設計する**（★ 第 1 弾 = 離席候補アームのみ）。

## スコープ

### 含むもの
- `experiments/20260906-p321-resumption-baseline/` — B1 の実測（★ 実行まで）
- `experiments/20260906-interruption-resumption-arm1/` — M1 の**設計** ＋ 実行可能性プローブ
- ★ `experiments/` 規約（`docs/experiment-tracking.md`）の**読み替え**の明記

### 含まないもの
- ⚠️★★★ **アート（表現の形）の議論**（★ 研究者判断で後回し）
- ⚠️ **ADR の新規起票**（★ ADR-023 で足りる）
- ⚠️ **既存 ADR（017/018/020/021/022/023）本文の書き換え**
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` の書き換え**
- ⚠️★★★ **`p_flow` 依存の是正（ADR-023 M3）** —— ★ `HMM_VERSION` bump ＋ ゴールデン再生成を伴うため**単独コミット**
- ⚠️ **`self_recovery_without_paste` の改名（M2）** —— ★ 別タスク
- ⚠️ **M1 のアウトカム本解析**（★ 設計まで。→ `notes.md` §7）
- ⚠️ **「慣れているか（習慣化）」**（★ 扱うなら ADR-020 に当たる・M7）
- ⚠️ **`scripts/secrets-filter.sh` への `email=` 追加**（★ fail-closed で over-block・M10）

## 受け入れ条件

- [x] **検算 A が通る**（★ 論文の既報値と突き合わせ、全項目緑）
- [x] **R₀ / R₁ を算出し、差を「放棄の混入量」として報告**した
- [x] `notes.md` に**外挿の限界**を書いた
- [x] `experiments/` 規約の**読み替え**を「省略」ではなく「読み替え」として明記した
- [x] ⚠️★★★ **検査自体が空回りしていないか**を 3 状態（正常 / 不在 / 壊れている）で試した
- [x] **`run.sh` を実際に実行して exit 0 を確認**した（★ 予測しない）
- [x] M1 の設計に **ADR-023 の 7 制約**を入れた（★ + B1 由来の 8 番目）
- [x] ⚠️ **生データを repo にコミットしない**（★ `raw/` は `.gitignore` 済み・集計値のみ `results/`）

## 関連ドキュメント

- `docs/adr/ADR-023-coupling-as-primary-outcome.md` D6 / D7 / D8 / §Migration
- `docs/experiment-tracking.md`（★ `experiments/` 規約の SSOT）
- `docs/research-positioning.md` §5 **H-Y**
- `.claude/skills/reproducibility-discipline/SKILL.md` / `verify-before-claiming` / `browser-verification`

## 運用メモ

- **/reimagine 適用**: **No**
- **理由**: ★ 本タスクは (a) 外部公開データの決定的な集計と (b) 既決の ADR-023 を
  `experiments/` の形に落とす作業であり、⚠️ **設計の選択肢が複数あるタスクではない**。
  ★ 判断の分岐（畳み方 / 定義の揺れ）は **感度分析として両方出す**ことで解いた。
