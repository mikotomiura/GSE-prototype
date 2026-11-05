# 引き継ぎ —— 公開データの知見の論文（4）: 判断 14 の直し・感度の全部の実装・空回し・round 4

> 作成: 2026-11-05（Mac のセッション）。このメモを一次資料にしない。決めたことの一次は `.steering/20261105-public-data-findings-paper/decisions.md`（判断 1〜14）、草案は `paper-write/prereg-draft.md`（v4・commit dad32265）、査読の記録は `attack-me/prereg-paper1/round-1〜3/`、計算は `experiments/20261105-findings-paper1-prefreeze/`。

## 0 入口の文

```
/Users/johnd/GSE-prototype-public-findings/.steering/_handoff/next-session-gse-public-data-findings-paper-4.md を読んで、公開データの知見の論文の続きをして。§2 の順で。
```

作業の場所: worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`。push はまだ（研究者の手元で）。コミットの前に `git branch --show-current` を見る。

## 1 前のセッションで済んだこと

- 凍結の前の計算 1（条件 529a32c3・結果 c04d4c7f）: 幅の換算と 146 人での精度の見積もり。⚠️ CS1 の見た 319 人の AUC の向きが出力に漏れた（notes の逸脱 1・草案 P0 に開示済み）。取り置きは未開封。
- attack-me round 2（major）→ 判断 13 → 確認の解析スクリプト `scripts/confirm_p1.py`（09f33230）と空回し（条件 6d26990c・`results/confirm_seen.json`・判定の値は出していない）→ 草案 v4（dad32265）。取り置きで 1 回だけ回す手順 `run-confirm-holdout.sh`（走らせていない）。
- attack-me round 3（major・査読者は R1 major・R2 minor・R3 minor・Codex major）→ 判断 14（7e73546d・562ffe87）。
- 環境: `~/gse-public-data/venv-findings1`（`requirements-confirm.txt`）。`OMP_NUM_THREADS=1` が門（無いと勾配ブースティングがスレッドを奪い合い 7 倍遅い）。319 人の空回しは約 8 分。
- 元のチェックアウトの attack-me と paper-reviewer の定義を main の版にそろえた（研究者の依頼・未コミット）。

## 2 次にやること（順に）

1. 判断 14 の 5 点と既定の直しをスクリプトに入れる（`confirm_p1.py`）。
   - H3 の欠測: 押下の数（u 以前 30 秒と、その前の 30 秒）を量に加え、取れない量は NaN（HGB）／訓練の分割の中で中央値の補完と欠測の印（LR）。除く版は感度。どちらの窓が欠けたかを数える。H3 の評価は対照の重複を 1 回に。
   - 対照にも u の (u − 30 秒, u] で条件 A が偽（`CondA.net(u) ≥ 1`）を課す。今の非対称は感度。
   - H1 の支持は ε = 0.001 と ε = 0 の両方で分岐 1。完全な同値は 0.5。
   - H2 の支持は揃えない AUC の下限 > 0.55 かつ R の下限 ≥ 0.5。
   - 学習の失敗率が 5% を超えたら判定できない。
   - selftest を足す（停滞の選び方・対照の除外と u < s・H2 の正例・退化の分岐）。
2. P8 の感度を全部入れる（判断 14 の 5・研究者は全部を選んだ）。
   - 今の中間でできる: 先読み 30・120 秒／t0 基準の正例／対照の上限 10・60 秒／区切りを空白・記号に／ε = 0／層の窓を休止の終わりまで／非対称の u < s／H3 の除く版／信号の差の窓（d_ の 30 秒）15・60 秒（⚠️ P8 の「窓の長さ」がどちらの窓かを先に確かめる。停滞の定義の W なら replay の回し直し）／正例を持てた割合・書き手ごとの AUC の分布／バーストの閾値を θ の倍数に／P6 の格子の調整（入れ子の交差検証）。
   - replay を回し直す: q = 0.995（`gse-replay --features --set q=0.995`。⚠️ 固定したバイナリ SHA 26cae610… で `--set` が効くかを先に確かめる）／CS1 の θ を課題をまたいで累積した版（書き手の課題を時刻順につないで `--features` に通す build の変種）。中間は repo の外に別名で置く。Mac の空きを先に確かめる（11-05 に 13 GB）。
   - 感度は見た 319 人の空回しでは件数だけを出し、値は出さない（今の seen の規則と同じ）。
3. 取り置きの手順を直す（`run-confirm-holdout.sh`）: build_cs1.py・analyze_item2.py・analyze_cs1.py・自身の SHA-256 の照合、build も `$PY` で走らせる、Python の版の照合、作業ツリーがきれいか、開始の前に SHA と時刻をコミットする（1 回だけの記録）、途中の失敗の扱い（P10）。
4. 条件を先にコミットしてから、空回しをやり直す（`conditions-3.md`）。スクリプトの SHA-256 が変わるので、草案 P2 と手順の照合の値を書き換える。
5. 草案 v5: 判断 14 の全部（verdict の「直す順」）。漏れた値の定義の注記・KLiCKe の値の呼び方（K6 の推定量 0.515・0.521 と登録の推定量 0.511・0.517 を分ける）・CoAuthor の停滞の範囲 0.49〜0.50・換算の言い方・正の順位・多重性・P9 の H3 の対象・境界の文。外枠: H3・H2 が崩れたときの主張。
6. attack-me round 4（同じ立場・同じ接地。round 1 の `tmp/sources/` を使う）。⚠️ 判定の推移は major × 3。Step 5 の基準で回す前に研究者に聞く。Codex を加えるかも聞き、既知の未決の一覧を添える（判断 13・14 で研究者が採らなかった案: 閾値の指標を確認に足す案）。
7. minor が 2 回続くか accept なら、OSF で凍結（研究者の手元）→ `run-confirm-holdout.sh <OSF の URL>` で 1 回だけ。

## 3 未決・注意

- 判定の値（CS1 の見た書き手の点推定・区間の位置・分岐・R・ずらしの量）をファイルにも返答にも出さない。試しの走りは `CONFIRM_SMOKE` で実験の dir の外へ。
- 外部の LLM（Codex を含む）に書き手ごとの値を送らない。`~/gse-public-data` の書き手ごとの値は人が開かない。
- 中間: KLiCKe `~/gse-public-data/klicke/work`（展開済み・893 MB）、CS1 `~/gse-public-data/cs1/work2019`（464 MB）。計算が済むまで消さない。
- 依頼文はファイルを読ませる形で渡した（round 3）。paper-reviewer は `model: opus`。
- 返答・問い・記録は日本語で。記号を多用しない。push は研究者の手元で。docs だけの PR は `[skip ci]`。
