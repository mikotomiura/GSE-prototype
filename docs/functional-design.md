# 機能設計書

> 現行版（2026-11-15 に書き直した・ADR-053）。書き直す前の全文は `docs/history/functional-design-2026-11-15.md`。研究の問いと主張は `docs/research-positioning.md`、決定の一次は ADR、実装の状態の地図は `docs/architecture/gse-design-map.md`。

## 1. 概要

- **プロダクト名**: GSE (Generative Struggle Engine)
- **何をするか**: デスクワークの打鍵の時刻と種類（本文は保存しない）と打鍵の外の記録（フォーカスの遷移・ポインタ・貼り付けの文字数）を観測し、作業上の停滞を記録する。研究の段 1 では、本人の申告（C4）を問いで取り、停滞の中身と観測の対応を確かめる（ADR-043・047）。系が判断しない所では本人の手の痕跡（手跡）だけを返す（ADR-048）。
- **介入の今**: Nudge は本体の介入として出さない（既定は無効・ADR-040 D1）。身体回帰の機会を差し出す招待（Physical Anchor の PC 面・採点しない・ADR-018）は実装があり、EH3 モードと通常のモードの第 2 週で動く。段 1 は招待を出さない（ADR-043）。段 2 の招待は段 2 の設計で決める（ADR-047 D4）。
- **推定**: HMM 0.5.0（固定 baseline）が 1 Hz で `p_flow`・`p_inc`・`p_stuck` を出す。列名は識別子で、状態の主張ではない（ADR-046 D1）。段 1・段 2 の主の比べで推定は契機を作らない（ADR-044・ADR-047 D2）。
- **対象**: Windows 11 と macOS 13 以降で日常的にキーボード作業をする人。

## 2. モード

GSE は配布フォルダの印・環境変数・開始の画面の選択で、次のモードで走る。モードごとに出すもの・記録するものが違う。

| モード | 入口 | 記録 | 問い | 介入 | 一次 |
|---|---|---|---|---|---|
| 通常 | 開始の画面の「開始する」 | セッション単位の NDJSON | Phase1 期のランダムプローブ（較正） | Nudge は既定で無効。招待は第 2 週の宣言と研究者の設定 `~/.gse/invitation_trigger.json` が揃ったときだけ | ADR-040 |
| O1（自然作業の常時収集） | 配布フォルダの `o1.mode` | 常時・日次ローテート・48 時間の猶予の後に自動提出 | 出さない（`GSE_DISABLE_PROBES=1`） | 出さない | ADR-014・016 |
| 段 1（`s1`） | O1 の上に `s1.mode`（または `GSE_S1_MODE=1`） | O1 の器を共有し、問いの行を足す | C4 のプローブ（無作為の枠が主）・日の終わりの問い | 出さない | ADR-043・052 |
| 手跡（段 1 の後期） | 段 1 のモード ＋ 割付の表（入口の門） | `handmark_day` 行（表示の量・入れ切りの時刻）。手跡のためのポインタの値（座標・押下・場）は記録しない（`pointer_bin` の 1 秒の量は 3.3 のとおり別に記録する） | 段 1 のまま（手跡ありの日に日の終わりの問いへ項目を足すのは PR 7・ADR-051 D6） | 出さない | ADR-050・051 |
| G1（統制課題） | G1 のモード | 5 分のブロック | 出さない | 出さない | `experiments/20260801-controlled-friction-task/` |
| EH3 | O1 の上に `eh3.mode` | O1 ＋ 稼働日の行 | 出さない | 肖像と招待 | ADR-049 で研究としては実施しない（コードは残す） |

## 3. 機能

### 3.1 打鍵の観測

- **概要**: OS レベルのキーボードフックにより、すべてのキー入力イベントをリアルタイム収集する
- **入力**: 物理キーボード入力（Windows: WH_KEYBOARD_LL / macOS: CGEventTap）
- **出力**: InputEvent ストリーム（vk_code, timestamp, is_press, is_repeat, is_backspace）
- **振る舞い**:
  - 専用スレッドでフックを実行し、メインスレッドをブロックしない
  - crossbeam チャネル経由で分析スレッドへイベントを送信
  - オートリピートキーを識別しフィルタリング可能にする
  - macOS: **Input Monitoring tap（ListenOnly tap）** を優先し、**3 回**連続失敗後に **Accessibility tap（Default tap）** へ自動フォールバック（`hook_macos.rs` の `consecutive_failures >= 3`）
  - macOS: CGKeyCode を Windows VK コードにマッピングし、analysis 層のプラットフォーム非依存性を維持
- **エラー条件**:
  - Windows フック登録失敗時: tracing::error でログ出力、アプリは起動するが推定不能状態
  - macOS TCC 権限未付与時: システム設定ダイアログを表示し、ポーリングでタップ再作成を試行
  - macOS ad-hoc 署名時: TCC CDHash 不安定のため Input Monitoring が機能しない場合あり → Accessibility フォールバック
  - チャネル満杯時: try_send でイベントをドロップ、warn ログ出力

### 3.2 IME の状態

- **概要**: 日本語 IME の ON/OFF 状態および変換候補ウィンドウの表示状態を検出する
- **入力**: Windows: IME API (ImmGetOpenStatus, VK_DBE_\*, WinEvent) / macOS: CGEventTap 状態機械 + TIS (Text Input Source) ポーリング
- **出力**: IME_OPEN（日本語/英数切替）、IME_ACTIVE（候補ウィンドウ表示）のアトミックフラグ。macOS では追加で IME_COMPOSING（ローマ字→かな変換中）
- **振る舞い**:
  - Windows: 多層検出戦略 — WinEvent フック（主）→ EnumWindows（副）→ UIAutomation（補助）
  - macOS: デュアルパス検出 — Path A: JIS キーボード物理キー検出（英数/かなキー、高速 \~5ms）→ Path B: ANSI キーボード TIS ポーリング（GCD メインキュー経由、100ms 間隔）
  - macOS: CGEventTap コールバック内の状態機械でインライン変換（下線テキスト）を追跡
  - Writing head の中で、IME の状態に応じて β を切り替える（`β_writing` / `β_writing_latin`。どの head を走らせるかは宣言された `task_kind` が決める・ADR-006）
  - IME 変換中はバックスペースペナルティを抑制
- **エラー条件**:
  - Windows: ImmGetContext が NULL → VK_DBE_\* ダーティフラグへフォールバック
  - IME_ACTIVE の検出漏れ: 8 秒安全弁で自動リセット
  - IME_ACTIVE は推論を止めない（記録のみ・HMM 0.5.0）
  - IME ポーリングスレッド起動失敗: IME 状態検出なしで継続
  - macOS: TIS クエリは GCD メインキュー必須（dispatch_sync_f）。メインスレッド以外から直接呼ぶと不正な結果を返す

### 3.3 打鍵の外の観測

- **フォーカスの遷移**（`input/observe*.rs`）: 前面のアプリが替わった時刻だけを `focus_transition` 行に記録する（どのアプリかは記録しない）。
- **ポインタ**: 1 秒ごとの量（移動・ボタン・ホイール）の `pointer_bin` 行（`analysis/pointer_bin.rs`）。打鍵の無い作業を離席と取り違えないためと、停滞の手の様子を記述するため（ADR-014・016・041 D2）。
- **貼り付け**: 文字数だけを持ち出す（`clipboard.rs`・`Paste{t, external_paste_chars}`）。本文は文字数を数えるためにメモリへ取り込み、関数の中ですぐ破棄する。保存も送信もしない。
- **記録しないもの**: 打鍵の内容・クリップボードの本文・ウィンドウタイトル・URL・アプリ名（`data-privacy` Skill）。macOS では `EnableSecureEventInput` の区間を `secure_input` 行で印す（中身は読まない）。

### 3.4 推定（HMM 0.5.0・固定 baseline）

- **入力**: 5 特徴量（F1 Flight Time・F3 Correction Rate・F4 Burst Length・F5 Pause Count・F6 Pause-After-Delete Rate）を 30 秒のローリングウィンドウで算出する。
- **流れ**: 特徴量 → 潜在の 2 軸（X 摩擦・Y 前進）→ 26 の観測ビン → HMM の Forward Algorithm → EWMA とヒステリシス EMA で表示の確率を安定化。どの head（Writing / Coding）を走らせるかは宣言された `task_kind` が決める（ADR-006）。
- **出力**: `p_flow`・`p_inc`・`p_stuck`（1 Hz）と `ewma_x`・`ewma_y` を `feat` 行に記録する。
- **役**: 申告と照らす観測の 1 つ（H3）と、固定の比べの床に限る（ADR-044 D2）。段 1 の終わりまで直さない（ADR-044 D1）。重み・遷移・放出は手で置いた値で、ラベルで合わせたものは無い（`docs/architecture/gse-design-map.md` §1 の推定の行）。
- **沈黙**: 無入力の間は合成特徴量と摩擦のフロアで、停滞側への侵食を抑える。バックスペース 14 連続以上でペナルティビン（obs=25）。
- **コールドスタート**: 初期確率 [0.80, 0.15, 0.05]。

### 3.5 介入

- **Nudge**: 判断のロジック（`analysis/intervention.rs`: Need `p_stuck >= 0.60`・Opportunity・cooldown 10 分・1 日 6 回・dismiss の後 20 分・離席 180 秒以上で出さない）は残すが、本体の既定では出さない（`INTERVENTION_ENABLED` の初期値が無効・ADR-040 D1）。時機の評価は記録から `gse-replay --intervention` で後から計算する（ADR-040 D2）。
- **招待**（`analysis/invitation.rs`）: 出す規則（1 区間 1 回・失効 60 秒・閉じた後 30 分・1 日の上限・時間帯・研究の条件・一時停止）を共有し、契機だけを差し替える（`estimator` / `rising` / `random` / `none`）。図像は文字の無い小さな印で、押すと説明と設定の窓が開く。招待は採点せず、開始・継続・完了を系は測らない（ADR-018）。身体活動は測らない（ADR-017 D10）。
  - 通常のモード: 第 2 週の宣言と研究者の設定が揃ったときだけ。設定が読めなければ出さない。記録は `invitation_condition` と `invitation_present`。再現は `gse-replay --invitation`。
  - EH3: 割り当ての段の契機（研究としては実施しない・ADR-049）。
  - 段 1・O1・G1: 出さない。
- 詳細は `docs/architecture.md` の「招待の契機と通常のモードの配線」。

### 3.6 段 1 のモードと問い（ADR-043・ADR-031 M5）

段 1（本人の試しと確認の段）は、O1 の収集の器の上に載る層である（EH3 と同じ作り方）。O1 の提出・自動起動・導入 ID・区間の削除をそのまま共有し、問いだけを足す。
問いは C4 のプローブ（無作為の枠が主・層化は補い・Q3 の選択肢の申告）と日の終わりの問い（ADR-048 D3）。計画は `.steering/20261105-gse-m5-probe-wiring-plan/`。

- **2026-11-06 時点（M5 の 1 本目・`.steering/20261106-gse-m5-s1-core/`）**: モードの判定（`s1.rs`・印 `s1.mode`・env `GSE_S1_MODE=1`・O1 のときだけ・EH3 の印と同時なら両方を落とす）、純粋な調停器（`analysis/probe_arbiter.rs`）、行種 `probe_frame`・`probe_suppressed`・`day_question` と `meta.s1_mode`・`skip_reason` の `superseded` がある。
- **2026-11-07 時点（M5 の 2 本目・`.steering/20261107-gse-m5-s1-driver-ui/`）**: 段 1 の駆動役（`s1_driver.rs` の純粋な部分と `lib.rs` の駆動スレッド）が 1 秒ごとに調停器を回し（時刻は 2 秒遅らせ、押下が届き切ってから判定する）、問いを overlay のカードに出す。
  - 本人が登録の画面で「問いに同意する」を押すまで問いは出ず、行も 0。押すと O1 のローテートを 1 回起こし、新しいファイルの起点で枠を作る。「問いへの同意を取り消す」で開いているカードを行なしで下ろし、以後の行は 0。
  - プローブのカードは 3 問を 1 枚（摩擦・前進・固定の選択肢・自由記述なし）。選択肢は本人の段 1 が 6 択、3 名の版から「作業」を足した 7 択で、重なるときは「いちばん長かったもの」、同時にしていたときは詰まっていたなら「詰まり」、そうでなく手が動いていたなら「作業」を選ぶ（ADR-055）。`realtime_label` と `activity_label` を同じ `probe_id` で 2 行書く。層化のカードを無作為が差し替えたときは `superseded` の 2 行。
  - 日の終わりの問いは「今日の作業にどのくらい熱意を持てましたか」1〜5（仮の文 `dq-draft-1`・拾い直しは「昨日の作業に」）。無作為の問いが出ている間は伏せ、閉じたら出し直す。トレイの「GSE を終了」は、時間帯の中で当日まだ尋ねていなければ「答えて終了／答えずに終了」で尋ね、60 秒で終わる。どの終了の経路でも、開いている日の問いの行を `End` の前に書く。
  - 一時停止の間はカードを出さない（開いているプローブは行なしで下ろす）。段 1 の overlay は画面共有・録画から外す。capabilities は 4 行種（`activity_label`・`probe_frame`・`probe_suppressed`・`day_question`）を段 1 のときだけ `config_gated` に宣言する。
  - O1 の配布の門は、6 択の送出元が段 1 の門だけを通るなら O1 の同意の ESM 追補を求めず、O1 の配布物に `s1.mode` を書かないことを確かめる。
- **2026-11-07 時点（M5 の 3 本目の PR 1・`.steering/20261107-gse-m5-s1-replay-gate/`）**: 再生 `gse-replay <s1.ndjson> [s2.ndjson ...] --probes [--utc-offset-secs <N>] [--day-state <s1_day_state.json>]` が、記録の `key`（押下）・`focus_transition`・`recording_pause`・`probe_frame` から同じ調停器を回し直し、`probe_assignment`・`probe_suppressed`・差し替えのラベル・`day_question` と照合した結果を JSON で出す（`s1_replay.rs`）。
  - 開いているカードは再生の発火からでなく記録から渡す（1 件の食い違いを後ろへ波及させない）。照合の鍵は候補の時刻（tick の位相に依らない）で、位相を 4 通りに振って割れたものは境目に分ける。
  - 分類: `match`・`differ`・`missing`（再生にあり記録に無い）・`extra`（記録にあり再生に無い）と、一時停止の行の前 2 秒（`boundary_pause`）・枠の動き出し・記録に無い情報（時差・前日の状態・スリープの復帰・起動・同意の取り消し）で照合できないもの（`unverified`）。回答率は差し替え・一時停止や終了で下ろしたカードを分母から外して出す。
  - `--day-questions --utc-offset-secs <N>` は、答えた日の問いごとに次の現地 4:00 までの押下の数を出す。
  - 確かめ用のボタン（`GSE_DEBUG=1` の下だけ）で出したカードの行には `"debug":true` を付け（本物の行は変わらない）、再生は照合の外で数える。
  - 限界: 区間の削除は NDJSON に印を残さないので、削除をまたぐ記録は一致しない。一時停止の間に閉じた日の問いと同意の取り消しは行が無い。
- **2026-11-07 時点（M5 の 3 本目の PR 2）**: 本人の試し（R5）の配布物を `make-common-app-zip.sh --mode s1` で組む（`o1.mode`・本人用の印として中身 `audience=self` の `s1.mode`・プローブを止める環境変数を付けず `eh3.mode` の同居で中断する launcher）。配る前の門 `scripts/check-s1-release-readiness.sh --audience self|participants --dist <Windows> --dist <macOS>` を通す（両 OS を求め、片方だけなら `--os-only`）。他の参加者向け（`participants`）は段 1 の同意文書の承認の印を求め、本人用の配布物を弾く。参加者向けの組み立ては R9 で作る。
- **調停の順**: 無作為の枠 → 層化 → 日の問い。無作為の候補の時刻の列は `frame_seed` と起点だけで決まり、層化と日の問いは枠を読むだけ（記録から再現できる）。推定器の出力を入力に持たない（ADR-031 D2）。頻度と閾値は探索用の仮の定数（確定は R6′）。
- **6 択の門**: `o1::activity_label_allowed(段 1, 本人の同意の印)`。素の O1 では同意があっても通さない（ADR-043 D8）。同意の印は `~/.gse/s1_probe_consent`（時刻と版だけ）。
- **プライバシー**: 新しい行は数値・真偽・固定の文字列だけ。`day_question` は現地の分を書かず、時間帯の中かの真偽だけ（時差を出さない）。区間の削除で `probe_frame` は残し（系の設定だけ）、他の 2 行種は 2 つの時刻を両端とする区間で消える。

### 3.7 手跡（段 1 の後期・ADR-048・050・051・macOS と Windows）

段 1 の後期に、デスクトップの高さの透明な窓へ自然世界（霧・草・粒）を描き、本人の打鍵とポインタで動かす（glossary「手跡」）。入口の門（段 1 のモード・割付の表と SHA-256）が通る日だけ動き、それ以外では窓も読みも作らない。

- **PR 1・1b（#401・#402）**: 割付の表（`gse-handmark-table`）・行種 `handmark_day`（割付・表示の量・切った／戻した時刻・種・出せなかった理由）・入口の門・打鍵の状態の純関数（`analysis/handmark/state.rs`・250ms の格子・「今 − 0.5 秒」まで）・背景の窓・トレイの「やめる」／「描く」。
- **PR 2（#408）**: 画面の下の縁の帯（`handmark_edge_strip.rs`）と表示の量 `visible_ms`。
- **PR 3（#403）**: カーソルと左クリック。
  - 読み: 専用のスレッドが 16ms ごとに、いまの一点（`NSEvent.mouseLocation`）と左の押下（`pressedMouseButtons` の最下位ビット）を読む。権限もフックも使わない。窓が閉じている・一時停止・両方切っている間は読まない。
  - 状態: 跡は、画面を縦 1・横 1.6 に直した箱の 16 × 10 の格子の場（マスごとに草を倒す量と粒を寄せる 2 成分）で、16ms の固定刻みで進み、数秒で 0 へ戻る（`analysis/handmark/trace.rs`）。打鍵の状態とも草や粒の配置とも独立で、描画の回数に依らない。波紋は押した瞬間の位置だけを窓へ送り、窓の 6 枠（1.6 秒）で描く。
  - 再生: `pointer_bin` の 1 秒の量から、描画の種で決めた合成の軌跡と等間隔の押下を作り、同じ関数に入れる（`trace_replay.rs` の `replay_trace`）。位置は再現できず、押下はどのボタンも左とみなす（ADR-051 D3 の限界）。
  - 入れ切り: トレイの「カーソル」「クリック」（窓が出ている日だけ）。その日のうちは保ち、翌日は入った状態に戻る。切った・戻した時刻を `handmark_day.input_toggles` に書く。
- **残り**: PR 4（記録から描き直して漏れを確かめる机上の道具・ADR-051 D3）・PR 5（ホイール・ADR-050 の条件 (b) の後）・PR 6・PR 7。Windows 版は下の項目（2026-11-19）。
- **Windows 版（2026-11-19・`.steering/20261119-handmark-windows/`・ADR-050 補訂 2）**:
  - 読み: `GetCursorPos` と `GetAsyncKeyState(VK_LBUTTON)` の最上位ビットだけ（権限もフックも使わない）。左上が原点の物理ピクセルを macOS と同じ約束に直す。
  - 背景の窓: 画面共有に写さないトップレベルの窓（読み戻して確かめ、できなければ出さない）。デスクトップのアイコンは `Progman` の子なので、専用のスレッド（`handmark_desktop_windows.rs`）が 16ms ごとに窓を `Progman` のすぐ上へ保ち（Win+D・デスクトップのクリックの後も）、デスクトップの一覧の絵（`PrintWindow`）を取って、変わった区画だけを窓へ渡す（イベントでなく、背景の窓の WebView だけでの `eval`）。窓は模様のある画素にだけアイコンの写しを重ねる（`source-atop`）ので、模様がアイコンの後ろを流れて見える。取り直すのは一覧の出来事（WinEvent）を受けたときと 5 秒ごと。開くときに `Progman` の子に一覧が無い並び（24H2 より前・壁紙のアプリなど）では背景を出さない（`window_unavailable`）。
  - 帯: 最前面・クリック透過・作業領域の下端（前面の窓が主画面の全体を覆えば画面の下端）。画面のロック中は見えていない側に倒す。
  - アイコンの画素は記録しない・溜めない（区画の要約だけを持つ）・背景の窓だけへ送る。名前の文字列は読まない。
- **プライバシー（ADR-050 D2〜D4）**: ポインタの値（座標・押下・場・画面の大きさ）は、記録・applog・`tracing`・提出物・ネットワーク・推定のどこにも入れず、手跡の窓だけへ専用のイベント（`handmark-trace`・`handmark-ripple`）で送る。窓は保存も返送もしない。持つのは最後の一点と 0 へ戻る値と固定の数の枠だけ。型・ソース・振る舞いの検査（`handmark_guard.rs`）で縛る。記録の一時停止の間は、両方を切ったのと同じに扱う。区間の削除で `input_toggles` の区間内の時刻も消える。

### 3.8 記録・一時停止・区間の削除

- **NDJSON**: 1 行 1 イベント。保存先は `GSE_DATASET` が設定されていれば `$GSE_DATASET/raw/P000/`、無ければ `~/Documents/GSE-sessions/`（`logger.rs` の `default_log_path`）。O1 系は日次でローテートする。
- **書き方**: バウンドチャネル（512）でバッファし、バックグラウンドのスレッドが 5 秒ごとにフラッシュする。`meta` 行に `hmm_version` を埋め込み、`gse-replay` で照合する。書き込み先が temp へのフォールバックや無効に縮退したら Dashboard に警告のバナーを出し続ける。
- **一時停止**（`set_recording_paused`）: 止めている間は記録しない。段 1 の問いと手跡も止める。
- **区間の削除**（`delete_time_range`）: 指定した区間の行を消す。自己申告の行と手跡の入れ切りの時刻も消える（ADR-031 D6・ADR-052 D2）。
- **作業の種類の宣言**（`declare_task_kind`・O1 系）: 5 択（論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業・ADR-016・037）。

### 3.9 提出

セッションが閉じた後にだけ、匿名化（`analysis::anonymize`）→ age 暗号化（`packaging.rs`）→ `.age` を作る。被験者の確認（`.ok`）が無ければ送信の経路は開かない（`submission.rs`）。O1 系は 48 時間の猶予の後に自動提出し、6 時間ごとと起動時・日次ローテート時に収束器を回す（`reconcile.rs`）。受け口の上限（32 MiB）を超える `.age` は送らず `oversize/` へ移す。削除保証の台帳は `docs/o1-deletion-ledger.md`・`docs/g1-deletion-ledger.md`。

### 3.10 オフラインの解析（`gse-replay` ほか）

記録の NDJSON を再生し、アプリを起動せずに解析する。モード系のフラグは相互排他。

| 使い方 | 中身 | 状態 |
|---|---|---|
| `--snapshot` | `FeatSnapshot` 列の byte-equal 回帰（Replay-as-Truth） | 現行 |
| `--features` | 停滞の特徴行（下の節） | 現行（P1・O1） |
| `--probes`・`--day-questions` | 段 1 の調停器を記録から回し直して照合（`s1_replay.rs`） | 現行（段 1） |
| `--invitation` | 通常のモードの招待の契機の再現 | 現行 |
| `--intervention` | Nudge の判断の時機のオフライン評価（ADR-040 D2） | 現行 |
| `--metrics` | 混同行列・F1 と、アウトカムの指標（`receipt_free_resumption`・`paste_after_stuck_rate` など・`metrics.rs`） | Phase1 期の集計と、アウトカムの算出 |
| `--calibration`・`gse-cohort` | v0.3 較正の C-index・2 段ゲート・コホート判定（`calibration_eval.rs`・`cohort.rs`） | Phase1（終了・`docs/preregistration-v0.3.md`）。手順は `docs/history/calibration-smoke-runbook-2026-11-15.md` |
| `--segment`・`--segments` | 沈黙で区切った事後レビューのラベル付け | Phase1 期 |

#### 停滞の特徴行（`gse-replay --features`）

O1 の自然作業のセッション NDJSON から、1 Hz の特徴行（stall onset・`T0`〜`T1d`・品質）を作る解析専用の経路
（ADR-030 D1「検出器はオフライン側に置く」）。出力は封筒 `{ provenance, config, rows }`。
仕様の SSOT はこの節ではなく、`docs/adr/ADR-030-stall-onset-and-decision-episode.md`（補訂 1〜5）と
`docs/preregistration-p1-episode.md`（値・探索・読み方）、値は `src-tauri/prereg/p1-episode.json`。

- **設定**: 既定は凍結 JSON。`--set <key>=<value>` / `--feature-config` で外れた値は封筒 `config.overrides` に残る。極は `--pole`。
- **観測区間の前処理**（2026-10-08・事前宣言 v1.2 §6・issue #330）: 観測区間を作る前に、長い穴（`idle_trim_min_gap_ms` 以上）の直前と
  ファイルの最後で、最後の入力（`key` 行と `pointer_bin` 行）を含む秒の `feat` 行より後を、最大 `idle_trim_max_ms` さかのぼって落とす。
  Windows のモダンスタンバイで、寝た後も `feat` 行が続く（電源につないだ試験で 16 分）ことへの対処。
  落とした量は `provenance.idle_trim`。前処理なしの実行（`--set idle_trim_max_ms=0`）を必ず並べて報告する（2 本は真の値を挟む上下界ではない）。
- **長い無入力の前処理**（2026-10-11・事前宣言 v1.3 §7）: 続けて、入力と入力の間（ファイルの最初と最後を含む）が `idle_trim_input_gap_ms`（30 分）以上
  空いた区間の `feat` 行を落とす（前後の入力を含む秒の行は残す）。O1 のアプリは宣言を自分では外さず、PC が起きていれば `feat` 行が途切れないことへの対処。
  落とした量は `provenance.input_gap_trim`。この前処理なし（`--set idle_trim_input_gap_ms=0`）、無入力の末尾の前処理なし（`idle_trim_max_ms=0`・v1.3 では長い無入力の前処理は掛かったまま）、両方なしの 3 本を並べて報告する（v1.3 §7.4）。
- **振る舞い上の制約**: 出力は `gse-dataset` へ共有しない（`scripts/check_no_feature_output.sh`）。`features.rs` / `engine.rs` は変えない。

### 3.11 フック生存監視（hook liveness）

「フックの**設置**に成功した」と「イベントが**届いている**」は別概念として扱う。
OS が低レベルフックを黙って外した場合、従来はどこにも痕跡が残らず
**打鍵ゼロのブロックが「正常」として提出された**
（`experiments/20260801-controlled-friction-task/windows-verification.md` §5-7 に実測記録）。
- **検知**: OS が持つ「最後の入力時刻」（フックとは独立な情報源）の**変化**と、
  自前フックのコールバック回数の**変化**を 1 Hz で突き合わせ、
  「システムには入力があるのに自前のフックは呼ばれない」時間を累積する（`input/liveness.rs`）。
  ⚠️ ★ **キーの内容も種別も読まない**（`data-privacy`）。
- **通知**: 30 秒でアプリログに `ERROR`、120 秒でトレイを `⚠ 計測できていません` にする。
  ⚠️ ★ **被験者向けの文言・通知は増やさない**（盲検と介入規制。トレイ表示までに留める）。
- **復旧**: 既存の再設置経路を **1 エピソードにつき 1 回**だけ起こす。
  ⚠️ ★ 繰り返すと、誤検知時に**生きているフックを壊し続ける**。
- **記録**: NDJSON に `hook_health` 行（`alive` / `starved_ms` / `rehook`）を残す。
  ★ **判断ではなく測った量**を載せるので、後から閾値を変えて再解釈できる。
- ⚠️ **既知の限界**: 情報源にマウス入力が含まれるため、
  「読んでスクロールしているだけ」の時間を誤検知しうる（単体テストで仕様として固定）。

### 3.12 Phase1 期の経路（残っているもの）

Phase1（v0.3 較正）は 2026-08-18 に終了した。次の経路はコードに残り、記録を読むために使う。仕様の詳細は `docs/history/functional-design-2026-11-15.md` の機能 7・2.x・2.x+1 と UC-GT1〜GT3・UC-OM1。

- ホットキーの自覚ラベル（`user_label`・3 値）・レビューマーカー（`review_marker`）。3 値は状態の主張に使わない（ADR-046 D1）。
- 較正モードの blind dashboard（被験者にモデルの出力を見せない）。
- ランダムプローブ（Q1 摩擦・Q2 前進・`realtime_label`）。段 1 の問いはこの上に Q3 の選択肢（本人の段 1 は 6 択・3 名の版から 7 択）を足した（3.6）。

## 4. ユースケース

### UC-1: 段 1 の本人が、ふだんの作業をする

- **前提**: 配布フォルダに `o1.mode` と `s1.mode` があり、本人が登録の画面で問いに同意した。
- **流れ**:
  1. 本人はふだんどおり作業する（「開始する」を押さずに記録が続く）。
  2. 無作為の時刻に、画面の隅に 3 問（摩擦・前進・何をしていたかの選択肢）のカードが出る。答えても閉じてもよい。理由は問わない。
  3. 夕方に打鍵がしばらく途切れると、日の終わりの問いが 1 つ出る。答えなければ翌日の最初の利用で 1 回だけ「昨日の作業について」尋ねる。
  4. 後期の手跡ありの日は、背景と画面の下の縁が打鍵とポインタで動く。トレイから切れる。
  5. 一時停止・区間の削除・問いへの同意の取り消し・やめることはいつでもできる。
- **記録**: `realtime_label`・`activity_label`（同じ `probe_id`）・`probe_frame`・`probe_suppressed`・`day_question`・`handmark_day`。手跡のためのポインタの値（座標・押下・場）と手跡の見た目は記録しない（`pointer_bin` の 1 秒の量は記録する）。

### UC-2: 通常のモードで作業し、研究者が招待の条件を試す

- **前提**: 研究者が `~/.gse/invitation_trigger.json` を置き、開始の画面で第 2 週を宣言した。
- **流れ**: 契機が立つと、図像が 60 秒出る（1 区間 1 回・閉じた後 30 分）。押すと説明と設定の窓が開く。Nudge は出ない。
- **記録**: `invitation_condition`・`invitation_present`。立ったが出さなかった契機は記録しない。

### UC-3: 日本語入力での作業

- **アクター**: 日本語で文章を書く知識労働者
- **前提条件**: セッションが進行中、IME が ON
- **トリガー**: ユーザーが日本語入力を開始する
- **基本フロー**:
  1. IME ON が検出され、Writing head の β が `β_writing` に切り替わる
  2. 変換候補選択中は IME_ACTIVE がセットされる
  3. IME 変換中のバックスペースはペナルティから除外される
  4. 変換確定後、通常の特徴量計算が再開される
- **代替フロー（macOS）**:
  - 1a. JIS キーボード: 英数/かな物理キーで即座にモード切替を検出（\~5ms）
  - 1b. ANSI キーボード: TIS ポーリングによるメニューバー入力ソース切替の検出にフォールバック（100ms 間隔）
  - 2a. macOS: CGEventTap 内の状態機械でインライン変換（IME_COMPOSING）を追跡
- **事後条件**: IME 状態遷移がセッションログに記録される

### UC-4: macOS TCC 権限セットアップ

- **アクター**: macOS ユーザー（初回起動）
- **前提条件**: GSE アプリケーションを初めて起動する。TCC 権限は未付与
- **トリガー**: アプリケーション起動時のフック初期化
- **基本フロー**:
  1. CGPreflightListenEventAccess() が false を返す
  2. CGRequestListenEventAccess() がシステム設定を開く（Input Monitoring）
  3. ユーザーがシステム設定で GSE に Input Monitoring 権限を付与する
  4. CGEventTap が **Input Monitoring tap（ListenOnly tap）** で作成される
  5. フックがアクティブになり、キーストローク収集が開始される
- **代替フロー**:
  - 3a. Input Monitoring を拒否 → Accessibility 権限チェックへ移行
  - 3b. ad-hoc 署名で CDHash 不安定 → ListenOnly tap が **3 回**連続失敗
  - 4a. ListenOnly 失敗 → AXIsProcessTrustedWithOptions ダイアログ（GCD メインキュー経由）を表示
  - 4b. ユーザーが Accessibility 権限を付与 → **Accessibility tap（Default tap）** でタップ作成
  - 5a. Dashboard の「システム設定を開く」ボタンから手動で Accessibility を付与
  - 5b. Dashboard の TCC リセットボタンで権限状態をリセットし再試行
  - 5c. ad-hoc 署名ビルドでは CDHash 不安定のため、システム設定で**権限を一度オフにしてから再度オンに戻す**手動操作が必要になる場合がある (Dashboard が再トグル手順を案内)。自動回復はシームレスではない点に注意
- **事後条件**: 権限状態（Input Monitoring / Accessibility / フォールバック使用中）が Dashboard に表示される

## 5. 非機能要件

### パフォーマンス

- **推定レイテンシ**: 1Hz（1 秒ごとに状態確率を更新）
- **フック遅延**: フックコールバック内での処理は最小限（アトミック操作 + チャネル送信のみ）
- **UI 更新**: 500ms ポーリング間隔

### セキュリティ・プライバシー

- **キーストロークデータ**: NDJSON にはキーの**種類**（`KeyCategory` 14 種）と押下/離上のみを記録する。
  生 VK コードも書かない（ADR-014 判断 6。回帰テスト `key_line_records_category_and_never_raw_vk` が固定）。
- **セッションログ（運用時）**: ローカルファイルシステムに保存。リアルタイム推定中の外部送信なし
- **セッションログ（学習データ収集）**: ML モデル学習目的の外部送信はオプトイン + 匿名化 + セッション終了後バッチのみ許可
- **ローカルのポート**: GSE はローカルの HTTP ポートを開かない。
- **提出パス（★ 現行で唯一の外部送信経路）**: セッションが閉じた後にのみ、匿名化（`analysis::anonymize`）
  → age 暗号化（`packaging.rs`）→ `.age` を生成する。★ **被験者の確認（`.ok`）が無ければ送信経路が開かない**
  （`submission.rs`）。送信済みは `.age.sent` で表す。O1 では 48 時間の猶予後に自動提出する（`o1.rs`）
  - ★ **O1 の送信見送り（G-5・2026-09-28）**: 受け口の上限（32 MiB・`Form_O1/GSE_O1_Submit.gs` の `MAX_BYTES`）を
    **超える** `.age` は送らず、提出物フォルダの `oversize/` へ移す（送る前の大きさ検査と、受け口の `too large` 応答の両方）。
    ⚠️ **消さない**（研究者が手で回収する・`docs/o1-deletion-ledger.md` B-4b）。日番号は台帳も見て決まるので再利用されず、
    受領台帳の欠番検知が研究者に知らせる。⚠️ **G1 は対象外**（凍結）
- ⚠️ **PC ↔ スマホの境界を将来作るときは ADR-017 D4 の S1–S6 を満たすこと**
  （S1 明示的ペアリング / S2 送信元認証 / S3 偽造・リプレイ対策 / S4 端末紐付けと失効 / S5 LAN 露出の明示 /
  S6 ペイロードに本人性を載せない）。★ **常設の LAN リスナを置かない**（ADR-017 D4）

### 可用性

- **想定稼働率**: デスクトップアプリケーションのため、OS 起動中は常時利用可能
- **障害復旧**: フック登録失敗やチャネル溢れは graceful degradation（推定精度低下はあるがクラッシュしない）
- ⚠️★ **O1 の稼働継続（2026-09-28・`.steering/20260928-o1-resilience-g1-g2-g5/`）**:
  - **自動起動（G-1）**: O1 の配布形（`o1.mode` 由来）で**初めて起動したときに 1 回だけ**、ログイン時起動に登録する
    （macOS = `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist`・Windows = HKCU `Run` の `GSE-O1`（引用符つき））。
    ★ **O1 の同意確認の後**だけ。新しく作るのは端末で 1 回だけ（`~/.gse/o1_autostart_registered`）で、新しい版のフォルダでは
    **OS に登録が残っているときだけ**付け替える（被験者が切った・消したら作り直さない）。配布フォルダの印 `o1.autostart` は処理済みの印。
    ⚠️ 環境変数 `GSE_O1_MODE=1`・G1・通常運用では登録しない（`autostart.rs`）
  - **定期再送（G-2）**: O1 では起動時・日次ローテート時に加えて **6 時間ごと**に収束器を回す
    （`ReconcileReason::O1Periodic`・`o1::PERIODIC_RECONCILE_MS`）。排他は既存のロックに任せる
### ユーザビリティ

- **対応デバイス**: Windows 11（Surface Pro 8 + Type Cover）/ macOS 13 Ventura 以降（MacBook Pro/Air — JIS / ANSI 両キーボード対応）
- **UI**: ダッシュボードウィンドウ + オーバーレイウィンドウの 2 ウィンドウ構成
- **操作**: 通常運用は**セッション開始/終了**のみ。加えて **記録の一時停止・再開**（`set_recording_paused`）、
  **区間指定削除**（`delete_time_range`）、**作業の種類の宣言**（`declare_task_kind`・O1 のみ。5 択 = 論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業 —— ADR-016 判断 4b-2・ADR-037）、
  **参加者 ID 入力と提出**（`submit_latest_session` / `approve_pending_submissions`）、
  **自己マーカー**（`record_self_marker`）、段 1 の**問いへの同意と取り消し**・**手跡の入れ切り**（トレイ）、macOS の**権限リセット / システム設定を開く**を持つ
  （モードごとに表示を出し分ける）。
