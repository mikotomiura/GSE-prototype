# 次セッション開始プロンプト（**Mac 側**）— v0.1.28 をリリースし、配布物を差し替える

このファイルの「===」以下をコピペして開始する。
★ ⚠️★★★ **Mac で実行する。** 理由は §2-3（`hdiutil` / `codesign` / `ditto` が要る）。

---

===

## §0 ★ ここまでの状態（★ 議論し直さない）

2026-08-21 に `.steering/20260821-precollection-close-and-x-axis/` を実施し、
**収集開始前にしか閉じられない 2 件（T-0 / T-1）を閉じた**。

| # | 何 | 結果 |
|---|---|---|
| **T-0** | `starve_window` の陽性対照 | ★ **発火した（初観測）**。`win_ms=60000` / `n_lt30=3` / `hook_health` 0 行 |
| **T-1** | 自動終了 × 押下の競合（D-1）＋ 所見 C | ★ `BLOCK_TRANSITION`（最外側の直列化点）＋ `g1::decide_block_end`（エポック照合）で交錯 2 方向を閉じた |
| **T-2** | ADR-013 Migration 3/4 | ★ `scripts/capabilities_gate.py` を CI 込みで実装。Migration 2b/2c/3/4 完了 |
| **T-3** | X 軸再定義の議論 | ★ ADR-009 は **Proposed のまま ＋ Accepted 条件を明文化**。⚠️ **実装していない** |

★ **ブランチ `fix/precollection-close-and-x-axis` に 3 コミット。⚠️ 未 push・未マージ。**

```
c5a8e17 docs(adr): ADR-009 に Accepted 条件を明文化する (T-3・議論のみ)
987fcac feat(analysis): capabilities の機械判定ゲートを追加する (ADR-013 Migration 3/4)
c42b0e4 fix(g1): ブロック遷移を直列化し、自動終了と押下の競合を閉じる
```

検証は全部緑: `cargo test --workspace` **468 passed** / ゴールデン **6 本 byte-equal** /
`HMM_VERSION` **0.4.0 据え置き** / `emit_schema` **byte-equal** / schema parity **exit 0** /
Python **83 tests** / `--self-test` 2 本 / `check_citations` 緑。

## §1 ⚠️★★★ なぜこのタスクが要るか — **修正が被験者の手元に届いていない**

- 配布済み zip は **v0.1.27** で作られ、**Drive へは研究者がアップロード済み**（2026-08-19）
- ★ T-1 の修正は**ブランチ上にあるだけ**で、`main` にも入っておらず、
  ⚠️ **`package.json` / `tauri.conf.json` / `Cargo.toml` は 0.1.27 のまま**

→ ⚠️★★★ **いま収集を始めると、被験者は修正前のビルドを走らせる。**
★ 「収集開始前に閉じる」という T-1 の動機がそのまま無効になる。

### ⚠️★★ しかも「後から差し替える」ができない

収集途中で v0.1.28 に差し替えると、**新旧が混ざったコホート**になる。
★ これは今回作った `capabilities_gate.py` が **`MIXED` で止める**、まさにその失敗様式である
（`meta.app_version` と `capabilities` がファイルごとに食い違う）。

→ ★ **差し替えるなら収集開始前の一度きり。** ⚠️ 走り出したら `§3.6` により回復不能。

## §2 ★ 手順（★ この順に実行する）

### §2-1 PR → CI → main マージ

```bash
git checkout fix/precollection-close-and-x-axis
git push -u origin fix/precollection-close-and-x-axis
gh pr create --fill   # ★ 本文に .steering/20260821-precollection-close-and-x-axis/ を参照させる
```

⚠️★★ **CI が全ジョブ緑になるまでマージしない。**
`check` は **win / mac とも self-hosted**（`gse-win=G-GEAR` / `gse-mac`）で走る。
→ ★ **その Mac がオンラインである必要がある**（本セッションを Mac でやるなら好都合）。
⚠️ Windows 側が offline なら 30 秒で hosted へ fallback する（`decide-win-runner`）。

★ `frontend-check` には**今回追加した 2 ステップ**がある
（`capabilities_gate.py --self-test` ／ 単体テスト）。⚠️ ここが赤ならマージしない。

### §2-2 バージョンを 0.1.28 へ上げる

⚠️ **4 ファイルを同時に**直す（★ v0.1.27 の bump コミット `2261652` と同じ集合）:

| ファイル | 直す場所 |
|---|---|
| `package.json` | `"version": "0.1.28"` |
| `src-tauri/tauri.conf.json` | `"version": "0.1.28"` |
| `src-tauri/Cargo.toml` | `version = "0.1.28"` |
| `src-tauri/Cargo.lock` | ★ `cargo build` で自動更新される（**手で書かない**） |

⚠️★ `src-tauri/src/capabilities.rs` の `app_version()` は
`env!("CARGO_PKG_VERSION")` 由来なので、**`Cargo.toml` を直せば `meta` 行に載る**。
→ ★ これが「どのビルドが出したログか」の追跡子である（ADR-013）。

```bash
cd src-tauri && cargo build   # Cargo.lock を更新させる
cargo test --workspace        # ★ 468 passed のままであることを確認
```

コミット例: `chore(release): v0.1.28 へ上げる`

### §2-3 タグを push → CI が自動でビルドしてリリースを作る

```bash
git tag v0.1.28
git push origin v0.1.28
```

★ `.github/workflows/ci.yml` はタグ push で次を走らせる:

| job | runner | 出す物 |
|---|---|---|
| `build-windows` | `windows-latest`（**hosted**） | `gse-next.exe` / `gse-submit.exe` |
| `build-macos` | ⚠️ **`[self-hosted, gse-mac]`** | `gse-next_0.1.28_aarch64.dmg` / mac tools |
| `release` | `ubuntu-latest` | ★ **GitHub Release**（両方の成果物を添付） |

⚠️★★★ **`build-macos` は self-hosted。その Mac が落ちているとリリースが片肺になる。**

### §2-4 ⚠️★★★ 配布 zip を作り直す（★ ここが macOS 必須の理由）

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --tag v0.1.28
```

⚠️★★★ **`--tag` を必ず付ける。既定は `v0.1.24` である**（スクリプト内の `TAG="v0.1.24"`）。
★ 前回（2026-08-19）も「`--tag` を付けた。既定の `v0.1.24` ではない」とわざわざ記録されている。

★ このスクリプトが macOS を要求する理由: **dmg をマウント → 署名検証 → `.app` を取り出し
→ フォルダ配置後に再度署名検証**（`hdiutil` / `codesign` / `ditto`）。
→ ⚠️ **Windows では mac zip を作れない。**

★ 出力（★ Drive に置くのはこの 2 個）:

```
dist/_common/G1_実施用_macOS.zip
dist/_common/G1_実施用_Windows.zip
```

⚠️ **`make-distribution.sh` と混同しない。** そちらは**被験者 1 人ぶん**（課題ページ入り・割付が要る）。
★ 今回アプリだけが変わったので、**差し替えるのは共通 zip の 2 個だけ**である。
⚠️ 課題ページ（`blockNN.html`）を共通側に入れてはならない（全員が同じ課題を持ってしまう・D-1）。

### §2-5 Drive を差し替える

⚠️★★★ **上げるのは研究者の判断**（スクリプトは意図的に Drive へ上げない）。

★ 前回（2026-08-19）は研究者がアップロードし、**Drive 上の実体を検算**している
（バイト数一致 / 置き場所 / 旧版と余計な物の不在 / 共有範囲）。★ 今回も同じ検算をする。

⚠️★★ **旧 v0.1.27 の zip を残さない。** 残ると被験者がどちらを落としたか分からなくなり、
★ `MIXED` コホートを人手で作ることになる。

## §3 ★ 受け入れ条件（Done）

- [ ] PR の CI が**全ジョブ緑**（★ `frontend-check` の capabilities gate 2 ステップを含む）
- [ ] `main` にマージされ、`v0.1.28` が main の祖先
- [ ] GitHub Release `v0.1.28` に **Windows / macOS 両方**の成果物がある
- [ ] `make-common-app-zip.sh --tag v0.1.28` の**機械検査が全て緑**
      （★ 署名検証 2 回 / `--selftest` 2 回 / README 文言 grep / zip の UTF-8 フラグ /
      `__MACOSX` `.DS_Store` 不在 / 共通配布物に `block*.html` が無い）
- [ ] ⚠️★★★ **実起動の NDJSON `meta` 行で `app_version = 0.1.28` を確認**
      （★ 「ビルドできた」ではなく「**そのビルドが動いてログに刻んだ**」を見る）
- [ ] ★ G-1 二度押しの実機確認（前ファイルが閉じ、新ファイルができる）
- [ ] Drive の差し替えと検算、⚠️ **旧 v0.1.27 zip の削除**
- [ ] ⚠️ Windows 実機スモークの依頼（§4）

## §4 ⚠️ Windows 側でしかできないこと（★ 忘れると片肺になる）

★ `G1_実施用_Windows.zip` は **Mac で組まれる**が、⚠️ **Windows で起動確認していない**。
→ ★ リリース後、Windows 側セッションで次を実施する:

- [ ] zip を展開して `gse-next.exe` が起動する
- [ ] `meta` 行に **`app_version = 0.1.28`** と **`g1_mode = "marker"`** が出る
- [ ] G-1 二度押しで前ファイルが閉じ、新ファイルができる
- [ ] ⚠️ 生 NDJSON は repo に置かない（★ 値だけを `.steering/` に転記）

## §5 ⚠️ 落とし穴（★ 実測）

1. ⚠️★★★ **`make-common-app-zip.sh` の `--tag` 既定は `v0.1.24`。** 付け忘れると**古いアプリを配る**
2. ⚠️★★ **`build-macos` は self-hosted。** Mac が落ちているとリリースが片肺になる
3. ⚠️★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）。`cd src-tauri` するか `--manifest-path`
4. ⚠️★★ **Windows コンソールは cp932** → Python は **`PYTHONUTF8=1`**
5. ⚠️★★ **`| tail` にパイプすると `$?` が tail のものになり赤を見落とす** →
   **リダイレクトしてから `echo $?`**
6. ⚠️ `.claude/settings.json` / `.gitignore` に**タスクと無関係の未コミット変更**が残っている
   （★ 今回も触っていない。コミットに巻き込まないこと）
7. ⚠️ `C:\gse-dataset` の `schema/current.json` が**未コミット**（別 repo・parity は通っている）
8. ⚠️ `experiments/*/dist/` が `.gitignore` の対象外という積み残しがある
   （`.steering/20260819-mac-build-distribution-zips/decisions.md` 所見 3）。
   ★ `dist/` に `g1-submit.json` が入るので **commit しないこと**

## §6 ⚠️★★★ やらないこと

- ⚠️ **`src-tauri/` の記録仕様に手を入れない。** ★ 計器は 2026-08-21 に**凍結した**。
  気づいた点は `.steering/20260821-precollection-close-and-x-axis/blockers.md` に足すだけにする
- ⚠️ **X 軸（ADR-009）の実装をしない。** ★ D7「軸を書き換えても G1 は免除されない」／
  Migration 1「Phase1 完了 + 研究者承認まで着手しない（凍結）」
- ⚠️ **`preregistration.md` を変えない**（第 17 版・凍結）
- ★ 割付（`assign.py`）を回さない。⚠️ 梱包のついでに走らせてよいものではない

## §7 ★ 完了報告に必ず書くこと

- [ ] `app_version = 0.1.28` を**実起動のログで**確認した値
- [ ] `make-common-app-zip.sh` の機械検査の結果（★ 何が緑だったか）
- [ ] Drive の差し替えと**旧 zip の削除**を確認したか
- [ ] ⚠️ Windows 実機スモークが**未実施**なら、そう書く（★ 「たぶん動く」と書かない）
- [ ] ★ **収集を開始してよい状態になったか**の明示

## §8 ★ このタスクの「次」

| いつ | 何を |
|---|---|
| ★ **本タスク完了直後** | **収集開始**（⚠️ 前提条件 4 件 ＋ ADR-013 Migration 2〜4 はすべて充足済み） |
| ★ **並行（Windows 側）** | `.idea/20260819-smartphone-computational-media-channel.md` の議論 → `_handoff/next-session-prompt-smartphone-expression-channel.md` |
| **収集が一定量たまってから** | ADR-012 **Stage 0**（★ 新 G1 ログの `starve_window` が入力になる） |

## §9 ⚠️ 研究者判断の積み残し（★ 忘れると事故る）

- **P015 が本番ロスターに実採番された**（提出経路テストの副作用・2026-08-20）。
  ★ 行は消さない決定。⚠️ **ロスター上にテストと分かる印が無い**ので
  `20260820-consent-form-live-sync/decisions.md` が唯一の目印。
  → ★ **P015 は実参加者に割り当てない**（焼けた扱い）。次の実参加者は **P016**。
- テストで生じた `P999_block05_gse_20260811_042646.age`（未承認・未送信）の扱い。
  ⚠️ 2026-08-21 に `C:\Users\johnd` 配下（深さ 5）と `C:\gse-dataset` を探したが**見つからなかった**
  （★ 「消えた」とは断定しない。Mac 側にある可能性がある）。
