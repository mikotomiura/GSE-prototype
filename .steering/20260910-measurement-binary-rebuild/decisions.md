# decisions

## D1 ⚠️★★★ 引き継ぎ §5 の「記録だけ救出してから削除」は **前提が古い** —— 救出は不要

★ 引き継ぎ (`next-session-prompt-after-cpu-instrument-fix.md` §5) と
`.steering/20260910-intake-windows-and-cpu-convention/decisions.md` D3 は逐語で
「`.steering/20260708-*` **3 ディレクトリ**＋ `_handoff/next-session-prompt-phase1-prep.md` が
**main に無い** → **記録だけ救出してから削除**」としていた。

⚠️ **一次資料で確かめると、4 件とも main に既にある**（★ しかも**中身が同一**）:

```
$ git ls-tree -r --name-only main -- .steering/20260708-form-clearform-guard | wc -l   → 3
$ ... 20260708-phase1-reminder-emails → 4 / 20260708-reminder-plan-tab → 4
$ ... _handoff/next-session-prompt-phase1-prep.md → 1
$ git diff --stat main feature/phase1-reminder-and-dashboard -- <上記4件>
  (出力なし ＝ ★ 差分ゼロ)
```

★ ブランチにあって main に無いファイルは **5 本だけ**で、⚠️ **全部 main が意図して消したもの**:

| ファイル | ★ main で消えている理由 |
|---|---|
| `src-tauri/src/wall_server.rs` | ★ ADR-015 で Lv2 Wall 削除 |
| `docs/gse-v2-redesign.md` | ★ 旧設計 docs の撤去（PR #72） |
| `docs/[提案プロジェクト補足資料]GSE_proposal_参考文献.md` | ★ `docs/references.md` へ統合（PR #73） |
| `.claude/commands/implement.md` | ★ 現行コマンド体系に無い |
| `memo` | ★ 追跡外の作業メモ |

★ 逆に `Form_G1/` `Form_O1/` の **13 ファイル・14,069 行**は **main にしか無い**。

→ ★ **結論: 救出すべき記録は無い。ブランチは削除して失うものが無い。**
⚠️ **ただし削除は私からは実行しない**（★ 作業規約・外界操作）。研究者判断へ回す。

⚠️★★★ 教訓: ★ 引き継ぎメモ（三次資料）の「main に無い」を**そのまま作業にしない**。
★ `git ls-tree` / `git diff` の 2 行で反証できた（`verify-before-claiming` ルール 1）。

## D2 ★ 走っていた 8h 再測を **停止して破棄**した（★ 版が違うため）

★ 12:04 開始の `results/with-gse-20260910-macos-8h` は **v0.1.31** を測っていた
（⚠️ 引き継ぎ §3-2 が「配布物と違う版を測っている」と指摘したその状態のまま）。
→ ★ 45 分時点で停止し `_aborted-with-gse-20260910-macos-8h-v0131/` へ**退避**（⚠️ 削除していない）。
★ 理由: ⚠️ **ビルドは計測を汚す**うえ、★ 測っても配布物 (v0.1.33) の値にならない。

## D3 ⚠️ 計測用フォルダの注意書きが**実体と食い違っている**（★ 観測のみ・変更していない）

★ `~/Desktop/O1_計測用_macOS/これは計測用です.txt` は逐語で
「⚠️ 自動提出は外してあります（`~/.gse/o1_consent_ack` を `.bak` へ退避）」と書いている。

⚠️ **一次資料は違う**: `ls -la ~/.gse/` に `o1_consent_ack`（**2026-08-30**）が**実在**し、
★ `.bak` は**無い**。→ ⚠️ **注意書きが書かれた後に武装し直されている**。

★ また同ファイルの「版: v0.1.31」は正しい（★ ゲート ① と一致）が、
⚠️ 差し替え後は**この記述も更新しないと三次資料が実体からずれる**。

→ ★ 対応: ① 差し替え時に注意書きの版を更新する。
② ⚠️ `o1_consent_ack` の扱い（外すか残すか）は**研究者判断**として報告する（★ 私は触らない）。

## D4 ★ §4 取り込みの下調べ（⚠️ **取り込みは未実施**・判断材料のみ）

⚠️ 引き継ぎ §4 が最大のリスクとした「`analysis/metrics.rs` +909 行 ＝
`recovery` → `pflow_exit` の改名。★ `HMM_VERSION` の bump が要るか／ゴールデンが割れないか」を
**一次資料（git diff）で見た**:

| ★ 確認したこと | ⚠️ 実測 |
|---|---|
| `src-tauri/src/analysis/engine.rs` の差分 | ★ **無し** |
| `src-tauri/src/schema_dto.rs` の差分 | ★ **無し** |
| 改名が乗っている経路 | ★ `--metrics`（`compute_outcome_metrics`）。⚠️ `--snapshot`（`FeatSnapshot` byte-equal）**ではない** |

→ ★ **見立て**: `HMM_VERSION` の bump は**要らない**・ゴールデン snapshot は**割れない**。
⚠️★★★ **ただしこれは diff を読んだだけの見立てであり、実測ではない。**
★ 取り込む時は必ず `gse-replay --snapshot` を**走らせて**確かめること。

★ 改名の**下流の消費者**（⚠️ 取り込むなら一緒に直す）:
`scripts/build_analysis_db.py` / `scripts/fixtures/analysis_join/metrics/**.metrics.json` **4 本**
（★ ブランチ側で更新済み）／⚠️ **docs 14 本**が旧名を書いている
（★ うち `docs/adr/ADR-018,019,020` は**本文を書き換えない規約**なので**そのまま残す**）。

★ 規模は `git diff --stat main origin/feat/resumption-outcome-arbitration` で
**214 ファイル / +26,664 行** ＝ ⚠️ **1 セッションで終わる量ではない**。系統ごとに分けて出すこと。

## D5 ⚠️★★★ **`open -a` で起動した新 app は 2 分間 1 行もログを書かなかった**（★ 実測）

★ 差し替え直後、`open -a ~/Desktop/O1_計測用_macOS/gse-next.app` で起動すると:

| ★ 観測 | ⚠️ 実測値 |
|---|---|
| プロセス | ★ 実在（pid 15800・`ps` のパスは**新 app**） |
| CPU | ★ 0.0 % / state `S` |
| ウィンドウ | ★ **0 個**（AX `System Events` で確認） |
| `gse-app.log` の mtime | ⚠️ **12:49 のまま**（★ 起動から 2 分経っても 1 行も増えない） |
| 新しい NDJSON | ⚠️ **作られない** |

→ ⚠️ **「プロセスが居る」を「動いている」と読んではいけない**
（★ memory `silent-success-is-not-visible` と同型）。

★ **バイナリを直接叩いたら正常に立ち上がった**（`.app/Contents/MacOS/gse-next` を nohup）:

```
CGEventTap installed (macOS keyboard hook active) tap_mode=Input Monitoring
  input_monitoring=true accessibility=true
tray state -> Measuring
Session log: gse_o1_20260910_040427.ndjson
```

⚠️★★ **原因は未特定**（★ Gatekeeper / LaunchServices のキャッシュを疑うが**実測していない**）。
★ 分かっているのは「**`open -a` では立ち上がらず、直接実行では立ち上がった**」ことだけ。
→ ★ **計測用 app の起動は直接実行で行う**（⚠️ 被験者配布版の起動経路とは別物なので、
  ⚠️ **配布版でも同じことが起きるとは言えない**。★ 配布版の起動確認は別途要る）。

## D6 ✅ ゲート rc=0 到達（★ 一次資料）

```
① 版: repo 0.1.33 / app 0.1.33 → ★ 一致（ビルド 2026-09-10 13:02）
② 陽性対照 4/4 ＋ tap_enabled 1 件 → ★ 入っている
③ 稼働中 gse_o1_20260910_040427.ndjson の meta.app_version: 0.1.33 → ★ 一致
✅ rc=0
```

★ 旧 v0.1.31 は `~/Desktop/O1_計測用_macOS/_old-gse-next-v0131-20260910-130251.app` に**退避**（⚠️ 削除していない）。

## D7 ★ 8h 再測を v0.1.33 で開始（⚠️ 完了は 2026-09-10 21:05 頃）

★ 計器の校正を**先に**通した（`calibrate-cpu.sh`）:
地上真実 90.6 % に対し `top -l 3` = **100.1**、⚠️ `top -l 2` = **22.3**（★ 過小報告を再現）。
★ サンプラが使うのは `ps -o cputime delta`（★ 地上真実と同じ算法）＝ `meta.json` の `cpu_source` で確認。

```
label: with-gse-20260910-macos-8h-v0133
started_utc: 2026-09-10T04:05:37Z / duration_s 28800 / interval_s 30
cpu_source: "ps -o cputime delta" / cpu_pct_basis: "one_core_100"
```

⚠️ **この 8h の最中にビルドを走らせないこと**（★ CI 窓で 4.30 % が出た前例）。

## D8 ⚠️★★★ **スリープ跨ぎ検証は「蓋を閉じたのに寝なかった」で不成立**（★ 一次資料で確定）

★ 2026-09-10 13:16:31 に蓋を閉じ 13:32:31 に開いた（**16 分**）。⚠️ **Mac は寝ていない**:

| ★ 証拠 | ⚠️ 実測 |
|---|---|
| ★★★ `feat` の連続性 13:15:00〜13:33:19 | ★ **1,100 行 / 最大の穴 1 秒 / 5 秒超 0 個**（★ 960 秒の閉蓋中も 1 Hz で回り続けた） |
| ★ `powerd` の lid イベント | ★ `clamshelled: YES` 13:16:31 → `com.apple.powermanagement.lidopen` 13:32:31 |
| ★ wake 理由（⚠️ 自己参照を除いた後） | ★ **0 件** |
| ★ `kern.waketime` | ★ **0**（⚠️ `kern.boottime` = 2026-07-26 以来 wake の記録なし） |
| ★ 電源 / 設定 | ★ Battery Power・`sleep 1` 分（⚠️ それでも寝ていない） |

★ 閉蓋中ずっと `coreaudiod` と `AirPlayXPCHelper` が `PreventUserIdleSystemSleep` を握っていた
（★ 解放は 13:29:45 / 13:31:54）。⚠️ **音声が止まっていなかった**。
★ 加えて `caffeinate`（親 = Claude Code）は**殺しても復活する**（★ 新 pid で再出現を実測）。

### ⚠️★★★ 検出器を **3 つ**壊していた（★ 通算 13・14・15 回目）

| # | ⚠️ 壊れ方 | ★ 塞ぎ方 |
|---|---|---|
| 1 | ★ `pmset -g log` の Sleep/Wake 行が **この機には 1 行も無い**（⚠️ 種別は Assertions / Notification / BatteryHealth のみ）。→ ⚠️ 前版は「0 件 ＝ **このマシンは寝ていない**」と**断定して出力していた** | ★ **陽性対照**を先に取り、当たらないなら **判定しない** |
| 2 | ⚠️★★★ **shell で結果が変わる** —— ★ zsh 経由の `log show` は **0 行**、bash では **736,502 行**。⚠️ 私は 0 行を見て「log show は使えない」と**書きかけた** | ★ bash で走らせ、⚠️ **無フィルタの陽性対照**で生死を見る |
| 3 | ⚠️★★★ **自己参照** —— ★ `log show --predicate '... CONTAINS "Wake reason"'` が**自分のコマンドラインをログに書く**ので、⚠️ **自分自身が 5 件ヒット**した（★ 「寝た証拠が出た」と読みかけた） | ★ `process != "log"` で送り主を除き、⚠️ **検索語は実行時連結**で作る |

→ ★ `post-wake-check.sh` の項目 3 を上記 3 点ぶん書き換え、
★ 新規 `check-can-sleep.sh` で**寝かせる前に**「寝られるか」を見るゲートを置いた。

## D9 ⚠️★★★ **v0.1.33 が SIGSEGV で落ちた**（★ 収集が無言で止まる）

★ 13:42:04、起動から 37 分で `gse-next` が**クラッシュ**した（⚠️ 終了ログは出ない）。
★ 一次資料: `~/Library/Logs/DiagnosticReports/gse-next-2026-09-10-134223.ips`

```
app_version 0.1.33 / Segmentation fault: 11 / EXC_BAD_ACCESS
KERN_INVALID_ADDRESS at 0x0000000000388be2
faultingThread 20:
  gse-next   cg_event_tap_callback_internal     ← ★ CGEventTap コールバックの trampoline
  SkyLight   processEventTapData
  SkyLight   _XPostEventTapData
  SkyLight   eventTapMessageHandler
  CoreFoundation __CFMachPortPerform → __CFRunLoopDoSource1 → CFRunLoopRun
```

★ 直前の時系列（★ **新しく入れた診断がここで効いた**）:

```
13:38:53 WARN  CGEventTap CFRunLoop exited (tap invalidated by macOS). Re-creating in 2s...
13:38:53 ERROR ... starved_ms=120387 rehook_requested=true tap_enabled=Some(true) watchdog_recoveries=0
13:38:55 INFO  CGEventTap installed
13:42:04 ⚠️ SIGSEGV
```

⚠️ **過去 3 件の `.ips` は別物**（★ `SIGKILL (Code Signature Invalid)`＝未署名バイナリの kill）。
→ ★ **segfault はこの 1 件だけ**。⚠️ **v0.1.33 で新しく入ったとは言えない**（★ v0.1.31 で
これだけ長く回した記録が無い）。

### ★ 機序の**仮説**（⚠️ 実測で確かめていない）

★ core-graphics 0.25 の一次資料:

```rust
pub struct CGEventTap<'tap_life> { mach_port: CFMachPort, _callback: Box<CGEventTapCallbackFn> }
impl Drop for CGEventTap<'_> { fn drop(&mut self) { CFMachPortInvalidate(...) } }
unsafe extern "C" fn cg_event_tap_callback_internal(..., user_info: *const c_void) -> ... {
    let callback = user_info as *mut CGEventTapCallbackFn;
    let response = (*callback)(proxy, etype, &event);   // ⚠️ 生存確認なしで deref
}
```

⚠️ **Drop は mach port を invalidate するが、`_callback` の Box は解放される。**
★ trampoline は `user_info` を**素で deref する**ので、解放後に 1 度でも配送されれば UAF。

★ `hook_macos.rs` の再作成ループは **`CFRunLoopSource` を毎周 `add_source` するだけで
1 度も `remove_source` していない**（⚠️ `wc -l` 1265 行中、`remove_source` は **0 件**）。
★ 同じファイルは **timer については**「⚠️ 無効化された runloop に残った timer を掴む余地が出る」
と逐語で書いて**毎周作り直している** —— ⚠️ **source だけ同じ配慮が無い**。

→ ⚠️★★★ **仮説**: 前周の tap を Drop → ★ callback の Box が解放 → ⚠️ runloop に**残った
stale source** 経由で 1 度でも配送されると trampoline が解放済みポインタを deref して落ちる。
★ スタックが `__CFMachPortPerform → eventTapMessageHandler` である点と整合する。

⚠️ **確かめていないこと**: ★ 落ちたのが「古い tap」か「現在の tap」かは trace からは決まらない。
→ ★ 再現には **tap 失効を繰り返し起こす**必要がある。

### ⚠️ 影響（★ 事実だけ）

- ★ 落ちると **NDJSON の追記が止まる**（⚠️ 13:42:04 以降 0 バイト増）。
- ⚠️ **無言で止まる** —— ★ 終了ログが無く、tray アイコンが消えるだけ。
  → ⚠️ **被験者は気づかない**可能性が高い。
- ★ 復旧は手動再起動のみ（★ 13:43:49 に再起動して `Measuring` に戻したことを確認）。
