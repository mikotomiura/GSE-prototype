# 次セッション開始プロンプト（**Mac 側**）— v0.1.29 をリリースし、配布物を差し替える

このファイルの「===」以下をコピペして開始する。
★ ⚠️★★★ **Mac で実行する。** 理由は §3-2（`hdiutil` / `codesign` / `ditto` が要る）。

> ## ⚠️★★★ このファイルは `next-session-prompt-v0128-release-and-redistribution.md` を **置き換える**
>
> ★ **v0.1.28 はタグが打たれないまま中身が変わった。** 旧ファイルの手順（`git tag v0.1.28`）を
> そのまま実行してはならない。⚠️ **番号も、載っているものも違う。**
>
> | | 旧ファイル (v0.1.28) | ★ 本ファイル (v0.1.29) |
> |---|---|---|
> | タグ | ⚠️ 未 push のまま | ★ **`v0.1.29` を打つ** |
> | 載っているもの | T-1 修正 + IME WinEvent **定数**の修正 | ★ **＋ `IME_ACTIVE` の駆動源の変更**（下記） |
>
> ★ 旧ファイルの §2-4 / §2-5（zip 再作成・Drive 差し替え）の**手順そのものは有効**である。
> ⚠️ **タグ名と「何が載っているか」だけが変わった。**

---

===

## §0 ★ このセッションの仕事

| # | 何 | 種別 |
|---|---|---|
| **R-1** | ★ **macOS で CI が緑になることを確かめる**（⚠️ 新規ファイルが macOS でもコンパイルされる） | 検証 |
| **R-2** | ★ `v0.1.29` をタグ push → リリース生成 | 作業 |
| **R-3** | ★ 配布 zip を作り直す（⚠️ **macOS 必須**） | 作業 |
| **R-4** | ★ Drive を差し替える（⚠️ **旧版を先に削除**してから） | 作業 |

⚠️★★★ **R-2 に進む前に、Windows 側の実起動確認が終わっていることを確認する**（→ §1.3）。

---

## §1 ⚠️★★★ 何が変わったのか（★ Mac 側も知っておく必要がある）

### 1.1 ★ `IME_ACTIVE` の駆動源が変わった（Windows のみ）

★ Windows 11 の IME 候補 UI は `ShowWindow` ではなく **DWM の cloak/uncloak** で
表示制御されており、⚠️ 文書化された `EVENT_OBJECT_IME_*`(0x8027-29) は
**60 秒 × 8 回の実測で 1 件も飛ばない**。
→ ★ PR #109（定数修正）は正しかったが、⚠️ **その結果 `ime_shadow` が 0 行になっていた。**

★ v0.1.29 では `EVENT_OBJECT_CLOAKED`/`UNCLOAKED` ＋ **ウィンドウクラス完全一致 `IME`**
で駆動し直した。⚠️ **実測で確定した事実**（打鍵 257・変換 12 回）:

| # | 実測 |
|---|---|
| 1 | ★ 変換していないとき（打鍵から 4 秒以上）は **100% cloaked** → **`UNCLOAKED` = 候補表示** |
| 2 | ★ 無操作 60 秒で cloak は **0 件**（false positive 無し） |
| 3 | ★ 候補が隠れている区間の最小 **308ms** → debounce は **150ms** |

★ 詳細: `.steering/20260823-ime-active-cloak-rewiring/`（`findings.md` / `decisions.md`）。

### 1.2 ⚠️★★★ **G1 の挙動が 2 つ変わる**（★ ここが Mac 側にも効く）

| # | ⚠️ 何が変わるか |
|---|---|
| 1 | ★ **`ime_shadow` 行が復活する**（v0.1.27 以前は誤った量、v0.1.28 は 0 行） |
| 2 | ⚠️★★★ **変換中に推論が pause する**（`engine.set_paused`）——★ 設計意図どおりだが、**推定窓が減る** |

★ pause の割合は**自然な打鍵で約 15〜20%** の見積り。
⚠️ **2026-08-23 の計測で出た 52.1% は採らない** —— ★ 辺の向きを判定するために
「候補を出したまま 3 秒止まる」を指示した結果であり、**計測手順の産物**である
（`findings.md` §4.4）。★ 代表値は Windows 側が自然な打鍵で別途取る。

### 1.3 ⚠️★★★ **Windows 側の宿題が終わっているか確認してから始める**

★ 本タスク（R-2 以降）は、⚠️ **次の 2 つが済んでいることが前提**である:

- [ ] ★ 実起動で `ime_shadow` 行が**出る**（⚠️ **G1 画面 = GSE 自身の窓でも**確認済みであること）
- [ ] ★ 実起動・無操作 60 秒で `ime_shadow` が **1 行も出ない**

⚠️ **なぜ G1 画面での確認が要るか**: IMM32 は **GUI スレッドごとに `IME` クラス窓を作る**ので、
★ **GSE 自身の窓に日本語を打つと cloak するのは GSE 自身の窓**である。
→ ⚠️ そのため cloak hook からは `WINEVENT_SKIPOWNPROCESS` を**意図的に外してある**。
★ ここが落ちていると **G1 でだけ `ime_shadow` が 0 行**になる。

★ 確認できていなければ **Windows 側へ差し戻す**。⚠️ 未確認のまま配布しない。

---

## §2 ★ R-1 — macOS で CI が緑になることを確かめる

⚠️★★★ **新規ファイル `src-tauri/src/input/ime_cloak.rs` は `#[cfg]` を付けていない。**
★ 意図的である —— 畳み込みロジックを **OS 非依存**にして
**macOS の CI でもテストが走る**ようにした（`agent-shared.md`「OS ごとに規則が違う
ロジックは両 OS に対のテストを置く」）。

→ ⚠️ **したがって macOS でもコンパイルされ、12 本のテストが走る。**
★ Windows 側では検証できないので、**ここが Mac 側で最初に見るところ**である。

```bash
cd src-tauri
cargo build
cargo test --workspace          # ★ ime_cloak の 12 本を含む
cargo clippy --all-targets
cargo fmt --all -- --check
```

★ 期待: **すべて exit 0**。⚠️ Windows 側での実測 exit code は
`findings.md` §6 にある（test 462 passed / clippy 0 / fmt 0）。

⚠️★ **落ちた場合の切り分け**:

| 症状 | ★ 見るところ |
|---|---|
| `ime_cloak.rs` が macOS でコンパイルできない | ⚠️ `std::collections::BTreeSet` しか使っていないはず。OS 依存が混入していないか |
| dead_code 警告 | ★ `pub mod ime_cloak` 経由で公開されているので出ないはず。出るなら `input/mod.rs` を見る |
| `const _: () = assert!(...)` で落ちる | ★ `MAX_SESSION_MS + 1000 <= 8000` の不変条件。⚠️ 意図的な静的表明なので**消さない** |

★ ⚠️ **macOS 側に「修正」は原則要らない見込み**である（Win32 呼び出しは
`ime_windows.rs` / `hook_windows.rs` に隔離してある）。⚠️ **ただし Windows では確かめられない。**
→ ★ 落ちたら直し、**直した内容を `.steering/` に記録**してから R-2 へ進む。

---

## §3 ★ R-2〜R-4 — リリースと配布

### §3-1 タグを push → CI が自動でビルドしてリリースを作る

⚠️★★★ **先に PR がマージされ、`main` が v0.1.29 になっていることを確認する。**

```bash
git checkout main && git pull
grep -m1 '"version"' package.json          # ★ 0.1.29 であること
git tag v0.1.29
git push origin v0.1.29
```

★ `.github/workflows/ci.yml` がタグ push で走らせるもの:

| job | runner | 出す物 |
|---|---|---|
| `build-windows` | `windows-latest`（hosted） | `gse-next.exe` / `gse-submit.exe` |
| `build-macos` | ⚠️ **`[self-hosted, gse-mac]`** | `gse-next_0.1.29_aarch64.dmg` / mac tools |
| `release` | `ubuntu-latest` | ★ GitHub Release（両方の成果物を添付） |

⚠️★★★ **`build-macos` は self-hosted。その Mac が落ちているとリリースが片肺になる。**

### §3-2 配布 zip を作り直す（⚠️★★★ ここが macOS 必須の理由）

```bash
cd experiments/20260801-controlled-friction-task
./make-common-app-zip.sh --tag v0.1.29
```

⚠️★★★ **`--tag` を必ず付ける。既定は `v0.1.24` である**（スクリプト内の `TAG="v0.1.24"`）。
★ 前回（2026-08-19）も「`--tag` を付けた。既定の `v0.1.24` ではない」と記録されている。

★ 出力（★ Drive に置くのはこの 2 個）:

```
dist/_common/G1_実施用_macOS.zip
dist/_common/G1_実施用_Windows.zip
```

⚠️ **`make-distribution.sh` と混同しない。** そちらは被験者 1 人ぶん（課題ページ入り・割付が要る）。
★ 今回もアプリだけが変わったので、**差し替えるのは共通 zip の 2 個だけ**である。
⚠️ 課題ページ（`blockNN.html`）を共通側に入れてはならない（全員が同じ課題を持つ・D-1）。

### §3-3 Drive を差し替える

⚠️★★★ **上げるのは研究者の判断**（スクリプトは意図的に Drive へ上げない）。

⚠️★★★ **旧版の zip を「先に削除」してから新しいものを置く**（★ 研究者指示 2026-08-22）。
★ 順序は **削除 → 検算（不在確認）→ 設置 → 検算（バイト数一致）**。
⚠️ 上書きに頼らない —— 名前が同じでも**古い実体が残る事故**がある。

⚠️★ **今回は v0.1.27 の zip が Drive にある**（v0.1.28 は配布されていない）。
→ ★ 消すのは **v0.1.27 のもの**である。

---

## §4 ⚠️★★★ 差し替えは **収集開始前の一度きり**

★ 収集途中で差し替えると **新旧が混ざったコホート**になり、
`scripts/capabilities_gate.py` が **`MIXED` で止める**（`meta.app_version` と
`capabilities` がファイルごとに食い違う）。⚠️ `preregistration.md §3.6` により回復不能。

★ 現状は **確証標本 0/3 名 = 収集開始前**なので、いま差し替えれば問題ない。

---

## §5 ⚠️ やらないこと（★ 混ぜない）

### 5.1 ⚠️★★★ **macOS 側に「候補ウィンドウ滞在」の計器を足さない**

★ **研究者判断（2026-08-23）で `(a) Windows 単独で収集開始` に決まっている**
（`.steering/20260823-ime-active-cloak-rewiring/decisions.md` D-9）。

⚠️ **したがって macOS の `kCGWindowList` ポーリング（A-2）は実装しない。**
★ 良かれと思って足すと、⚠️ **記録仕様が収集直前に変わる**ことになる。

★ 決めた内容と、それが作る非対称:

| | Windows (v0.1.29〜) | macOS |
|---|---|---|
| `IME_ACTIVE` の出所 | ★ **観測**（候補 UI の cloak/uncloak） | ⚠️ **推定**（keycode ヒューリスティック） |
| `ime_shadow` | ★ **出る** | ⚠️ **構造的に出ない**（`emit_ime_shadow` が Windows 限定） |

★ ⚠️ この非対称は **`capabilities` の `config_gated` が機械的に申告する**ので、
「測れて 0 だった」という偽の結論にはならない。→ ★ **これで良い、と決めた。**

### 5.2 ⚠️ その他

- ⚠️ `ime_dwell_med` の再解釈（→Q2 = 0.729 の系列）—— ★ 別セッション
- ⚠️ ADR-014 の研究者判断 6 件 —— `.steering/20260822-ime-active-rewiring/adr014-open-decisions.md`
- ⚠️ 推論への配線（段 3）—— **ADR-011 D4 により G1 判定後**

---

## §6 ★ 受け入れ条件（Done）

- [ ] ★ **macOS で `cargo build` / `cargo test --workspace` / `clippy` / `fmt --check` が全部 0**
- [ ] ★ PR の CI が**全ジョブ緑**（`frontend-check` の capabilities gate 2 ステップを含む）
- [ ] ★ `main` にマージされ、`v0.1.29` が main の祖先
- [ ] ★ GitHub Release に **Windows / macOS 両方**の成果物が付いている
- [ ] ★ `G1_実施用_macOS.zip` / `G1_実施用_Windows.zip` を **`--tag v0.1.29`** で作り直した
- [ ] ★ Drive: **旧 v0.1.27 を削除 → 不在を検算 → 設置 → バイト数一致を検算**
- [ ] ⚠️ **Windows 側の実起動確認（§1.3）が済んでいることを確認した**

---

## §7 ⚠️ 落とし穴（★ 実測）

1. ⚠️★★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/` にある）
2. ⚠️ `--tag` を忘れると **v0.1.24** の zip ができる（★ 既定値）
3. ⚠️★ CI の **cache 保存ステップが長い** —— 実質的な検査が全部 ✓ になってから **30 分以上**
   かかる。★ 止まっているのではない
4. ⚠️ `build-macos` は self-hosted（`gse-mac`）。**その Mac がオンラインである必要がある**
5. ⚠️ `.claude/settings.json` / `.gitignore` に**タスクと無関係の未コミット変更**がある（★ commit しない）

---

## §8 ★ 完了報告に必ず書くこと

- [ ] ★ macOS での `cargo test --workspace` の**実測 exit code と件数**
- [ ] ⚠️ macOS 側に**修正が要ったか**（★ 要ったなら何を）
- [ ] ★ タグ / Release の URL
- [ ] ★ 配布 zip の**バイト数**（Drive 検算に使う）
- [ ] ⚠️ Drive の**削除 → 設置**を実際にどうしたか
