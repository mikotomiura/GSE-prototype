# 次セッション開始プロンプト（**Windows 側**）— `IME_ACTIVE` の配線を直し、`.idea` の残りを議論する

このファイルの「===」以下をコピペして開始する。
★ **Windows で実行する**（⚠️ `EnumWindows` / WinEvent の実機確認が要る）。

---

===

## §0 ★ このセッションの 2 つの仕事（★ 優先順）

| # | 何 | 種別 |
|---|---|---|
| **B** | ⚠️★★★ **`IME_ACTIVE` の配線を直す**（★ 収集開始前にしかできない） | 実装 |
| **C** | `.idea/20260819-…` の残り論点と ADR-014 の凍結 | 議論 |

⚠️★★★ **B を先にやる。** ★ **収集が始まると `preregistration.md §3.6` により回復不能**になる。

---

## §1 ⚠️★★★ B の背景 — **実測で分かったこと**（★ 議論し直さない）

### 1.1 ★ 何が起きているか

2026-08-22 に `examples/ime_winevent_probe.rs` で **60 秒 × 3 回**測った結果:

| 実測 | 数値 |
|---|---|
| ★ フックは**完全に生きている** | `alive = 6544`（0x8000-0x8030 の全オブジェクトイベント） |
| ★★★ **日本語入力は確かに行われた** | `TEXTSELECTIONCHANGED` **298** / `VALUECHANGE` **246** / `CREATE` **680** = `DESTROY` **680** / `SHOW` **1645** / `HIDE` **1624** |
| ⚠️★★★ **IME イベントは 1 件も飛ばない** | `EVENT_OBJECT_IME_SHOW`(0x8027) / `IME_HIDE`(0x8028) / `IME_CHANGE`(0x8029) / `CONV_TARGET`(0x8030) **すべて 0** |
| ⚠️ `ImmGetContext` は**一度も成功しない** | 試行 120 / **成功 0**（★ repo の既存記録どおり） |
| ⚠️ 旧定数の**誤検知率** | `CLOAKED` 84 ＋ `UNCLOAKED` 88 = **60 秒で 172 件**（★ G1 の 5 分ブロックなら約 860 件） |

→ ★★★ **この Windows 11 の IME は候補 UI を *汎用イベント* で表現しており、MSAA の IME イベントを上げない。**

### 1.2 ⚠️★★★ **配線の非対称**（★ これが B で直す対象）

| 何 | 駆動源 | 状態 |
|---|---|---|
| `is_candidate_window_open()`（**問い合わせ**・`ime_windows.rs:61`） | ★ WinEvent **OR** EnumWindows **OR** UIA | ★ **動く**（★ `lib.rs:2731` が毎周期呼んでいる） |
| ⚠️ `IME_ACTIVE`（**Atomic**） | ⚠️★★★ **WinEvent コールバックだけが `true` を書く**（`hook_windows.rs:209`） | ⚠️ **死んでいる** |
| `ime_shadow` / `dwell_ms` / `nav` | ⚠️ **Atomic 側**（`IME_SHADOW_READY` は WinEvent の `IME_HIDE` 枝でしか立たない） | ⚠️ **0 行** |

→ ★★★ **働く検出器（EnumWindows）が「無効化用（stale 判定）」にしか繋がっておらず、
データを産む側は死んだ経路（WinEvent）に繋がっている。**

### 1.3 ★ 既に済んでいること（⚠️ やり直さない）

| # | 何 | どこ |
|---|---|---|
| 1 | ★ **IME WinEvent 定数の修正**（0x8016-18 → 0x8027-29）＋ 範囲を `(SHOW, CHANGE)` へ | **PR #109 / v0.1.28**（マージ済み） |
| 2 | ★ **`capabilities` の `ime_shadow` を `unconditional` → `config_gated` へ**（＝ 0 行を「判定不能」と読ませる） | ★ **A**（本引き継ぎの直前に実施） |
| 3 | ★ 診断ツール `examples/ime_winevent_probe.rs` | 同上 |

---

## §2 ★ B の作業（★ 新規 API はゼロ）

### 2.1 ⚠️ 先に実機で確かめる（★ これを飛ばさない）

★ **`is_candidate_window_open()` の EnumWindows 経路が実際に効くか**を測る。
⚠️ **今回のプローブは WinEvent しか測っておらず、EnumWindows 経路は未計測である。**

```bash
cd src-tauri
cargo run --example ime_winevent_probe   # ★ 60 秒・日本語入力 → 変換 → ←→ で文節移動
```

⚠️★ **プローブに `is_ime_candidate_window_visible()` の呼び出しを足してから測る**こと
（★ 現状のプローブは WinEvent とヒストグラムと IMM しか見ていない）。

| 結果 | ★ 次 |
|---|---|
| ★ EnumWindows が候補ウィンドウを**検出する** | ★ **2.2 へ進む** |
| ⚠️ 検出しない | ⚠️★★★ **B は成立しない。** ★ `IME_ACTIVE` は「取れない」と結論し、`config_gated` のまま据え置く（★ A で既に安全側になっている） |

### 2.2 ★ 配線（★ `hook-constraints` に触れない）

★ **`lib.rs:2731` の `active`（＝ `is_candidate_window_open()` の戻り値）を `IME_ACTIVE` の
*正の駆動源* にする。** ⚠️ **コールバック内ではなく既存のポーリングスレッドで行う**ので、
`hook-constraints` Win-1（コールバック内は Atomic ＋ `try_send` のみ）に抵触しない。

- `false → true` の遷移 → `IME_COMPOSITION_START_MS` を刻む / `IME_CANDIDATE_NAV_COUNT` をリセット
- `true → false` の遷移 → `dwell_ms` を計算し `IME_SHADOW_READY` を立てる

⚠️★★★ **意味が変わることを必ず記録する。**

| | 旧（WinEvent 前提） | ★ 新（EnumWindows） |
|---|---|---|
| 何を測るか | **composition 中**（ローマ字→ひらがなを含む） | ★ **候補ウィンドウが開いている間**（＝変換中） |
| ⚠️ 取れないもの | — | ⚠️ **候補が出る前の composition 段階**（`ime_windows.rs:46-48` 逐語「WinEvent is the only method that reliably detects the romaji→hiragana composition phase」） |

★ **`ime_dwell_med` が測りたいのは「変換に迷っている時間」**なので、
⚠️ **候補ウィンドウの滞在時間の方がむしろ目的に近い**とも言える。★ ただし**別の量である**ことを明記する。

### 2.3 ⚠️ B を入れたら `capabilities` を見直す

★ **`ime_shadow` が実際に出るようになるなら `unconditional` へ戻すか**を判断する。
⚠️ ただし **EnumWindows も環境依存**（IME / アプリのクラス名に依存）なので、
★ **`config_gated` のままが安全**である可能性が高い。⚠️ **実測で決める。**

### 2.4 ★ 受け入れ条件

- [ ] `cargo test --workspace` 緑
- [ ] ★★★ **ゴールデンが byte-equal**（⚠️ 変わったら `HMM_VERSION` の扱いを裁く）
- [ ] `emit_schema` が `schema/current.json` と同一 / schema parity exit 0
- [ ] ⚠️ **実起動ログで `ime_shadow` 行が実際に出る**（★ 「実装した」ではなく「**出た**」を見る）
- [ ] ★ `.steering/` に**意味が変わったこと**を記録

---

## §3 ★ C — `.idea` の残りと ADR-014 の凍結（★ B の後）

### 3.1 ⚠️ 先に読む

| # | 何 |
|---|---|
| 1 | ★★★ `.steering/20260821-workspace-behavior-triage/triage.md`（**突き合わせ表**・★ 再導出しない） |
| 2 | ★★★ `docs/adr/ADR-014-continuous-natural-work-collection.md`（**Proposed**） |
| 3 | ★ `.steering/20260821-workspace-behavior-triage/survey-input-channels.md`（**§5 の段 1 候補表** / §6 アイドル分離 / §7 TSF） |
| 4 | `.steering/20260821-workspace-behavior-triage/decisions.md` D-1〜D-19 |

### 3.2 ★ 閉じるべきこと

| # | 何 | ⚠️ 状態 |
|---|---|---|
| 1 | **ADR-014 の研究者判断 6 件** | ⚠️ 対象者 / 同意文言 / 倫理審査 / 開始時期 / **argumentative lock 解除** / **`consent.md` の粒度ずれ** |
| 2 | ★ **R3 の段 1 を凍結する**（ADR-014 Migration 3） | ⚠️ **凍結したら候補を足さない** |
| 3 | ⚠️ `triage.md §D` の**閉じなかった 4 件** | L-d の feasibility / `vibe_coding` の判定量 / 6 段階 ablation の事前宣言 / R3 の同意粒度 |

### 3.3 ⚠️ やらないこと

- ⚠️ **`docs/research-positioning.md §5` を変更しない**（研究者確認が要る節）
- ⚠️ **ADR-009 の X 軸・現行 G1 を動かさない**
- ⚠️ **利得を主張する語を使わない**（ADR-012 の禁止語規約）

---

## §4 ⚠️ 落とし穴（★ 実測）

1. ⚠️★★★ **`| tail` にパイプすると `$?` が tail のものになる** → リダイレクトしてから `echo $?`
2. ⚠️★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/` にある）
3. ⚠️ **Windows コンソールは cp932** → Python は `PYTHONUTF8=1`
4. ⚠️★ **`.rs` に `println!`/`eprintln!` を書くとガードに止められる**（★ **コメント内の文字列でも止まる**）。
   ★ CLI 出力は `std::io::stdout()` ＋ `writeln!` を使う（`bin/replay.rs` と同じ形）
5. ⚠️ `.claude/settings.json` / `.gitignore` に**タスクと無関係の未コミット変更**が残っている（★ commit しない）

## §5 ★ 完了報告に必ず書くこと

- [ ] ★ **EnumWindows 経路が実測で効いたか**（⚠️ 効かなければ B は不成立と明記）
- [ ] ⚠️ **意味が変わったこと**（composition → 候補ウィンドウ滞在）
- [ ] ★ ゴールデン / schema / parity の**実測 exit code**
- [ ] ⚠️ **`capabilities` をどう扱ったか**（`config_gated` 据え置きか `unconditional` へ戻したか）
- [ ] ★ ADR-014 の研究者判断のうち**埋まったもの / 埋まらなかったもの**
