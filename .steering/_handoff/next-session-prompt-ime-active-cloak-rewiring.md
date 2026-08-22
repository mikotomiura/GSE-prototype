# 次セッション開始プロンプト（**Windows 側**）— `IME_ACTIVE` を cloak 経路で復旧する（A）

このファイルの「===」以下をコピペして開始する。
★ **Windows で実行する**（⚠️ cloak/uncloak の実機確認が要る）。

---

===

## §0 ★ このセッションの仕事

| # | 何 | 種別 |
|---|---|---|
| **A-1** | ⚠️★★★ **`IME_ACTIVE` を `CLOAKED`/`UNCLOAKED` ＋ クラス絞りで復旧する** | 実装 |
| **A-2** | ★ **macOS 側を同じ量にするか**を裁く（⚠️ 実装は別セッション・Mac 必須） | 判断 |

⚠️★★★ **収集開始前にしかできない。** ★ 収集が始まると `preregistration.md §3.6` により回復不能。

★ **必ず `/start-task` から始める**（CLAUDE.md 行動規範）。作業記録は
`.steering/[YYYYMMDD]-ime-active-cloak-rewiring/` に置く。

---

## §1 ⚠️★★★ 背景 — **2026-08-22 に実測で確定した。議論し直さない**

### 1.1 ★ 何が分かったか（★ すべて実測。60 秒 × 8 回）

| # | 事実 | 根拠 |
|---|---|---|
| 1 | ★★★ **Windows 11 の IME 候補 UI は `ShowWindow` ではなく DWM の `cloak/uncloak` で表示制御される** | 実測: 変換中に `CLOAK/UNCLOAK` が `IME` ×34 / `Xaml_WindowedPopupClass` ×17 / `ApplicationFrameWindow` ×17 |
| 2 | ⚠️ **正しい `EVENT_OBJECT_IME_*`(0x8027-29) は 1 件も飛ばない** | 60 秒 × 8 回すべて 0 |
| 3 | ⚠️ **`EnumWindows` も UIA も 0** | `is_candidate_window_open()` = 0/2400・立ち上がり 0 |
| 4 | ⚠️ **0x8030 (`CONV_TARGET`) も 0** | ★ UIA プロバイダを起こした状態（`TextEdit` 240/240）・打鍵 282 で 0 |
| 5 | ★★★ **無操作 24 秒で cloak は 1 件も起きない** | 「遠い(>2s)」= **0**（★ false positive が無い） |
| 6 | ★ `IME` : 候補UI : ホストフレーム = **2 : 1 : 1**、dwell 中央値は 3 クラスとも **701ms** | 同上 |

→ ⚠️★★★ **PR #109（定数修正）は「働いていた信号」を消していた。**
★ 旧定数（`IME_SHOW=0x8017`=`CLOAKED` / `IME_HIDE=0x8018`=`UNCLOAKED`）は
**偶然ではなく実際の候補 UI を拾っていた**。
⚠️ ただし旧実装も正しくない —— **クラス絞りが無く、無関係な窓の cloak も混ざる**。

### 1.2 ★ 既に済んでいること（⚠️ やり直さない）

| # | 何 | どこ |
|---|---|---|
| 1 | IME WinEvent 定数の修正 | **PR #109 / v0.1.28**（マージ済み） |
| 2 | `capabilities` の `ime_shadow` を `config_gated` へ | **PR #110**（マージ済み） |
| 3 | ★ **プローブの全診断**（cloak 統計・打鍵計数・UIA 起こし・旧駆動の再現） | `examples/ime_winevent_probe.rs`（★ ブランチ `chore/ime-active-enumwindows-probe`） |
| 4 | ★ 実測記録・撤回記録・論点整理 | `.steering/20260822-ime-active-rewiring/`（★ `findings-enumwindows-probe.md` は **§1-16**） |

⚠️★ **`findings-enumwindows-probe.md` を先に読むこと。** ★ 途中で 3 回結論が変わっており、
**§14 の撤回**と **§15/§16 の確定**を読まないと誤った前提で実装する。

⚠️ **ブランチ `chore/ime-active-enumwindows-probe` は未 push・未マージ**（★ 2026-08-22 時点）。
★ 本タスクはその上に積むか、先にマージするかを最初に決める。

---

## §2 ★ A-1 の設計（★ 実装前にここを読む）

### 2.1 ⚠️★★★ `hook-constraints` Win-1 に抵触させない

★ 判定にクラス名が要るが、⚠️ **WinEvent コールバック内で `GetClassNameW` は呼べない**
（`hook-constraints` Win-1: コールバック内は **Atomic ＋ `try_send` のみ**）。

★ **設計**:

```
win_event_callback (CLOAKED/UNCLOAKED)
  └─ try_send(CloakEvent { hwnd: isize, cloaked: bool })   ← ★ Atomic + try_send のみ
        │
        ▼
  cloak resolver スレッド（新規 or 既存 IME Monitor に相乗り）
        ├─ GetClassNameW(hwnd) でクラス名を解決
        ├─ 対象クラスなら IME_ACTIVE / START_MS / SHADOW_READY を更新
        └─ ⚠️ hwnd は解決に使うだけで **保存も送出もしない**
```

⚠️ `HWND` は `Send` でないので **`isize` で渡す**（★ 既存の `ThreadSafeHook` と同じ発想）。

⚠️★ **WinEvent の購読範囲**: `eventMin`/`eventMax` は**単一の連続範囲**しか取れない。
★ `CLOAKED`(0x8017) / `UNCLOAKED`(0x8018) は現行の IME 範囲（0x8027-0x8029）と**連続していない**
→ ⚠️ **フックをもう 1 本張る**か、範囲を広げてコールバックで弾く。
★ 広げると `0x8017..=0x8029` の全イベントが届くので、**負荷を実測して決めること**。

### 2.2 ⚠️ クラス絞りの選択（★ 実測に基づく）

| クラス | ★ 評価 |
|---|---|
| **`IME`** | ★ **第一候補**。名前が IME 固有。⚠️ **1 変換 = 2 周期**なので畳み込みが要る |
| `Xaml_WindowedPopupClass` | ⚠️ **汎用**（ツールチップ・メニュー・フライアウト）。★ ただし 1 変換 = 1 周期 |
| `ApplicationFrameWindow` | ⚠️ **汎用**（全 UWP のホスト）。★ 単独では使わない |

⚠️★★★ **`ime_windows.rs` の `is_ime_candidate_class_name` は完全一致 `"IME"` を
*明示的に除外* している**（★ 常時可視で false positive を起こした前科・回帰テスト
`excludes_language_bar_and_imm32_system_window` が固定）。
→ ★ **cloak は「可視」と別の軸なので同じ事故にはならない**が、
⚠️ **既存の除外理由と衝突しないよう、別関数として実装しコメントで理由を書き分けること**。
⚠️ **既存の回帰テストを壊さない。**

### 2.3 ⚠️ 1 変換 = 2 周期をどう畳むか

★ 実測で `IME` は 1 変換につき 2 回 cloak/uncloak する。
⚠️ そのまま流すと `ime_shadow` が **変換 1 回につき 2 行**出る。

★ 案（⚠️ どれを採るかは実装セッションで決めてよい。**根拠を `decisions.md` に残すこと**）:
1. ★ **デバウンス**: uncloak 後 N ms 以内の再 cloak を同一セッションとみなす
2. ★ **`Xaml_WindowedPopupClass` を使う**（1 : 1）。⚠️ ただし汎用クラスの誤検知リスク
3. ★ **両方を見て AND を取る**（`IME` かつ 候補UI）

### 2.4 ⚠️ 重なり（`pending` 単一スロット）

★ プローブの実測では **cloak 18 に対し dwell が 8 本**しか取れなかった。
⚠️ **クラス単位の `pending` が単一スロットで、重なった対が畳まれた**ため。
→ ★ **本番実装でも同じ畳み込みが起きる**。⚠️ HWND 別に持つかどうかを決めること。

---

## §3 ⚠️★★★ **A の帰結 — 記録だけの話ではない**（★ ここを飛ばさない）

### 3.1 ★ `engine.set_paused()` が**復活する**

★ `lib.rs` の IME Monitor は毎周期 `engine.set_paused(active)` を呼ぶ。
★ `set_paused` は飾りではなく **`engine.rs:356` / `:499` で `update()` を丸ごと `None` で返すゲート**である。

| 時期 | ⚠️ 実際の挙動 |
|---|---|
| PR #109 以前 | ⚠️ cloak イベントで**無関係に pause**（★ フィルタ無し） |
| **現在（v0.1.28）** | ⚠️ **一度も pause しない**（★ IME イベントが飛ばないため） |
| ★ **A の後** | ★ **変換中に pause する**（＝ 設計意図どおり） |

### 3.2 ⚠️★★★ **推定窓が減る。量を見積もること**

★ 実測: 候補表示 **9 回 / 36 秒の打鍵**、dwell 中央値 **701 ms**。
→ ⚠️ **概算で打鍵時間の 15〜20% が pause 区間になる**。

⚠️★★★ **これは G1（日本語論述）の較正データ量に直接効く。**
★ 「変換中の打鍵で推定を汚さない」という設計意図は正しいが、
⚠️ **収集開始前に量を見積もり、研究者が受け入れるかを決めること。**

### 3.3 ⚠️ **replay 経路にも入っている**（★ Replay-as-Truth の背骨）

★ `analysis/loop_step.rs:302` が `LoopInput::ImeActivate` で
**NDJSON の `ime_state.active` から pause を再構成している**。
→ ⚠️★★★ **A で `active` が true になると、replay の出力も変わる。**

★ **既存ゴールデンは不変**（★ 入力 NDJSON が変わらないため）。
⚠️ **ただし A 以降に収集した NDJSON をリプレイすると、pause 区間で `FeatSnapshot` の出方が変わる。**
→ ★ **受け入れ条件に「既存ゴールデン byte-equal」を必ず入れる**（§5）。

### 3.4 ⚠️ MhD の**入力項目は増えない**

★ `ime_dwell` を推論へ流すことは **ADR-011 D4 が禁じている**（逐語
「`paste` / `keys` / `bs_keys` / `ime_dwell` を推論へ流すことは、現時点では SSOT が置いた順序に反する」）。
→ ★ **A がやるのは「記録を正しい量に戻す」ことと「pause を設計どおりにする」ことだけ。**
⚠️ **推論への配線（段 3）は G1 判定後。本セッションでは行わない。**

---

## §4 ★ A-2 — macOS を同じ量にするか（★ 判断のみ。実装は Mac セッション）

### 4.1 ⚠️★★★ **A は非対称を作る**

| | Windows（★ A の後） | macOS（現状） |
|---|---|---|
| `IME_ACTIVE` の出所 | ★ **観測**（候補 UI の cloak/uncloak） | ⚠️ **推定**（`hook_macos.rs::update_compose_state` の keycode ヒューリスティック） |
| `ime_shadow` | ★ **出る** | ⚠️★★★ **構造的に出ない**（`emit_ime_shadow` が `#[cfg(target_os = "windows")]`） |

⚠️★★★ **これは 2026-08-22 に混乱の原因になったのと同じ非対称である**
（★ `personalization §49` の「4 割で欠測」は、実は **macOS に計器が無い**という意味だった）。
→ ★ **A を Windows 単独で入れると、その非対称を *設計として固定する* ことになる。**

### 4.2 ★ macOS に**同じ量**を取る道はある（⚠️ ただし制約付き）

★ サーヴェイ逐語（`.steering/20260821-workspace-behavior-triage/survey-input-channels.md §7.5`）:

> **候補ウィンドウの検知**: ★ `kCGWindowLayer` / `kCGWindowOwnerPID` は
> **Screen Recording 権限なしで取れる**（⚠️ `kCGWindowName` だけが gated）。
> ⚠️ しかし (i) **通知が無くポーリング専用**、(ii) **変換前（ローマ字入力中・下線のみ）は候補窓が出ない**

★★★ **重要**: (ii) の限界は **A 後の Windows にも等しく当たる** ——
★ cloak が飛ぶのは**候補ウィンドウが出るとき**であって、ローマ字入力中ではない。
→ ⚠️★★★ **A を入れると Windows 側の意味も「候補ウィンドウ滞在」に変わる**ので、
★ **両 OS が初めて *同じ量* を測れるようになる。**

⚠️ **残る非対称**: macOS 純正の「ライブ変換」は Space を押さずに変換が進む（`survey §3.2`）。
★ 候補窓の出方が違う可能性がある。⚠️ **実機確認が要る。**

⚠️★★ `survey §7.6` の設計提案（「**推定器は下に揃え、較正と評価は上を使う**」）とも
整合するかを確認すること。★ `FeatSnapshot` スキーマも `HMM_VERSION` も OS で割らない。

### 4.3 ★ 決めること

| 選択肢 | 含意 |
|---|---|
| **(a) A-1 のみ（Windows 単独）で収集開始** | ★ 早い。⚠️ **非対称を設計として固定**。★ `capabilities` の `config_gated` が申告するので偽の結論にはならない |
| **(b) A-2（macOS `kCGWindowList` ポーリング）まで待つ** | ★ **両 OS が同じ量になる**。⚠️ Mac セッションが要る・収集開始が遅れる |
| **(c) A-1 を入れ、A-2 は収集開始後に追加しない** | ⚠️ **(a) と同じ**。★ 記録仕様は収集中に変えられない |

⚠️★★★ **dev では決められない**（★ 収集スケジュールと募集の問題）。**研究者判断**。
→ ★ 本セッションでは **判断を仰ぎ、`decisions.md` に記録する**。

---

## §5 ★ 受け入れ条件（★ 全部 exit code で確認する）

- [ ] `cargo fmt --all -- --check` = 0
- [ ] `cargo test --workspace` = 0
- [ ] `cargo clippy --all-targets` = 0（★ 変更ファイルの警告 0 件）
- [ ] ★★★ **既存ゴールデンが byte-equal**
      （`cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`）
- [ ] `emit_schema` が `schema/current.json` と byte-equal
- [ ] `python scripts/check_schema_parity.py --dataset C:/gse-dataset` = 0
- [ ] ⚠️★★★ **実起動ログで `ime_shadow` 行が実際に出る**（★ 「実装した」ではなく「**出た**」）
- [ ] ⚠️★★★ **無操作 60 秒で `ime_shadow` が 1 行も出ない**（★ false positive の回帰確認）
- [ ] ★ `capabilities` をどう扱ったか記録（⚠️ **1 台でしか確認していないので `config_gated` 据え置きが安全**）
- [ ] ★ §3.2 の **pause 区間の割合**を実測して記録
- [ ] ★ `decisions.md` に (i) クラス絞り (ii) 2 周期の畳み込み (iii) A-2 の判断 を記録
- [ ] ★ `code-reviewer` + `security-checker` を**並列**起動 → HIGH 対応
- [ ] ★ `/cross-review`（⚠️ `run-codex-review.sh -- <paths>` でパス限定。★ `findings-*.md` は**外部へ渡さない**）

---

## §6 ⚠️ 落とし穴（★ 2026-08-22 に実際に踏んだもの）

1. ⚠️★★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/` にある）
2. ⚠️★★ **git-bash ではパスにバックスラッシュを使わない**（★ `cd /c/GSE-prototype/src-tauri`）
3. ⚠️ **Windows コンソールは cp932** → Python は `PYTHONUTF8=1`。★ 非 ASCII を print すると落ちる
4. ⚠️★ **`.rs` に `println!`/`eprintln!` を書くとガードに止められる**（★ コメント内の文字列でも）。
   ★ CLI 出力は `std::io::stdout()` ＋ `writeln!`
5. ⚠️★★★ **このリポジトリは `anyhow` を依存に持たない**
   （`overlay_panel.rs:40` 逐語「このリポジトリは anyhow を依存に持たず」）。
   ★ `std::io::Error::other` か `Result<_, String>` を使う
6. ⚠️ `| tail` にパイプすると `$?` が tail のものになる → **リダイレクトしてから `echo $?`**
7. ⚠️ `.claude/settings.json` / `.gitignore` に**タスクと無関係の未コミット変更**がある（★ commit しない）
8. ⚠️★★★ **null 結果を主張する前に「入力が実際に起きたか」を確認する**
   ★ プローブは `WH_KEYBOARD_LL` で打鍵を数えており、**30 未満なら判定に使えない**と表示する
9. ⚠️ **長い heredoc は git-bash のクォートで壊れることがある** → ★ Write ツールか Python で書く

---

## §7 ★ 完了報告に必ず書くこと

- [ ] ★ **どのクラスで絞ったか**と、その根拠
- [ ] ★ **2 周期をどう畳んだか**
- [ ] ⚠️★★★ **pause 区間が全体の何 % になったか**（★ 実測値）
- [ ] ★ 実起動ログで `ime_shadow` が**出たか**／無操作で**出なかったか**
- [ ] ★ ゴールデン / schema / parity の**実測 exit code**
- [ ] ⚠️ **`capabilities` をどう扱ったか**（★ 据え置き推奨）
- [ ] ★ **A-2（macOS）の研究者判断**（a/b/c のどれか）

---

## §8 ⚠️ 本タスクの外にあるもの（★ 混ぜない）

- ⚠️ **v0.1.28 のリリース**（★ タグ `v0.1.28` は**まだ無い**。最新は `v0.1.27`）は
  **Mac 側担当**（`_handoff/next-session-prompt-v0128-release-and-redistribution.md` §2-3 以降）
- ⚠️ **ADR-014 の研究者判断 6 件**（★ 律速は判断 1「R3 の対象者」）は
  `.steering/20260822-ime-active-rewiring/adr014-open-decisions.md` に依存グラフ付きで整理済み
- ⚠️ **`ime_dwell_med` の再解釈**（★ →Q2 = 0.729 の系列）は
  `findings-enumwindows-probe.md §13-15` に記録済み。**本タスクでは触らない**
- ⚠️ **推論への配線（段 3）** は **ADR-011 D4 により G1 判定後**
