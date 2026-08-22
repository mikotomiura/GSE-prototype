# 次セッション開始プロンプト（**Mac 側**）— v0.1.28 をリリースし、配布物を差し替える

このファイルの「===」以下をコピペして開始する。
★ ⚠️★★★ **Mac で実行する。** 理由は §2-4（`hdiutil` / `codesign` / `ditto` が要る）。

> ## ★★★ 2026-08-22 更新 — **§2-2（bump）は Windows 側で完了済み**
>
> ⚠️★★★ **v0.1.28 の中身が変わった。** 単なる T-1 の反映ではなく、
> **計器のバグ修正が 1 件入っている**（★ 下記）。
>
> | 何 | 状態 |
> |---|---|
> | **§2-2 バージョン bump（4 ファイル）** | ✅ **Windows 側で実施済み**（PR: `chore/v0128-ime-winevent-fix`） |
> | ⚠️★★★ **IME WinEvent 定数の修正** | ✅ **Windows 側で実施済み**（★ 下記・**これが今回の主目的**） |
> | **§2-3 タグ push 〜 §2-5 Drive 差し替え** | ⚠️ **Mac 側の担当（本タスク）** |
>
> ### ⚠️★★★ 何を直したのか（★ Mac 側も知っておく必要がある）
>
> `hook_windows.rs` の IME WinEvent 定数が **3 つとも別のイベントを指していた**:
> `0x8016`=`EVENT_SYSTEM_ARRANGMENTPREVIEW` / `0x8017`=`EVENT_OBJECT_CLOAKED` /
> `0x8018`=`EVENT_OBJECT_UNCLOAKED`（★ 正しくは `0x8027`/`0x8028`/`0x8029`）。
> → ⚠️ **背景ウィンドウの cloak（UWP サスペンド・仮想デスクトップ切替）で `IME_OPEN` が立ち、
> 片方向ラッチされて `β_writing` に固定される**。★ `β` は `obs` → `p_*` に直結するので **G1 の確証データに効く**。
>
> ★ **確証標本 0/3 名 ＝ 収集開始前**なので `preregistration.md §3.6` の回復不能問題は起きない。
> ⚠️ **収集が始まれば直せなくなる。だから v0.1.28 に載せる。**
>
> ★ 詳細: `.steering/20260821-workspace-behavior-triage/findings-instrument-defects.md`
>
> ### ⚠️★★ Windows 側に残っている宿題（★ Mac は待たなくてよい）
>
> ⚠️★★★ **`IME_ACTIVE` の配線を直す（B）** —— ★ **働く検出器（`EnumWindows`）が「無効化用」に
> しか繋がっておらず、データを産む側は死んだ経路（WinEvent）に繋がっている。**
> → ★ **別セッションで実施する**
> （`_handoff/next-session-prompt-ime-active-rewiring-and-idea-followups.md`）。
>
> ⚠️ **これはリリースを止めない** —— ★ **A（`config_gated` への移動）で安全側に倒してある**ので、
> **0 行が「信号が無かった」と誤読されることはもう無い**。
>
> → ⚠️★★★ **本セッションは `git checkout main && git pull` の後、`§2-3`（タグ push）から始める。**

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

### ✅ **PR #108 は 2026-08-21 にマージ済み**（★ §2-1 は完了している）

```
1d0a6b2 Merge pull request #108 from mikotomiura/fix/precollection-close-and-x-axis
e6198fa docs(steering): Windows 側の次を作業場行動メモの仕分けと議論に差し替える
ff49117 docs(steering): 次の 2 セッション (Mac=リリース / Windows=表現層) の引き継ぎを書く
c5a8e17 docs(adr): ADR-009 に Accepted 条件を明文化する (T-3・議論のみ)
987fcac feat(analysis): capabilities の機械判定ゲートを追加する (ADR-013 Migration 3/4)
c42b0e4 fix(g1): ブロック遷移を直列化し、自動終了と押下の競合を閉じる
```

★ CI は**全ジョブ緑**だった。⚠️ 特に **`check` が win / mac の self-hosted 両方で**
`Cargo build` / `Cargo test --workspace` / `Snapshot regression` / `Schema drift check` を通した
（★ 「手元の検証は CI の代替にならない」への答え）。
`frontend-check` には**今回追加した capabilities gate の 2 ステップ**が含まれ、これも緑。

→ ⚠️★★★ **本セッションは §2-2（バージョン bump）から始める。**
★ 最初に `git checkout main && git pull` すること。

検証は全部緑: `cargo test --workspace` **468 passed** / ゴールデン **6 本 byte-equal** /
`HMM_VERSION` **0.4.0 据え置き** / `emit_schema` **byte-equal** / schema parity **exit 0** /
Python **83 tests** / `--self-test` 2 本 / `check_citations` 緑。

## §1 ⚠️★★★ なぜこのタスクが要るか — **修正が被験者の手元に届いていない**

- 配布済み zip は **v0.1.27** で作られ、**Drive へは研究者がアップロード済み**（2026-08-19）
- ⚠️★★★ **2026-08-22 更新**: `main` は **v0.1.28**（PR #109 でマージ済み）になったが、
  ★ **配布物はまだ v0.1.27 のまま**である。→ ⚠️ **ここが本タスクで埋める穴。**
- ★ v0.1.28 に載っているもの: **T-1 の修正**（PR #108）＋ ⚠️★★★ **IME WinEvent 定数の修正**（PR #109）

→ ⚠️★★★ **いま収集を始めると、被験者は修正前のビルドを走らせる。**
★ 「収集開始前に閉じる」という動機がそのまま無効になる。
⚠️ **とりわけ IME 修正は G1 の `obs` / `p_*` に直結する**（★ 冒頭の更新ヘッダ）。

### ⚠️★★ しかも「後から差し替える」ができない

収集途中で v0.1.28 に差し替えると、**新旧が混ざったコホート**になる。
★ これは今回作った `capabilities_gate.py` が **`MIXED` で止める**、まさにその失敗様式である
（`meta.app_version` と `capabilities` がファイルごとに食い違う）。

→ ★ **差し替えるなら収集開始前の一度きり。** ⚠️ 走り出したら `§3.6` により回復不能。

## §2 ★ 手順（★ この順に実行する）

### ~~§2-1 PR → CI → main マージ~~ ✅ **完了済み（2026-08-21・PR #108）**

★ **やることは無い。** 最初に `git checkout main && git pull` して
`1d0a6b2` 以降になっていることだけ確認し、**§2-2 へ進む**。

⚠️ 参考（次に PR を出すときのため）: `check` は **win / mac とも self-hosted**
（`gse-win=G-GEAR` / `gse-mac`）で走る。★ **その Mac がオンラインである必要がある**。
⚠️ Windows 側が offline なら 30 秒で hosted へ fallback する（`decide-win-runner`）。
⚠️★ **cache 保存ステップ（`Post Run rust-cache`）が長い** —— 実測で
**実質的な検査が全部 ✓ になってから 30 分以上**かかった。★ 止まっているのではない。

### ~~§2-2 バージョンを 0.1.28 へ上げる~~ ✅ **完了済み（2026-08-22・Windows 側）**

⚠️★★★ **やることは無い。** ★ `git pull` して `package.json` / `tauri.conf.json` /
`Cargo.toml` / `Cargo.lock` がすべて **`0.1.28`** になっていることだけ確認し、**§2-3 へ進む**。

★ 併せて **IME WinEvent 定数の修正**（冒頭の更新ヘッダ）も同じ PR に入っている。

<details><summary>★ 参考（Windows 側が実施した内容）</summary>

### 旧 §2-2 バージョンを 0.1.28 へ上げる

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

</details>

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

⚠️★★★ **旧 v0.1.27 の zip を「先に削除」してから新しいものを置く**（★ 研究者指示 2026-08-22:
「**前回の app らを削除したうえで乗せなおす**」）。
⚠️ 上書きに頼らない —— ★ 名前が同じでも**古い実体が残る事故**があるため、
**削除 → 検算（不在確認）→ 設置 → 検算（バイト数一致）** の順にする。
★ 残ると被験者がどちらを落としたか分からなくなり、⚠️ `capabilities_gate.py` が `MIXED` で止める
コホートを**人手で作る**ことになる。

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
- [ ] ⚠️★★★ **Drive の差し替え — 旧配布物を *先に削除* してから新しいものを置く**（★ 研究者指示 2026-08-22）
      - [ ] **旧 v0.1.27 の `G1_実施用_macOS.zip` / `G1_実施用_Windows.zip` を削除**（★ 上書きではなく削除）
      - [ ] v0.1.28 の 2 個を置く
      - [ ] 検算（バイト数一致 / 置き場所 / **旧版と余計な物の不在** / 共有範囲）
      ⚠️ **残すと被験者がどちらを落としたか分からなくなり、`capabilities_gate.py` が `MIXED` で止める
      コホートを人手で作ることになる。**
- [ ] ⚠️ Windows 実機スモークの依頼（**§4-1**）
- [ ] ⚠️★★★ **IME 修正の実機確認の依頼（§4-2）** —— ★ **リリースは止めないが、収集開始前に必ず**

## §4 ⚠️ Windows 側でしかできないこと（★ 忘れると片肺になる）

### §4-1 配布 zip の起動確認（★ 従来どおり）

★ `G1_実施用_Windows.zip` は **Mac で組まれる**が、⚠️ **Windows で起動確認していない**。
→ ★ リリース後、Windows 側セッションで次を実施する:

- [ ] zip を展開して `gse-next.exe` が起動する
- [ ] `meta` 行に **`app_version = 0.1.28`** と **`g1_mode = "marker"`** が出る
- [ ] G-1 二度押しで前ファイルが閉じ、新ファイルができる
- [ ] ⚠️ 生 NDJSON は repo に置かない（★ 値だけを `.steering/` に転記）

### §4-2 ✅ **IME の実機計測は完了済み**（2026-08-22・★ Windows 側で実施）

⚠️★★★ **結果は「IME イベントは 1 件も飛ばない」だった**（★ 60 秒 × 3 回）。

| 実測 | 数値 |
|---|---|
| ★ フックは生きている | `alive = 6544` |
| ★★★ 日本語入力は確かに行われた | `TEXTSELECTIONCHANGED` **298** / `VALUECHANGE` **246** / `CREATE`=`DESTROY` **680** |
| ⚠️★★★ **IME イベントは 0** | `IME_SHOW`/`HIDE`/`CHANGE`/`CONV_TARGET` すべて **0** |
| ⚠️ 旧定数の誤検知率 | `CLOAKED` 84 ＋ `UNCLOAKED` 88 = **60 秒で 172 件** |

→ ★ **対処は済んでいる**: `capabilities` の `ime_shadow` を **`config_gated`** へ移した（A）。
⚠️ **0 行が「信号が無かった」と誤読されることはもう無い。**
→ ★ **配線の修正（B）は別セッション**（`_handoff/next-session-prompt-ime-active-rewiring-and-idea-followups.md`）。

⚠️★ **`EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED`(0x8030) は入れない**と決めた
（★ 実測で **0 件**だったため）。⚠️ **測ってから決めた**ので、根拠は推測ではない。

### §4-3 ★ 配布後に Windows 側で見ること

- [ ] ⚠️ 実起動ログの `meta` 行で **`capabilities.config_gated` に `ime_shadow` が入っている**こと
- [ ] ★ `app_version = 0.1.28`

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
