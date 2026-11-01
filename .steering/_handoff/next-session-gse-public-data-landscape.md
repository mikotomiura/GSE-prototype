# 引き継ぎ — 今の位置づけを 1 枚にまとめ直し、公開データを記述だけで俯瞰する（合流の前）

> 作成: 2026-11-01（研究者の依頼）。T2（KLiCKe）を終えた後の相談で決めた。
> このメモを一次資料にしない。事実は一次で確かめ直す。

## 0 なぜやるか

- 項目 1（CoAuthor で AI の提案を求める手前）は、AI の要求を的にした古い問いで立てていた（`next-session-gse-three-parallel-tracks.md` §4 の「結果の読み方」）。古い基準で見る失敗を繰り返さないため、今の位置づけを先に固めてから公開データを見る。
- 合流（同 §4）で決めることは、招待の契機の中身と、主要アウトカム `receipt_free_resumption` を残すかどうか。この俯瞰はその 2 つの材料になる。

## 1 研究者が決めたこと（2026-11-01・AskUserQuestion）

1. 順番は、位置づけ → 俯瞰 → 合流。
2. 俯瞰に使うデータは KLiCKe・CoAuthor・CS1 の 3 つ。
3. T1（差し替えの口の実装）は並行して進める。契機の中身を決めずに作れる設計なので、俯瞰を待たない。
   - 訂正（2026-11-02）: 当初「T1 は未着手」と書いたが誤り。T1 の実装は `/Users/johnd/GSE-prototype-nudge-off`（ブランチ `feature/nudge-default-off`・未 push）で済んでいる。研究者から Loop で回すかを問われたが、実装が済んでいるので Loop にしない。残りは下の §6。

## 2 段 1: 今の位置づけを 1 枚にまとめ直す

- 一次の資料: `docs/research-positioning.md` §1 の 2026-10-31 改訂、ADR-040、`.steering/20261031-gse-small-n-research-design/decisions.md` の判断 10〜18、three-parallel-tracks §4。
- 研究者の指示で、`research-positioning.md` の後から変わったことがある。
  - 主要アウトカムは、合流で見直す（同 §4 の 4。`research-positioning.md` は「据え置く」のまま）。
  - GSE の目標は AI を的にしない。ふつうのデスクワークでの作業上の認知状態を見る。AI 疲労は別の研究（AF の系統）。
  - 「作業中の」ではなく「作業上の認知状態」と書く。
- 作るもの
  - 位置づけの要約。何を推定し、いつ何を差し出し、何を主張しないか。
  - GSE が見られる信号の一覧。打鍵の 5 特徴量、休止、停滞の始まり（`stall_onset`）、`friction_rising`、フォーカスの遷移、ポインタ、IME、貼り付けの文字数。それぞれについて、どの公開データで見られ、どれが O1 でしか見られないかを書く。
  - 俯瞰で見る問いの一覧。どの問いが合流の 1〜4 のどれの材料になるかを添える。
- 置き場は新しい `.steering/<日付>-gse-public-data-landscape/`。要約が `research-positioning.md` と食い違うところは、要約に書くだけにする。positioning の本文の改訂は合流の後の別タスクで行い、勝手に直さない。

## 3 段 2: 公開データを記述だけで俯瞰する

- 検定はしない。分布と傾向だけを見る。見る問いと集計の仕方は、計算の前に conditions.md に置いてコミットする（項目 2 の K1〜K7 と同じやり方）。
- 後で確かめに使えるよう、各データの一部（例えば書き手の 3 割）を種で固定して取っておき、見ない。
- データ
  - KLiCKe: 中間 `~/gse-public-data/klicke/work.tar.gz` が使える（`experiments/20261101-klicke-early-stall-trigger/`。θ と onset は replay と全件一致を確かめ済み）。
  - CoAuthor: `~/gse-public-data/coauthor/`（48 MB）。項目 1・案 A で使った。AI の提案を求める出来事の前後を除き、ふつうの書く区間として見直す。
  - CS1: AI が出る前のプログラミング（510 万打鍵・[V317] か [V340] の本文に公開があると書いてある）。まだ取っていない。利用条件・出来事の種類・大きさを先に確かめる。人口統計や ID を尋ねる調査票のファイルは取らない。
- 限界: どれも 1 つの文書の中の打鍵で、フォーカスの遷移・アプリをまたぐ作業・受領は無い。俯瞰で言えるのは打鍵と休止の層まで。デスクワーク全体は研究者本人の O1（T3 と同じ）でしか見られない。

## 4 守ること（three-parallel-tracks §2 を引き継ぐ）

- worktree を分ける。コミットの前に `git branch --show-current` を確かめる。T1 の worktree とファイルが重ならないようにする。
- docs と experiments だけなら、PR なし・`[skip ci]` の `--no-ff` マージで main へ入れてよい。差分にコードと CI の設定が無いことを確かめる。直前に fetch する。
- 打鍵の本文・NDJSON の生ログ・被験者のログは外部の LLM（Codex を含む）に送らない。repo に入れるのは集計だけ。書き手・参加者の ID を結果に出さない。
- KLiCKe の人口統計のファイルは取らない。Kaggle [V265] は KLiCKe 由来なので使わない。
- `docs/references.md` の [Vn] は append-only。
- ディスク: 2026-11-01 時点の空きは約 3.9 GB。3 GB を切ったら重い段を始めない。CS1 を取る前に大きさを確かめる。他のトラックの中間を消さない。
- 照合論文のトラック（`/Users/johnd/GSE-wt-matching-manuscript`）の成果物は読むだけ。

## 6 T1 の残り（このタスクと並行・一次は T1 の枝の引き継ぎ）

- 一次: T1 の枝にある `.steering/_handoff/next-session-gse-invitation-wiring.md`（main にはまだ無い）。記録は同じ枝の `.steering/20261031-nudge-default-off/` と `.steering/20261101-invitation-wiring/`。最後の検証は d83d0468 で `cargo test --workspace` 1054 passed・clippy 0・tsc 0・emit_schema byte-equal。
- 残り（この順）
  1. 実機の確かめ（研究者が押す。トレイの後から差し込む項目は AX から見えないため。手順は上の一次の §1 の 1）。
  2. `git fetch` し、origin/main を取り込む（T2・T3 と、このメモの後のコミット）。テストを回し直す。G-GEAR が空いているかを研究者に確かめてから push する（`feature/*` は self-hosted の CI が走る）。PR も研究者に確かめてから出す。
  3. gse-dataset の schema parity（`InvitationCondition` が増えた・同期は別作業）。
  4. push の時に `_handoff/README.md` の T1 の行を更新する。
- 合流に回すこと: 説明と設定の窓の文（`InvitationSettings.tsx`）が推定器の契機を前提にしている点、通常のモードの同意文書の扱い、契機の中身。
- ディスク: T1 の worktree のビルドの中間は 2.9 GB ある。テストを回し直すと増えるので、俯瞰の重い段と同じ時に回さない。空きが 3 GB を切ったら止める。

## 5 終わった後

- 結果を持って合流に入る（three-parallel-tracks §4）。合流の問いは AskUserQuestion で、推奨と理由を添えて日本語で聞く。
