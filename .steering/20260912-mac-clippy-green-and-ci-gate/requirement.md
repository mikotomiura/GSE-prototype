# mac 側 clippy を exit 0 にし、CI に clippy ゲートを閉じる

## 背景

2026-09-12 に Windows 側 (G-GEAR) で clippy 51 件を潰して `--all-targets` 込みで
`exit 0` にした。⚠️ しかし `hook_macos.rs` / `ime_macos.rs` / `observe_macos.rs` /
`sensors_macos.rs`、および `lib.rs` の `#[cfg(target_os = "macos")]` ブロックは
**Windows では 1 行もコンパイルされない**ため、mac 側の状態は原理的に測れなかった。

★ 本セッションの着手前に mac 実機で実測済み (引き継ぎ §7.3):
`cargo clippy --quiet --all-targets -- -D warnings` は **exit=101**（7 件見えている）。

⚠️★★★ **CI (`check` job) に clippy step を足すのは「両 OS が緑になってから」でなければ
ならない** —— 赤のまま足すと main の CI が即赤になり、全作業が止まる。

一次資料: `.steering/20260912-post-mac-sync-cleanup/decisions.md` 判断 8/9/12/13/14 /
`.steering/_handoff/next-session-mac-clippy-and-ci-gate.md` §7。

## ゴール

1. mac 実機で `cargo clippy --quiet --all-targets -- -D warnings` が **exit 0**。
2. `ci.yml` の `check` job に clippy step を追加し、両 OS で緑になる状態にする (R-1)。
3. `blockers.md` 起票 10② (`IME_OPEN.store` の Ordering) を両 OS 対で修正する。

## スコープ

### 含むもの
- mac 固有ファイル + `#[cfg(target_os = "macos")]` ブロックの clippy 修正 (振る舞い不変)
- 起票 10②: `ime_macos.rs` / `ime_windows.rs` の `IME_OPEN.store` を `Relaxed` → `Release`
  （⚠️ **lint 修正とは別コミット**にする）
- `.github/workflows/ci.yml` の `check` job に clippy step を追加 (R-1)

### 含まないもの
- ⚠️ 起票 10①（`macos_vk_to_vk` の素通しアーム）—— VK 分布が動き `HMM_VERSION` 判断が要る。
  起票 6（ライブ変換）と一緒に Mh-D 全体の修正として扱う (decisions 判断 12)
- ⚠️ R-2（toolchain 固定）/ R-3（MSRV 1.87 の実証）/ R-5（`run-codex-review.sh` の Windows 対応）
  —— 未決。本タスクでは触らない
- ★ R-4（CI の `USERPROFILE` / `HOME`）は R-1 と同じ機会に **観察だけ**する（修正は別）

## 受け入れ条件

- [ ] `cargo clippy --quiet --all-targets -- -D warnings` が mac で **exit 0**
- [ ] `cargo fmt --check` clean
- [ ] `cargo test --workspace` が 659 passed / 0 failed 以上（★ 減っていないこと）
- [ ] ゴールデン全 fixture が byte-equal（⚠️ **ずれたら `HMM_VERSION` を bump せず、修正が誤り**）
- [ ] `emit_schema` が `schema/current.json` と byte-equal
- [ ] `ci.yml` に clippy step が入り、CI の両 OS job が緑
- [ ] lint 修正コミットと Ordering 修正コミットが**分かれている**

## 関連ドキュメント

- `.steering/_handoff/next-session-mac-clippy-and-ci-gate.md`（★ 一次資料ではない）
- `.steering/20260912-post-mac-sync-cleanup/decisions.md`
- `.steering/20260911-outcome-arbitration-and-o1-preflight/blockers.md` 起票 10
- `.claude/skills/hook-constraints/SKILL.md` 共通-2（`IME_OPEN` の store は Release）

## 運用メモ
- /reimagine 適用: **No**
- 理由: 方針・スコープ・受け入れ条件が研究者裁定 (引き継ぎ §7.1 S-1 / R-1) で確定しており、
  設計上の選択肢が残っていない。lint 修正は振る舞い不変の機械的作業。
