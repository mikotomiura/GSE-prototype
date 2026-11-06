# 次のセッション —— 公開データの知見の論文 1: 草稿の attack-me（manuscript round 1）の直し

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-9.md` の §2 の 1〜3 は済んだ。

## §1 状態

- 計数 X9: 済み（条件 bb4a3575 → 結果 b390fd32・判断 33）。
- 草稿 v1: `papers/public-data-findings/manuscript/`（18fd94f0・本文 6,262 語・要旨 277 語・25 頁）。ビルドは `bash build.sh <JEDM のテンプレート> <repo の外の出力>`（テンプレートの取り方は BUILD.md・前の scratchpad の写しは消えうる）。公開物の書き方の検査は `.steering/20260927-ime-observation-paper-eval-design/issues/_style_check.py --root . papers/public-data-findings`（違反 0）。7 語の繰り返しは `paper-write/ngram_check.py`。
- 推定器の呼び方: 「係数を手で定めた打鍵の状態推定器」（判断 33・直接入力の基準値は β_coding の改名で Dhakal 2018 の中央値を手で調整した値）。
- attack-me（manuscript）round 1: major（`attack-me/manuscript-paper1/round-1/verdict.md`・0d5b09bd）。研究者の採否は判断 34。

## §2 やること（この順）

1. **探索の条件を先にコミット**（`experiments/20261106-findings-paper1-exploration/conditions.md` に X10〜）:
   - X10 推定器の陽性対照: 見た書き手（CS1 2019 年版の 319 人）で、停滞の側の手前 30 秒の打鍵に既知の変化（打鍵の間隔を伸ばす・訂正を足す。量を数段）を入れて replay（`--features` まで）に通し、2 信号の識別の AUC が帯を越えて動くかを見る。取り置きは使わない。門と陽性対照・変異の確かめを決めてから回す。replay の回し直しは時間がかかる（1 本約 20 分の作り直しが前の例）。
   - X11 比べの表: 取り置きの同じ組で、推定器の 2 信号の差・水準と学習器 2 つ（確認の値を再利用できるか先に確かめる）の識別の AUC と、差の区間（書き手の再標本）。判定に使わない。
   - X12 停滞の実効の長さ: 取り置きの主の層の停滞で、u から onset（t0 − u）と u から再開（G(u)）の分布。合わせて較正の 500 回の引きの実効の書き手の分布が出せるか（凍結の前の計算の再走が要るなら研究者に聞く）。
2. **公開物**: 推定器の全係数の表（`engine.rs` の遷移・放出行列・初期確率・ヒステリシス、`heads/writing.rs` の基準値と軸の重み）を補足に。推定の行（u と u−30 秒の 2 信号・対の id）の書き出しと、CS1 の Dataverse の利用条件の確認（CC0 か）。評価のコードの置き場は研究者に聞く。
3. **本文の直し**（verdict.md の「直す順」・判断 34）: 題名と貢献の文を「帯の内側」の型に・抄録に下向きの 1 句と漏れの後の確認の 1 句・結論と考察を「u の時点の 30 秒の変化」に・停滞の平叙の定義・block の誤り・全組を数える定義と重み・"conservatively"→広め・"without change" の言い過ぎ・"opened once"→完走 1 回・確認の柱の理由（事前登録した取り置き）・序論の床の文を外す・但し書きを限界へ・E の細部を補足へ・S1 に OSF の時刻とローカルのコミットの並び（P11）・S5 に fold の分け方（P8 の逐語）・S9 の調べの手順・補足の数値 3 つ（5.3→5.2・4.6→4.5・0.504→0.503）・表 1 の Other の値・生成 AI の申告・見た書き手の人数の内訳・情動の検出の先行（文献のラウンドが要る・/literature-review かサブエージェント）。直したら語数を測り length-log へ。
4. **attack-me round 2**（同じ panel・Codex あり・既知の未決は round 1 の Codex に添えた 16 件の組み直し版を tmp から写し直す〔round-1/tmp/codex-input.md の冒頭〕。tmp は閉じるまで消さない）。

## §3 気をつけること

- 凍結した文書と manifest を書き換えない。事前登録の語（P0・P2 の conservatively・P10・P11）を論文で言い換えるときは S1 に 1 文。
- 推定器の係数を「学んだ」と書かない。書き手ごとの値を repo に出さない・外部の LLM に送らない。
- 取り置きは開いた後なので、取り置きでの新しい計算は [探索・取り置き]。条件を先にコミットしてから回す。
- `.codex/budget.json` は台帳で未ステージのまま（巻き戻さない）。
