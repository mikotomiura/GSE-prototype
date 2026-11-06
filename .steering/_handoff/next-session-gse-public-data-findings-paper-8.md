# 次のセッション —— 公開データの知見の論文 1: 外枠の attack-me round 4・草稿

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-7.md` の §2 の 1 と 2 は済んだ（2 は round 2・3 まで）。

## §1 状態

- 関連研究の文献のラウンド: 済み（判断 26・`docs/literature/20261106-public-data-findings-related-work.md`・[V427]〜[V464]・commit 2696cc33。位置の記述は判断 27 で訂正済み）。
- 休止の位置の探索 X8: 済み（判断 27・`experiments/20261106-findings-paper1-exploration/` の conditions.md X8・notes.md・`results/explore_position.json`・df14c58d）。3 区分で揃えても 0.490・0.488、位置の偏りは約 3 ポイント。
- 外枠: v4（判断 29・`paper-write/outline.md`）。貢献は C1（事前登録した同等の確認）の 1 つ。較正（最大 5.2%）は評価の設計・限界・考察の事例に下げた。
- attack-me outline の推移: round 1 major（判断 25）→ round 2 major（査読者 3 人 minor・E 直してから・判断 28）→ round 3 major（R1・R3 minor・R2 major・E 直してから・指摘は C2 に収束・判断 29）。記録は `attack-me/outline-paper1/round-1〜3/`。

## §2 やること（この順）

1. **草稿の前の文献 1〜2 本**: 少ないクラスタで群単位の再標本（cluster bootstrap）の区間が過小被覆になることの方法論の文献（考察の較正の段落と関連研究の柱 3 で引く）。サブエージェントに探させ、メインが一次で照合し citation-ssot で登録（V465 から。他の枝で V465 以上が使われていないか先に確かめる）。
2. **attack-me outline round 4**（同じ panel・同じ接地。本文は round-3/tmp/sources/ から写す）。役ごとの引き継ぎ（round 3 の各役の指摘と v4 の対応）と、Codex に既知の未決の一覧（round 3 の 14 件＋「C2 は貢献から外し手順と限界へ」）を添える。round 3 の R3 は「C2 を手順と限界に下げるなら再査読は要らない」と書いた。E が「査読に回す」になれば minor 以下。Step 5: major なら直してもう 1 回、minor が 2 回続いたら閉じる。推移が major のまま続くなら、次の round の前に研究者に問う。
3. **草稿**（英語・MacTeX・7,000 語・補足 S1〜S9 は参考文献の後の付録）。paper-write の Step 2〜6。

## §3 気をつけること

- 凍結した文書と manifest のファイルを書き換えない。取り置きの手順は完走で止まっている（再実行しない）。X8 のような取り置きの上の探索は、条件を先にコミットしてから回し、[探索・取り置き] の印で書く。
- 外枠に推論を書くときは、結果の JSON（`results_holdout/confirm_holdout.json` の `sensitivity`）にすでに値がないかを先に grep する（round 3 で、休止の中に出来事を含む停滞を除いた感度 `layer_until_resume` の値を見落とし、推論を事実の形で書いた）。
- 書き手ごとの値を repo に出さない・外部の LLM に送らない。Codex に送るのは外枠の全文（集計の値だけ）と既知の未決。
- 査読者・監査役の応答は tmp に置いて secrets-filter と絶対パスの検査を通してから記録に写す（round 1〜3 はメインが縮めて写した。逸脱として verdict に書いてある）。
- `.codex/budget.json` は台帳で、未ステージのまま（巻き戻さない）。
- 推定器と gse-replay の公開の場所は研究者が決める（投稿の条件）。
