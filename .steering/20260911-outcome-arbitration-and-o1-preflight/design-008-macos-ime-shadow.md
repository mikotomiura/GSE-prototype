# 設計 — issue 008: macOS で IME の確定 / 放棄を判別する

> 作成: 2026-09-11 / 対象 issue: `issues/008.md` / ブランチ: `feat/macos-ime-shadow`
> ⚠️ 本ファイルが 008 の設計 SSOT。`design.md`（テンプレのまま）は本タスク全体用。

## 1. 調査で確定した事実（★ 一次資料はコード本体）

| # | 事実 | 一次資料 |
|---|---|---|
| 1 | **Windows の `abandon` / `nav` は WinEvent 由来ではなく「打鍵推論」である** | `input/hook_windows.rs:188-194` `classify_ime_nav_key`（`0x1B`→`Abandon` / `0x25..0x28`→`Navigate`）を `hook_windows.rs:659-670` が `IME_ACTIVE` 中の keydown に当てている |
| 2 | Windows で **WinEvent 由来なのは `dwell_ms` だけ** | `hook_windows.rs:297-308`（`IME_SHOW`→`START_MS` / `IME_HIDE`→`DWELL_MS`）。⚠️ 実機ではこの経路が飛ばず、実質 cloak 経路（`ime_cloak.rs`）が駆動している |
| 3 | **macOS には既に「確定 / 放棄」を区別する状態機械が存在する** | `input/hook_macos.rs:688-700` — `0x0D`(Enter) と `0x1B`(Escape) を**別の match 腕**で処理している。⚠️ **どちらも同じ reset をするだけで、区別を記録していない** |
| 4 | macOS の `ime_shadow` 送出元は構造的に無い | `capabilities.rs:197-199`（`#[cfg(target_os = "windows")] v.push("ime_shadow")`）/ `lib.rs:3145` `#[cfg(target_os = "windows")] fn emit_ime_shadow` |
| 5 | `ime_shadow` の行型は **schema に既にある**（`t`/`dwell_ms`/`nav`/`abandon`） | `schema_dto.rs:278-283` |
| 6 | ⚠️ **doc コメントは `current.json` の `description` に載る** | `schema/current.json` に「IME 変換セッションの影ログ (Phase 2b, Windows のみ)。」が実在（実測） |
| 7 | OS 非依存の純ロジックを `input/` に置く先例がある | `input/mod.rs:5-9` — `ime_cloak` は「**OS 非依存にしてあるので `#[cfg]` を付けない。そうすると macOS の CI でも `CloakFold` のテストが走る**」 |
| 8 | ⚠️★★★ **`key` 行の `category` は `escape` と `enter` を別カテゴリとして残す** | `analysis/anonymize.rs:16-56`（14 種）/ `schema_dto.rs:116-124` |
| 9 | ⚠️★★★ **2026-08-23 の研究者判断 D-9 が「Win=観測 / mac=推定 の非対称を設計として固定する」と決めている** | `.steering/20260823-ime-active-cloak-rewiring/decisions.md:201-215` / `_handoff/next-session-prompt-v0129-release-and-redistribution.md §5.1` |
| 10 | macOS の公開 API では composition を観測できない（★ **全数確認**: AX 定数 101+9+25=135 個すべてに該当なし・`NSTextInputClient` は in-process・IMKit は独立プロセス） | `survey-input-channels.md §7.5` |

### ★ 結論

**macOS で新しい OS API は要らない。** Windows が `abandon`/`nav` に使っているのと
**同型の打鍵推論**を、macOS 側の既存状態機械から**記録するだけ**で判別できる。
⚠️ 差が出るのは `dwell_ms` の由来だけ（Windows = 窓イベント / macOS = 打鍵）。→ §5 で明記する。

## 2. 採用する方針

**打鍵推論による `ime_shadow` の macOS 実装 + 判断ロジックの OS 非依存モジュール化。**

### 2.1 なぜ純ロジックを切り出すか（★ ここが設計の肝）

⚠️ `hook_macos.rs` の `#[cfg(test)] mod tests` は **Windows では 1 行も走らない**
（`hook_macos.rs:1195-1202` が自分でそう書いている）。
→ ★ 状態機械を `hook_macos.rs` に書くと、**Windows 側の CI も開発機も一切検証しない**。
`docs/agent-shared.md` の「OS ごとに規則が違うロジックは両 OS に対のテストを置く」に反する。

→ ★ **`ime_cloak.rs` と同じ形にする**: 純粋な畳み込み器を `#[cfg]` 無しのモジュールに置き、
`hook_macos.rs` は atomics を駆動する薄いドライバにする。**両 OS の CI でテストが走る。**

### 2.2 セッションの定義（macOS）

| 項目 | 定義 |
|---|---|
| 開始 | `IME_OPEN` 中に英数字キー（`0x30..=0x39` / `0x41..=0x5A`）が押され、`composing` が false→true になった時 |
| 終了（確定） | `Enter`(`0x0D`) / **その他キー**（Tab・記号など。IME の自動確定にあたる） |
| 終了（放棄） | `Escape`(`0x1B`) → `abandon = true` |
| 終了（モード離脱） | `IME_OPEN` が false の状態でキーが押された（かな→英数 切替など）→ 確定扱い |
| `nav` | セッション中（`composing \|\| active`）の矢印キー `0x25..=0x28` の押下回数 |
| 上限 | `MAX_SESSION_MS`(20s) 超過は **行を出さない**（⚠️ 上限そのものを dwell と偽らない） |

⚠️ Windows の `IME_ACTIVE` は実測で**変換セッション全体（ローマ字入力〜確定）**を覆う
（`ime_cloak.rs:155-166`）。→ ★ macOS 側も `composing` の寿命に合わせるのが同型であり、
`active`（Space 後の候補表示）に合わせると**短すぎて対応しない**。

## 3. 変更対象

| ファイル | 変更 | Allowed Files |
|---|---|---|
| `src-tauri/src/input/ime_compose.rs` | **新規**。`ComposeFold`（純粋・OS 非依存） | ⚠️ **追加**（§6） |
| `src-tauri/src/input/mod.rs` | `pub mod ime_compose;` | ⚠️ **追加** |
| `src-tauri/src/input/hook.rs` | shadow atomics の `#[cfg(windows)]` を両 OS へ開く | ⚠️ **追加** |
| `src-tauri/src/input/hook_macos.rs` | `update_compose_state` を `ComposeFold` へ委譲し atomics を駆動 | ⚠️ **追加** |
| `src-tauri/src/lib.rs` | `emit_ime_shadow` の `#[cfg]` を外す / READY ポーリング経路を両 OS 有効化 | ⚠️ **追加** |
| `src-tauri/src/capabilities.rs` | `config_gated` の push を両 OS に。テスト 3 本を改訂 | ✅ issue 記載 |
| `src-tauri/src/schema_dto.rs` | `ImeShadow` の doc から「Windows のみ」を外し、由来の差を明記 | ✅ issue 記載 |
| `src-tauri/schema/current.json` | 上記に伴う**意図的再生成** | ✅ issue 記載 |

⚠️ `input/ime_macos.rs` は **触らない見込み**（issue の Allowed Files は実体と食い違っていた・§6）。

### 3.1 ⚠️ `lib.rs` の 3 経路のうち **1 つだけ**を macOS で有効にする

| 経路 | 場所 | macOS |
|---|---|---|
| stale valve（`IME_ACTIVE` が 25 秒スタック） | `lib.rs:3519` | ⚠️ **Windows 限定のまま** |
| `active → false` 遷移 | `lib.rs:3544` | ⚠️★★★ **Windows 限定のまま** |
| `IME_SHADOW_READY` ポーリング | `lib.rs:3559` | ★ **両 OS で有効化** |

⚠️★★★ **遷移経路を macOS で開いてはならない。** macOS の `IME_ACTIVE` は
「候補表示中に別の字を打った」「候補表示中に Backspace」でも false に落ちる
(`hook_macos.rs:665` / `:700`) が、これは**セッションの途中**である。
→ ここで `emit_ime_shadow` を呼ぶと stale 経路（`lib.rs:3170` の `START_MS>0` 分岐）が
**セッション途中の偽の行を出し、`START_MS` を 0 にしてセッションを壊す。**

★ READY ポーリング経路だけなら、`READY.swap(false)` が true の時しか入らないので安全。

## 4. テスト戦略

| # | テスト | 走る OS |
|---|---|---|
| T1 | `ime_compose.rs` の `ComposeFold` 単体（確定 / 放棄 / nav / 上限 / モード離脱 / 二重開始） | ★ **両 OS** |
| T2 | `capabilities.rs` の OS 対テスト改訂（両 OS で `ime_shadow` が宣言される） | ★ 両 OS（`#[cfg]` で対） |
| T3 | `lib.rs` の送出元 `#[cfg]` をソース文字列で検査（`capabilities.rs` の既存様式を踏襲） | ★ 両 OS |
| T4 | `hook_macos.rs` のドライバ（atomics 駆動）の回帰 | ⚠️ macOS のみ |
| T5 | ゴールデン `minimal.ndjson --snapshot` | ★ 両 OS |
| T6 | `emit_schema` parity | ★ 両 OS |

⚠️★★★ **AC 6（macOS 実機で確定 / 放棄が区別できること）は本機（Windows）では実施できない。**
→ §7 に引き継ぎとして明記する。

## 5. ⚠️ 忠実度の差（★ 記録しないと解析が誤読する）

| 項目 | Windows | macOS |
|---|---|---|
| `dwell_ms` の由来 | 窓イベント（`EVENT_OBJECT_IME_*` / DWM cloak） | ★ **打鍵推論**（最初の英数字キー〜終端キー） |
| `nav` / `abandon` の由来 | 打鍵推論 | 打鍵推論（**同型**） |
| 取りこぼし | ⚠️ IME/アプリによって丸ごと出ない（実測） | ⚠️ ANSI キーボードでは `IME_OPEN` が 100ms TIS ポーリング由来のため、**セッション先頭を落としうる** |
| マウスで候補確定 | 窓イベントで拾える | ⚠️ **拾えない**（打鍵が無い） |

→ ★ `config_gated`（**0 行は判定不能**）のままにする。⚠️ `unconditional` に上げない。

## 6. ⚠️ issue 008 の Allowed Files は実体と食い違っていた

issue は `ime_macos.rs` / `capabilities.rs` / `schema_dto.rs` / `current.json` の 4 つを挙げるが、
**macOS の IME 状態機械は `ime_macos.rs` ではなく `hook_macos.rs` にある**
（`ime_macos.rs` は TIS ポーリングと `ImeMonitor` だけ）。
shadow atomics は `hook.rs`、送出は `lib.rs` にある。→ ★ Allowed Files を §3 の表へ拡張する。

⚠️ issue 009（修飾キー同時押下フラグ）とは `hook_macos.rs` / `hook_windows.rs` /
`schema_dto.rs` で**交差する**。→ ★ issue 008 が先に完了してから 009 に着手する
（issue 008 の Dependencies が既にそう指示している）。

## 7. 実行結果（2026-09-11）

★ コミット `bd5e6b8`（ブランチ `feat/macos-ime-shadow`）。
★ 受け入れ条件の結果は `issues/008.md` の Execution Result が SSOT。

- ✅ `cargo test --workspace`: **636 passed / 0 failed**（ベースライン 577 → +59）
- ✅ ゴールデン: `OK: 15 snapshots match`
- ✅ `cargo fmt --check`: 差分なし
- ✅ schema drift check（CI と同じ `diff -u`）: PASS。⚠️ 差分は `description` **1 行のみ**
- ⚠️★★★ **AC 6（macOS 実機）は未実施**（本機は Windows）→ `blockers.md` 起票 4

### ★ §3 からの設計変更（実装中に判明したこと）

⚠️ **§2.1 で「`hook_macos.rs` は薄いドライバにする」と書いたが、それでも足りなかった。**
★ ドライバ（Atomic への書き戻し層）を `hook_macos.rs` に置くと、**そこも Windows では
1 行も走らない**。→ ★ `hook.rs::IME_COMPOSING` の `#[cfg(target_os = "macos")]` を外し、
**ドライバ `ime_compose::drive` ごと OS 非依存にした**。

→ ★ **macOS 専用に残ったのは `hook_macos.rs` の呼び出し 1 行だけ**になった。
⚠️ 実機でしか確かめられないのは「CGEventTap がそのキーを届けるか」だけである。

### ⚠️ 実装中に見つけた落とし穴（★ 記録しないと再発する）

1. ⚠️★★★ **`nav` / `abandon` をセッション外でも Atomic へ書き戻すと、放棄フラグが消える。**
   セッション終了後・IME Monitor の 100ms ポーリングが来る前に英数キーが 1 つ来ると、
   `next.abandon = false` で上書きされる。→ ★ **セッション中のときだけ書く**。
   回帰テスト: `a_keystroke_after_the_session_does_not_erase_the_pending_row`
2. ⚠️★★★ **`lib.rs` の `active → false` 遷移経路を macOS で開いてはならない**（§3.1）。
3. ⚠️ **旧 `update_compose_state` にはコールバック内 `tracing::debug!` が 5 か所あった** ——
   `hook-constraints` 共通-1 違反。★ 移設ついでに撤去した。

## 8. ロールバック / 未完了の引き継ぎ

- ロールバック: ブランチ `feat/macos-ime-shadow` を破棄すれば main は無傷。
- ⚠️★★★ **AC 6（macOS 実機確認）は未実施** → `blockers.md` 起票 4。
  ★ **まず PR を出して self-hosted macOS runner の `check` を通すこと**
  （⚠️ 本機では macOS のコンパイルすら通していない）。
- ⚠️ `schema/current.json` 再生成 → `gse-dataset` 側と drift → `blockers.md` 起票 5。
- ⚠️ ライブ変換下での ESC の意味 → `blockers.md` 起票 6。
- ★ **再配布はしない**（`decisions.md` 判断 8）。既配布ぶんの macOS の確定 / 放棄は
  `key` 行の `category` から事後再構成する。⚠️ **その実装は別タスクで起票する**。
