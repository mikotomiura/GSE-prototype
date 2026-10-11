# 設計 — EH3 の実装

> 要件の SSOT は `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`（R-I・R-P・R-L・R-D・R-1〜R-9）。
> 本タスクの決定は `decisions.md` 判断 1〜3。値（§6）は根拠つきの提案で、凍結の前に稿 §10 へ戻す（F-2・F-9）。

## 1. アプローチ

EH3 は **O1 の収集の器に載せた層**である（判断 3 #1）。EH3 の配布物は O1 と同じ収集（自動起動・日次のファイル切り替え・
異常終了の後始末・age で暗号化して提出）で動き、その上に 3 つの層を足す。

1. **日の割り当て**（`eh3.rs`・OS 非依存）: 配布フォルダの印 `eh3.mode` に書いた参加者ごとの割り当て
   （ブロックの順序と A の初日の none / seed）と、端末に残す稼働日の数から、その日の条件（空 / D / A-none / A-seed）を決める。
2. **招待**（`analysis/invitation.rs`・OS 非依存の状態機械）: 1Hz の分析ループから進め、overlay の小図像に出す。
3. **肖像**（`analysis/portrait/`・OS 非依存の生成と予定 → `wallpaper.rs` ＋ `wallpaper_{windows,macos}.rs`・OS 依存の書き込み）。

記録は `meta` 行の断片 2 つと新しい行種 2 つだけで、EH3 のモードでないときは 1 byte も変わらない。

PR は層ごとに 4 本に分ける（判断 1 #4）: **PR1 記録とモード** → **PR2 招待** → **PR3 肖像と壁紙** → **PR4 配布と文書**。
各 PR は単独で merge でき、EH3 のモードでないビルドの挙動を変えない。

## 2. PR1 — 記録とモード

### 2.1 モードの決まり方（`src-tauri/src/eh3.rs`・新規・`o1.rs` の鏡像）

- 印 `eh3.mode`（配布フォルダ。`o1.mode` と同じ探し方）か、開発用の環境変数 `GSE_EH3_MODE`。
- **EH3 は O1 を前提にする**: EH3 の印があるのに O1 でないときは起動時に EH3 を無効にし、`tracing::warn!` を 1 行出す
  （配布の誤りを黙って通さない）。G1 と衝突したら G1 が勝つ（`o1::resolve` と同じ）。
- 印の中身（1 行・研究者が割り当ての表から作る）: `order=E,D,A;a_first=seed`（`E`=空・`D`=日替わりの地模様・`A`=その回の形）。
  中身が読めない・不正なら EH3 を無効にする（既定の条件を勝手に選ばない）。
- EH3 のときの切り替え（`lib.rs` の O1 の分岐に足す）:
  - `INTERVENTION_ENABLED` は O1 と同じく偽のまま（Nudge は出ない・R-D2）。
  - 招待の研究の条件 `INVITATION_ENABLED` を別に持ち、EH3 のときだけ真（R-1 (i)・判断 1 #1）。
  - O1 の ESM（`activity_label`）を切る（判断 3 #1）。

### 2.2 稼働日の数え方（R-7・判断 2 #2）

- 日付は**現地時刻で早朝 4:00 を区切り**とする（`local_day(ts_ms, utc_offset)`）。
- その日に **打鍵を 1 回でも観測した**ら、その日を稼働日として数える（閾値を上げると、少しだけ使った日の条件が宙に浮く）。
- 条件は「その日を数えた時点」で決まり、日中は変わらない。15 稼働日を超えた日は **期間の後** とし、肖像を出さず元の壁紙に戻す
  （招待も出さない）。
- 端末に残す状態は `~/.gse/eh3_state.json`（数えた稼働日の日付の列）。⚠️ これは端末の中だけで、提出物にも NDJSON にも入れない。
  稼働日の日付は NDJSON の打鍵からも分かるので、新しい情報を作らない。

### 2.3 記録（R-L1・R-L2・R-L5・R-L6）

| 何 | 形 | いつ |
|---|---|---|
| `meta` の断片 `eh3_mode` | `"marker"` / `"env"`（O1 の `o1_mode` と同じ形） | EH3 のときだけ |
| `meta` の断片 `invitation_enabled` | `true` | EH3 のときだけ（R-1 (i)。O1 は `session_meta` を書かないので `meta` に置く・判断 3 帰結） |
| 新しい行種 `eh3_day` | `{"type":"eh3_day","t":…,"day":1..15,"condition":"blank"\|"decor"\|"a_none"\|"a_seed"}` | その日を数えた時点で 1 回。すでに数えた日にアプリが起動した時・一時停止から再開した時・日次の切り替えの後にも、その日の行を出し直す（その時刻の日で引くので、別の日の条件は書かない・判断 4 G2〜G4）。一時停止中の打鍵は数えない |
| 新しい行種 `invitation_present` | `{"type":"invitation_present","t":…}`（理由を載せない） | 招待を出した時点 |

- 時刻のキーは `t` にする（`redaction.rs` の区間削除の既定の対象に入る・リスク 3）。
- 記録しないもの（R-L1・R-P9）: 壁紙を書き込んだ時刻・復元の成否・「戻せない背景なので動かさない」・招待の解除の時刻・
  招待の設定の値（R-L4: 値は生活時間の代理になりうるので記録しない。ADR-035 D4 の「値そのものを記録するかは実装時」をここで閉じる）。
- 同時に直す: `schema_dto.rs`・`logger.rs`（`LogEntry`・行種名の match・断片）・`schema/current.json`（`emit_schema`）・
  `capabilities.rs`（`KNOWN_LINE_TYPES`・EH3 のときだけ `config_gated` に `eh3_day`。`invitation_present` は送出元ができる PR2 で宣言する）・`bin/replay.rs`（variant と網羅テスト）・
  `redaction.rs`（既存の網羅テストが新しい行種の `t` を拾うことを確かめる・変更は不要）・`anonymize.rs`（新行のゲートテスト）。
  gse-dataset 側の `schema/current.json` も同期する（`check_schema_parity.py`）。`capabilities_gate.py` は宣言を `meta` から読むので変更は不要。
- `scripts/sync-session.{sh,ps1}` は**変えない**（実装で改めた）: EH3 の記録は `meta` に `o1_mode` を持つので、既存の O1 の門で
  gse-dataset への同期が止まる。EH3 の記録は O1 と同じく自動提出（reconcile）で研究者へ届き、研究者の側で `meta.eh3_mode` によって
  O1 の記録と分ける（参加者 ID も別の名前空間で振る・PR4 の配布の手順）。
- O1 の ESM（`activity_label`）は現時点で production の送出元が無い（`capabilities.rs` の `activity_label_has_no_emitter_until_it_is_wired`）。
  ADR-031 M5 で配線するときに、EH3 では出さない門を同時に入れる（PR4 の引き継ぎに書く）。
- byte 同一の検査: `o1_meta_fragment_is_empty_outside_o1` と同じ形の EH3 版、`session_meta` の完全一致テストは変えない、
  ゴールデンの snapshot は meta を含まないので再生成しない（`HMM_VERSION` は上げない）。

## 3. PR2 — 招待

### 3.1 状態機械（`src-tauri/src/analysis/invitation.rs`・新規・OS 非依存）

入力（1 tick ごと）: 実時間 `now_ms`・現地の時刻（分）・`p_stuck`（`clean_score`）・`idle_ms`・本人の設定・研究の条件・
セッションの区切り（始まり・終わり）。出力: `present` / `none` と、出した瞬間の `Presented` の事象。

- **契機**（R-I6）: `p_stuck ≥ 0.60` が **30 秒続いた**とき（離席候補 `idle_ms ≥ 180 s` の中では出さない）。機会のスコアは使わない。
- **1 区間 1 回**（R-I7・U-3）: 停滞の区間は、`p_stuck < 0.60` が 60 秒続くか、離席候補に入るか、セッションが区切れたら終わる。
- **失効**（R-I2）: 提示から **T = 60 秒**（実時間）で、応答の有無に依らず `none`。失効は提示ごとの通し番号に結び付け、
  古い失効は新しい提示を消さない（番号は状態機械の中だけにあり、境界・記録に出さない）。
- **即時に下げる**（R-I3）: 本人が止めた瞬間・時間帯の終わり・研究の条件が偽になった瞬間・セッションの終わり。
- **閉じた後の間隔**（R-I4）: 30 分（時間だけ。閉じた理由に依らない）。
- **上限**（R-I5・PC-6）: 1 日（4:00 区切り）の上限は本人の選択 {1, 2, 4}・既定 2。内側の上限 4（PC-6）。
- **本人の設定**（R-I8・ADR-035 D1〜D3）: 有無（出す / 出さない・既定 出す）・時間帯 {9–18 時（既定）, 8–20 時, 6–22 時}・
  1 日の上限 {1, 2, 4}（既定 2）。N 択だけで自由入力を置かない。
- **内側の制約**（ADR-035 D1 の 4 つ）は設定より内側で効く: ① 系の控え（閉じた後の間隔・1 区間 1 回）②上限 4 ③夜間 22:00–6:00 は出さない
  ④ 研究の条件 `INVITATION_ENABLED` が偽なら出さない。
- **応答を入力に持たない**（R-I9・R-I10・ADR-033）: 状態機械の入力に、図像を押した・押さなかったの情報を入れる口を作らない。
  設定の変更は外枠だけを変え、控え（①）を解かない。
- 1Hz の差し込み点: `lib.rs` の分析ループで `step()` の後（`p_stuck` は `out.feat`・`idle_ms` は既存の関数）。
  `Presented` で `LogEntry::InvitationPresent` を送る。状態は `InvitationState`（`Arc<Mutex<…>>`）に置き、overlay は
  `get_invitation_state`（`present` / `none` だけを返す）を poll する。

### 3.2 overlay の小図像（`src/components/Overlay.tsx`・`InvitationGlyph.tsx`・新規）

- 文字の無い図像を 1 つ、固定の大きさ（40×40 px・画面の右下）で出す。提示ごとに不変（大きさ・動き・色・出ている時間で強さや回数を表さない）。
- 図像の候補を 3 つ作り、研究者が見本で選ぶ（F-3）。図像に `aria-label` 以外の文字を置かない。
- 押すと「説明と設定」の窓を開く（その操作は記録しない・状態機械に渡さない）。
- 画面共有からの受動的除外: EH3 のときだけ overlay 窓に Tauri の `set_content_protected(true)` を掛ける
  （Windows は `SetWindowDisplayAffinity`、macOS は `sharingType`。⚠️ Windows で `WDA_EXCLUDEFROMCAPTURE` になるかは tao の版で確かめる）。
  共有・録画の状態は検出しない（PC-8・R-I11）。
- 肖像の上に重ねない（R-I14）: overlay の窓は前面のアプリの上にあり、壁紙の一部には見えない。図像の地の色を肖像の色から取らない。

### 3.3 説明と設定の窓（`src/components/InvitationSettings.tsx`・新規）

- `setup()` で隠した窓として事前に作る（Windows のデッドロックの回避・`lib.rs:4900` の注記に倣う）。トレイにも入口を置く。
- 中身: 図像の意味、規則と目的の開示（U-2 の文面・R-3: 「規則は書くが、個々の提示の理由には触れない」）、設定の 3 項目の N 択。
- 本人の量（何回出た・残り・累計）を置かない（ADR-035 D6）。統制的な語を使わない（I-4・R-I15）。文面は研究者が確かめる（F-3）。
- 設定は `~/.gse/eh3_invitation.json` に保存する（記録には出さない）。

### 3.4 ADR-026 M11 の検査（同じコミットで入れる・R-I13）

`scripts/check_invitation_surface.py`（CI の frontend-check に足す）:

| # | 失敗条件 | 検査 |
|---|---|---|
| ① | 招待面に文字・量が出る | `InvitationGlyph.tsx` に JSX の文字ノード・数値の補間が無い／`InvitationSettings.tsx` に回数・残り・累計の語と、状態からの数値の補間が無い |
| ② | 共有状態を検出する API を呼ぶ | `src-tauri/src` と `src` に禁止語（例: `GraphicsCaptureSession`・`CGWindowListCopyWindowInfo`・`SCShareableContent`・`EnumWindows`・`getDisplayMedia`）が無い |
| ③ | `present` の間に招待面が空 | Rust の状態機械のテスト（`present` のとき図像の ID が出る）と、`Overlay.tsx` が `present` で図像を描く静的検査 |
| ④ | 引用・未決の参照が解決しない | 既存の `check_citations.py` |

各検査は陽性対照（違反を仕込んだ一時ファイル）で赤になることを `--selftest` で確かめる。

### 3.5 テスト（`analysis/invitation.rs` の `#[cfg(test)]`）

- ADR-035 Migration 1: 経路独立性 ①（同じ現在の設定なら、変更の履歴が出す量を変えない）②（広げた後は最初から広い設定を超えない）
  ③（設定の変更で控えが解けない）。陽性対照として「広げたら閾値を下げる」偽の実装をテストの中に置き、① か ② が赤になることを確かめる。
- 内側の制約を、設定を最大に広げた状態で 4 つとも確かめる。
- ADR-033 の単調性: 状態機械に応答の口が無いことを型で固定し、図像を押す操作が出力に影響しないことを確かめる。
- 失効: 提示 A の失効の時刻が、A が閉じて提示 B が出た後に来ても、B を消さない。
- 即時の解除・1 区間 1 回・上限・夜間・研究の条件が偽。

## 4. PR3 — 肖像と壁紙

### 4.1 生成（`src-tauri/src/analysis/portrait/`・新規・OS 非依存）

- `canvas.rs`: 320×180 の f32 RGB（EH1 の `config.json` の canvas と同じ）・ガウスの印・拡散（scipy の `gaussian_filter` の
  `mode="nearest"`・`truncate=4.0` と同じ）。
- `generator.rs`: `raw` と `lattice`（EH1 第 5 回の `portrait.py` の `Generator` の移植）・drift は `none` / `diffuse`。
  **研究者が見本で 1 つに選ぶまで両方を持ち、印 `eh3.mode` の `grammar=raw|lattice` と `drift=none|diffuse` で固定する**（F-1）。
  材料は f1・f3・f4・f6 と 1 秒ごとの打鍵の有無だけ（R-P1・E1-1）。`p_stuck` などの推定と招待を受け取る口を作らない（型で固定）。
- `schedule.rs`: U-4 の型（`recent`・I = 300 s・W = 5 s・recent = 60 s。打鍵の最中は次の予定へ・60 s 以上の不在の中では更新しない・
  スリープ中は更新しない）。予定の起点はセッションの始まり（R-P3）。
- `decor.rs`（D・R-P7）: 日付と種から作る日替わりの地模様（打鍵を材料にしない）。EH1 の地の色を基に、低い彩度の大きな印を
  日付で決まる位置に置く。
- `ending.rs`（R-P6・R-4）: **none** は何もしない（次の始まりで地から）。**seed** は `render_e18.py` の最後のコマ
  （地の上に、形の重心に平均の色の小さな印 1 つ・σ 4・α 0.8）を書く。形が地のままなら何も書かない。
- 中立（R-P4・E1-7）: 観測が足りないとき（累積の打鍵 60 秒未満）の地は、セッションの始まりにだけ当てる。
- 移植の検算: EH1 の合成セッション 2 本について、Python と Rust の最後の絵の差が小さいことを、`experiments/` の外の
  一時スクリプトで確かめ、結果を `decisions.md` に書く（同一にはならない: 浮動小数の順序）。

### 4.2 終わりと始まり（R-7・判断 3 #2）

- 終わり: アプリ（PC）の終了・OS のスリープの直前の通知・4:00 の日付の区切り。始まり: 次の起動・スリープからの復帰・日付の区切りの直後。
- 終わりで A-seed なら seed を書く。A-none なら何もしない。始まりではその日の条件の地（空なら元の壁紙・D なら地模様・A なら地）を書く。
- スリープの直前の通知: Windows は `RegisterSuspendResumeNotification`（`DEVICE_NOTIFY_CALLBACK`・窓を作らない）、macOS は
  `NSWorkspaceWillSleepNotification`。置き場所は `input/power_{windows,macos}.rs`（新規）で、`AtomicBool` と channel だけで分析側へ渡す
  （`hook-constraints` と同じ作法）。⚠️ スリープの前に書き込みが終わる保証は無い（Windows の猶予は約 2 秒）。書けなかった日は記録しない（R-P9）。
- ブロックの境界・期間の終わり（R-7・R-P8）: 期間の後の最初の起動と、トレイの「研究を終える」で、seed を残さずに元の壁紙へ戻す。
  A の最後の日の seed の印が次のブロックの初日の起動前に見えることは避けられない（稿 F-9 に書く）。

### 4.3 壁紙の書き込みと復元（`src-tauri/src/wallpaper.rs` ＋ `wallpaper_windows.rs` / `wallpaper_macos.rs`・新規）

- 専用のスレッド（Windows は STA の COM）で動かし、分析側からは channel で「この絵を出す」「元に戻す」だけを受ける。
- 始める前に、モニタごとに元の壁紙（パス・位置の型・SHA-256）を `~/.gse/eh3_wallpaper_original.json` に保存する。
  戻せない背景（スライドショー・単色・スポットライト・動く壁紙・パスが読めない）なら動かさない（R-P8）。
- 書く絵は 320×180 をモニタの解像度へ双線形で拡げて PNG にし、`~/.gse/eh3/` に交互の 2 つの名前で置く（同じ名前の上書きは OS がキャッシュする）。
- 本人が自分で替えた検出: 書く前に OS から読み戻し、直前に自分が書いたパスでなければ本人が替えたとみなし、期間の終わりまで書かない。
  その場合、期間の終わりにも戻さない（本人の壁紙を上書きしない）。
- 復元: 元のパスを書き戻し、OS から読み戻したパスと、元のファイルの SHA-256 の両方を確かめる（R-P8）。異常終了の後の起動では、
  保存した元の状態が残っていれば先に復元してから始める。
- 記録しない（R-P9）: applog に出すのは起動時の「EH3 の肖像の層: 有効 / 無効（理由の種類）」の 1 行だけで、書き込み・復元・本人が替えたことは
  `tracing` にも出さない（debug ビルドの `trace!` も置かない）。
- Windows の features に `Win32_UI_Shell`（`IDesktopWallpaper`）と `Win32_System_Power` を足す。macOS は `objc2-app-kit` の
  `NSWorkspace` の `setDesktopImageURL:forScreen:options:error:` と `desktopImageURLForScreen:`。
- `docs/agent-shared.md` 技術的制約 11 の「OS 依存を置いてよい場所」に `wallpaper_*.rs` を足す（`autostart.rs` と同じ扱い）。

### 4.4 肖像への操作が出力に写らないことの試験（R-P9）

- `analysis/portrait` と `eh3` の上流を、時計と打鍵の列を与えて動かす結合テストを置く。同じ入力の列で、肖像への操作（止める・戻す・
  自分で替える）の有無だけを変え、NDJSON（`LogEntry` の列）・applog（テスト用の `tracing` の購読者で拾った行）・提出物（`packaging` の
  入力）が byte-equal であることを確かめる。陽性対照として「書き込みのたびに行を出す」偽の実装を置き、赤になることを確かめる。

## 5. PR4 — 配布と文書

- `docs/eh3-distribution-tag.md`（新規・O1 の `docs/o1-distribution-tag.md` の形）: タグ・zip の SHA-256・印 `eh3.mode` の作り方。
  O1・G1 のタグとは分ける（R-D1）。
- 同意文書の記録項目と participant-guide の **案**（本文は研究者が確定・R-L3）。招待はいつでも止められる、壁紙はいつでも戻せる、
  止めた後に提示が出なくなることは記録から読める（ADR-035 D4 の条件で扱う）、を載せる。
- `docs/functional-design.md`・`docs/glossary.md`（招待の図像・EH3 のモード・稼働日）・`docs/architecture.md`・`docs/repository-structure.md`。
- ADR-035 の見直しの記録（本文は書き換えない。Accepted にするかは研究者に聞く）。
- macOS の実機の確認の引き継ぎ（`.steering/_handoff/`）。

## 6. 値の提案（F-2・F-9 へ戻す）

| 値 | 提案 | 根拠 |
|---|---|---|
| 契機 | `p_stuck ≥ 0.60` が 30 秒続く・離席候補の中では出さない・機会のスコアは使わない | 閾値は Nudge と同じ（較正中の推定に新しい値を足さない）。瞬間値だと 1 tick の揺れで出る。機会は「作業の切れ目」の推定で、PC-5 が切れ目を待つことを要件にしない |
| 1 区間 | `p_stuck < 0.60` が 60 秒続く・離席候補・セッションの区切りで終わる | U-3 の候補「1 区間に 1 回」 |
| 失効 T | 60 秒（実時間） | PC 面の曝露予算の実測は無い（PC-11）。見逃されても主課題を傷つけない側（PC-4）に短く置く |
| 閉じた後の間隔 | 30 分 | Nudge の cooldown 10 分より長く（招待は作業を離れる誘い）、1 日 4 回の上限の中で 9–18 時に散る |
| 上限 | 本人の選択 {1, 2, 4}・既定 2・内側 4 | §6.3 の 2–4（[P259]）。PC-6 で Nudge の 6 とは別に決める。既定は狭い側（ADR-035 D2） |
| 時間帯 | {9–18, 8–20, 6–22}・既定 9–18 | 既定は狭い側。夜間 22–6 は内側の制約 ③ |
| 日の区切り | 現地 4:00 | 夜更けの作業を前の日に入れる |
| 稼働日 | 打鍵を 1 回観測した日 | 判断 2 #2 |
| 肖像の更新 | `recent`・I 300 s・W 5 s・recent 60 s | U-4（親の判断 13）と EH1 の既定 |

## 7. 既存パターンとの整合

- モードは `o1.rs` / `g1.rs` の OnceLock と印の探し方に倣う。`meta` の断片は `o1_mode_fragment` と同じ書き方。
- 行種の追加は `pointer_bin` / `focus_transition` の足跡（`schema_dto.rs`・`logger.rs`・`capabilities.rs`・`replay.rs`・`redaction.rs`）に倣う。
- overlay は Nudge と同じ poll と画面外への退避（`Overlay.tsx:24`・`:245`）、クリック透過（`set_overlay_interactive`）を使う。
- OS 依存は `autostart.rs` と同じく crate 直下の `{module}_{platform}.rs`、電源の通知は `input/` に置く。`analysis/` に OS API を入れない。
- 設定の保存は `~/.gse/` の先例（`submission.rs` の 1 値のファイル）に倣い、json 1 つにする。

## 8. テスト戦略

- `cargo test --workspace`: 招待の状態機械（§3.5）・肖像の生成と予定・稼働日の数え方・`eh3.mode` の解析・新しい行種の round-trip・
  replay の網羅テスト・byte 同一（EH3 でないとき）・肖像への操作の試験（§4.4）。
- `gse-replay --snapshot`: 既存の 6 本が緑のまま（HMM は触らない）。
- `emit_schema` と `schema/current.json` の byte 一致・`check_schema_parity.py`・`capabilities_gate.py`・`check_invitation_surface.py --selftest`。
- tsc・clippy・両 OS の CI。
- 手動（Windows・本機）: 壁紙の差し替え → 復元（読み戻しと SHA-256）、異常終了・再起動・スリープ復帰・複数モニタ（あれば）・本人が替えた場合、
  招待の図像の表示と失効、説明と設定の窓、画面共有からの除外。
- 手動（macOS）: 引き継ぎに分ける。

## 9. 決めていないこと（研究者に確かめる・凍結の前）

- 図像の形（3 候補から）・説明と設定の文面（F-3）。
- 形の文法と drift（F-1・見本）。
- ADR-035 を Accepted にするか（Migration 2）。
