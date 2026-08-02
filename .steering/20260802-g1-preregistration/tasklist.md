# タスクリスト

## 事前確認
- [x] Phase1 の実態を確認（GATE2 pass / GATE3 **DataInsufficient**・Kill ではない）
- [x] G1 の既存設計を全読（README / config.json / notes.md / SEED / data.md / env.md / run.sh）
- [x] `notes.md` の未解決 5 件を洗い出し

## 先行プロトコル調査（未調査だった 1 件）
- [x] integrated vs independent writing task の系譜を確認 → **存在する**
- [x] [P43] Chan 2017（N=2・差あり）/ [P44] Michel et al. 2020（**N=60**・概ね差なし）を特定
- [x] **結果が一貫していない**ことを確認し、設計への帰結 3 点を導出

## 研究者判断
- [x] positive control（copy task）を入れる → **入れる・先頭と末尾に 1 本ずつ**
- [x] 被験者数 n → **5 名に凍結**

## 設計の改訂（すべて判定を厳しくする方向）
- [x] positive control の新設と解釈規約（✗ なら **G1 を無効**）
- [x] 位置固定による交絡を明記し **floor チェックに限定**（効果量を主張しない）
- [x] 負の結果の価値を**事前に**宣言（§3.7）
- [x] 産出量交絡の報告義務と解釈制限（`keys` 単独 AUC の descriptive 報告）
- [x] 強制比較の鎖を G1 8 ブロック内に閉じる（copy には聞かない・分母は異条件ペアのみ）
- [x] Fisher 統合を凍結（離散性による**保守化**を明記）
- [x] Tier 1 特徴量の定義を確定（帯域別の率は**採らない**理由つき）
- [x] optional stopping の明示的禁止

## 文書化
- [x] `preregistration.md` 作成（凍結）
- [x] `config.json` 更新（機械可読・本文書と一致）
- [x] `README.md` / `notes.md` / `SEED` を改訂に整合
- [x] `docs/references.md` に [P43] [P44] を append-only 登録
- [x] 文献カード `20260802-controlled-task-manipulation-prior-protocols.md` ＋ `_index.md` 1 行

## 検証
- [x] コード変更ゼロ・凍結対象に触れていない
- [x] `preregistration-v0.3.md` / `research-positioning.md §5` 未変更
- [x] 全 inline [n] が references.md に実在
- [x] `preregistration.md` と `config.json` の数値が一致（ブロック数 10 / n=5 / λ=1.0 / 0.70 / 0.60 / 80%）
- [ ] 実施前に残る作業 5 件（課題文・倫理・Tier0/1 実装・解析スクリプト・Phase1 凍結解除）
