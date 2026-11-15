# 設計（v1・/reimagine の前）

## 全体の流れ

```
NDJSON（本人の記録 or 合成）
  └─ gse-replay --handmark-windows OUT.ndjson [--handmark-table T.json] [--utc-offset-secs N] [--leak K]
       窓ごとに 1 行: 日・A の特徴・B の状態の特徴・画素を描く入力（コマ）・T1・T2
  └─ node experiments/.../scripts/render_pixels.mjs OUT.ndjson → pixels.ndjson
       描画の純関数（src/components/handmarkStageDraw.ts）でコマを小さく描き、画素の特徴を出す
  └─ python experiments/.../scripts/leak.py → results/verdict.json
       1 日ずつ抜く交差検証・AUC・日のブートストラップ・3 値・天井・合わせ方
```

判断 1（二段）・判断 2（描画の純関数）に従う。

## 1. gse-replay の新モード `--handmark-windows`

- 既存のモード（`--snapshot`・`--metrics`・…）と相互排他。
- 入力: セッションの NDJSON（複数）。
- 推定は記録の `feat` の行を使わず、`key` の行から既存の再生の道（`loop_step::step`・HMM 0.5.0）で計算し直す。合成の入力と本人の記録で同じ道を通すため。記録に `feat` の行があれば、計算し直した `p_stuck` との食い違いの数を表の末尾の要約の行に出す（一致の確かめ）。
- 窓: 30 秒。セッションの始まりから刻み、日の境（`eh3::local_day`・`--utc-offset-secs`）とセッションの境で切る。`feat` の刻み（1 Hz）が 1 つも無い窓は落とす。
- 打鍵の時刻: `key` の行で `press = true` のもの（ライブの `handmark_send_press` と同じ入力）。
- 描き直しの種と `t0`:
  - その日に `handmark_day` の行があれば `draw_seed` を使う。
  - 無ければ（前期）`assignment::draw_seed(table_sha256, day)`。表は `--handmark-table` で渡し、SHA-256 は `canonical_bytes` から出す（ADR-051 D3「前期の日の種」）。表が無ければ止める（fail-closed）。
  - `t0` はセッションの始まり（`meta.session_start`）。ライブの `t0`（手跡を出し始めた時刻）とは違うが、前期には `t0` が無いので、全部の日で同じ規則にする。
- 状態: `state::replay_live`（打鍵）と `trace_replay::replay_trace`（`pointer_bin`）を、窓の中の 5 秒おきの 6 時点で出す。
- 行の項目:
  - `day`・`t_start`・`t_end`・`session`（番号）
  - A（許した情報）: 打鍵の数・打鍵の間隔の平均・標準偏差・中央値・変動係数・2 秒以上の止まりの数と最長・打鍵の無い秒の割合・`pointer_bin` の `moved` のバケットの和と平均・`buttons` の和・`wheel` の和・ポインタの動いた秒の割合
  - B 状態（`b_state`）: 6 時点の `speed`・`irreg`・`sin(phase)`・`cos(phase)`、跡の場の `|bend|` の平均・`pull` の大きさの平均・0 でない格子の数、窓の中の波紋の数。`drift`・`layout_seed` は入力に依らないので入れない（入れても害はないが雑音）。
  - コマ（`frames`）: 6 時点ぶんの `StageState` と跡の場の格子（画面へ送る `handmark-trace` と同じ符号化）と生きている波紋。node が描く。
  - T1: 窓の中の全部の `feat` の刻みで `p_stuck ≥ 0.60`（招待の契機 `TRIGGER_P_STUCK` と同じ値・「30 秒続いた」に合わせる）なら 1。
  - T2: 窓の `p_flow`・`p_inc`・`p_stuck` の平均の最大のもの（0・1・2）。判断 3。
- `--leak K`（机上だけ・陽性対照・判断 4）: 描き直しの状態に、窓の直前までの `p_stuck` の平均を混ぜる。`speed' = speed + K × (p̄ − 0.5)`、`irreg` も同じ。`K = 0` は混ぜない。製品の写像には入れない（`analysis/handmark/` の関数は変えず、モードの中で後から足す）。
- 出力はバイト単位で決定的（浮動小数は `ryu` の既定の書式・並びは時刻の順）。

## 2. 描画の純関数への切り出し

- `src/components/HandmarkStage.tsx` の描く部分を `src/components/handmarkStageDraw.ts` へ移す。
  - `drawStage(ctx, W, H, shown, fieldShown, ripples, nowMs)` の形。React・Tauri・`performance.now()` に依らない。
  - `HandmarkStage.tsx` はこの関数を呼ぶだけにする。
- 画面の振る舞いは変えない。切り出しの前後で、同じ状態を入れた 1 枚の画素を比べるテスト（node の canvas で描き、前後のバイトの一致）と、実機の画面を見る確かめ（`ui-changes-need-eyes`）。
- node の canvas は `@napi-rs/canvas`（ビルド済みのバイナリ・ネイティブのビルド不要）を、実験のディレクトリの `package.json` と lockfile に閉じて入れる（製品の依存に入れない）。`dependency-checker` で確かめる。
- 画素の特徴: 1 コマを 160×90 に描き、明るさの 16×9 の平均の格子（144）と、隣のコマとの差の大きさ（5）を出す。画素の特徴の数は状態の特徴より多いので、予測器 B は L2 の罰で抑える。

## 3. 統計（`experiments/20261115-handmark-leak-desk/`）

- `reproducibility-discipline` に従う: `SEED`・`run.sh`・`conditions.md`・`env.md`・`data.md`・`results/`・`notes.md`。Python は numpy だけ（過去の実験と同じく回帰と AUC は自作し、selftest で numpy の閉じた形と照らす）。numpy の版は `requirements.lock` に固定、venv は repo の外。
- 予測器: L2 の罰つきロジスティック回帰（特徴は学習の日だけで標準化）。罰の強さは固定（λ = 1）。T2 は一対他の 3 本。
- 予測器 B は 2 つ: `B_state = A ＋ b_state`・`B_pixel = A ＋ 画素`。漏れの判定は両方で出し、どちらかが「満たさない」なら全体を「満たさない」とする（保守側。どちらを今後の主にするかは本人の記録の後に決める・ADR-051 決めずに残すもの 2）。
- 交差検証: 1 日ずつ抜く。抜いた日の予測を固定する。
- AUC: 全部の日の予測を合わせて計算する。T2 はクラスごとの一対他の AUC の平均（マクロ）。
- 区間: 日を単位に引き直すブートストラップ 2000 回、差の分位点で両側 90%。天井は同じ標本の A の AUC の 5% 点が 0.95 を超えるとき（ADR-051 D3）。天井のときも差の上限が δ 未満であることを確かめる。
- 入れ子の引き直し（ADR-051 D3 限界 3）: 引き直した日の集合で 1 日ずつ抜く学習をやり直す方式も実装し、合成の入力で固定の予測の方式と区間の幅を比べる。どちらを本番に使うかは conditions.md で比べの前に決めた規則（幅が広い方＝保守側）で選ぶ。
- 判定（3 値）・天井・2 つの対象の合わせ方・主と感度分析の合わせ方: ADR-051 D3 の表のとおりに実装し、表ごとに単体のテストで縛る。

## 4. 記録を開く前に固定する条件（conditions.md の案）

| 項目 | 案 |
|---|---|
| クラスの最小の数 | T1: 両方のクラスが 30 窓以上かつ 3 日以上にある。T2: 対象のカテゴリは 30 窓以上かつ 3 日以上あるものだけ。対象のカテゴリが 2 つ未満なら T2 は判定不能 |
| 1 日抜いた学習でクラスが欠けた | その日の予測は学習の集合の事前の割合（定数）にする（日は落とさない） |
| 引き直しの標本でクラスが欠けた | その標本を落とし、落とした数を報告する。落とした割合が 5% を超えたら判定不能 |
| T2 の定義 | HMM の 3 状態の平均の最大（判断 3） |
| 前期の種 | `assignment::draw_seed(table_sha256, day)`・`t0` はセッションの始まり |
| 感度分析の日 | 後期の「あり」で `visible_ms` が 1 時間以上の日。切った時間の割合で日を落とさない（見えていた窓だけを使う） |
| 引き直しの方式 | 合成の入力で比べ、区間の幅が広い方 |
| B の 2 つ | 両方で判定し、どちらかが満たさなければ満たさない |

## 5. 合成の入力（判断 4）

- `experiments/.../scripts/synth.py`: 種つきで、日ごとに 3 つの打ち方（速く一定・遅く不規則・長い止まりが多い）を数分ずつ切り替える打鍵の列と、`pointer_bin` の列を作り、NDJSON（`meta`・`key`・`pointer_bin`・前期の扱いで `handmark_day` なし）に書く。20 日・1 日 2 時間。
- 打鍵の内容は持たない（`category` だけ）。
- 対照: `--leak` の K を 0・0.05・0.1・0.2・0.4 で回し、K = 0 が「満たさない」にならないこと、K が大きいと「満たさない」になることを見る。陽性対照が効かない強さも報告する（検出の力の目安）。
- 計算時間を実測する（判断 6・2 時間を超えたら研究者に聞く）。

## 6. テスト戦略

- Rust: 窓の境（日・セッション）、T1・T2 の定義、種の選び方（`handmark_day` あり／なし・表なしで止まる）、決定性（2 回の出力のバイト一致）、`--leak 0` が混ぜないこと、記録の `feat` との一致の数。
- TS: 切り出しの前後の画素のバイト一致。
- Python: 回帰・AUC を閉じた形と照らす、判定の表を全部のマスで縛る、引き直しのクラス欠け。変異（わざと壊して赤）を `mutate.sh` で。
- 画面: 実機で手跡を出して見た目が変わらないこと。

## 7. 変更対象

- `src-tauri/src/bin/replay.rs`（モードの引数と配線）
- `src-tauri/src/analysis/handmark/windows.rs`（新規・窓の表を作る純関数。OS に依らない）・`mod.rs`
- `src/components/handmarkStageDraw.ts`（新規）・`HandmarkStage.tsx`
- `experiments/20261115-handmark-leak-desk/`（新規）
- `docs/experiment-tracking.md` は変えない。`docs/adr/` は変えない（読み替えは decisions と事前登録の改訂へ）

## 8. 限界（notes.md へ）

- 再生の契約の判定で、実際の表示の全体の合格ではない（ADR-051 D3）。
- `t0` がライブと違う（前期に `t0` が無いため）。`drift` は入れないので、状態の特徴への影響は小さいが、`phase` の起点が違う。
- node の canvas と WebKit の画素は完全には一致しない。
- 推定は計算し直したもの（記録の `feat` と食い違えば数を出す）。
