# EH3 の凍結の前の準備（F-1 の見比べ → 肖像と招待の分け方の検査）

## 背景

- 引き継ぎ: `docs/tangibility-design` ブランチの `.steering/_handoff/next-session-eh3-pre-freeze-f1-and-separation.md`
  （タスク `.steering/20261015-tangibility-design/` の判断 2・3・16・21）。
- EH3 の配布物を固定（タグ）する前に、次の 2 つが要る。
  1. F-1（形の文法 `raw` / `lattice` × drift `none` / `diffuse`）が未決。見本のページはあるが、壁紙として日をまたいで見たときの慣れや読まれ方は分からない（判断 3）。`raw` の歩みは縁（左上の角）に寄って留まる（`.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 3）。
  2. 肖像と招待の分け方は設計とコメントで守っているだけで、`analysis/portrait/` が `engine`・`invitation`・`p_stuck` に依存しても赤になる検査が無い（判断 2）。さらに、呼び出し側の `PortraitRunner`（`src-tauri/src/lib.rs:842`）は `FeatSnapshot` をまるごと受け取り、その中に `p_stuck`・`p_flow`・`raw_x` などがある（2026-10-16 にコードで確かめた）。推定が肖像へ漏れうる場所は生成器ではなく呼び出し側にある。

## ゴール

1. 段 1: 配る Rust の生成器に合成の打鍵を与えて、4 候補ぶんの壁紙の画（日中の育った画と、その終わりの seed）を 8 日ぶん作り、研究者が自分の Mac の壁紙で見比べられる状態にする。研究者が選んだ F-1 を decisions.md に記録する。
2. 段 2: 推定（`p_stuck` など）・招待が肖像に入らないことを、参照の検査と振る舞いの検査の 2 つの Rust の単体テストで守る。それぞれ壊すと赤になることを確かめ、Windows と macOS の CI で緑にする。

## スコープ

### 含むもの
- 既存の手で回すテスト `render_portrait_samples`（`analysis/portrait/mod.rs`）を広げ、日ごとに合成の列の seed を変えた画を出す。
- `f1-viewing-notes.md`（研究者が書く記録の欄）を用意する。
- `analysis/portrait/` の全 `.rs` に推定・招待の参照が無いことを確かめる単体テスト。
- `PortraitRunner` の画を出す処理を戻り値にする小さな直し（振る舞いは変えない）と、同じ f1..f6・打鍵・時計で推定の値だけを変えても、出す画と時刻が変わらないことを確かめる単体テスト。
- 陽性対照（参照を 1 行足す・推定で更新を止める分岐を 1 つ足すと赤）。

### 含まないもの
- 研究者の打鍵で EH3 の実物を回すこと（判断 3 の「合成の列だけ」を守る）。
- 時計の 5 分ごとの更新の再現（日中は育った画 1 枚・終わりに seed 1 枚）。
- F-1 の結論で `eh3.mode` の `grammar=`・`drift=` の既定を変えること自体（結論が出たら別に決める）。
- F-3（図像）・F-2 の契機の値の見直し・小面（案 A・C）の実装。
- G-GEAR の相対のタイミングの机上の検査。

## 受け入れ条件

- [ ] 8 日ぶんの PNG（日中・seed）が 2560×1664 の画面で壁紙として置け、順と seed が decisions.md に記録されている
- [ ] 研究者の F-1 の選択が decisions.md に記録されている
- [ ] 参照の検査のテストが緑で、`analysis/portrait/` に `use crate::analysis::invitation` 等を 1 行足すと赤になる
- [ ] 振る舞いの検査のテストが緑で、`PortraitRunner` に `p_stuck` で更新を止める分岐を 1 つ足すと赤になる
- [ ] `cargo test`・`cargo clippy`・`cargo fmt --check` が手元で緑、CI（Windows・macOS）で緑
- [ ] `/cross-review` を通す

## 関連ドキュメント

- `.steering/20261015-tangibility-design/decisions.md` 判断 2・3・16・21（`docs/tangibility-design` ブランチ）
- `.steering/20261011-portrait-eh3-impl/`・`.steering/20261011-portrait-eh3-after-impl/`
- `docs/adr/` ADR-035
- `experiments/20261011-portrait-eh3/preregistration-draft.md` §10

## 運用メモ
- /reimagine 適用: No
- 理由: 設計の分岐は grill（decisions.md 判断 1〜3）で研究者が決めた。段 2 は既存の振る舞いを変えない小さな直しとテストの追加で、複数案の比較を要しない。
