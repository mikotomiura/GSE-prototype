# セッション開始プロンプト — **R-2〜R-5 を裁定する (★ ADR-029 の前に)**

> ⚠️★★★ **本メモは 2026-09-12 に実施済み。裁定と結果は
> `.steering/20260912-r2-r5-decisions/decisions.md` にある（★ こちらが一次資料）。**
>
> | | 結果 |
> |---|---|
> | **R-2** | ✅ **実装済み**（**PR #194**）。⚠️★★★ **固定先は `1.94.1` ではなく `1.98.1`** —— ★ 初稿は本機の `stable` を見て 1.94.1 と書いたが、**CI は 1.98.1 で走っていた**（本機のローカルが 5.5 か月古かった）。★ `profile = "minimal"` ＋ **明示 `rustup toolchain install` step**（disk guard より前）を 3 job に追加 |
> | **R-3** | ✅ **完了**（**PR #193** → main `2bcf35d`）。⚠️★★★ **`1.87` は誤りだった** —— 依存 (`time@0.3.47` 他) が **1.88.0** を要求。★ **`1.88` へ訂正**し `cargo +1.88 check` exit 0 を実証。★ 手順を `docs/verification-runbook.md` §1 (f) に恒久化 |
> | **R-4** | ✅ **完了**（**PR #193** → main `2bcf35d`）。★★★ **CI 実測で元の問いに答えが出た** —— **Windows: `USERPROFILE` = set / macOS: ⚠️ `USERPROFILE` = unset・`HOME` = set**（★ mac 側の保護は `HOME` だけに依存していた）。★ 無音 skip → `panic!` ＋ CI に env 前提の検査 step。⚠️★★★ **初稿は Windows で空振りだった** —— `pwsh → git-bash` で **MSYS2 が `HOME` を合成する**ので、Windows は `USERPROFILE` だけで判定する形に直した |
> | **R-5** | ✅ **閉じた**。★ `run-codex-review.sh` が **exit 0** で完走し、**予算台帳が自動計上**された（= ラッパー経由の客観証拠）。⚠️ ただし 2 回とも codex-cli **0.152.1** なので、版差か権限差かの切り分けは**未了**（★ 実務上は「使ってよい」で足りる） |
>
> ★ 以下は**着手前の記述**（履歴として残す）。⚠️ **§1 の「判断の軸」は決着済み**なので蒸し返さないこと。
>
> ✅ **現行**（作成 2026-09-12・Windows 機 = G-GEAR のセッションから・**未着手**）。
> ⚠️★★★ **このメモを一次資料にしない。** 実体は
> `.steering/20260912-post-mac-sync-cleanup/decisions.md` /
> `.steering/20260912-mac-clippy-green-and-ci-gate/decisions.md` §8.6 /
> `.steering/20260912-ime-active-ordering/decisions.md` 判断 12 にある。

## §0 ⚠️★★★ なぜ「ADR-029 の前に」なのか

★ **R-1 (CI の clippy ゲート) が 2026-09-12 に入った**ことで、R-2 の性質が変わった。

| | R-1 の前 | ⚠️ R-1 の後 (現在) |
|---|---|---|
| toolchain が上がって新 lint が増えたら | ★ ローカルの `stop-check.sh` が **WARN を出すだけ** | ⚠️★★★ **main の CI が赤になり、全 PR が止まる** |

→ ⚠️ **コード差分ゼロでも、ある朝いきなり全部赤になりうる。**
★ ADR-029 は `/reimagine` ＋ cross-review を伴う**重いタスク**なので、
⚠️ その最中に CI が赤くなると「ADR の議論」と「lint の後始末」が混ざる。

⚠️★★★ **赤くなったときに `-D warnings` を外して逃げてはならない**
(★ mac 側の記録の明示指示。外した瞬間「見えないまま緑」へ戻る)。

## §1 ★ R-2: `rust-toolchain.toml` で toolchain を固定するか (⚠️ **最優先**)

### ★ 2026-09-12 に実測したこと (⚠️ ここだけは推測でない)

★ scratchpad に `rust-toolchain.toml` を置いて `rustup show active-toolchain` を実行した:

```
[toolchain]
channel = "1.94.1"
components = ["clippy", "rustfmt"]
```
```
info: syncing channel updates for 1.94.1-x86_64-pc-windows-msvc
info: downloading 6 components
1.94.1-x86_64-pc-windows-msvc (overridden by '<dir>/rust-toolchain.toml')
```

→ ★ **判明した事実 2 つ**:

1. ★ **`rust-toolchain.toml` は rustup の既定 (`stable`) を上書きする。**
   ⚠️ したがって CI の `dtolnay/rust-toolchain@stable` が入れた stable ではなく、
   **ファイルが指す版で cargo が走る**。
2. ⚠️★★★ **未導入なら rustup が自動でダウンロードする。**
   ★ `components = ["clippy", "rustfmt"]` をファイルに書けば**一緒に入る**
   → ⚠️ mac 側が判断 8 で塞いだ「clippy が入っていないのに step を置くと
   『走らなかった』と『緑だった』が区別できない」穴は、**ファイル側で閉じられる**。

### ⚠️ だから R-2 は 1 行の変更ではない —— 検証が要る

| 論点 | ⚠️ 確かめること |
|---|---|
| ★ CI の 3 つの toolchain step | ⚠️ `check` / `build-macos` / `build-windows` の**すべて**が `dtolnay/rust-toolchain@stable`。★ ファイルを置くと**全部が上書きされる**ので、`components: clippy` を持つのが `check` だけで足りるか確認する |
| ⚠️★★★ **self-hosted のディスク** | ★ 固定した初回は**フル toolchain のダウンロードが走る**。⚠️ mac ランナーはディスクガードが `threshold=15 GiB`・実測の空きが 18〜20 GiB で、`src-tauri/target` が既に 3.0 GiB。→ ★ **掃除が走る条件に近づく** |
| ★ `targets:` の扱い | ⚠️ `check` は `targets: ${{ matrix.target }}` を渡している。★ ファイル側に `targets = [..]` を書くか、action 側に残すかを決める |

### ★ 判断の軸 (⚠️ 私は決めない)

- **固定する**: ★ lint 増加の不意打ちが止まる。⚠️ 本 repo は `reproducibility-discipline` で
  **Cargo.lock / seed / `HMM_VERSION` を固定する**規律を既に敷いており、
  ★ **toolchain だけ浮いているのは一貫していない**。
  → ⚠️ 版を上げるのは「別 PR で意図的に」になる (★ `HMM_VERSION` bump と同じ作法)。
- **固定しない**: ⚠️ rustc / std のセキュリティ修正に自動で追従できる。
  ★ ただし ⚠️ **依存の脆弱性は `Cargo.lock` 側の話**なので、ここで守られるのは
  **rustc / std 由来のもの**に限られる (★ 頻度は低いが 0 ではない)。
- ★ **中間案**: 固定したうえで、**非ブロッキングの「latest stable で回す job」**を別に置く。
  ⚠️ 代償は CI 時間と複雑さ。

## §2 ★ R-3: `rust-version = "1.87"` の実証

- ★ 現状: `src-tauri/Cargo.toml` に宣言済み。根拠は **ローカル `rust-src` の
  `#[stable(since=..)]` 実測** (`is_multiple_of`=1.87.0 / `is_none_or`=1.82.0 /
  `repeat_n`=1.82.0 / `abs_diff`=1.60.0)。
- ⚠️ **「1.87 で crate 全体がビルドできる」ことの実測ではない**。
  ★ MSRV を検査する CI job は**存在しない**。
- ⚠️ **R-2 と強く結びつく** —— ★ 固定するなら「固定版」と「MSRV」の関係を
  1 回だけ決めればよい (⚠️ 別々に議論しない)。
- ★ 低コストの選択肢: `cargo +1.87 check` を**非ブロッキング**で 1 回だけ回して確かめる。

## §3 ⚠️★★★ R-4: **「観察不能」と判明した** —— ★ 質問そのものを変える必要がある

- ★ 元の問い: 「CI 実行環境で `USERPROFILE` / `HOME` が立っているか」。
- ⚠️★★★ **観察できない。** ★ `redact_home_path_masks_real_home_from_env` は
  **env が無いと沈黙して `return` する**ので、**CI ログでは「通った」と「skip した」が
  区別できない** (★ mac 側 §8.3 の指摘)。
- → ⚠️ **先にテストを loud にしないと、R-4 は答えられない。**
  ★ これは `silent-success-is-not-visible` と同型の問題である。
- ⚠️ **なぜ放置できないか**: これは **security review MEDIUM を閉じるために足したテスト**で、
  ★ 壊れると**被験者に見せる提出失敗メッセージへ OS ユーザー名を含むフルパスが素通り**する
  経路を守っている。→ ⚠️ **守っているつもりで守っていない**状態が最も悪い。
- ★ 選択肢: ① env が無ければ **fail** させる (⚠️ CI に env が無いと即赤)
  ② skip したことを**標準出力に必ず出す** (★ `--nocapture` 前提になる弱さ)
  ③ **CI 側で env を明示的に設定**し、テストは fail 側に倒す (★ 最も loud)。

## §4 ★ R-5: `run-codex-review.sh` の Windows 対応 (⚠️ **前提の再確認が先**)

- ⚠️★★★ **2026-09-12 に「1312 は再現しない」と実測された。**
  ★ `/cross-review` の cross-reviewer が、私が渡した
  「Windows では `--sandbox read-only` が 1312 でシェル起動不可」という指示を**鵜呑みにせず**、
  診断コールで先に確かめた結果、⚠️ **再現せずラッパー経由で正常に動いた** (★ 予算も自動計上)。
- ⚠️ **恒久的に直ったとは断定されていない** —— ★ codex-cli の版差
  (0.142.5 → **0.152.1**) か実行時の権限差かは**切り分けられていない**。
- ★ 一次記録: `.codex/budget.json` の `_comment_diag_2026_09_12`。
- → ★ **R-5 は「直す」タスクではなく「もう要らないかを確かめる」タスクかもしれない。**
  ⚠️ 次に Windows で cross-review を回すとき、**まずラッパーを試す**こと。
  ★ 2 回連続で動けば R-5 は閉じてよい (⚠️ 1 回では版差の可能性を消せない)。
- ★ **ADR-029 との関係**: ADR-029 は cross-review を伴うので、⚠️ **そのとき自然に検証できる**。

## §5 ★ 済んでいること / 未実施 (⚠️ 混ぜない)

**済み** (2026-09-12・Windows 実機 = G-GEAR):
- ★ Windows 側 clippy **51 件** → `--all-targets --features package` で **exit 0** (PR #188)
- ★ mac 側 clippy **7 件** ＋ **R-1 = CI の clippy ゲート** (PR #190・mac セッション)
- ★ `IME_ACTIVE` の Ordering **7 箇所** ＋ 再発防止ガード (PR #191)
- ★ `rust-version = "1.87"` の**宣言**のみ (⚠️ 実証は未了 = R-3)

**未実施** (★ このメモの仕事):
- ⚠️ **R-2 / R-3 / R-4 / R-5 はいずれも未決**
- ⚠️ R-2 は**実測 (§1) までしか進んでいない**。★ 決定も実装もしていない

## §6 ⚠️ ついでに直すとよい小さな失効

- ★ `.steering/_handoff/next-session-mac-clippy-and-ci-gate.md` **§8.6 の 1 行目**
  「PR #190 を main へマージするか = **未実施**」は⚠️ **失効している**
  (★ `5900ab4` でマージ済み)。マージ前に書かれた行が残ったもの。
