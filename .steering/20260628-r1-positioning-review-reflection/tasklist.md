# タスクリスト

## 準備
- [x] requirement.md / design.md / decisions.md を読む
- [x] ground truth を読む（functional-design §3/4/7・glossary・preregistration・intervention(_eval).rs）
- [x] **★A-1 をユーザーと確定**→ 3 層 GT ラダー（L0 軸/L1 Stuck/L2 Need 判断性能）。コードは Edit せず docs に明示

## 反映（C=Physical Anchor は除外）
- [x] A-1: §0 層構造表＋§1/§5 で「C-index は L0 X/Y を検証、p_stuck(L1) は別」橋渡し・H-X1c 新設
- [x] A-2: §8「方法論的限界」新設（全 GT 主観・客観脳内 GT 不在・三角測量・軽減策）
- [x] B: H-X2 を探索的(heterogeneity)へ格下げ・cutoff 凍結明記＋L2 Need 判断性能(HIR/Precision/recall/sweep)明示
- [x] D: H-Y 交絡＋追加アウトカム＋軽減を §5/§8＋experiment-tracking
- [x] E: §4 差分に「本文非保存制約下の統合プロトタイプ＋前向き較正」を新規性核として明示
- [x] F: glossary 略語に MhD 登録（Stage1 HMM/Stage2 ロジ・L1/L2 注記）
- [x] G: GATE1 延期の整合（§5/§6/§8・experiment-tracking、X1 鎖は GATE2 起点）
- [x] H: C-index 0.65/0.55 を PreReg-4 事前登録値と明記
- [x] I: §2 依存主張から [P11] を外し [P4] のみ（P11/V6 は keystroke 検出文脈のみ）
- [x] J: [P15] を §2 概念引用から外し §5/§8 測定点（自己効力感 副指標）で引用
- [x] K: §1/§8 に真の Kill vs DataInsufficient/放棄 の区別を併記
- [x] L: [v0.4§0/§9]→[v0.4§0] 訂正・GATE1-3↔PreReg を glossary 登録

## 検証
- [x] 全 inline [Pn]/[Vn] が references.md に実在（grep 集合比較・orphan ゼロ）
- [x] overclaim 語ゼロ（grep・全て否定/自制文脈）
- [x] R1 docs 間の整合（research-positioning ↔ experiment-tracking ↔ references ↔ glossary）

## レビュー
- [x] code-reviewer による再レビュー → HIGH(§4 層取り違え)＋MED×2＋LOW×4 を全反映
- [x] /cross-review（Codex gpt-5.5・scoped diff・bash 経由）→ #1 headline 確証誤読・#2 p_stuck=likelihood・#3 兆候センシング過剰・#4 UserLabel 介入下汚染・#5 GATE1延期感度 を反映
- [x] HIGH 指摘への対応（両レビュアは「確証 L0 vs 探索 L1/L2」「p_stuck の帰属」で収束、全て修正済）

## 完了処理
- [x] design.md / decisions.md の最終化（判断5 追記済）
- [ ] git commit（`docs(research): R1 ポジショニングへレビュー指摘を反映 (Physical Anchor 除く)`）
- [ ] /finish-task

## 別タスク化（本タスク外・着手判断待ち）
- [ ] Windows overlay 透過バグ修正（index.html body 背景・start-screen/Vignette 背景・Win 実機確認）
- [ ] （任意）較正 CLI に p_stuck↔criterion 分析を追加（後段オフライン・収集不変）
