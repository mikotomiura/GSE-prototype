# gse-m5-s1-driver-ui —— M5 の 2 本目: 段 1 の駆動役と画面

## 背景

- プローブの配線 M5（ADR-031・design-map §4・R2）の計画は `.steering/20261105-gse-m5-probe-wiring-plan/`（design.md v2 ハイブリッド・decisions 判断 0〜10・tasklist の B1〜B7）。
- 研究者の判断で 3 本の PR に分けた（`.steering/20261106-gse-m5-s1-core/decisions.md` 判断 1）。1 本目（B1〜B3: 段 1 の層 `s1.rs`・純粋な調停器 `analysis/probe_arbiter.rs`・行種と schema）は PR #390 で main に入った（2026-11-06・`e067f4bc`）。
- 1 本目の後も、調停器と行種はあるが送出元が無い。本タスクはその 2 本目で、調停器を 1 秒ごとに回す駆動役と、問いの画面を作る。

## ゴール

段 1 の印 `s1.mode` と本人の同意の印があるとき、O1 の記録の上で無作為・層化のプローブと日の終わりの問いが画面に出て、答え・未回答・差し替え・抑制・枠が行として NDJSON に残る。印が無い O1 の挙動と記録は変わらない。

## スコープ

### 含むもの（計画の tasklist の B4・B5 と、1 本目の引き継ぎ §2 の約束）

- B4: 今のプローブのスレッドを段 1 で起こさない・段 1 の駆動スレッド（起点 `O1_LOG_OPENED_MS`・世代 `S1_FRAME_GEN`・`probe_frame` の出し直し・`GSE_DISABLE_PROBES` は見ない）・押下とフォーカスの遷移の入力・電源の通知・`s1_day_state.rs`・コマンド（`record_probe_response`・`record_probe_skip`・`record_day_question`・`get_s1_mode`・`acknowledge_s1_probe_consent`・同意の取り消し）・overlay を段 1 で `show()`・トレイの終了の補助・一時停止の再開の予約。
- B5: `ProbeCard.tsx`（6 択・3 問を 1 枚）・`DayQuestionCard.tsx`・`Overlay.tsx` の排他・`App.tsx` の `get_s1_mode`・登録の画面の同意と取り消しの項目・画面の確かめ。
- 引き継ぎ §2 の 1〜8（capabilities の `emitterless` → `config_gated` と検査の削除・起動ログの文・6 択の門の引数と本文の検査・`TickInput` の作り方と JST/UTC の検査・`in_eod_window` の写し・`superseded` の書き方・security-checker の LOW 2 件・日の問いのカードの `card_id` の契約）。

### 含まないもの

- 3 本目（B6・B7）: `gse-replay --probes`・`--day-questions`・段 1 の配布の門と launcher・文書・R3（gse-dataset の schema の同期・引き継ぎ §2 の 9）。
- 回答率の集計で `superseded` を分けること（引き継ぎ §2 の 10・3 本目の `--probes` で）。
- 仮の定数の確定（R6′）・同意文書（R4）。

## 受け入れ条件

- [ ] 引き継ぎ §2 の 1〜8 がそれぞれ実装または検査で満たされている（tasklist で項目ごとに照合）
- [ ] `capabilities::tests::activity_label_has_no_emitter_until_it_is_wired` を消し、4 行種が段 1 のときだけ `config_gated` に入る検査がある
- [ ] 6 択の送出元が `o1::is_o1()` を渡さないことを本文の検査で縛っている
- [ ] 駆動役の `local_day`・`local_minute` の計算に JST と UTC の両方の検査がある
- [ ] 印の無い O1 で、今のプローブのスレッド・overlay・行が変わらない（検査と既存のゴールデン）
- [ ] `cargo test --workspace`・`cargo clippy --all-targets -- -D warnings`・`cargo fmt --check`・`npx tsc --noEmit` が緑
- [ ] `emit_schema` の出力が `schema/current.json` と byte-equal
- [ ] 画面の確かめ（macOS は自分で AX と画面の取得）: 同意の前は出ない・カードが見える・押せる・背後のクリックを奪わない・一時停止の間は出ない・「答えずに終了」が 60 秒以内に終わる。Windows は CI と研究者の手
- [ ] `/finish-task`（`/cross-review` を含む・Codex に記録の本文を送らない）

## 関連ドキュメント

- `.steering/20261105-gse-m5-probe-wiring-plan/`（design.md・decisions.md・tasklist.md の B4・B5）
- `.steering/20261106-gse-m5-s1-core/`（design.md の「計画から変えた点」「実装中に変わった点」・decisions 判断 1〜13）
- `/Users/johnd/GSE-prototype-m5-core/.steering/_handoff/next-session-gse-m5-part2-driver-ui.md` §2
- ADR-031・ADR-043・ADR-048・ADR-013、`docs/architecture/gse-design-map.md` §4

## 運用メモ

- /reimagine 適用: Yes
- 理由: 研究者の選択（2026-11-07）。計画の段で /reimagine は済んでいるが、駆動役の組み方（スレッド・入力の集め方・カードの状態の持ち方）は計画では細部が無く、別案と比べる。
