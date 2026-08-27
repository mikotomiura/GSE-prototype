# tasklist — 摩擦操作サーヴェイ 第 2 ラウンド

## Step 0–1: ラウンドの確定
- [x] `git fetch` してから作業ブランチの状態を確認（★ 古い main から切っていないこと）
- [x] `origin/main` が `docs/references.md` / `docs/literature/` を触っていないことを確認（採番競合なし）
- [x] 採番の機械検算（★ `[P134]` / `[V87]` まで使用済み → 次は P135 / V88）
- [x] 下位問い R1–R4 と gate 基準を handoff からそのまま採る（★ 議論し直さない）

## Step 2: 多角探索（★ subagent 5 並列）
- [x] R1（[P133] 一次全文 ＋ MDC 系譜）
- [x] R2（時間圧下の writing）
- [x] R3（課題文の難易度 norming）
- [x] R4（方向性のある操作チェック）
- [x] **反証専任**（★ 対称性の担保）
- [x] 追加: [P135] Rong & Révész の一次全文取得専任

## Step 3: claim 抽出（★ メイン）
- [x] gate を動かす claim だけに絞る（4 件）

## Step 4: 敵対的検証（★ 1 claim × 3 票 = 12 票）
- [x] D パネル（R3 標準手続き）→ **3-0 refuted**
- [x] E パネル（R4 逆転検出）→ **3-0 refuted**
- [x] F パネル（封印の決着）→ **3-0 refuted**
- [x] G パネル（R1 の中心命題）→ **3-0 refuted**
- [x] ★ 判定を左右する逐語・数値をメインが一次で照合し直す

## Step 5–8: 生成・登録・還元
- [x] カード生成（10 カード）
- [x] `references.md` へ append-only 登録（`[P135]`–`[P143]` / `[V88]`–`[V105]`）
- [x] ⚠️ `[P142]` の二重登録を tombstone で是正し、`[P36]` へ追記
- [x] `_index.md` へ 1 行追記
- [x] `research-positioning.md §8` へ還元（プローブ反応性の精緻化）
- [x] `notes.md §15` へ実験側の結論と第 18 版の議題を起票
- [x] `python3 scripts/check_citations.py` → **違反なし**

## Step 9: Grill Me（自己点検）
- [x] 反証 angle を含めたか（★ 専任 subagent 1 ＋ 各パネルが refuted 側に倒す設計）
- [x] 下位問いごとに温度が分かれているか（R1 = PLAUSIBLE BUT UNPROVEN / R2 = 判定不能 / R3・R4 = 確定）
- [x] `判定不能` を「弱い支持」に丸めていないか（★ R2 は 2 ラウンド連続で `判定不能` と書いた）
- [x] 否決リストを残したか（7 件）
- [x] 全カードの `[n]` が `references.md` に実在するか（★ 機械検算で確認）
- [x] provisional と active を取り違えていないか（★ provisional 5 件を明記）
- [x] `_index.md` の「やり残し」が次ラウンドの入口になっているか（9 件）
- [x] ⚠️ **自分の誤りを隠していないか**（★ `notes.md §15-7` に 4 件記録）

## 残（★ 研究者の判断・別セッション）
- [ ] ⚠️ **`git rebase` と `git push`**（★ 環境ゲートで dev からは実行できない）
- [ ] `preregistration.md` 第 18 版の改訂（★ 研究者の行為）
- [ ] `produced_chars` の回収（★ 次回実施時の最優先）
