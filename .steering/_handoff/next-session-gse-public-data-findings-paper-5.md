# 引き継ぎ —— 公開データの知見の論文（5）: 判断 18 の直し・空回し・予行・round 6

> 作成: 2026-11-06（Mac のセッション）。このメモを一次資料にしない。決めたことの一次は `.steering/20261105-public-data-findings-paper/decisions.md`（判断 1〜18）、草案は `paper-write/prereg-draft.md`（v6・036fbd92）、査読の記録は `attack-me/prereg-paper1/round-1〜5/`、計算は `experiments/20261105-findings-paper1-prefreeze/`（条件 conditions〜conditions-4.md・notes.md）。

## 0 入口の文

```
/Users/johnd/GSE-prototype-public-findings/.steering/_handoff/next-session-gse-public-data-findings-paper-5.md を読んで、公開データの知見の論文の続きをして。§2 の順で。
```

作業の場所: worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`。push はまだ（研究者の手元で）。コミットの前に `git branch --show-current` を見る。

## 1 前のセッションで済んだこと（2026-11-05〜06）

- 判断 14〜18。草案は v5 → v6（構成の組み直し・編集者の役 E の指摘）。attack-me round 4・5（どちらも major。査読者は round 4・5 とも minor 3。major は編集者 E と条件つきの指摘による）。編集者の役 E は round 4 から（研究者の指示・prereg でも置く）。
- 確認のスクリプト `confirm_p1.py`: H3 の欠測を残す・対照と停滞の両方に条件 A・ε = 0.001 と 0・H2 の R の下限と 5% の上限・H2 の除外を全ての長い休止に・学習の失敗の上限・感度（P9）・境界の近くの較正・床の割合と床にない対・H3 の門（埋め込みの回収・揺らぎで同値を崩す・届いた AUC の検算）。/cross-review を 2 回（c5fc89d0 まで・cec6c31b まで）当てて全部直した。
- replay の感度の中間（q = 0.995・W = 15・60 秒）: `rebuild_onsets.py`・`build-variants.sh`。見た書き手の分は `~/gse-public-data/cs1/work2019_{q995,w15,w60}`（陽性対照 1,078 課題すべて一致）。
- 取り置きの手順 `run-confirm-holdout.sh`: manifest（`make-manifest.sh`・草案も含む・manifest の値は OSF の欄にだけ書く）・開始・完走・中断の自動コミット・完走か結果のファイルのコミットがあれば止める・書き手の数の照合。独立の clone で見た書き手 40 人の仮の取り置きで予行（20.5 分・全段通過・中断の道で bash 3.2 の欠陥を見つけて直した 29979262）。
- 計算 4 の最後の空回し（ddfbf6d9）: 照合は全て通過・判定の値は出していない。数は草案の付録 C・D。床（`p_stuck` < 0.02）は主の層の停滞の 58%・対照の 62%。揃えない窓の対照は見た書き手で 2 学習器とも通らない。較正は境界で 0.2〜1.6%。
- 環境: `~/gse-public-data/venv-findings1`・`OMP_NUM_THREADS=1` が門。見た書き手の空回しは `SKIP_VARIANTS=1 bash experiments/20261105-findings-paper1-prefreeze/run-confirm-seen.sh`（約 60 分）。

## 2 次にやること（順に）

1. 判断 18 の 3 点をスクリプト・手順・草案に入れる。
   - 正の順位: 判定は最初の完走の値で固定。出し直した値は並べるだけ・分岐が割れたら保留・食い違いは全部報告・文書が明示しない細部はコードが定める（草案の冒頭を 1 文にして詳細は P11 へ）。
   - H3 を記述に（P0 の表・P1・P8・P10・外枠 C1）。`h3_summary` の `H3_supported` と branch を記述の名前に。
   - 取り置きの手順を 2 段に: 1 段目は照合と開始のコミットまでで止まる。研究者が start.json を OSF に添えて時刻を刻んだら、2 段目（計算）を回す（2 段目は start.json がコミット済みで、OSF の添付の URL を引数に取る形など）。完走の結果も OSF に添える。予行の clone で 2 段の道を確かめる（⚠️ 必ず仮の取り置きに書き換えた clone で）。
2. 既定の直し（判断 18 の「既定で直すこと」の全部）。コードに触れるもの: 床にない対を始点で選ぶ版（主の感度）と終点の版・較正に復元抽出の版・H2 の負例から「停滞と数えなかった長い休止の手前の窓」を除く感度とその窓の数・課題の中だけの比べと書き手均等の重みの感度・休止の中の出来事（層の窓を休止の終わりまで取った版と同じ集合の割合）と休止の中の押下の数の報告・`in_stall` の語は草案をコードに合わせる・門の揺らぎの鍵に書き手の番号・スクリプトの注記を v6 の節番号と語に。selftest を足す。
3. /cross-review（前回の cec6c31b 以降の diff）→ 直す。
4. 条件を先にコミットしてから、見た書き手の空回しをやり直す（`conditions-5.md`）→ 付録 C を更新 → 予行（2 段の手順）。
5. 草案 v7: E と監査役の本文の指摘（推定器と信号の定義・H1 × H2 の組・H2 の言明・H1 の分岐が割れたときの優先順位・英語版を正とすること・内部参照の残り・幅の錨と貢献の前提の根拠・用語）と外枠の直し。
6. attack-me round 6（同じ立場・同じ接地・E を含む・Codex は既知の未決を更新して添える）。⚠️ 判定の推移は major × 5（査読者は minor 3 が 2 回続いた）。Skill の Step 5 の基準で回す前に研究者に聞く。minor が 2 回続くか accept なら、英語版を作って OSF で凍結（研究者の手元）→ 2 段の手順で 1 回だけ。
7. C2 の揃えない比べを記述のデータ（KLiCKe・CoAuthor・CS1 2021 年版）で回す手順を、凍結の前に決めて登録の外の探索として書く（監査役 1-4）。

## 3 未決・注意

- 判定の値（CS1 の見た書き手の点推定・区間の位置・分岐・R・書き手ごとの AUC・ずらしの量）をファイルにも返答にも出さない。試しの走りは `CONFIRM_SMOKE` で実験の dir の外へ。取り置きの手順の試しは必ず仮の取り置きに書き換えた独立の clone で（同じ repo の worktree は不可）。
- 外部の LLM（Codex を含む）に書き手ごとの値を送らない。Codex の入力は草案の全文と既知の未決（`round-5/tmp/codex-input.md` の型）。
- 中間: KLiCKe `~/gse-public-data/klicke/work`・CS1 `~/gse-public-data/cs1/work2019` と `_q995`・`_w15`・`_w60`。計算が済むまで消さない。空きは約 14 GB。
- 返答・問い・記録は日本語で。記号を多用しない。push は研究者の手元で。docs だけの PR は `[skip ci]`。
