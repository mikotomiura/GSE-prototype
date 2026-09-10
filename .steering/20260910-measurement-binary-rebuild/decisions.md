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
