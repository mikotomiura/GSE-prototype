# 申し送り F-1 / F-2 / F-3 / F-5 の決着 (supply-chain 検知経路と CI 権限)

> ★ 出自: `.steering/_handoff/next-session-followups-f1-f5.md`
> ★ 一次資料: `.steering/20260912-r2-r5-decisions/decisions.md` 判断 52〜54 / 同 `tasklist.md` 末尾の申し送り表

## 背景

2026-09-12 に R-2〜R-5 (toolchain 固定 / MSRV 訂正 / 無音 skip 撲滅) が PR #193 / #194 / #195 で
main に入った。その過程で **security-checker と Codex が独立に同じ穴**を指摘し、申し送り F-1〜F-7
として残った。F-6 (予算上限) と F-7 (`git-workflow` の `wall` 残存) は前タスクで決着済み。

★ 残った穴の構造 (⚠️ ここを取り違えない):

| 層 | 固定の仕方 | 現在の検知手段 |
|---|---|---|
| 依存 crate (630 個) | `Cargo.lock` に **checksum 付き** | ⚠️ **無し** (`cargo-audit` 未導入・`ci.yml` に audit step 0 件・dependabot 設定なし) |
| ⚠️ **toolchain** (rustc / std / cargo / clippy) | `rust-toolchain.toml` に **名前のみ** (ハッシュなし) | ⚠️ **`cargo audit` の射程外**。緩和は「版上げ手順 0 で人が見る」だけ |
| フロント npm | `package-lock.json` | ⚠️ **無し** |

⚠️★★★ **「`cargo audit` を入れれば足りる」は成立しない** —— ★ cargo-audit は `Cargo.lock` の依存しか
見ず、**toolchain 同梱の cargo / rustc / std は見ない**。⚠️ RustSec DB に `std` の advisory は 1 件も無い
(★ rust-lang/rust の repo advisory にしか無い)。

★ **頻度の実像** (2026-09-12 実測・`gh api repos/rust-lang/rust/security-advisories` → **6 件 / 約 7 年**):
⚠️★★★ 唯一の critical (**CVE-2024-24576** / `std::process::Command` の Windows 引数エスケープ) が
GSE の製品コードのクラスに当たる。→ ★ 「低頻度だから無視してよい」ではなく
「**低頻度だが当たれば自分のコードに当たる**」。

加えて `ci.yml` の 4 job (`decide-win-runner` / `check` / `build-windows` / `build-macos`) に
`permissions:` が無い (既存の穴)。⚠️ `check` は **self-hosted 実機**で走るので、
既定の広い権限のままにしておく理由が無い。

## ゴール

1. ★ **検知経路を 1 か所に置く** —— 依存層と toolchain 層を **単一の CI workflow** が検査し、
   同じ script を**人も手元で回せる**形にする (⚠️ 「回す場所が無い手順は回らない」= 判断 20 M4 の教訓)。
2. ★ `ci.yml` の `permissions:` 欠落 4 job を `contents: read` で塞ぐ。
3. ★ F-3 を裁定し、**変更しない理由を記録**して申し送りから落とす。

## スコープ

### 含むもの

- **F-5 (PR-A)**: `ci.yml` の 4 job へ `permissions: contents: read` を明示する。
- **F-1 + F-2 (PR-B)**: 新規 workflow `.github/workflows/supply-chain.yml` を追加し、
  - (a) `scripts/check-toolchain-advisories.py` で rust-lang/rust advisory と
    `rust-toolchain.toml` の `channel` を突合する (★ **手元でも回る**)
  - (b) `cargo-audit` で `src-tauri/Cargo.lock` を検査する
  - (c) `npm audit --omit=dev` で**被験者に届く経路の**フロント依存を検査する
  - (d) `rust-toolchain.toml` 手順 0 と `docs/verification-runbook.md` を (a) の script に差し替える
- **F-3 の裁定記録** (⚠️ コード変更は伴わない)。

### 含まないもの

- ⚠️★★★ **F-4 (default features のみの clippy を CI に足す)** —— ★ **mac 実機の先行検証が必須**
  (判断 54)。`next-session-mac-default-clippy.md` を mac で回してから別タスクで行う。
- ⚠️ **dependabot の導入** —— ★ 今回は入れない (⚠️ 検知は上記 workflow に一本化する。
  自動更新 PR は 2-3 人チームにはノイズが勝る)。★ 判断として記録する。
- ⚠️ dev 依存 (`npm audit` の 7 件) を**赤にすること** —— ★ 被験者に配る Tauri バイナリの
  実行時経路ではない。⚠️ 「無い」わけではないので、**production だけを門にし、全体は情報として出す**。
- ⚠️ `stop-check.sh` の変更 (= F-3。★ 足さないと裁定した)。
- ⚠️ R-2 の蒸し返し (固定するか / 固定先の版 / `targets` / `@stable`)。★ すべて決着済み。

## 受け入れ条件

- [ ] ★ `scripts/check-toolchain-advisories.py` が **手元 (Windows git-bash) で exit 0** で完走し、
      ⚠️ **「6 件を検査した」ことが出力から読める** (= 「何も起きていない」と「成功した」を区別する)
- [ ] ★ 同 script が**当たる版でちゃんと赤になる**ことを、⚠️ **既知の脆弱版を渡した変異テスト**で実証する
      (例: `1.88.0` → CVE-2025-11233 に当たる / `1.76.0` → critical に当たる)
- [ ] ★ `cargo-audit` を `src-tauri/Cargo.lock` に対して回し、⚠️ **CI に足す前に現状の赤/緑を実測**する
      (= R-1 の順序: ① 緑を確かめる → ② CI に足す)
- [ ] ★ `npm audit --omit=dev` が 0 件であることを実測する
- [ ] ★ `ci.yml` の全 job が `permissions:` を持つ (yaml パースで検査)
- [ ] ★ `ci.yml` / `supply-chain.yml` が **actionlint 相当**で構文的に妥当
- [ ] ★ 既存ゲート (fmt / clippy `-D warnings` / test / ゴールデン / schema) が緑のまま
- [ ] ★ `code-reviewer` + `security-checker` を**並列**起動して指摘を反映
- [ ] ★ `/cross-review` を回す (⚠️ ラッパー `scripts/run-codex-review.sh` を先に・パス限定で)
- [ ] ★ **PR-A / PR-B の CI run ログを実際に読む** (⚠️ 「緑になった」ではなく、
      新 job が**どの入力で何件を検査したか**をログで確認する)

## 関連ドキュメント

- `docs/verification-runbook.md` §1 (f) — MSRV 検査の置き場所 (★ 今回 (g) を足す)
- `rust-toolchain.toml` 版上げ手順 0 — ⚠️ 現状の唯一の緩和策
- `.steering/20260912-r2-r5-decisions/decisions.md` 判断 20 / 39 / 50 / 52〜54
- `docs/development-guidelines.md` §9 (Hook) / §10 (データ repo 連携)

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 方式選択 (単一 CI job で両層 / cargo-audit のみ / docs のみ / + dependabot) は
  **grill でユーザーが裁定済み**であり、残りは実装の詳細である。⚠️ アーキテクチャ判断でも
  公開 API 定義でもなく、複数案の比較は既に閉じている。
