# 設計

## 実装アプローチ

**2 段構え。§A の実測が §B の実装を gate する。**

### §A 計測 (先) — EnumWindows 経路は実際に効くのか

⚠️ **これを飛ばして配線してはならない。** 2026-08-22 のプローブは **WinEvent しか測っておらず**、
EnumWindows 経路は**未計測**である。「WinEvent が死んでいる」ことは
「EnumWindows が生きている」ことを**含意しない**。

`examples/ime_winevent_probe.rs` に**本番の検出関数そのもの**を叩く経路を足す:

- `gse_next_lib::input::ime::is_ime_candidate_window_visible()` を **25ms** でポーリング
- **100ms へ間引いた系列**も併記する (★ 本番 `lib.rs` の IME Monitor は 100ms なので、
  「25ms なら見えるが本番の 100ms では取りこぼす」を検出できる)
- 立ち上がり回数 (false→true) / 検出率 / 候補ウィンドウ滞在時間 (合計・最長)

⚠️★ **プローブ側に検出ロジックを複製しない。** 複製を測ると「複製の方が動いた」という
無意味な計測になり、本番経路の可否を答えられない。
→ `is_ime_candidate_window_visible` を `pub` へ上げ、`input/ime.rs` から再エクスポートした
(★ **可視性だけ**の変更。シグネチャも中身も変えていない)。

**さらに: 診断用クラス名センサス** (プローブ内に閉じる、本番へは持ち込まない)。
0 件だったときに次の 2 つを区別するために要る:

| 0 件の理由 | ★ 結論 |
|---|---|
| 候補ウィンドウ**そのものが EnumWindows に出ない** (別プロセス所有) | ⚠️ **B 不成立**。`config_gated` 据え置き |
| 候補ウィンドウは**居るが** `is_ime_candidate_class_name` の網 (`Candidate` 部分一致) が細すぎる | ★ **網を広げれば成立** |

⚠️ この 2 つは**結論が正反対**なので、区別できない計測は意味がない。

### §B 配線 (後・§A が肯定的な場合のみ)

`lib.rs` の **IME Monitor スレッド** (100ms ポーリング) で、
`let active = monitor.is_candidate_window_open()` の遷移を `IME_ACTIVE` の**正の駆動源**にする。

- `false → true`: `IME_ACTIVE=true` / `IME_COMPOSITION_START_MS=now` /
  `IME_CANDIDATE_NAV_COUNT=0` / `IME_SHADOW_ABANDON=false`
- `true → false`: `IME_SHADOW_DWELL_MS = now - start` / `IME_SHADOW_READY=true (Release)` /
  `IME_ACTIVE=false`

★ **`hook-constraints` Win-1 に抵触しない**: コールバック内ではなく**既存のポーリング
スレッド**で行う。Win-1 が縛るのは `LowLevelKeyboardProc` / `win_event_callback` の中だけ。

★ **`IME_ACTIVE` を書くこと自体に意味がある** (単に `lib.rs` 内で完結させないのはなぜか):
`hook_windows.rs:512` の `if is_press && IME_ACTIVE.load(..)` が
`IME_CANDIDATE_NAV_COUNT` / `IME_SHADOW_ABANDON` の**唯一の入口**である。
→ `IME_ACTIVE` を蘇生させないと nav / abandon は永久に 0 のままになる。

★ **無限ラッチにはならない**: `is_candidate_window_open()` は
`winevent_active && !enumwindows && !uia` を stale とみなして `IME_ACTIVE=false` に落とす。
候補ウィンドウが閉じれば次の周期で自動的に降りる。

## 変更対象

### 修正するファイル
- `src-tauri/src/input/ime_windows.rs` — `is_ime_candidate_window_visible` を `pub` へ (可視性のみ)
- `src-tauri/src/input/ime.rs` — 上記を再エクスポート (Windows 限定)
- `src-tauri/examples/ime_winevent_probe.rs` — 問い 3 (EnumWindows 経路) とクラス名センサスを追加
- `src-tauri/src/lib.rs` — (§A が肯定的なら) IME Monitor スレッドの遷移駆動
- `src-tauri/src/capabilities.rs` — (実測に応じて) `ime_shadow` の区分を再判定

### 新規作成するファイル
- なし (★ 新規 API はゼロ)

## 影響範囲

| 影響先 | 内容 |
|---|---|
| `LogEntry::ImeShadow` | ⚠️ **0 行 → 出るようになる**。⚠️ **意味が変わる** (下記) |
| `LogEntry::ImeState` の `active` | ⚠️ 常に false → 候補ウィンドウ滞在中 true |
| HMM 推論 | ★ **変わらない**。`engine.set_paused(active)` は既に `active` (EnumWindows 込み) で駆動されており、`IME_ACTIVE` の書き込みは pause 判定に新しい情報を足さない |
| ゴールデン NDJSON | ★ リプレイ入力は既存 NDJSON なので **byte-equal のはず**。⚠️ 実測で確認する |

### ⚠️★★★ 意味が変わること (必ず記録する)

| | 旧 (WinEvent 前提・★ ただし 0 行) | ★ 新 (EnumWindows) |
|---|---|---|
| 何を測るか | **composition 中** (ローマ字→ひらがなを含む) | ★ **候補ウィンドウが開いている間** (＝変換中) |
| ⚠️ 取れないもの | — | ⚠️ **候補が出る前の composition 段階** |
| 時間分解能 | WinEvent 到着時刻 (即時) | ⚠️ **100ms ポーリング粒度** |
| `nav_count` の取りこぼし | なし | ⚠️ 候補表示から最大 100ms 以内の矢印キーは数えられない |

`ime_windows.rs:46-48` 逐語: "WinEvent is the only method that reliably detects the
romaji→hiragana composition phase (before the candidate list appears)"
→ ★ その段階は**構造的に失われる**。

★ ただし `ime_dwell_med` が測りたいのは「**変換に迷っている時間**」なので、
候補ウィンドウの滞在時間の方が**むしろ目的に近い**とも言える。
⚠️ **別の量であることを明記した上で**採用する。

## 既存パターンとの整合性

- ★ IME Monitor スレッドの `last_active` 遷移検出は**既にある** (`lib.rs`)。そこに相乗りする
- ★ Atomic の Ordering は `hook-constraints` 共通-2 に従う
  (`IME_SHADOW_READY` は Release / 読み手は AcqRel swap)
- ★ CLI 出力は `std::io::stdout()` + `writeln!` (`bin/replay.rs` と同形。`println!` はガードが弾く)

## テスト戦略

- **単体**: `is_stale_winevent_active` / `is_ime_candidate_class_name` の既存純関数テストは不変。
  遷移駆動を純関数へ切り出せるなら同様にテストする
- **回帰 (最優先)**: `gse-replay --snapshot` のゴールデンが **byte-equal**
- **schema**: `emit_schema` が `schema/current.json` と同一 / parity exit 0
- ⚠️★ **実機**: 実起動ログに `ime_shadow` 行が**実際に出る**ことを見る
  (★ 「実装した」ではなく「**出た**」)

## ロールバック計画

- §A のみ (プローブ + 可視性変更) は**本番挙動を 1 バイトも変えない**ので単独で残せる
- §B は `lib.rs` の IME Monitor スレッド内に閉じるので revert が容易
- ⚠️ `capabilities` を `unconditional` へ戻した場合は**必ず一緒に revert する**
  (過大申告に戻ってしまうため)
