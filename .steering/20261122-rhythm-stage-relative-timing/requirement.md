# 相対のタイミングの写像（案 D）の机上の検査

## 背景

- 案 D は「打ち方の全体の速さを割り引いた相対のタイミング（間隔の比など）を形に写せば、速さを写さず、状態も写さない」という仮説の上にある（`origin/docs/tangibility-design` の `.steering/20261015-tangibility-design/` 判断 14・17）。
- 背景のステージの机上の検査（6 回）では、打鍵 1 つずつの時刻から作ったテンポの秒ごとの揺れ（`r_absdiff`・`r_sd`）に、A_speed の要約を超える停滞の手がかりが残った（`.steering/20261017-rhythm-stage-summary/summary.md` §4・合成の world・探索的な読みを含む）。相対のタイミングはこの種の量なので、仮説の (b)（停滞と速さを写さないか）を検査する価値がある。
- 背景のステージの次の段は判断 8（`.steering/20261017-rhythm-stage-summary/decisions.md`）で決まった。そこでは入力の列 I・試作の写像 M・案 D・錨の 4 つを並べる案だったが、2026-10-17 の後に main で手跡が進んだ:
  - 手跡の漏れの机上の道具（ADR-051 D3・PR 4・`experiments/20261115-handmark-leak-desk/`）が main にあり、I の上限の問いと重なる。
  - ADR-056（2026-11-20 Accepted）で、手跡は打鍵の止まりを意図して返すことになり、M について「停滞を写すか」は漏れではなく仕様になった。
  - M の写し元は spike の `HandmarkStage.tsx` から main の `analysis/handmark/state.rs` に替わった。
  - 研究者は 2026-11-22 に、このタスクを案 D と `rank` だけで立てると決めた（判断 1）。
- 始める条件（引き継ぎ §0）は 2026-11-22 に一次で確かめた（判断 1）。

## ゴール

案 D の写像が、停滞と速さをどれだけ写すかを、背景のステージの world・攻撃者・陽性対照の上で、`rank` と `res=sec` の錨と並べて測る。設計（相対のタイミングの定義・world・比べる基準・合格の定義・段の数）は、どの結果（下見を含む）よりも前に固定する。

grill で決めた骨組み（decisions.md 判断 2〜8）:

- 主の問い: 案 D の写像は、打鍵の有無（モデル A）を超えて L300 の停滞を写すか。副: A_speed を超えて写すか。速さの要約が A に足す分（A_speed − A）を物差しとして並べる。
- world: `g(0.5)` と `f(2)` の 2 段（SEED は design で決める）。
- 候補: 案 D の 2 本（続きの中の間隔だけ・休止も含める。`a` と `r` はどちらも倍率に不変な相対の量・止まり方は hold）と、錨の 4 本（`S-raw-hold-sec`・`S-raw-hold-sub`・`S-rank-hold-sec`・`S-rank-hold-sub`）。
- 合否: 前の 6 回と同じ規則（上乗せの 95% 区間と 0.03 の幅・3 値と判定不能）を、基準 A と A_speed のそれぞれに当てる。ラベルは L300 だけ。
- 記述: 速さの写り方（窓の打鍵の数と、`f(2)` のセッションの倍率を D から当てる当てはまり・合否なし）。

検証できる終わりと止まり:

- 終わり: 2 段それぞれで、`run.sh` の下見 0・下見 1・スモーク・本番が終了コード 0 で終わり、`results/<段>/main/summary.json` に 6 本の候補の判定（基準 A・A_speed）があり、`selftest.py` が失敗 0・変異をすべて捕まえ、`check_notes.py` が notes の主表を一次の JSON と照らして通る。
- 止まり: 下見 0 で段が天井か `unmeasured` なら、その段は規則どおり先へ進まず、判定不能（`ceiling`）として書く（段を足したり動かしたりしない）。自己検査の失敗・計器の汚れ（`provenance.json` の `dirty`）・同じ seed の再実行での不一致のときは、本番へ進まない。

完了の形:

- 設計（design.md）が `/reimagine` と `/cross-review` 2 巡を経て、結果の前にコミットされている。
- 計器（実験の台本・自己検査・陽性対照）が `experiments/` に置かれ、再実行でバイト一致する。
- 固定した段を回し、notes.md に結果と読みが記録されている（読みは合成の world の上での結果として限定する）。

## スコープ

### 含むもの
- 案 D の写像の定義（元の引き継ぎ §3 の 2）と Python の実装
- 錨: `rank`（`rank` を速くするなら、出力が変わらないことを固定の前に確かめる）と、前の回の `res=sec` の候補
- 問い (a) 停滞を A_speed を超えて写すか（天井への手当てとしての速さの揺れの world `d(c)`・`h(c)`・`f(c)` の選び方を含む）と、A_speed を基準にしない問いを並べるか
- 問い (d) 速さの写り方（記述・合否なし）
- ~~`r` の側の陽性対照（PCr-level・PCr-var）を案 D に当てること~~ → 判断 9 で外した。代わりに、赤の候補で `a` と `r` の量を落とした変種を探索的に並べる
- 個人の再識別・個人ごとの読み手（元の §3 の 5・6）を入れるかの決定

### 含まないもの
- 入力の列 I（入力の契約）と試作の写像 M（手跡）の検査。I の上限は ADR-051 PR 4 の道具、M の止まりは ADR-056 が扱う
- 背景のステージの 6 回とまとめの入れ物・判定・notes・design の書き換え
- `src-tauri/`・EH3 のファイル・手跡の製品の写像
- Mac のブランチ（`docs/tangibility-design` ほか）の書き換え（G-GEAR では読むだけ）
- 照合の論文の worktree（`C:\GSE-wt-matching-prereg`）とその計算
- 実データ・NDJSON の生ログ（合成の列だけを使う）
- 人の段（注意を引く力・状態計として読むか・共存の感覚）
- 論文化（notes は方法の章や付録に再利用できる形で残す）

## 受け入れ条件

- [x] design.md の固定のコミットが、下見を含むどの結果のファイルより前にある（git log で確かめる）
- [x] `/reimagine` を設計の承認後に回し、採用案と理由を decisions.md に記録した
- [x] `/cross-review` 2 巡を固定の前に回した（パス限定・合成の列の生ログは送らない）
- [x] 計器の自己検査（陽性対照・陰性対照・変異）が緑で、変異が狙った検査で落ちることを確かめた
- [x] 同じ SEED での再実行で出力がバイト一致する（スモークで確かめた・本番は回し直していない・判断 17）
- [x] 計測の run の最中は push だけにし、PR を出していない
- [x] notes.md に結果・判定・読みを記録し、主表を一次の JSON と照らした

## 関連ドキュメント

- 引き継ぎ: `C:\wt\rhythm-stage-speed-confound\.steering\_handoff\next-session-tangibility-relative-timing-desk-check-ggear.md`（2026-10-17）と、元の `origin/docs/tangibility-design:.steering/_handoff/next-session-tangibility-relative-timing-desk-check.md`（§3 の 0〜6）
- `.steering/20261017-rhythm-stage-summary/summary.md`・`decisions.md` 判断 8
- `experiments/20261015-rhythm-stage-speed-shape-world/`（計器の写し元の候補・PCr-level・PCr-var）
- `docs/experiment-tracking.md`・`reproducibility-discipline` Skill
- ADR-048・ADR-051・ADR-056（main）

## 運用メモ
- /reimagine 適用: Yes
- 理由: 相対のタイミングの定義・world・合格の定義・比べる基準は最良案が自明でなく、設計は結果より前に固定して後から直せないため（研究者 2026-11-22）
- 作業場所: worktree `C:\wt\rhythm-stage-relative-timing`・ブランチ `docs/rhythm-stage-relative-timing`（`origin/docs/rhythm-stage-summary` の 1cf9fcb9 から。背景のステージの 3 本が main に未 merge で、計器が最新の段にあるため）
