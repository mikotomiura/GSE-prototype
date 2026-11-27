# 次のセッション: 段 1 の解析の script を書き、attack-me を通して事前登録を凍結する（A-1 の残り）

作成: 2026-11-27（まとめの引き継ぎ `.steering/_handoff/next-session-gse-integrated-before-freeze-then-slides.md` の「全体の修正計画」の 3）。worktree `/Users/johnd/GSE-prototype-prereg-values`・枝 `docs/stage1-prereg-values-and-stop-rule`（push 済み・PR 未作成）。

## 前提（このセッションの外で進むもの）

- カードの枝（K1・作業の説明・作業は Q2 を先に・同意文書の承認）は PR #441、データの repo の schema の写しは gse-dataset #13。main に入ったかを fetch して確かめる（tasklist の 2 行）。
- G-GEAR: Windows のポインタの直しとカードの確かめ（カードの枝の `.steering/_handoff/next-session-ggear-s1-n3-windows-before-start.md`）。凍結を待たない。
- 正本のフォームは、カードの枝が main に入り、3 名の配布物のフォルダ（`S1_APP_DOWNLOAD_URL`）が決まってから作る（配る前の条件 2・13）。

## やること（順に）

1. **§2 の空欄を埋める**（凍結の条件 3）: S1-F8 の項目の文と配分が未定。研究者が 11-27 に承認した同意文書は「日の終わりの問いは動機づけの 1 問だけ・手跡の日に項目を足さない・足すときは同意を取り直す」（配る前の条件 7）なので、その形で決めるかを研究者に聞く。S1-F3 の比べの量（後期の後で決める部分）は空欄の扱いを確かめる。
2. **E1 連結**（S1-E7・判断 33）の実装の形を決め、検査で固める。
3. **解析の script**（凍結のコミットに含める）。tasklist の未了の行をすべて。主なもの:
   - カードの区間の操作を落としてから C1・C2 を検出する（S1-B3・判断 21）。「表示の直前まで手が動いていた」印（判断 59）。
   - S1-A3 の広げた定義（(i)〜(iii)・欠測・両端・(i)〜(iii) の件数・判断 38 の定義の感度・閾値の格子と各組での下限・判断 62・63）。作業は Q2 → Q1 の順で、q1 の無い q2 の行がある（ADR-057 補訂 2）。
   - H1（人ごと・SD 0 は上端と下端を Wilson・判断 61・65）、H2・H3（3 名を合わせ、人を固定して人ごとに日を巡回で引く・前期を終えた人だけ・2 名未満は判定不能・下限は H3 が両クラス 10、H2 が合計 10 かつ C1・C2 それぞれ 5・H2 の重なりは支持・S1-A7 の 1 人の発動での出し直し・判断 64・65）。前期だけ（判断 47）。
   - S1-A4 の 30 秒の感度（判断 59）・S1-B6 の推定（模擬で取り戻せることを確かめてから）・S1-E8 の副の比べ（リズム 2 量・並べ替えの帰無 200 回・判断 60）・G1 の 3 段の開け方（判断 50）。
   - 模擬の部品は `experiments/20261127-stage1-required-stuck-rate/scripts/`（判定の写し・`/cross-review` 済み）と `experiments/20261121-stage1-stop-rule/scripts/stoprule.py`。判定の関数は 1 か所にまとめ、模擬と解析で同じものを使う。
   - 合成の記録で陽性対照と変異（守りの関数を差し替えて赤になるか・memory の guard-test-must-stub-guarded-action）。本人の記録で回すのは件数の確かめだけ（中身を出さない）。
4. **attack-me**（Codex を加える・凍結の条件 4）。Codex には事前登録の本文を渡してよいかを先に確かめる（本人の記録の集計を含む節がある。送れない節は除くか、研究者に聞く）。判定の推移を見て回し続けない（memory の feedback-attack-me-stop-when-minor）。既知の未決は Codex に渡す（feedback-codex-gets-known-open-items）。
5. **凍結**: 3 名の C4 を開く前に凍結のコミットを記す（§0 の 5）。push と PR は研究者に確かめる。

## 決めてあること（読み直す先）

- 判断 59〜65（`.steering/20261121-stage1-prereg-values-and-stop-rule/decisions.md`）。§3 の 8・9 の見込み（H2 はほぼ判定不能・H3 は真の AUC 0.5 付近で詰まりの率 0.10 ほどなら出る・S1-E3・E4 は段 1 では出ない）。

## 守ること

- 本人の記録の中身・個々の申告・日ごとの割付を出力しない。記録の集計を Codex に送らない。
- 段 1 の途中で HMM を手で動かさない（ADR-044 D1）。gse-next（`~/Desktop/S1_実施用_macOS/`）を止めない。
- 決めることは AskUserQuestion で、日本語で、推奨と理由を添えて聞く。
