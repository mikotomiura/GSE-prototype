# 次のセッション —— 公開データの知見の論文 1: 草稿の前の計数と草稿

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-8.md` の §2 の 1 と 2 は済んだ。

## §1 状態

- 少ないクラスタの被覆の文献: 済み（判断 30・[V465] MacKinnon・Nielsen・Webb 2023、arXiv 版で逐語照合・f611db9f）。Field & Welsh 2007（[V464]・抄録だけ）・MacKinnon & Webb 2017 の本文は未取得（方向〔過小被覆〕を言うなら要る。Chrome か RePEc の working paper 版）。
- attack-me outline: round 4（major・査読者 3 人 minor・判断 31）→ round 5（major・査読者 3 人と Codex は minor・止め手は編集者の役だけ）→ 研究者の判断で閉じた（判断 32）。推移は round 1〜5 すべて major（E が毎回「直してから回す」）。記録は `attack-me/outline-paper1/round-1〜5/`（tmp/ は消した）。
- 外枠: v6（`paper-write/outline.md`・6d1944e3）。題の案 2 つ・語の対応（Stuck 状態とラベルの停滞を分ける・推定量の定義）・限定と桁の置き場の規則が冒頭と末尾にある。
- 私の誤り 2 つ（判断 32）: v5 で抄録から較正の括弧を外した（事前登録 P0 に反する・戻した）／round 1 から「作文の打鍵で学んだ推定器」と書いていたが、HMM 0.5.0 の係数は手で定めた値（`engine.rs` の `// TUNE:`・`heads/writing.rs:83`）。

## §2 やること（この順）

1. **草稿の前の計数**（[探索・取り置き]・判断 32）: (a) CS1 の取り置きで、編集の出来事のうち複数の文字の挿入（補完・貼り付け・自動のインデント）と範囲の削除が占める割合（3 節の写し方の小表）、(b) 取り置きの全時間での 2 つの信号の床の割合と分散・u の後の値（計器が CS1 の入力で動いていることの記述）、(c) 休止の位置の 3 区分の実効の書き手（S7・`explore_position.json` に鍵が無い）。どれも判定に使わない。X8 と同じく、条件を `experiments/20261106-findings-paper1-exploration/conditions.md` に先にコミットしてから回す。取り置きの手順は完走で止まっている（再実行しない）。
2. **草稿**（英語・MacTeX・7,000 語・補足 S1〜S9 は参考文献の後の付録）。paper-write の Step 2〜6。外枠 v6 の規則（語の対応・限定の置き場・桁）に従う。抄録と序論の第 1 文は較正の括弧つき（P0）。
3. **草稿の attack-me（manuscript）**: 外枠の段で残った編集者の役の論点（期待の根拠・一般性の柱）は散文で見る。同じ panel・Codex あり（既知の未決の一覧は round 5 の 16 件を引き継ぐ。11 番は「分岐 4〔その他〕」に直した版）。

## §3 気をつけること

- 凍結した文書と manifest のファイルを書き換えない。直す前に事前登録（英語版が正）の全文を同じ語で grep する（P0 の「抄録でも落とさない」を見落とした）。
- 外枠・草稿に推論を書くときは、結果の JSON（`results_holdout/confirm_holdout.json` の `sensitivity`）に値がないかを先に grep する。
- 推定器の係数を「学んだ」と書かない（手で定めた値）。推定器の状態は「Stuck 状態」、ラベルは「停滞」。
- 書き手ごとの値を repo に出さない・外部の LLM に送らない。Codex に送るのは本文（集計の値だけ）と既知の未決。
- 推定器・gse-replay・変換の公開の場所と、推定の行（u と u − 30 秒の 2 信号・対の id）を元のデータの利用条件の上で出せるかは、研究者が草稿の後・投稿の前に決める（投稿の条件・判断 31）。
- `.codex/budget.json` は台帳で、未ステージのまま（巻き戻さない）。
