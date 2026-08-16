# 設計 — Step 4（層 2 粒子 ＋ 混同テスト）

## 実装アプローチ

**Web Audio / AudioWorklet**（S4-D2）。既存 `player/layer0.html` の合成グラフに層 2 を**足す**。

```text
                         ┌─ 層 0（既存・S3 から複製） ────────────────┐
  osc[1..8] (n*f0) ──> partialGain[n] ──┐                            │
  lfo[rates] ──> lfoAmpGain ────────────┼──> sum -> drift -> expr ───┼──┐
  lfo[rates] ──> lfoTiltGain[n] ────────┘   （B/C 案はこちら）        │  │
                         └───────────────────────────────────────────┘  │
                         ┌─ 層 2（新規・AudioWorklet） ──────────────┐   ├─> master -> dest
  grain-processor  ──> grainBand(BPF) ──> grainGain ────────────────┼───┘        │
     ↑ 粒子率 / 粒長 / 中心周波数 / 帯域 / seed                       │            └─> analyser（観測用・音に影響しない）
                         └───────────────────────────────────────────┘
```

★ **層 0 は 1 実装のまま**（S4-D8）。★ **切替は全てランプ**（オンセットを作らない・`spec` §2）。

### なぜ AudioWorklet か（`AudioBufferSourceNode` を粒ごとに作らない）

★ **S3-D3 の要件 (a)「メモリが増え続けない」**——100 grains/s × 600 s = **6 万個**。
粒ごとにノードを作ると生成・GC が積み上がる。★ **Worklet 内でサンプルを直接書けばノード生成は 0 回**。
⚠️ **`OfflineAudioContext` でも `audioWorklet.addModule()` は使える**ので、
★ **S3-D4（本番と同じグラフを測る・二重実装しない）を層 2 でも維持できる。**

### 粒の作り方（★ 合成音のみ。実物音の引用禁止 = S3-D14 を維持）

1 粒 = **Hann 窓を掛けた正弦バースト**。
★ **Hann 窓は端点が厳密に 0** なので、★ **粒の始端にクリック（オンセット）が立たない**。
周波数は中心 ± 帯域から **seed 固定の PRNG** で引く（`SEED` に実値を書く = C2）。

## 変更対象

### 新規作成

| ファイル | 役割 |
|---|---|
| `experiments/20260812-expression-step4-grain/step4.config.json` | ★ **凍結物**（S3-D5 の形を維持）。層 0 候補 / 層 2 / A・B・C 案 / 盲検設定 |
| `.../player/step4.html` | player 本体（層 0 ＋ 層 2 ＋ 混同テスト ＋ 検算） |
| `.../player/grain-processor.js` | AudioWorklet。★ 粒子生成・粒数カウンタ・seed 固定 PRNG |
| `.../scripts/step4_selftest.py` | 静的検査 ＋ ★ **meta 検査**（検査を壊して赤くなること） |
| `.../run.sh` | `check` / `data` / `serve`（Step 3 の形を踏襲） |
| `.../SEED` `.../env.md` `.../data.md` `.../notes.md` `.../results/` | `reproducibility-discipline` ルール 1 |

### 修正

| ファイル | 何を |
|---|---|
| `.steering/20260811-expression-prototype-step0/scripts/expr_smooth.py` | `EXPR_VERSION` を `0.3.0-step4` へ（S4-D3）。★ **他は 1 行も変えない** |
| `experiments/20260812-expression-layer0-drone/layer0.config.json` | `expr_version` を追随（S4-D3） |
| `experiments/20260812-expression-layer0-drone/env.md` `notes.md` | ★ 追随した事実を 1 行追記（**実測値は書き換えない**） |
| `docs/glossary.md` | ✅ 済（層 0 の定義を S3-D12 に合わせ、Step 4 の用語 7 件を追加） |
| `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` | ★ 耳の結果が出てから §9 を更新（**先に書かない**） |

### 触らない

`docs/preregistration-v0.3.md` / `engine.rs` / `probe_scheduler.rs` / `schema_dto.rs` / `App.tsx` /
`src-tauri/` 全般 / `experiments/20260812-expression-layer0-drone/player/layer0.html`。

## A/B/C 案の実装（S3-D13）

| 案 | 層 0 の自律変異 | 層 2（状態）| 実装 |
|---|---|---|---|
| **A: 周波数で分ける** | **振幅**・★ **≤0.0005 Hz**（周期 33 分以上） | 密度・帯域 | `lfoAmpGain` を使い、レートを 0.0005 / 0.00031 Hz に |
| **B: 次元で分ける** | ★ **音色（倍音傾斜）のみ**・0.005 / 0.0031 Hz | 密度・帯域 | `lfoTiltGain[n]` を使い `lfoAmpGain` を 0 に |
| **C: 両方** | **音色のみ**・★ **≤0.0005 Hz** | 密度・帯域 | 上記の組合せ |

★ **倍音傾斜（B/C 案）の作り方**: LFO を各倍音のゲイン AudioParam へ、
**重み `w_n`（低次は −・高次は ＋）**を掛けて入れる。★ **`Σ w_n·a_n ≈ 0` に正規化する**ので
**全体の音量はほぼ動かず、音色だけが動く**。→ ★ **これが「次元で分ける」の実体である。**

⚠️ **3 案とも常に最大構成で組み、使わない経路はゲイン 0**（Step 3 の教訓・引き継ぎ §5-5）。
★ **案の切替で鳴らし直しが起きない。**

## 混同テストの実装（S4-D4 / S4-D5）

```text
連続再生したまま、60 s の窓を 10 個並べる（★ トライアル間で音を止めない = オンセットを作らない）
  各トライアル開始時に、seed 固定の順序で 1 つだけ目標値を階段状に変える
       ↓ ★ 必ず τ≥60 s の一次遅れを通す（spec §1.3・合成注入でもステップを直接当てない）
  60 s 後に「基層 / 自分 / わからない」を強制選択
       ↓
  10 回終わったら results/blind-<plan>.json へ書き出す（★ 途中で正誤を出さない）
```

- **内訳**: 層 0 が動く **4** / 層 2 が動く **4** / ★ **catch（何も動かない）2**
- **採点**: 8 問（catch を除く）。★ **案を残す閾値 = 7/8 以上**
- ⚠️★ **感度合わせ（非盲検）を先に置く** —— 2 種類の変化を**別々に・ラベル付きで**聴ける
  「見本」モードを用意する。★ **これが無いと「案が悪い」と「そもそも聞こえない」が混ざる。**
  ⚠️ **変化量は知覚的に等化していない**（等化していないことを `notes.md` に明記する）

## テスト戦略

★ **機械が言えるのは「危険でないと言えない」ことだけである**（`spec` §1.4）。以下は必要条件であって十分条件ではない。

### 静的（`scripts/step4_selftest.py` — 標準ライブラリのみ・S4-D7）

- config と player の整合（粒子率下限・禁止帯・τ 下限・`EXPR_VERSION` 3 箇所一致）
- ★★ **層 0 の 2 実装防止（S4-D8）**: `step4.html` と `layer0.html` から
  **同名関数（`partialAmps` / `buildGraph` / `dbToLinDev` / `hannAmplitude` / `decimate` / `sincGain`）を
  抽出して正規化比較**し、**一致しなければ FAIL**
- 停止ボタン・音量スライダの実在（★ **Step 3 で silent pass を出した箇所なので厳密な id 一致で書く**）
- 外部リソース参照 0 件 / `alert(` 0 件 / `await ctx.resume()` の裸待ち 0 件
- ★ **meta 検査**: 各検査を壊して**赤くなること**を実測（`--selftest`）

### 動的（player 内・`OfflineAudioContext`）

| # | 何 | 判定 |
|---|---|---|
| A3 | 層 0 ＋ 層 2 合成の包絡 4 Hz と **側帯波 f0±4 Hz** | ≤ **−60 dB** |
| A4 | ★ **逆検査**（4 Hz 注入） | ★ **FAIL になること** |
| A5 | ★ **陽性対照**（層 2 密度変調の周波数） | ★ **検出されること**（−inf は測定死の証拠にしない） |
| A6 | 粒子率の実測（Worklet のカウンタ） | 既定 ≥ **100 grains/s** |
| — | ★ **下限を割ったプリセット**（50 / 20 / 8 grains/s）の変調スペクトル | ★ **判定しない。測って出す**（禁止帯に出るかを見る） |

⚠️★ **A6 を「設定値が 100 だから 100」で済ませない** —— **Worklet が実際に発した粒を数える。**

### 実時間（`browser-verification`）

- **B4** ★★★ 停止・音量が**実クリック**で効く（交渉不可・**未実測のまま先へ進まない**）
- **A7** 10 分連続でノード数・粒子率が一定（★ **オフラインレンダで代用しない**）

## 既存パターンとの整合性

- 凍結物は **JSON**、HTML は読むだけ（S3-D5）
- 実データは **`FileReader`** で渡す。★ **リポジトリに入る経路を作らない**（S3-D9）
- 検算は **Hann 窓 ＋ 線の位置**。窓なし DFT / 帯域 RMS を使わない（S0-D8）
- 出力は **repo の外**（既定 `../../../gse-layer0-out`）
- ★ `run.sh check` が **`git check-ignore` で混入を毎回実測**（S0-D9）

## ロールバック計画

★ **本 Step は `experiments/` 配下の新規ディレクトリと `docs/glossary.md` しか触らない**ので、
ディレクトリごと削除すれば戻る。唯一の例外は **`EXPR_VERSION` の bump（S4-D3）**で、
これは **3 ファイル（`expr_smooth.py` / `layer0.config.json` / Step 3 の `env.md`・`notes.md`）を
元の `0.2.0-step3` に戻す**だけで済む。★ **GSE 本体は 1 行も変えないので、製品側のロールバックは不要。**
