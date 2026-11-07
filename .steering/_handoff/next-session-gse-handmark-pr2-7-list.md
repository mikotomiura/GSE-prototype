# 引き継ぎ —— 手跡 PR 2〜7 と条件 (b) の実測（一覧）

> 作成: 2026-11-08（`.steering/20261108-handmark-to-main-plan/`）。PR 1 が入るまで、ここに書いた前提は動きうる。各 PR を始めるときに、ADR-051 D7 と PR 1 の記録を読み直してから、1 本ずつ引き継ぎを書き起こす。決定の一次は ADR-051 と ADR-050。

## 入口の文（例）

```
/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-handmark-pr2-7-list.md を読んで、手跡の PR <n> を /start-task から始めて。
```

## 一覧

| PR | 中身 | 前提 | 確かめ方 | 材料（試作の枝 `spike/handmark-stage`） |
|---|---|---|---|---|
| 2 帯 | 下の縁の帯（14pt・非アクティブの NSPanel・Dock の上端に沿う・全画面では画面の下端）と、見えていた時間の計り方（覆われ方の判定）。描画は入力があれば 30 回／秒、無ければ 10 回／秒で、完全に覆われたら止める | PR 1 | 画面を見る・CPU（1 コアの割合を累積の秒の差で測る。memory: macos-top-l2-undercounts-cpu） | `handmark_edge_strip.rs`・`HandmarkEdgeStrip.tsx`・`.steering/20261030-handmark-edge-strip-impl/`・tangibility 枝の `20261029-handmark-edge-strip-design/` 判断 3〜7 |
| 3 カーソルとクリック | 16ms ごとに一点を読む（権限なし）・左だけ・状態の関数への入力・`pointer_bin` からの近似の写像（漏れの確かめ用）。ADR-050 D2〜D4 の検査を、ポインタの行まで広げる | PR 1 | `cargo test`・`node --test`（`handmark-stage-trace.test.mjs` の 9 件を写す）・画面を見る | `handmark_stage_pointer.rs`・`input/handmark_pointer{,_macos}.rs`・`handmarkStageTrace.ts`・ADR-050 補訂 1 の項目 1・2・6・8 |
| 4 机上の道具 | 記録から描き直し、予測器 A（速さ・リズム・止まり＋`pointer_bin`）と B（A＋見た目）の AUC の差を出す。1 日ずつ抜く交差検証・日のブロックのブートストラップ 95%・3 値・δ = 0.05（ADR-051 D3）。見た目の特徴は、画素からと状態からの両方を作って比べる（ADR-051 決めずに残すもの 2）。本人の前期の記録で、区間の幅を測る | PR 1・PR 3 | 合成の入力で既知の漏れを入れた陽性対照（人の記録を使わない） | 新規。`reproducibility-discipline`（`experiments/`・seed・HMM_VERSION）。計算が重ければ G-GEAR（11 月はふさがっている） |
| 5 条件 (b) の実測 → ホイール | ① 実測: PR 3 が入った main のビルドで、ホイールの tap を開発用の設定で入れた日と切った日を比べ、打鍵の tap の失効の数を見る。入れ切りと一時停止を繰り返して tap が残らないことも確かめる。② 通れば: ホイール専用の聞くだけの tap（入力監視の許可が要る）を入れ、ADR-050 を Accepted（macOS の射程）にする | PR 3 | 失効の数・tap の数 | `input/handmark_wheel_macos.rs`・ADR-050 補訂 1 の項目 3・4 |
| 6 「背景を見る」 | 他のアプリをどける・戻す（押したときに見えていたアプリだけを戻す）。全画面の中では、最大 1 秒待って前面に出られなければ隠さずやめる。終了のときに戻す。どけた回数の行と schema・同意の文の改訂。macOS 14 より前の `activate()` の分岐 | PR 1（帯の後が自然） | 画面を見る・同意の文の差分を研究者が読む | `handmark_reveal.rs`・tangibility 枝の `20261023-handmark-window-boundary/` 判断 5 と `20261029` 判断 6・7・論点 6・7 |
| 7 日の問いの項目 | 手跡ありの日だけ、`day_question` のカードに同期・共存の項目を足す（`items_version` を上げる）。契機と回数は変えない | 文献のラウンド（尺度の文）・PR 1 | `cargo test`（`probe_arbiter.rs` の既存のテストの形） | `analysis/probe_arbiter.rs` の `DayQuestion`・`logger.rs` の `DayQuestionRow`・`src/components/DayQuestionCard.tsx` |

- 2・3・6 は、1 の後なら順を入れ替えてよい。
- 後期の途中で PR が足されたら、その日からの刺激の違いが日ごとの行とビルドの版で分かるようにする（ADR-051 Consequences）。

## 条件 (b) の実測で守ること

- 本人の段 1 の Mac で、別のビルドを並べて走らせない。記録が混ざり、AX が取り違える（memory: jxa-same-name-process-ax-crosstalk）。
- 実測の時期と機械は、始める前に研究者に AskUserQuestion で確かめる。本人の段 1 の記録に影響しうる。実測の日の記録は探索として扱う。

## 共通

- UI の PR は画面を見るまで完了にしない。O1・段 1 の記録の本文を Codex に送らない。push・PR は研究者に確かめてから。
