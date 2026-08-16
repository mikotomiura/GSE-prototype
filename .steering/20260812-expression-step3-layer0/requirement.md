# Step 3 — 層 0（基層）を鳴らす ＋ リアルタイム化

> 引き継ぎ: `.steering/_handoff/next-session-prompt-step3-layer0-realtime.md`
> 前提: Step 0（TD 往復の関門）PASS / Step 1（CSV 化）/ Step 2（平滑化）実装済み（commit `fcc06c8`）
> ★ **音も映像もまだ 1 つも出していない。本タスクが最初に「鳴らす」回である。**

## 背景

`media-expression-spec.md` §7 は表現層を Step 0→7 の順で作ると定めており、
**Step 3（層 0 だけを鳴らす・状態に応答させない）を飛ばすことを明示的に禁じている**——
「基層だけで耐えられるか」が確認できていない状態で状態応答を足すと、
**不快の原因が基層なのかマッピングなのか切り分けられなくなる**からである。

Step 2 までで「1Hz の目標値 → レンダレートで連続追従」という形は**数値としては**検証済み
（tau≥60 s・4 Hz 近傍 −63.5 dB・実データ 3 本で確認・S0-D7 / S0-D12 / verification-log §6.9）。
しかし **それが音として成立するかは 1 度も確かめていない。**

## ゴール

> **層 0（基層）を、研究者が実際に 10 分間聴ける形にして渡す。★ 状態には応答させない。**
> **併せて「1Hz の目標値 → レンダレートで連続追従」を、実際に音のパラメータへ通す。**

★ **判定するのは研究者の耳である。** エージェントは**候補を作って聴ける形にするところまで**。
**「機械検査が緑だから良い音だ」と言わない**（`verify-before-claiming`）。

## スコープ

### 含むもの

- **層 0 の実時間合成**（55–110 Hz 帯の持続音 ＋ 整数次倍音のみ / 非調和成分ゼロ / sharpness 低）
- **試聴媒体 = ローカル HTML + Web Audio**（grill で確定・S3-D1）
  - ★ **停止ボタン / 音量スライダ**を実装する（[P71] 要件 1 = 交渉不可）
- **候補の軸 3 つ**（grill で確定・S3-D2）: 基音 / 倍音の減衰則 / 超低速ゆらぎの有無
- **Step 3b**: 平滑化済み CSV（`expr_smooth.py` 出力）を、**聴こえない程度に**音のパラメータへ乗せる
- **Step 3c**: 研究者提供の Phase1 実データ 3 本（P010 / P011 / P013）で通す
- **`experiments/<YYYYMMDD>-<exp-name>/` を起こす**（Step 3 から `reproducibility-discipline` が義務）
- **機械検算**: 生成グラフそのものの変調スペクトルを Hann 窓 DFT で測り、4 Hz 近傍に乗っていないこと

### 含まないもの（★ 明示的に Out）

- ✗ **状態 → 音の本格的なマッピング**（層 1 うねり / 層 2 粒子 / 層 3 空間）→ **Step 4 以降**
- ✗ **MhD（推論層）の設計議論**（研究者指示・2026-08-11 から継続）。
  `p_stuck` / `ewma_x` / `ewma_y` は**入力として使うだけ**
- ✗ **GSE 本体（Rust / TS）の変更**、**OSC / WebSocket の実装**（D5・外部送信境界を増やさない）
- ✗ **凍結対象への変更**: `docs/preregistration-v0.3.md` / `engine.rs` / `probe_scheduler.rs` /
  `schema_dto.rs` / `App.tsx`
- ✗ **numpy / scipy / soundfile の追加**（層 0 には要らない。Step 4 / Step 6 で再検討）
- ✗ **左右デチューン（ステレオの広がり）** — grill で不採用。周期的な強弱＝ spec §2 の禁止事項
- ✗ **音の良し悪しの判定**（研究者の耳が判定する。エージェントは判定しない）
- ✗ **実データのコミット / 外部 LLM への送信**

## 受け入れ条件（★ Done は exit code / 観測可能条件で言う）

### DONE-A（エージェントが閉じられる = 機械で言える）

- [ ] **A1** 合成コアの selftest が **exit 0**、かつ ★ **「壊した状態で赤くなる」ことを実測**した
      （`verify-before-claiming` ルール 5b。§5 落とし穴 2 — このタスクで silent pass は 3 回出ている）
- [ ] **A2** HTML ページの**自己検査モード**が、**本番と同じ合成グラフ**を `OfflineAudioContext` で
      レンダリングし、Hann 窓 DFT で **3.995 / 4.0 / 4.005 Hz の値**を報告して基準内で **PASS**
      （★ 窓なし DFT を判定に使わない = S0-D8）
- [ ] **A3** 実データ 3 本（P010 / P011 / P013）の smoothed CSV が層 0 に通り、**exit 0**
- [ ] **A4** ★ **停止ボタン / 音量スライダが実際に効くことを Chrome で実測**した
      （`browser-verification`。「実装したから効くはず」と書かない）
- [ ] **A5** `experiments/<date>-<name>/` が規約一式を持つ
      （config / SEED / data.md / env.md / run.sh / results/ / notes.md・`EXPR_VERSION` 刻印）
- [ ] **A6** `scripts/repro.sh` 相当（`run.sh`）で **1 コマンド再現**できる
- [ ] **A7** 実データが **git に載っていない**ことを `git check-ignore` で実測確認

### DONE-B（研究者の耳が閉じる = エージェントは判定しない）

- [ ] **B1** 研究者が 10 分聴いて「ずっと鳴っていて気になるか」を答える
- [ ] **B2** 候補の中から採る軸を選ぶ（または「全部だめ」を返す）
- [ ] **B3** ★ **離席から復帰したとき「前の状態から続ける」か「無音から立ち上げる」か**を耳で決める
      （S0-D11 が未決として残した。実装は現在「値を持ち越す」側）

> ⚠️ **DONE-B が閉じないまま「Step 3 完了」と書かない。** Step 4 に進んでよいのは B が閉じてからである。

## Stop 条件（進めてはいけない合図）

- 層 0 が **10 分耐えられない**と研究者が判定した → **Step 4 に進まない。** 層 0 を作り直す
- 4 Hz 近傍のエネルギーが基準を超える → **原因を特定するまで止める**（平滑化の穴か合成側の穴か）
- 実データが git に載る / 外部へ出る経路が見つかった → **即停止**

## 関連ドキュメント

- `.steering/20260811-expression-prototype-step0/decisions.md`（**S0-D1〜S0-D14 = 実装の前提**）
- `.steering/20260811-impact-and-cognitive-core-map/media-expression-spec.md` §1 / §2 / §5
- `.steering/20260811-expression-prototype-step0/verification-log.md` §6.9（実データで分かったこと）
- `.steering/20260810-media-sound-modality-and-creative-tooling/decisions.md` **D21**（★ D13 より先に読む）
- `docs/literature/20260810-auditory-modality-and-aesthetic-sensitivity.md`
  （⚠️ **本編だけを引用しない。追補 2 が本編カード 4 を訂正している** —— ISE の条件は変化ではなく**分節**）
- `docs/experiment-tracking.md` / `reproducibility-discipline` skill

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 作るものの形は `media-expression-spec.md` §2（層 0 の仕様）と §7（順序）が既に確定させており、
  grill で残った 3 分岐（試聴媒体 / 候補の軸 / 試聴時間）も研究者が確定させた。
  **複数案が考えられる余地が設計上残っていない。** ★ 逆に **Step 4（層 2 粒子・系統 A/B の作り分け）は
  `/reimagine` の対象になりうる**（マッピングの案が複数ある）。
