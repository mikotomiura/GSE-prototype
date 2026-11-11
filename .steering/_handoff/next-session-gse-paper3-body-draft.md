# 引き継ぎ —— 論文 3（per-person learning）を外枠から本文へ

> 作成: 2026-11-11（Mac のセッション）。このメモを一次資料にしない。外枠は `papers/per-person-learning/manuscript/outline.md`（commit 9c2128d5）、判断は `.steering/20261111-gse-paper3-round3-computations/decisions.md`（判断 1〜13）と `.steering/20261107-gse-paper3-per-person-learning/decisions.md`（判断 1〜24）、査読の記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1〜7/`。

## 0 入口の文（次のセッションの最初に打ち込む）

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-body-draft.md を読んで論文 3 の続きを進めてください。最初に §2 の 1（目的と休止の集計のコードの /cross-review）、次に §2 の 2（Open items の一次の確かめ）、それから §2 の 3（paper-write で本文の草稿）です。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で聞いてください。
```

## 1 いまの状態（2026-11-11）

- 外枠の attack-me（stage outline）は round 7 で閉じた（判断 13）。判定は round 1〜7 すべて major だが、round 6・7 は査読者 R1〜R3 がそろって minor で、major は編集者の役 E の判定（Take-home の言い回し）による。研究者の選択で、メインの確かめで閉じ、本文の後に stage manuscript の attack-me を回す。
- 外枠の中心の主張（Take-home）: CoAuthor で 1 人ごとの 3 状態の HMM は同じ構造の弱い共通に k しだいで最大 0.19 nats/記号勝つが、両側を強い構造にすると利得の大部分が消える。構造と本人の縮みを他人で選ぶと、本人のデータの重みは k = 1〜12 で約 0.06〜0.8%（k = 15 で約 3%）で、当てはめはほぼ最頻値。15-session の残り（+4.1e-4〜+7.2e-4）は本人のデータを使わない平滑の少ない共通（最頻値）の利得と同じ大きさで、本人に帰せない。推奨は当てた手順（本人の連鎖・構造と本人の縮みを他人で選ぶ・検出の下限と平滑と記号化への依存を報告）に限り、平滑も他人で選ぶ・入れ子は評価していない拡張。
- 計算はすべて済み、notes がある: `experiments/20261110-per-person-sensitivity/`（CS1 の種の追加を含む）・`20261111-sensitivity-mode-decomposition/`（計算 1・分解は根拠に使わない）・`20261111-mode-in-selection/`（計算 3・HP Z2）・`20261111-objective-and-pause/`（目的を平均に替えた選び・休止の秒の割合・HP Z2）。HP Z2 で回す続きは無い。
- 枝は push 済み（9c2128d5）。`.codex/budget.json` は worktree では未コミットのまま（台帳は本線 `/Users/johnd/GSE-prototype/.codex/budget.json`・2026-11-11 は 260,463 / 2,400,000）。

## 2 次にやること（この順）

1. **/cross-review**（必須・まだ回していない）: `experiments/20261111-objective-and-pause/{conditions.md,SEED,run.sh,scripts/,.gitattributes}` の diff（8ea112c4〜eb764c9c）。Codex を加える（合成のコードと条件だけを渡す。results/・notes・pickle・記号は渡さない）。wrapper は本線から回す。前回の計算 1〜3 の /cross-review の採否は判断 8。
2. **Open items の一次の確かめ**（外枠の末尾）:
   - Uto et al. 2020（IJAIED 30(2):271–298・doi 10.1007/s40593-019-00189-9・[P270]）の評価の設計（同じ書き手の後のデータで予測するか・何と比べるか・学習者依存の母数の推定）。2026-11-11 は UEC のリポジトリ（uec.repo.nii.ac.jp/records/9675）が保守中で本文が取れなかった。窓（30 秒の枠・10 秒の歩み）は以前に本文で確かめてある。取れない URL は Chrome で。確かめたら Novelty の文を固める。
   - 離散の Markov-switching の系譜（double chain Markov model・MTD）の引用を一次で確かめて 2 章と 3.3 に（R1 の指摘）。
   - Liu & Meng: 接地に使った本文は arXiv 1510.08539v1。引く版を決めるか、2016 年版で逐語を照らす。
   - 元の記号の記録ごとのハッシュ（読者が公開の記号化を照らせるように）。実データが要るので、作るなら HP Z2 の引き継ぎを別に書く（研究者に問う）。
3. **本文の草稿**: `paper-write` Skill に従う（MacTeX・本文は簡潔に・細部は補足へ・直しは足すより移す）。投稿先は UMUAI（要旨 150〜250 語・キーワード 4〜6・Statements and Declarations・データの声明）。本文の予算 6,800 語、図表 4（Table 1・Figure 1・Figure 2・Table 2）。外枠の「Moved to the supplement」の列が補足の S1〜S15。数値はすべて notes と summary から引き、外枠の数を写すときも一次で照らす。
4. **本文の後**: `attack-me`（stage manuscript・Codex を加える・既知の未決の一覧を添える）。外枠の round 7 の verdict §9 の「残す」と、round 1〜7 の判定の推移を、引き継ぎと Step 5 の判断に使う。

## 3 守ること

- 実データ・書き手ごとの値・pickle・npz・NDJSON を開かない（集計値だけ）。外部の LLM（Codex を含む）に打鍵の内容・書き手ごとの値を送らない。
- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない。
- push と PR は研究者に確かめてから（PR は出さない方針・[skip ci]）。
- 返答は日本語。絵文字と記号を多用しない。報告を地の文の問いで終えない。

## 4 気をつけること（この 1 日で踏んだもの）

- 直しの文が次の round の指摘を生んだ（「検出の下限より下」「平滑が大部分を説明する」「could not have detected … of that size」）。埋めた差と返った量を同じ物差しで比べない。中央値の比べを配分として書かない。本文でも同じ。
- 書き直しで既存の結果を落とした（重ならない窓で hmm3 が連鎖に勝つ）。削るときは何を落とすかを確かめる。
- 本人 − 最頻値の正の数には +∞ の書き手（各セル 2 人）が入る。母数を書く。
- Windows（HP Z2）で書く JSON は改行を LF に固定する（`open(..., "w", newline="\n")`）。
