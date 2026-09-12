# 要件: R-2〜R-5 の裁定と実装

## 背景

2026-09-12 の 3 タスク (`post-mac-sync-cleanup` / `mac-clippy-green-and-ci-gate` /
`ime-active-ordering`) が、研究者判断に委ねる事項として **R-2〜R-5** を残した。
引き継ぎは `.steering/_handoff/next-session-r2-r5-decisions.md`。

⚠️★★★ **R-1 (CI の clippy ゲート・`-D warnings`) が 2026-09-12 に main へ入った**
(`5900ab4`) ことで R-2 の性質が変わった:

| | R-1 の前 | ⚠️ R-1 の後 (現在) |
|---|---|---|
| toolchain が上がって新 lint が増えたら | ローカル `stop-check.sh` が WARN を出すだけ | ⚠️★★★ **main の CI が赤になり全 PR が止まる** |

→ ⚠️ **コード差分ゼロでも、ある朝いきなり全部赤になりうる。**
★ ADR-029 は `/reimagine` ＋ cross-review を伴う重いタスクなので、その最中に
CI が赤くなると「ADR の議論」と「lint の後始末」が混ざる。→ **先に閉じる。**

## ゴール (★ Done/Stop が exit code / test 名で言える形)

### PR-B (先) — R-3 ＋ R-4

| ID | Done | Stop |
|---|---|---|
| **R-3** | `cd src-tauri && cargo +1.87 check --all-targets --features package` が **exit 0**。結果 (成否と実測日) を `Cargo.toml` の `rust-version` 注記へ反映 | exit != 0 → ★ 通らなかった真の下限へ `rust-version` を修正し、その根拠を記録 |
| **R-4** | `redact_home_path_masks_real_home_from_env` が **env 不在で `panic!`** する (無音 skip を廃止)。かつ `check` job に **env 前提を検査する step** があり、不在なら `::error::` で落ちる | ★ 変異テスト: `else` 節を一時的に `return` へ戻すと検査 step が意味を失うことを確認 |

### PR-A (後) — R-2

| ID | Done | Stop |
|---|---|---|
| **R-2** | repo 直下に `rust-toolchain.toml` (`channel = "1.94.1"` / `components = ["clippy","rustfmt"]`) が存在し、`rustup show active-toolchain` が **`overridden by ...rust-toolchain.toml`** を返す。CI の `check` 両レグ + `build-windows` + `build-macos` が **success** | ⚠️ mac self-hosted のディスクガードが `wiped=true` になる、または `os error 28` → ★ **`-D warnings` を外して逃げない**。revert して閾値を先に較正する |

### R-5 (⚠️ PR ではない)

- ★ **「直す」タスクではなく「もう要らないかを確かめる」タスク。**
- Done: 本タスクの `/cross-review` で **`scripts/run-codex-review.sh` を先に試し**、
  exit 0 で完走する。★ 2026-09-12 の診断 (判断 12) と合わせて **2 回連続**成功なら R-5 を閉じる。
- Stop: 1312 が再現する → ★ 再現条件 (codex-cli 版 / 権限) を記録し、R-5 を開いたまま残す。

## スコープ外 (★ 意図的にやらない)

- ⚠️ **ADR-029 そのもの** (本タスクは「その前に地ならしする」ことが目的)
- ⚠️ **`stop-check.sh` に `--features package` を足すか** (mac 側 follow-up 候補 1・**未決のまま残す**)
- ⚠️ **default features のみの clippy を CI に足すか** (同 follow-up 候補 2)
- ⚠️ **`check` job の `permissions: contents: read`** (同 follow-up 候補 3・**既存の穴**であり本差分が作ったものではない)
- ⚠️ **`cargo-audit` の導入** (post-mac-sync R-3 として別枠)
- ⚠️ **`.codex/budget.json` の `daily_token_budget` を 300000 のまま残すか戻すか** (2026-09-08 の一時引き上げ・研究者判断)
- ⚠️ **中間案 (非ブロッキングの latest stable job)** —— ★ 裁定で採らなかった (下記 決定 1)

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 4 件とも **選択肢が有限に列挙済み**で、handoff §1〜§4 が既にトレードオフを
  提示している。⚠️ アーキテクチャ判断ではなく **運用方針の裁定**であり、
  ゼロから別案を生成する価値より「実測で分岐を潰す」価値の方が大きい。
  ★ 実際、grill 中の実測 4 件 (下記 design.md) で分岐は機械的に閉じた。
