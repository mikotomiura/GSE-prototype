# タスクリスト — Step 4（層 2 粒子 ＋ 混同テスト）

## 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-prompt-step4-layer2-grain.md` を読む
- [x] §1 の一次資料を順に読む（S3-D1〜16 / spec §1・§2・§3・§5・§9 / notes §0・§3.5・§5 / S0-D7・D8・D10・D11 / D21）
- [x] 必須 Skill を読む（`reproducibility-discipline` / `verify-before-claiming` / `browser-verification` / `grilling`）
- [x] `/start-task` → grill（研究者判断 4 件 ＋ 追加 3 件を確定）
- [x] `decisions.md` に S4-D1〜S4-D8 を記録
- [x] `docs/glossary.md` に用語 7 件を追加 ＋ ★ 層 0 の定義を S3-D12 の改訂に合わせて訂正

## 実装
- [x] `experiments/20260812-expression-step4-grain/` を新規に起こす（★ Step 3 を上書きしない）
- [x] `SEED` に**実際の seed** を書く（20260812 ＋ 案ごとの導出を明記）
- [x] `step4.config.json`（層 0 候補 / 層 2 / A・B・C 案 / 盲検 / 検算）
- [x] `player/grain-processor.js`（AudioWorklet・seed 固定・Hann 窓・ジッタ・粒数カウンタ）
- [x] `player/step4.html`（層 0 逐語複製 ＋ 層 2 ＋ 傾斜 ＋ 混同テスト ＋ 検算）
- [x] `scripts/step4_selftest.py`（静的 ＋ meta。★ 層 2 作り直しで 79 / 80 件へ）
- [x] `run.sh` / `env.md` / `data.md` / `notes.md`
- [x] ★ `EXPR_VERSION` を `0.3.0-step4` へ（S4-D3。Step 3 の config も追随）

## テスト
- [x] `step4_selftest.py` **79 ok / 0 fail**（層 2 作り直しの 13 件を追加。中断前の記載 58 は古い）
- [x] ★ meta 検査 **80 ok / 0 fail**（★ 追加分で silent pass を 2 件見つけ、検査側を直した）
- [x] `expr_smooth.py --selftest` **51 PASS / 0 FAIL**
- [x] ★ Step 3 の検査が bump 後も **30 ok / 0 fail**
- [x] `git check-ignore` で実データ混入 0 件
- [x] A3 変調スペクトル（4 Hz / 側帯波 f0±4 Hz が ≤ −60 dB）
- [x] ★ A4 逆検査（4 Hz 注入で **FAIL になること**）
- [x] ★ A5 陽性対照 2 系統（A 案の自律変異 / 層 2 ゲイン変調）
- [x] ★ A6 粒子率の実測（Worklet カウンタ・4 プリセット・誤差 <2%）
- [x] ★ 倍音傾斜の機構確認（B/C 案の前提）
- [x] ★ 盲検の出題順が seed で再現すること
- [x] ★★★ **B4: 停止・音量が実クリックで効くこと**（**交渉不可**）
      → **2026-08-12 実測で 4 条件すべて PASS**（`notes.md` §3.9。3 セッションぶりに解除）
      ⚠️ macOS / `file://` は未確認
- [ ] ⚠️ **A7: 10 分連続でノード数・メモリが増えないこと**（★ 2026-08-12 に測定中）
- [ ] ⚠️ **実データ（P010 等）を通す**（`run.sh data` 未実行）

## 耳（★ 研究者が判定する。エージェントは判定しない）
- [ ] **B4** 停止・音量（交渉不可・★ 真っ先に）
- [ ] **B5** 減衰則 3 種の聴き比べ
- [ ] **B6** 粒子率 100 / 50 / 20 / 8 —— ★ 下限割れが本当に分節して聞こえるか
- [ ] 見本モード（非盲検）で 2 種類の変化を聴き分ける
- [ ] ★★★ **B7 混同テスト**: A / B / C 案を盲検 10 回ずつ（★ 7/8 未満は落とす）
- [ ] **B8** 系統 A / 系統 B の聴き比べ
- [ ] **B3** 離席復帰 carry / restart（★ P010 でしか出ない・2 Step 持ち越し）
- [ ] **B9** 「芸術的親和性」の再判定（S3-D11 が先送りした問い）

## レビュー（★ S4-D1: 実施すると研究者が判断）
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] `/cross-review`（⚠️ **Codex には diff のみ。実データを含めない**）
- [ ] HIGH 指摘への対応

## ドキュメント
- [x] `docs/glossary.md` 更新
- [ ] ⚠️ `media-expression-spec.md` §9 の更新（★ **耳の結果が出てから**。先に書かない）
- [ ] `notes.md` に耳の結果を追記（★ 機械の結果と混ぜない）
- [ ] 次セッションの引き継ぎを `.steering/_handoff/` に作成

## 完了処理
- [ ] `/finish-task`
- [ ] git commit
