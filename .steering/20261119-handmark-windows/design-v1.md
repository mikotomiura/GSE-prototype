# 設計

本タスクは 2 段に分かれる。§1 は確かめの段（使い捨ての試作で測る）の設計で、ここで承認を得る。
§2 は本番の実装の段の設計で、研究者が背景の層の候補を選んだ後（停止点の後）に書き、`/reimagine` を回す。

---

## §1 確かめの段

### 1.1 前提として先に分かっていること（一次で確かめた）

- Mac 版の背景の窓は `set_content_protected(true)` で画面の共有・収録・スクリーンショットに写さず、読み戻せなければ出さない（fail-closed・`src-tauri/src/handmark_stage.rs` の `prepare()`）。
- Windows の取り込み除外 `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` は、hWnd が「A handle to the top-level window」で、子の窓への呼び出しは FALSE を返す。DWM が合成しているときだけ効き、保証ではない（[V283]・`docs/references.md`）。
  - → **WorkerW の子として差し込む候補は、画面共有から外せない見込み**である。Mac 版と同じ fail-closed を守るなら、その候補は出せないことになる。実測で確かめる。
  - → 動かない壁紙（`IDesktopWallpaper`）も、壁紙そのものなので外せない。
- WorkerW は非公開で、24H2 で Lively が作り直しを要した（[V284]）。
- この機械: Windows 10.0.26300・昇格なしのシェル・windows crate 0.58（`src-tauri` と同じ版）。

### 1.2 候補（引き継ぎの 3 つに 1 つ足す）

| 記号 | 候補 | 層の意味 | 画面共有から外せるか（見込み） |
|---|---|---|---|
| W | WorkerW（または 24H2 以降の Progman の下の層）の子として差し込む | 壁紙の上・アイコンと窓の下（Mac 版と同じ） | 外せない（子の窓・[V283]） |
| B | **足す候補**: トップレベルの窓を z 順の最下（デスクトップの直上）に保つ。クリックを通し、焦点を取らない | 壁紙とアイコンの上・他の窓の下（アイコンより上になりうる） | 外せる見込み（トップレベル） |
| T | 最前面でクリックを通す透過の窓 | 他の窓の上に重なる（層の意味が変わる） | 外せる見込み（トップレベル） |
| S | 動かない壁紙の更新（`IDesktopWallpaper`・EH3 の先例） | 壁紙そのもの。跡が動かない | 外せない |

B を足す理由: W は画面共有の除外が効かない見込みで、T は層の意味が変わる。トップレベルのまま他の窓の下に置ければ、Mac 版の「窓の下・画面共有に写らない」の両方に最も近い。デスクトップのウィジェットでよく使われる形だが、「デスクトップを表示」（Win+D）やアイコンとの上下で崩れうるので、それも測る。

### 1.3 試作の置き場

- 試作は、本番のコード（`src-tauri/`）とは別の小さな Rust の crate にする: `.steering/20261119-handmark-windows/spike/`（ソースだけコミットし、`target/` は scratchpad に置く）。
- 依存は `windows` 0.58 だけ（キャッシュ済み・オフラインでビルドできる）。描画は GDI の単純な動く模様で、WebView2 は使わない。
  - 理由: 層が成り立つかは窓の種類で決まり、中身の描き方には依らない。Tauri（WebView2 の透過）がその層で動くかは、§2 で選んだ候補についてだけ確かめる。G-GEAR の release のビルドは遅い（memory）。
- 試作のコードは main に入れない（ADR-051 D7 の先例）。本番は §2 で本番の形として書き直す。

### 1.4 測ること

**(a) 位置とクリックの読み（ADR-050 の条件 (a)）** — `spike probe-pointer`
- 16ms ごとに `GetCursorPos` と `GetAsyncKeyState(VK_LBUTTON)` だけを読む（補訂 1 項目 1 の間隔）。キーボードの仮想キーは渡さない。プロセスは Per-Monitor DPI aware v2 にして、座標が物理ピクセルで返るかも見る。
- 出すのは数だけ: 押下の立ち上がりの回数・位置が変わった刻みの数・読みの失敗の数。位置の列は持たず、ファイルにも書かない（ADR-050 D2・D4 の精神）。
- 陽性対照: 研究者が手で、ふつうのクリックを 10 回、素早いクリックを 10 回する。数えた回数と比べる（合成の入力は使わない）。
- 条件を変えて繰り返す: ① ふつうの窓に焦点 ② 昇格した窓（タスク マネージャー）に焦点 ③ 画面のロック中・UAC の確認画面（0 になる見込み・読みの失敗にならないかを見る）。
- 昇格なしで行う（この機械のシェルは昇格していない）。

**(b) 背景の層** — `spike layer --candidate W|B|T`（S は EH3 の `wallpaper_windows.rs` で成り立ちが分かっているので、画面共有と更新のコストだけを見る）
- 候補ごとに、動く模様の窓を主画面の全体に 60 秒出し、次を記録する。
  1. 出たか・どこに見えるか（壁紙の上か・アイコンの上か下か・ふつうの窓の下か）。研究者の目で確かめる。
  2. Win+D・エクスプローラーの再起動・画面の解像度や倍率の変更の後に残るか。
  3. `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` の戻り値と `GetWindowDisplayAffinity` の読み戻し。
  4. 実際に写るか: (i) 試作が自分で画面を取り込んで（BitBlt）模様の有無を見る、(ii) 研究者が画面共有の道具で見る（道具は研究者が選ぶ）。
  5. CPU: 60 秒の描画の間のプロセスの CPU 時間（`GetProcessTimes`）。何も出さない対照も取る。
- 全画面のアプリ（ブラウザの F11 など）を前に出したときの見え方も見る。

**(c) 下の縁の帯** — `spike strip`
- 主画面の作業領域の下端（タスクバーの上端）に高さ 14 の最前面・クリック透過・焦点を取らない窓を出す。
- 条件: ① ふつう ② タスクバーを自動で隠す設定 ③ 全画面のアプリ ④ 多画面（この機械の画面の数を先に数える）。
- 置き場の読み方は `SHAppBarMessage(ABM_GETTASKBARPOS)` と `GetMonitorInfo` の作業領域の両方で取り、食い違いを記録する。
- 取り込みの除外は帯にも掛けて読み戻す（トップレベルなので効く見込み）。

### 1.5 結果の置き場と停止点

- `results.md` に、OS の版・画面の構成・候補ごとの表・条件 (a) の数を書く。
- 研究者の手が要る所は、その都度手順を示して頼む。
- 全部そろったら、候補ごとの長所と短所・推奨を添えて止まり、研究者に選んでもらう（判断 3）。

### 1.6 守ること

- 何も記録しない: 位置の列・押下の時刻をファイルにも tracing にも出さない。標準出力に出すのは数と成否だけ。
- O1 は止めなくてよい（読むだけで、Raw Input もフックも使わない）。ただし (a) の対照は、O1 の記録に研究者のクリックが入る。気になる場合は O1 を先に終えてもらう。
- 試作の窓は終了時にかならず壊す。WorkerW の差し込みはエクスプローラーの状態を変えうるので、終わったら元に戻ることを確かめる。

---

## §2 本番の実装の段

研究者の選択: 背景の層は B5（判断 9）。デスクトップのアイコンの画素を読むことを了承（判断 10）。帯は従（判断 4）。

### 2.1 全体の形（v1）

Mac 版の駆動役（`handmark_driver`・OS 非依存）と、ポインタのスレッド（`handmark_pointer_thread::run_loop`）はそのまま使う。
Windows で足すのは、OS に触る次の 4 つと、`lib.rs` の配線と、前端の 1 か所だけ。

| 部品 | ファイル | 中身 |
|---|---|---|
| ポインタの読み | `input/handmark_pointer_windows.rs`（新） | `GetCursorPos` と `GetAsyncKeyState(VK_LBUTTON)` だけ。仮想キーは `VK_LBUTTON` の定数 1 つ（ADR-050 D3）。左上が原点の物理ピクセルを、`PointerSample` の約束（左下が原点）へ `y = 画面の高さ − y` で直す。最初の読みの「前回から押された」ビットは使わない（最上位ビットだけ見る） |
| 背景の窓 | `handmark_stage.rs`（`imp` を OS ごとに分ける） | Tauri の WebView2 の窓（Mac と同じ `LABEL`・同じ前端の描画）。透明・枠なし・タスクバーに出さない・クリック透過（`set_ignore_cursor_events(true)`）・主画面の全体。画面共有の除外は `set_content_protected(true)` の後に `GetWindowDisplayAffinity` で読み戻し、`WDA_EXCLUDEFROMCAPTURE`（0x11）でなければ出さない（Mac 版の fail-closed と同じ。tao 0.34.5 は戻り値を捨てるので自分で読み戻す） |
| アイコンの写しと並びの番 | `handmark_desktop_windows.rs`（新・1 本のスレッド） | (1) 16ms ごとに z 順を見て、背景の窓を Progman のすぐ上に保つ。(2) 2 秒ごとに `PrintWindow(SysListView32, 0)` でアイコンの画素を取り、変わった区画だけを背景の窓へ送る |
| 帯 | `handmark_edge_strip.rs`（`imp` を OS ごとに分ける） | 最前面・クリック透過・焦点を取らない・高さ 14（論理）。作業領域の下端、全画面（前面の窓が主画面の全体を覆う）なら画面の下端。画面共有の除外は同じく読み戻し（帯は従なので、失敗したら帯だけ出さず 1 行残す） |
| 前端 | `src/components/HandmarkStage.tsx`・`handmarkStageDraw.ts` | 模様を描いた後に、アイコンの層（画面外の canvas）を `globalCompositeOperation = "source-atop"` で重ねる。模様のある画素にだけアイコンが乗る（試作 B5 と同じ規則）。Mac では何も届かないので、層は空のまま |

**アイコンを背景の窓の中で重ねる理由**（別の窓を上に重ねる案を捨てた）: 別の窓に写しを出すと、模様の無い所では写しが本物のアイコンの真上に重なる。半透明の画素（名前の文字の影・縁・取り込みの 9.2%）は二重にかかって濃くなる（透明度 0.5 の画素で、地との差の最大 25%）。背景の窓の中で `source-atop` で重ねれば、模様の無い所には何も描かないので、本物のアイコンがそのまま見える。研究者の目で 4 項目を満たした B5 と同じ見え方になる。

試作の B5 との違い: 試作は全画面を CPU で毎コマ合成した（CPU 5.78%）。本番は模様もアイコンの重ねも WebView2 の canvas（GPU）で行い、アイコンの画素は変わったときだけ送る。アイコンの矩形（UI Automation）は使わない。`PrintWindow` の画素はアイコンの外が透明度 0 なので（`iconsnap` の矩形の外の透明度の最大 0）、矩形で切り抜かなくてよい。読みはその分だけ狭くなる。

### 2.2 並びの番（z 順）

- 置き場: `GetWindow(Progman, GW_HWNDPREV)` から上へ、見えない窓（`IME` など）を飛ばしてたどる（試作の `first_visible_above_progman`）。背景の窓が最初に見える窓でなければ、Progman の 1 つ上の窓の下へ入れる。
- 毎コマ（16ms）見る。1 秒ごとでは、デスクトップのクリックや Win+D のたびに最大 1 秒消えた（試作の 4 回目）。
- 背景の窓は Tauri のメインスレッドが持つので、`SetWindowPos` に `SWP_ASYNCWINDOWPOS | SWP_NOACTIVATE | SWP_NOMOVE | SWP_NOSIZE` を付け、番のスレッドを止めない。
- Progman・SysListView32 が見つからない（OS の版で並びが変わった）: アイコンは送らず、背景の窓を `HWND_BOTTOM` に置く（B1 と同じ見え方）。理由を 1 行だけ警告に残す（クラス名だけ・窓の名前は出さない）。
- 番は窓が開いている間だけ動く（駆動役の `OpenWindow`／`CloseWindow` で始め・止める）。

### 2.3 アイコンの画素の扱い（判断 10・ADR-050 への追記）

- 読むのは `PrintWindow(SysListView32, 0)` の画素だけ。名前の文字列（UI Automation・`LVM_GETITEMTEXT`）も矩形も読まない。
- 画面を 64×64 の区画に分け、前回から変わった区画だけを、背景の窓だけへ送る（`emit_to(LABEL, …)`・全窓へ流す `emit` は使わない）。区画の画素は premultiplied の BGRA を各色を透明度で抑えてから送る（試作と同じ）。送り終えたら番の側は前回の画素の要約（区画ごとの hash）だけを持ち、画素は捨てる。
- 前端は届いた区画を画面外の canvas に置くだけで、送り返さない（`invoke` しない・保存しない）。窓を閉じたら（状態が `null`）canvas を消す。
- 記録・tracing（値）・ファイル・他の窓へは出さない。
- 検査（`handmark_guard.rs`）を陽性対照つきで足す:
  - `PrintWindow` を呼べるのは `handmark_desktop_windows.rs` だけ。
  - アイコンのイベント名を参照してよいのは `handmark_desktop_windows.rs`（送る側）と前端の `HandmarkStage` だけ。
  - `handmark_desktop_windows.rs` は `LogEntry`・`std::fs`・`emit(`（全窓）を使わない。
  - `capabilities/handmark-stage.json` は listen・unlisten だけのまま（窓から何も返せない）。
- 背景の窓は画面共有に写さない（読み戻しで fail-closed）ので、アイコンの写しも写らない。

### 2.4 ADR-050 D3 の検査を Windows へ広げる

- `input/handmark_pointer_windows.rs` を検査の対象のファイルに足す（Mac の読みと同じ扱い）。
- 仮想キーの検査: `GetAsyncKeyState` の引数は `VK_LBUTTON` だけ（`VK_` の他の名前・数値の直書きを禁じる）。陽性対照: 他の仮想キーを植えたら赤になる。
- 読みと写しを呼べるのは `lib.rs` だけ（Mac の検査と同じ形）。

### 2.5 `lib.rs` の配線

- `#[cfg(target_os = "macos")]` の門を `any(target_os = "macos", windows)` に広げる: `HANDMARK_POINTER_GATE`・`run_handmark_effects` の窓の出来事・`handmark_window_status`・`HandmarkWindowGuard`・`spawn_handmark_pointer`・`spawn_handmark_driver`・`setup` の窓の作成。
- ポインタの読みだけ OS で分ける（`handmark_pointer_macos::read` ／ `handmark_pointer_windows::read`）。
- Windows で手跡の行（`handmark_day`）が書かれ始める。行の形（schema）は変えない。

### 2.6 帯の Windows

- 置き場の読み: `SystemParametersInfoW(SPI_GETWORKAREA)` と `SHAppBarMessage(ABM_GETSTATE)`。全画面は前面の窓の矩形が主画面の全体を覆うか（試作の 3 回目と同じ）。
- 見えているか（Mac の `strip_seen`）: 画面のロック中は入力のデスクトップが `Default` でない（`OpenInputDesktop` ＋ `GetUserObjectInformationW(UOI_NAME)`）。読めなければ見えていない側に倒す。純関数の部分は OS 非依存のまま対のテストを置く。
- 多画面は主画面だけ（Mac と同じ）。確かめは画面 1 枚で、多画面は未確認として残す。

### 2.7 テスト

- OS 非依存の純関数（写し・置き場の計算・z 順の判定・全画面の判定・見えているか）は両 OS で走るテストにする。OS ごとに規則が違うもの（y の向き・作業領域）は両 OS に対のテストを置く。
- 窓・z 順・画面共有の除外は実機で研究者が目で確かめる（背景がアイコンの後ろを流れる・Win+D で戻る・窓の下・ちらつきなし・帯）。CPU を測る（WebView2 の背景とアイコンの重ね・並びの番）。
- 画面共有の道具（Teams・Zoom など）で写らないかを 1 つ確かめる。

### 2.8 危うい所

- WebView2 の透明な窓を `SWP_ASYNCWINDOWPOS` で Progman のすぐ上に置いて、透過とクリックの透過が保たれるか（試作は素の Win32 の窓だった）。実装の最初に確かめる。
- 背景の窓の描画は、場が静かなときに絞られる（`fieldLive`）。アイコンの区画が届いたら 1 コマ描き直す。
- 倍率が 100% でない画面: canvas は `devicePixelRatio`（上限 2）で描くので、アイコンの層は物理ピクセルで受けて画面の大きさに縮めて重ねる。倍率 100% の 1 台でしか確かめられない。

### 2.9 しないこと

- ホイール（ADR-050 D7）。配布・リリース。ADR-050 を Accepted にすること。
- 多画面の対応（主画面だけ）。
