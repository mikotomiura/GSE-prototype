# 設計判断: R-2〜R-5 の裁定

⚠️★★★ **本ファイルは「研究者が下した裁定」の一次記録である。**
★ handoff (`.steering/_handoff/next-session-r2-r5-decisions.md`) は案内であって裁定ではない。

---

## 決定 1: ★ R-2 = **toolchain を固定する** (`channel = "1.94.1"`)

- **決定**: repo 直下に `rust-toolchain.toml` を置き、`channel = "1.94.1"` ＋
  `components = ["clippy", "rustfmt"]` を宣言する。
- **理由**:
  1. ★ 本 repo は `reproducibility-discipline` で **`Cargo.lock` / seed / `HMM_VERSION` を固定する**
     規律を既に敷いている。⚠️ **toolchain だけ浮いているのは一貫していない。**
  2. ⚠️★★★ R-1 で `-D warnings` の CI ゲートが main に入った以上、
     **コード差分ゼロで main が一斉に赤くなる経路**が実在する。
  3. ★ 版上げは「別 PR で意図的に」になる —— ⚠️ これは `HMM_VERSION` bump と**同じ作法**である。
- **却下案 (a) 固定しない**: ⚠️ rustc / std のセキュリティ修正に自動追従できる利点はあるが、
  ★ **依存の脆弱性は `Cargo.lock` 側の話**なので、ここで守られるのは rustc / std 由来に限られる
  (⚠️ 頻度は低いが 0 ではない)。→ ★ **その低頻度のために「ある朝全部赤」を受け入れる**
  取引は割に合わない。
- **却下案 (b) 中間案 (非ブロッキングの latest stable job)**: ⚠️ `ci.yml` は既に **900 行超**で、
  job を 1 本足す複雑さの代償が、得られる「次に何が来るか事前に見える」利益に見合わない。
  ★ ⚠️ **ただし再検討の余地は残す** —— 版上げ PR が実際に苦痛になったら中間案へ戻ること。

## 決定 2: ★ R-3 = **ローカルで `cargo +1.87 check` を 1 回実測する** (CI job は足さない)

- **決定**: 本機で `cargo +1.87 check --all-targets --features package` を 1 回回し、
  結果を `Cargo.toml` の注記と本 steering に記録する。⚠️ **CI に MSRV job は足さない。**
- **理由**: ★ 実測 #2 で **`+1.87` は `rust-toolchain.toml` を上書きする**ことが確定したので、
  決定 1 と**衝突しない**。⚠️ 継続保証 (CI job) は self-hosted に toolchain をもう 1 本積むので、
  ★ **決定 1 でディスクを既に 1 本ぶん食う**状況では割に合わない。
- **却下案 (a) CI に非ブロッキング MSRV job**: ⚠️ ディスク (mac threshold 15GiB) との二重負荷。
- **却下案 (b) `rust-version` の宣言を撤回**: ⚠️ 宣言は古い toolchain での**エラーメッセージを
  親切にする**効果が実在する。★ 実証できるのに撤回する理由がない。
- **却下案 (c) 何もしない**: ⚠️ ★ `is_multiple_of` の安定化が **ちょうど 1.87.0** で
  **余裕がゼロ**である以上、実測 1 回のコストは安い。
- ⚠️★★★ **限界を明記する**: 本機は Windows なので `*_macos.rs` は 1 行もコンパイルされない。
  → ★ 実証されるのは **「Windows 側の cfg 集合で 1.87 が通る」** ことだけである。

## 決定 3: ⚠️ `rust-toolchain.toml` に **`targets` は書かない**

- **決定**: `targets` フィールドを置かず、`ci.yml` 側の `targets: ${{ matrix.target }}` に任せる。
- **理由** (★ 実測 #4 / #5):
  - ★ 新規 toolchain には **host target の std が同梱**される (`rustup target list --installed
    --toolchain 1.94.1` → `x86_64-pc-windows-msvc`)。
  - ★ `matrix.target` は **両レグとも host と同一** (win=`x86_64-pc-windows-msvc` /
    mac=`aarch64-apple-darwin`)。→ ⚠️ **追加インストールは元々起きていない。**
- **却下案**: ファイルに `targets = ["x86_64-pc-windows-msvc", "aarch64-apple-darwin"]` と書く
  → ⚠️ **相手 OS の std を両機に入れる**ことになり、★ mac のディスク (threshold 15GiB /
  実測の空き 18〜20GiB / `src-tauri/target` が既に 3.0GiB) を無駄に圧迫する。

## 決定 4: ⚠️★★★ R-4 = **env を上書きせず「前提を検査する step」を置く**

- **決定**: テスト側は `else { panic!(..) }` に倒す (無音 skip を廃止)。
  CI 側は `cargo test` の**前**に検査 step を置き、⚠️ **`env:` で HOME / USERPROFILE を
  上書きしない**。
- **理由**: ⚠️★★★ **job レベルで `HOME` を上書きすると mac self-hosted が壊れる。**
  ★ `CARGO_HOME` / `RUSTUP_HOME` の既定は `$HOME/.cargo` / `$HOME/.rustup` なので、
  `HOME` を変えると **toolchain を丸ごと再ダウンロード**し、⚠️ threshold 15GiB の
  ディスクを直撃する。★ しかも **「実機に env が立っているか」という R-4 の元の問いが
  永久に観測不能になる** (自分で立てたものを観測しても答えにならない)。
- ⚠️ **値は出力しない**: ★ `USERPROFILE` / `HOME` の値には **OS ユーザー名**が入る。
  これは**まさに本テストが守っている情報**である。→ **set/unset の別だけ**を出す
  (⚠️★★★ **判断 10 で `${VAR:+set}` 系は却下した** —— 初稿の `${VAR:+set}${VAR:-unset}` が値を漏らしたため、`if [ -n .. ]` を採用)
  (`data-privacy`)。
- **却下案 (a) job の `env:` で実際に設定**: ⚠️ 上記の理由で危険かつ自己言及的。
- **却下案 (b) テストを panic にするだけ (ci.yml を触らない)**: ★ 最小差分だが、
  ⚠️ 赤くなったとき「テストが壊れた」と「env が無かった」を **panic メッセージ 1 本**で
  区別することになる。★ step を分ければ **どの step が赤いか**で即断できる。

## 決定 5: ★ `dtolnay/rust-toolchain@stable` の 3 箇所は**残す**

- **決定**: `check` / `build-windows` / `build-macos` の 3 step をそのまま残し、
  **注記だけ**足して「実際に cargo が使う版は `rust-toolchain.toml` が決める」と明示する。
- **理由**: ★ action は **rustup の存在と既定 toolchain を保証**する役割が残る。
  ⚠️ 特に `check` は `decide-win-runner` が失敗したとき **hosted `windows-latest` へ
  fallback する経路**を持っており、そこを未検証にしたくない。
- **却下案 (a) 3 箇所を削除して rustup 自動 DL に任せる**: ★ `ci.yml` は減るが、
  ⚠️ **hosted fallback 経路を新たに未検証にする**。
- **却下案 (b) `@stable` → `@1.94.1`**: ⚠️★★★ **版番号が `ci.yml` 3 箇所 ＋ ファイル 1 箇所の
  計 4 箇所に分散する**。★ 版上げで 1 つ忘れると**黙って食い違う** (= SSOT が壊れる)。
  → ⚠️ 決定 1 の目的 (再現性) を自分で壊す案なので採らない。

## 決定 6: ★ PR は **2 本に分割し、PR-B (R-3/R-4) を先**に出す

- **決定**: PR-B = R-3 ＋ R-4 → main 緑を確認 → PR-A = R-2。
- **理由**: ★ R-2 は CI 3 job 全部・self-hosted のディスク・初回フル DL という
  **別種のリスク**を持つ。⚠️ PR-B を先に通して **直前の main が緑だと分かっている**状態で
  PR-A を入れれば、★ 赤くなったときの原因が**一意に定まる**。
- ⚠️ ★ 実測 #2 により **技術的な順序制約は無い** ことを確認済み
  (`+1.87` はファイルを上書きするので、R-3 は R-2 の前後どちらでも成立する)。
- **却下案 (a) 全部 1 PR**: ⚠️ CI 1 回・review 1 回で済むが、
  ★ 「toolchain 固定で赤い」のか「test の loud 化で赤い」のかが混ざる。
- **却下案 (b) 記録だけして実装は次セッション**: ⚠️ ★ handoff §0 が
  **「ADR-029 の前に閉じる」**ことを目的に挙げている。記録だけでは目的を達しない。

## 決定 7: ★ R-5 は **PR を作らず、本タスクの `/cross-review` で検証する**

- **決定**: ⚠️ `scripts/run-codex-review.sh` を**先に試す**。exit 0 で完走したら、
  2026-09-12 の診断 (ime-active-ordering 判断 12) と合わせ **2 回連続成功**として R-5 を閉じる。
- **理由**: ★ handoff §4 のとおり **「直す」タスクではなく「もう要らないかを確かめる」タスク**。
  ⚠️ 1 回では codex-cli の版差 (0.142.5 → 0.152.1) の可能性を消せない。
- ⚠️ **「使えない」という前提を持ち込まない** (★ 判断 12 の教訓: cross-reviewer が
  私の指示を鵜呑みにせず診断してくれたおかげで、誤った前提が 1 日で訂正された)。

---

# 実装中に判明した事実 (⚠️ 裁定を実行した結果・2026-09-12)

## 判断 8: ⚠️★★★ **R-3 の実測で `rust-version = "1.87"` が誤りと判明した**

- ★ `cd src-tauri && cargo +1.87 check --all-targets --features package` の実測結果:

  ```
  error: rustc 1.87.0 is not supported by the following packages:
    time@0.3.47 requires rustc 1.88.0
    time-core@0.1.8 requires rustc 1.88.0
    time-macros@0.2.27 requires rustc 1.88.0
  ```
  (exit 101)

- ⚠️★★★ **原因は「宣言の根拠が std API だけだった」こと。** ★ 前タスク (判断 12) は
  `rust-src` の `#[stable(since=..)]` を読んで下限を決めたが、
  ⚠️ **依存 crate 自身が宣言する `rust-version` を一切見ていなかった**。
- ★ 依存グラフ全体を機械的に走査した (`cargo metadata --all-features` の `rust_version`):

  | 要求 | crate |
  |---|---|
  | **1.88.0** | `time@0.3.47` / `time-core@0.1.8` / `time-macros@0.2.27` |
  | 1.87.0 | `wit-bindgen*` / `wasip2` / `wasip3` |
  | 1.87 | `zbus` / `zvariant` 系 |

  ★ 宣言のある crate は **424 / 630**。⚠️ **依存側が要求する最大 = `1.88.0`**。

- ⚠️★★★ **これは「R-3 は実測する価値がある」ことの実証そのものである。**
  ★ 却下案 (c)「何もしない」を採っていたら、**誤った MSRV を宣言したまま**になっていた。
- ★ `Cargo.toml` の旧注記「`edition = "2021"` は resolver "2" なので依存解決を変えない」は
  ⚠️ **それ自体は正しいが、論点がずれていた** —— ★ 問題は「自分の宣言が解決を変えるか」ではなく
  **「依存の宣言が自分をブロックするか」**であり、cargo は後者を**ハードエラーにする**。

## 判断 9: ★ `println!` 禁止 (rust-standards ルール 3) が R-4 の却下案②を独立に裏づけた

- ⚠️ handoff §3 の選択肢②「skip したことを標準出力に必ず出す」は、
  ★ 本 repo では **`println!` / `eprintln!` が規約で禁止**されているため
  (`rust-standards` ルール 3 / `docs/agent-shared.md` 技術的制約 8)、そもそも素直に書けない。
- → ★ 決定 4 (panic + 検査 step) は、**裁定の軸とは独立な規約の側からも支持される**。

## 判断 10: ⚠️★★★ 自分が書いた検査 step に **値を漏らすバグ**があり、実行前に潰した

- ⚠️ 初稿は `echo "USERPROFILE: ${USERPROFILE:+set}${USERPROFILE:-unset}"` と書いていた。
  ★ これは **set のとき `${VAR:-unset}` が値そのものを展開する**ので、
  ⚠️ **CI ログに OS ユーザー名を含むフルパスが出る**。
- ⚠️★★★ **守ろうとしている当の情報を、守るための step が漏らすところだった。**
- ★ `if [ -n ... ]; then echo "set"; else echo "unset"; fi` へ書き換え、
  **ローカル bash で両方向 (set / 両方 unset) を実行して確かめた** (unset → exit 1)。
- ★ 教訓: ⚠️ **`${VAR:+x}${VAR:-y}` のイディオムを「set/unset の三項演算子」として使わない。**

## 判断 11: ★ **同型の「無音 skip」は repo 内に他に無い**ことを機械的に確認した

- ⚠️ R-4 の欠陥は `silent-success-is-not-visible` の一例なので、★ **同じ形が他にもないか**を
  `src/**/*.rs` の全 `#[test]` 関数について走査した (⚠️ 目視ではなくスクリプトで)。
  - 判定: `#[test]` 属性から関数本体の対応 `}` までを追い、**裸の `return;`** を数える。
- ★ **結果**:

  | 対象 | 検出数 |
  |---|---|
  | `HEAD` (修正前) | **1 件** = `lib.rs:5268 fn redact_home_path_masks_real_home_from_env` |
  | 修正後 | **0 件** |

- ⚠️★★★ **検出器そのものを検算した** —— ★ 修正前の版に当てて**ちょうど 1 件**
  (＝私が直した当のもの) を検出することを確認してから「0 件」を主張している。
  ⚠️ これをやらないと「検出器が壊れていて 0 件」と「本当に 0 件」が区別できない
  (★ R-4 で直したのと**同じ形の誤り**を、検証側で繰り返すところだった)。
- → ★ **R-4 はこの欠陥クラスを repo 内で全閉した。** ⚠️ フォローアップは不要。

## 判断 12: ★ R-4 の変異テストを **3 形態**で回し、旧形が無音で緑だったことを**実証**した

⚠️★★★ **「旧形は skip していたはず」で済ませなかった** —— ★ 実際に旧形へ戻して測った。

| # | 形 | env | 結果 | 読み方 |
|---|---|---|---|---|
| A | **新形** (`panic!`) | あり | ★ `1 passed` / exit **0** | ✅ 通常経路は緑 |
| B | **新形** (`panic!`) | ⚠️ **両方 unset** | ★ `FAILED` / exit **101** ＋ 説明付き panic | ✅ **loud になった** |
| C | ⚠️ **旧形** (`return;`) | ⚠️ **両方 unset** | ⚠️★★★ `1 passed` / exit **0** | ⚠️ **保護ゼロで緑だった** |

- ★ C が本件の核心である。⚠️ **`cargo test` は「1 passed」と報告し、CI は緑になる。**
  → ★ `redact_home_path` の env 経路が丸ごと壊れていても、**誰も気付かない**状態だった。
- ★ 実行方法: ⚠️ `cargo test` 経由ではなく **コンパイル済みテストバイナリを直接**
  `env -u USERPROFILE -u HOME` で起動した (★ `cargo` 自身が `USERPROFILE` を必要とするため)。
- ⚠️★★★ **最初の試行は失敗していた** —— ★ `--exact` に短い名前を渡したため
  `running 0 tests` / exit **0** になり、⚠️ **「緑」に見えた**。
  ★ `--list` で完全 path (`submit_command_tests::...`) を取り直して是正した。
  → ⚠️ **検証手順そのものが同じ罠 (「0 件実行」を「合格」と読む) を踏みかけた**ことを記録する。

## 判断 13: ★ PR-B の検証結果 (2026-09-12・Windows 実機)

⚠️★★★ **この表は `show` クロージャ追加前の版に対するもの**である (★ code review MEDIUM 5)。
★ **最終版の実測は判断 22** を見ること。

| ゲート | コマンド | 結果 |
|---|---|---|
| 単体/統合 | `cargo test --features package --workspace` | ✅ exit **0** |
| lint | `cargo clippy --all-targets --features package -- -D warnings` | ✅ exit **0** |
| ゴールデン | `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot ...` | ✅ `OK: 15 snapshots match` |
| schema | `cargo run --bin emit_schema` vs `schema/current.json` | ✅ **byte-equal** |
| MSRV | `cargo +1.88 check --all-targets --features package` | ✅ exit **0** (4m58s) |

⚠️ `HMM_VERSION` は **bump しない** (★ 挙動を 1 ミリも変えていない —— 変更は
テストの失敗経路 ・ Cargo.toml の注記 ・ ci.yml の step のみ)。

## 判断 14: ⚠️★★★ **自分で「doc を関数から引き剥がす」罠を踏み、レビュー前に直した**

- ⚠️ 新 step を `ci.yml` に挿し込んだ初稿は、**既存の「`--features package` を落とすと…」
  コメントブロックと、それが説明する `Cargo test` step の *間***に入っていた。
  → ★ 結果、**既存コメントが私の新 step を説明しているように読める**状態になっていた。
- ⚠️★★★ **これは `post-mac-sync-cleanup` 判断 2 とまったく同型の欠陥である** ——
  ★ あちらは `9eb1384` が doc と `fn write_meta_start` の間に static を挿入し、
  **`meta` 行の仕様書が別の static の説明になっていた**。
- ★ 対応: 新 step ＋ その注記を**ひとかたまりで既存コメントブロックの前**へ移した。
  ⚠️ **step の実行順序は変えていない** (`Cargo build` → 新 step → `Cargo test`)。
  ★ YAML パースで step 列を機械確認した (11 step・順序不変)。
- ★ 教訓: ⚠️ **YAML / Rust を問わず、コメントブロックと被説明対象の間に何も挟まない。**
  ★ 挿入位置は「直前の行」ではなく「**直前のブロックの前**」で考える。

## 判断 15: ★ **toolchain 1 本 ≈ 1.3〜1.4 GiB** を実測した (⚠️ PR-A のディスク評価の根拠)

- ★ 実測 (2026-09-12・Windows 実機・`du -sh ~/.rustup/toolchains/*`):

  | toolchain | サイズ |
  |---|---|
  | `stable-x86_64-pc-windows-msvc` | **1.4 GiB** |
  | `1.94.1-x86_64-pc-windows-msvc` | **1.3 GiB** |
  | `1.87-x86_64-pc-windows-msvc` | **1.3 GiB** |

- ⚠️★★★ **PR-A (R-2) の意味**: 固定すると各ランナーに **stable ＋ 固定版の 2 本**が載る。
  → ★ **増分は約 1.3 GiB**。
  ⚠️ mac self-hosted はディスクガードが `threshold=15 GiB` / 実測の空きが **18〜20 GiB**
  (★ `5900ab4` の main run で `free before: 20 GiB (wiped=false)`)。
  → ★ **1.3 GiB を引いても threshold を割らない**が、⚠️ **余裕は確実に減る**。
- ⚠️ **初回 CI で `free before:` の行を必ず見ること** (★ 他の計器の数字で外挿しない ——
  `mac-clippy-green-and-ci-gate` §2 で `df -h` と guard の計器が 1 GiB 食い違った実績がある)。
- ★ 版を上げるたびに古い版が積むので、⚠️ **`rustup toolchain uninstall <old>` を版上げ手順に入れる**
  (★ `rust-toolchain.toml` の注記に書いた)。

### ⚠️ 本機の後片付け (★ 研究者判断)

- ★ R-3 の実証で本機に **`1.87` / `1.88` / `1.94.1` の 3 本**が増えた (計 **約 3.9 GiB**)。
  - `1.94.1` は **PR-A で使う**ので残す。
  - ⚠️ `1.87` / `1.88` は**一度きりの MSRV 実証**に使っただけ (計 **約 2.6 GiB**)。
  - → ★ 消すなら `rustup toolchain uninstall 1.87 1.88`。⚠️ **勝手に消さず研究者に確認する。**

## 判断 16: ⚠️★★★ security review LOW 1 を採用 —— **失敗メッセージ自身が実ホームを漏らしていた**

- ⚠️ 既存行 `assert!(!masked.contains(&home), "home leaked: home={home} masked={masked}")` は、
  ★ **このテストが失敗したとき (= 伏せ字が壊れたとき) にだけ発火する**。
  → ⚠️★★★ **守っている当の情報を、守りが壊れた瞬間に自分で CI ログへ出す**構造だった。
- ⚠️ security-checker の実測による重要な補強: ★ **GitHub Actions のログマスクは
  登録済み secret と `::add-mask::` にしか効かない。** `USERPROFILE` / `HOME` は secret ではないので、
  **echo すればマスクされずそのまま残る**。→ ★ 「出さない」ことが唯一の防御である。
- ★ 対応: `let show = |s: &str| s.replace(&home, "<HOME>");` を置き、**両方の assert** に適用した
  (⚠️ 2 つ目の `"got: {masked}"` も同じ穴を持っていた)。
- ⚠️★★★ **「書いたから効くはず」で終わらせず、変異で実測した**:
  ★ `redact_home_path` を「入力をそのまま返す」へ一時改変してテストを発火させたところ、

  ```
  home leaked: masked=could not read input <HOME>/Documents/GSE-sessions/x.ndjson: nope
  ```

  → ✅ **構造は読めて、OS ユーザー名は出ない**。⚠️ 改変は直後に復元し、`MUTATION` 残存 0 を確認した。
- ★ ⚠️ **これは本 PR の主題 (R-4) と同じ欠陥の再帰である** —— 「守っているつもりで守っていない」を
  直しに来て、**直す対象のすぐ隣に同じ穴が開いていた**。

## 判断 17: ★ security review LOW 3 を採用 —— **`data-privacy` ルール 7 の引用を撤回**

- ⚠️ 私は ci.yml の注記で「(`data-privacy` ルール 7 と同趣旨)」と書いたが、
  ★ ルール 7 は **非打鍵チャネル (ポインタ / フォーカス / `secure_input` / レイアウト識別子) の
  凍結表**であり、⚠️ **env 由来のホームパスは射程外**である (★ SKILL.md L191 で確認)。
- ⚠️ 本 repo は**文書の番号引用を根拠として扱う**運用なので、★ 番号の付け間違いは
  「根拠があるように見えて無い」状態を作る。→ **番号を外し、Skill 全体と当該 doc コメントを指す**形へ訂正。

## 判断 18: ⚠️ security review LOW 2 は **コードを変えず注記で残した**

- ★ 指摘: 検査 step は `shell: bash` だが、直後の `cargo test` は `shell:` 未指定
  (⚠️ `ci.yml` に `defaults:` ブロックは **0 件** —— 実測) なので **Windows では pwsh** で走る。
- ★ 実害が無いと判断した根拠 (⚠️ security-checker の実測):
  1. env は**どちらもランナープロセスから継承**される (★ shell が env を作るわけではない)。
  2. Windows では `USERPROFILE` が**常に立つ**。★ テストは **USERPROFILE を先に見る**。
  3. ⚠️ git-bash が `HOME` を合成する環境なら乖離がありうるが、★ 本機では**合成されないことを実測**。
- **却下案**: `cargo test` step にも `shell: bash` を足して揃える
  → ⚠️ **既存の・現に緑な step を触る**ことになり、得られる利益 (理論上の乖離の解消) に見合わない。
- → ★ **注記として ci.yml に残した** (⚠️ 次に触る人が同じ疑問を持ったとき、ここで止まれるように)。

---

# code-review 後の判断 (⚠️★★★ HIGH が 1 件出た)

## 判断 19: ⚠️★★★ **HIGH —— 私が ci.yml に書いた「実測済み」が、CI と同じ経路では偽だった**

- ⚠️ 私は注記に「★ 本機では (git-bash が `HOME` を) 合成しないことを実測済み」と書いた。
  ★ 根拠にしたのは security-checker の実測だが、⚠️ **それは `bash → bash` の経路**だった。
- ⚠️★★★ **CI の Windows レグは `pwsh → git-bash` である。** ★ code-reviewer が
  その経路で測り直し、⚠️ **合成されることを発見した**。→ ★ **自分で再現して確認した**:

  | 経路 | Windows 側の env | git-bash の中 |
  |---|---|---|
  | `bash → bash` (⚠️ 旧根拠) | `HOME`/`USERPROFILE`/`HOMEDRIVE`/`HOMEPATH` すべて unset | ★ `HOME: unset` |
  | ⚠️★★★ **`pwsh → git-bash`** (★ **CI と同じ形**) | **同上・すべて unset** | ⚠️★★★ **`HOME: set -> /c/Users/johnd`** |

  → ⚠️ MSYS2 ランタイムが **`HOME` を合成する**。★ 一方 **`USERPROFILE` は合成されない**。
- ⚠️★★★ **帰結: 私の検査 step は Windows レグで空振りだった。**
  ★ `HOME` 分岐は**構造的に失敗しえない**ので、⚠️ **「検査したつもりで検査していない」** ——
  **本タスクが潰しに来た欠陥クラスそのものを、潰すための道具の中で作っていた。**
- ★ **対応**: 検査ロジックを OS で分岐させ、⚠️ **Windows では `HOME` を見ず `USERPROFILE` だけで判定**する
  (★ pwsh 側の実態と一致する)。macOS は `cargo test` も bash なので bash の観測がそのまま忠実。
- ★ **検証** (⚠️ pwsh → git-bash の経路で 3 方向):

  | # | 条件 | 結果 |
  |---|---|---|
  | W1 | Windows・`USERPROFILE` あり | ✅ `USERPROFILE: set` / exit **0** |
  | W2 | ⚠️ Windows・Windows 側の env を**全部剥がす** | ✅ `::error::` / exit **1** (★ 旧ロジックなら合成 `HOME` で **PASS していた**) |
  | M1 | 非 Windows レグ相当 | ✅ 両方 report / exit **0** |

### ⚠️ 却下案: Windows だけ `shell: pwsh` にする (★ 観測は最も忠実)

- ★ `pwsh` (PowerShell **Core**) は本機に **7.6.6** が存在する。
- ⚠️ **ただし WindowsApps (Microsoft Store) 経由の導入**であり、
  ★ **ランナーサービスの PATH で解決できるかは未検証**。⚠️ `ci.yml` に前例も無い
  (★ memory: self-hosted Windows は「システム PATH / 実行ポリシー」で過去に躓いている)。
- → ★ **実績のある `shell: bash` を保ち、見る変数の側を正す**方を採った。
  ⚠️ 新しい未検証の依存 (pwsh の可用性) を、検査のために増やさない。

## 判断 20: ★ MEDIUM 5 件をすべて採用した

| # | 指摘 | 対応 |
|---|---|---|
| M1 | `.steering/_handoff/README.md:16` に**同一の失効文が逐語で残存** (★ 索引側の方が読まれる) | ✅ 訂正。⚠️ repo 全体を grep して**他に無い**ことも確認 |
| M2 | `show` は `home` **完全一致のみ**伏せる → ⚠️ 部分的な退行では 2 つ目の assert にユーザー名が残る | ✅ `home` の末端要素 (= ユーザー名) も `<USER>` へ伏せた |
| M3 | `docs/development-guidelines.md` の `check` job 手順が**逐語列挙**で、本 step も **R-1 の clippy step も載っていない** (★ 既存ドリフト) | ✅ **2 つとも**追記 (⚠️ 既存ドリフトの巻き取りを含む) |
| M4 | MSRV 再検査の運用指示が **`Cargo.toml` のコメントにしか無い** (★ `grep -rn "MSRV\|rust-version" docs/ scripts/ .claude/ .github/` = 0 件) → ⚠️ **回す場所が無い手順は回らない** | ✅ `docs/verification-runbook.md` §1 に **(f) MSRV 検査**と合格条件を追加 |
| M5 | 判断 13 の実測表は **`show` 追加前の版**に対するもの | ✅ 最終版で 5 ゲートを回し直した (判断 21) |

## 判断 21: ★ LOW の扱い

| 指摘 | 対応 |
|---|---|
| steering 3 ファイルが `${VAR:+set}` を処方したまま (⚠️ 判断 10 で方式変更済み) | ✅ 3 件とも「判断 10 で却下」と追随させた |
| step が `Cargo build` の**後**にあり、前提が崩れていると**フルビルドを消費してから**落ちる | ✅ **job の先頭 (checkout 直後) へ移した** (★ `timeout-minutes: 30` に対する fail-fast) |
| `rust-version = 1.88` の拘束元は自コードでなく **`Cargo.lock` の `time` 系** | ✅ `Cargo.toml` に明記 (⚠️ `time` が外れると宣言だけが過剰に残る) |
| `::error::` に `title=` が無い | ✅ `::error title=env precondition::` にした |

★ **code-reviewer の追加発見 (⚠️ 私の留保を弱められる)**: mac 専用 crate (`core-graphics` /
`cocoa` / `objc2`=1.71 / `block2`=1.71) も `--all-features` の**同じグラフに入っており**、
要求は 1.88 未満。→ ★ **「Windows の cfg 集合に限る」という留保は依存側には不要**で、
残る未検証は **GSE 自身の mac ソースが使う std API だけ**である。⚠️ `Cargo.toml` に反映した。

## 判断 22: ★★★ **最終版 (レビュー反映後) の検証結果** — ⚠️ これが PR-B の実測である

★ 2026-09-12・Windows 実機 (G-GEAR)。⚠️ **判断 13 の表はこれに置き換わる。**

| ゲート | コマンド | 結果 |
|---|---|---|
| 整形 | `cargo fmt --check` | ✅ exit **0** |
| 単体/統合 | `cargo test --features package --workspace` | ✅ exit **0** (★ **659 passed** ＋ 統合 41・**0 failed**) |
| lint | `cargo clippy --all-targets --features package -- -D warnings` | ✅ exit **0** |
| ゴールデン | `gse-replay --snapshot tests/snapshots/minimal.json` | ✅ `OK: 15 snapshots match` |
| schema | `emit_schema` vs `schema/current.json` | ✅ **byte-equal** |
| MSRV | `cargo +1.88 check --all-targets --features package` | ✅ exit **0** (4m58s) |
| ⚠️ MSRV 下限 | `cargo +1.87 check --all-targets --features package` | ✅ **exit 101** (★ 落ちることの確認 = 下限が正しい証拠) |

★ **変異による実証** (⚠️ 「書いたから効くはず」で終わらせない):

| # | 変異 | 期待 | 結果 |
|---|---|---|---|
| 1 | 新形 × env あり | pass | ✅ exit 0 |
| 2 | 新形 × env なし | **赤** | ✅ exit **101** ＋ 説明付き panic |
| 3 | ⚠️ **旧形** (`return;`) × env なし | ⚠️ **緑になってしまう** | ⚠️★★★ `1 passed` / exit **0** (= 欠陥の実証) |
| 4 | 伏せ字: `redact_home_path` を壊して assert を発火 | 値が出ない | ✅ `masked=... <HOME>/Documents/...` |
| 5 | CI step: Windows・env 剥奪 (`pwsh → git-bash`) | **赤** | ✅ `::error::` / exit **1** (★ 旧ロジックは PASS した) |
| 6 | CI step: 非 Windows | 緑 | ✅ exit 0 |

⚠️ **`HMM_VERSION` は bump しない** —— ★ 挙動を 1 ミリも変えていない
(変更はテストの失敗経路 / `Cargo.toml` の宣言と注記 / `ci.yml` の step / docs のみ)。

---

# `/cross-review` (Codex 独立レビュー) の結果

## 判断 23: ★★★ **R-5 を閉じる** —— ⚠️ ラッパーは Windows で動く

- ★ **`bash scripts/run-codex-review.sh main..HEAD -- <3 パス>` が exit 0 で完走した。**
  ⚠️ **1312 は再現しなかった。**
- ★ **ラッパー経由であることの客観的証拠**: `.codex/budget.json` が**自動で更新された**
  (`120,799 → 142,909` / `invocations 5 → 6`)。
  ⚠️ 前回 (post-mac-sync 判断 14) は `codex exec` 直呼びだったので**台帳が自己申告**だった。
  → ★ 今回は**機構が記録している**。
- ★ **2 回連続成功** (2026-09-12 の診断コール ＋ 本レビュー) なので、
  handoff §4 の条件「2 回連続で動けば R-5 は閉じてよい」を満たす。→ ✅ **R-5 = 閉じる。**
- ⚠️★★ **ただし切り分けは完了していない**: ★ 両回とも **codex-cli 0.152.1** だったので、
  「版差 (0.142.5 → 0.152.1) が直した」のか「元々実行時の権限差だった」のかは**未決のまま**。
  → ★ **実務上の結論は「ラッパーを使ってよい」**であり、⚠️ 原因の同定は不要と判断する
  (★ 0.142.5 へ戻して再現を試す価値は無い)。
- ★ `scripts/run-codex-review.sh` への**コード変更は不要**だった (⚠️ R-5 は「直す」タスクではなかった)。

## 判断 24: ⚠️★★★ **Codex 指摘 2 を採用 —— `show()` の伏せ字が診断を壊していた**

- ⚠️ 指摘: `t.replace(&user, "<USER>")` は**全文字列の部分一致**なので、
  ユーザー名が短い / 一般語だと期待文字列の構造まで壊れる。
- ★ **実測で再現した** (⚠️ 推測で採否を決めない):

  | user | ⚠️ 旧 (naive) の出力 |
  |---|---|
  | `Doc` | `~\<USER>/**<USER>uments**/GSE-sessions/...` |
  | `s` | `~\<USER>/**Document<USER>**/GSE-**<USER>e<USER><USER>ion<USER>**/x.ndj<USER>on` |

- ⚠️ **区切り文字を前に付けるだけ (`/{user}`) では不十分**だった —— ★ `Doc` は `/Documents` に当たる。
- ★ **採用した形**: `/` `\` で区切って **要素ごとに `==` で比較**する (⚠️ 部分一致を原理的に起こさない)。
- ★★★ **決定的な検証** (⚠️ 最初に使った指標「出力に user が部分文字列として残るか」は
  **指標自身が誤り**だった —— `Documents` に含まれる `Doc` を拾ってしまう。
  ★ 正しい基準は **「出力がユーザー名に依存しないか」**):

  | 方式 | ユーザー名 6 種 (`johnd`/`Doc`/`s`/`tanaka_taro`/`a`/`Users`) に対する出力の種類 |
  |---|---|
  | ⚠️ 旧 (naive) | **4 種類** → ★ **壊れ方そのものがユーザー名を漏らす** |
  | ✅ 採用 (要素完全一致) | **1 種類** → ★ **ユーザー名に非依存 = 漏れない** |

## 判断 25: ★ Codex 指摘 3 を採用 —— **Windows の実区切り `\` を覆っていなかった**

- ⚠️ 従来のテスト入力は `{home}/Documents/...` と **`/` を足していた**が、
  ★ **Windows で実際に出るパスは `C:\Users\<user>\Documents\...`** である。
- ★ `redact_home_path` は `home` を前方一致で置換するだけなので**区切り文字に依存しない** ——
  ⚠️ **が、それはテストが言っていることではなかった**。→ ★ `\` 形の assert を 2 本追加した。
- ★ この形は **macOS でも成立する** (`home=/Users/x` → `~\Documents\...`) ので `#[cfg]` は不要。

## 判断 26: ★ Codex 指摘 1 は **コメントの射程を明確化**して対応

- ⚠️ 指摘: 「ci.yml が『Windows で HOME を見てはならない』と書いているのに、
  テスト本体は OS 分岐していない」= 設計意図と実装が不一致に見える。
- ★ **不一致ではない**。⚠️ ただし**そう読めるのは注記が悪い**ので直した:
  - ★ 合成が起きるのは **git-bash の中だけ**。⚠️ pwsh から起動される `cargo test` は
    **合成されない素の env** を見る。→ ★ テスト本体が OS 分岐しないのは**正しい**。
  - ★ 開発者が git-bash から `cargo test` を回した場合は合成 `HOME` を拾うが、
    ⚠️ それは**実在するホームの値**なので検査は成立する。
- → ★ ci.yml に **「テスト側に OS 分岐を足さないこと」** を明記した
  (⚠️ 足すと本物の env 経路を検査しなくなる)。

## 判断 27: ⚠️ Codex 指摘 4 (MSRV の継続検査が無い) は **却下**

- ★ **既に研究者裁定 (決定 2) で「CI job は足さない」と決めてある**。
  ⚠️ Codex 自身も「コメントで明示されている」「リスクを受け入れる判断ならよい」と留保している。
- ★ **緩和策は入れてある**: `docs/verification-runbook.md` §1 に **(f) MSRV 検査**を追加し、
  ⚠️ **依存を更新した回に回す**手順として恒久化した
  (★ 従来は `Cargo.toml` のコメントにしか無く「回す場所が無い手順」だった)。

---

# ★★★ PR #193 (PR-B) の CI 実測 — ⚠️ **R-4 の元の問いに答えが出た**

★ run `34677596718` / 2026-09-12。**check 両レグ ＋ frontend-check すべて pass**
(mac 6m4s / win 5m7s / frontend 40s)。

## 判断 28: ⚠️★★★ **R-4 の元の問い「CI 環境で `USERPROFILE` / `HOME` は立っているか」の答え**

★ mac セッション §8.3 が「**観察不能**」と判定した問いに、**ついに答えが出た**。

| レグ | ランナー | `USERPROFILE` | `HOME` |
|---|---|---|---|
| Windows | `g-gear-win-x64` | ✅ **set** | (★ 見ない —— MSYS2 が合成するため) |
| macOS | `macbook-air-m-arm64` | ⚠️★★★ **unset** | ✅ **set** |

- ⚠️★★★ **macOS では `USERPROFILE` が立っていない。**
  → ★ あの回帰保護は **mac 側では `HOME` だけに依存していた**。
  ⚠️ もし誰かが「Windows 用だから」と `USERPROFILE` を先に見る実装を
  `USERPROFILE` **のみ**に狭めたら、**mac 側の保護が丸ごと消えて無音で緑になっていた**。
- ★ **これが「観察できるようにする」ことの価値である** —— ⚠️ 従来は
  テストが無音 skip するので、**この事実を知る方法が無かった**。
- ★ 検査 step の所要時間は **両レグとも 0 秒** (⚠️ fail-fast の代償はゼロ)。

## 判断 29: ★ step 別の所要時間 (⚠️ PR-A の見積もりの基準)

| step | win | mac |
|---|---|---|
| checkout | 6s | 4s |
| ★ **Env precondition (R-4)** | **0s** | **0s** |
| `dtolnay/rust-toolchain@stable` | **12s** | **2s** |
| `cargo build` | 120s | 130s |
| `cargo test` | 101s | 143s |
| ゴールデン | 10s | 17s |
| schema | 1s | 2s |
| clippy | 43s | 49s |
| **job 全体** | **5m7s** | **6m4s** |

⚠️ `timeout-minutes: 30` に対し **24 分近い余裕**がある。
→ ★ PR-A で toolchain の初回 DL (★ 1 本 ≈ 1.3〜1.4 GiB) が乗っても十分収まる見込み。

## 判断 30: ⚠️★★★ **ディスクは guard 自身の計器だけで論じる** (★ PR-A の可否)

- ★ 実測 (mac・**guard の出力行そのもの**):

  ```
  free before: 20 GiB (threshold=15 floor=8)
  free after:  20 GiB (wiped=false)
  ```

- → ★ **threshold まで 5 GiB の余裕**。⚠️ PR-A の増分は **約 1.3 GiB** (判断 15) なので、
  **20 - 1.3 = 18.7 GiB** で threshold を割らない。→ ✅ **PR-A を入れてよい。**
- ⚠️★★★ **`df -h` の数字で外挿しない** —— ★ `mac-clippy-green-and-ci-gate` §2 で
  自分の計器 (`df -h` = 16 GiB) と guard の計器 (`df -Pk` = 17 GiB) が **1 GiB 食い違い**、
  「次の run で掃除が走る」という**予測を外した**前科がある。

---

# PR-A (R-2) のレビュー結果 — ⚠️★★★ **HIGH 4 件。私の前提が 2 つ崩れた**

## 判断 31: ⚠️★★★ **security HIGH —— 固定先 `1.94.1` は「現状維持」ではなく *巻き戻し* だった**

- ⚠️ 私は commit メッセージにも `decisions.md` にも「**固定前も 1.94.1 だった**」と書いた。
  ★ 根拠は `rustc --version` を**本機で叩いた**こと。
- ⚠️★★★ **それは本機にしか当てはまらなかった。** ★ 自分で CI ログを確認した (一次資料):

  | | 版 | 日付 |
  |---|---|---|
  | ⚠️ **CI の両レグ** (PR #193 / run 34677596718) | **rustc 1.98.1** | 2026-09-01 |
  | ★ 本機 (G-GEAR) の `stable` | **rustc 1.94.1** | 2026-03-25 |

  → ⚠️ **本機のローカル `stable` が約 5.5 か月古かった**だけで、**CI は追従していた**。
  → ⚠️★★★ `1.94.1` に固定すると **4 マイナーの巻き戻し**になる。
- ★ **副次的に判明した重要な事実**: ⚠️ 従来 **ローカル `stop-check.sh` の clippy 1.94 と
  CI の clippy 1.98 は、別の lint 集合を検査していた**。→ ★ 固定はこの不一致も同時に閉じる。
- ★ **対応**: `channel = "1.98.1"` へ訂正。⚠️ R-2 の目的 (不意打ちを止める) は
  **版番号が何であれ達成される**ので、目的を損なわずに巻き戻しだけが消える。
- ★ security-checker はさらに「1.94.1 同梱の cargo 0.95.0 は CVE-2026-5222 / 5223
  (`cargo < 0.97.0`) に該当する」と報告した。⚠️ **発火条件 (third-party registry) は
  本 repo で不成立** (★ `Cargo.lock` の `source` は全件 crates.io・`[registries]` 置換なし) だが、
  ★ **巻き戻す理由が無い以上、確かめるまでもなく避けるべき**である。

## 判断 32: ⚠️★★★ **これは本セッション 2 度目の「手元の観測を CI に当てはめた」誤りである**

| # | 誤り | 正しい一次資料 |
|---|---|---|
| 1 (判断 19) | ⚠️ `bash → bash` で「`HOME` は合成されない」と測り、**CI の `pwsh → git-bash`** に当てはめた | ★ `pwsh → git-bash` で測り直す → **合成される** |
| 2 (判断 31) | ⚠️ **本機の `stable`** を見て「CI も 1.94.1」と当てはめた | ★ **CI の run ログ** → **1.98.1** |

- ⚠️★★★ **どちらも `verify-before-claiming` が名指しで禁じている形**である ——
  「**別の環境で測った値を、当の環境の値として使う**」。
- ★ **一般化**: ⚠️ **「実測した」と書くときは、*どの環境で* 測ったかを必ず併記する。**
  ★ CI について論じるなら **CI の run ログが唯一の一次資料**であり、
  ⚠️ 手元の `rustc --version` / `bash` の挙動は**傍証にすらならない**。

## 判断 33: ★ code review HIGH 3 件を **1 つの step で閉じた**

⚠️ 3 つとも「固定版を *誰がいつ入れるか* が CI に書かれていない」ことに帰着する。

| # | 指摘 | ⚠️ 放置した場合 |
|---|---|---|
| H-1 | ★ 固定版を**実際に入れる主体**が CI に無い (暗黙 auto-install 頼み) | ⚠️ `gse-mac` の rustup 版は**未測定**。auto-install が無効なら **全 step の手前で赤** |
| H-2 | ⚠️ 暗黙 DL は**ディスクガードより後**に起きる | ⚠️★★★ guard の `free before:` が **DL 前の数字**になる = **測りたい増分を測る前に測る** |
| H-3 | ⚠️ 固定が効いた**証拠が run ログに 1 行も残らない** (★ ci.yml に `rustc --version` は **0 件**) | ⚠️★★★ 「緑になった」だけでは **どの版で緑なのか判別できない** = **見えないまま緑** |

- ★ **対応**: `dtolnay` の直後・**ディスクガードの前**に明示 step を置いた (★ 3 job すべて)。

  ```yaml
  - name: Install pinned toolchain (rust-toolchain.toml)
    shell: bash
    run: |
      set -euo pipefail
      rustup toolchain install    # ★ 引数なし = active toolchain
      rustup show active-toolchain
      cargo --version
      cargo clippy --version
  ```

- ★ **逐語で確認した** (`rustup toolchain install --help`):
  「Install or update the given toolchains, **or by default the active toolchain**」
  → ⚠️ 引数なしで **toolchain file が指す版を `profile` / `components` 込みで**入れる。
- ⚠️★★★ **H-3 は本タスクの主題と同型である** —— ★ R-4 で「走ったか緑だったか区別できない」を
  潰しに来ておきながら、**同じ形の穴を PR-A で作っていた**。

## 判断 34: ★ `profile = "minimal"` を足した (code review MEDIUM)

- ⚠️ 省略すると**各実機の rustup 既定 profile** が使われる (★ 本機は `default`)。
  → **入る量が機械ごとに変わり決定性が無い。**
- ★ 実測: `rustup component list --toolchain 1.94.1` に **`rust-docs` が installed** で、
  ⚠️ **1.3 GiB のうち 726 MiB が docs** —— ★ CI はこれを **1 バイトも使わない**。
- ⚠️ `components` は profile と**独立に効く**ので、`minimal` でも clippy / rustfmt は入る。
- ⚠️★★★ **削減量を数字で断定しない** —— ★ 726 MiB は git-bash の `du -sm` (見かけサイズ) で、
  guard の `df -Pk` とは計器が違う。→ **実際の増分は初回 run の `free before:` で測る。**

## 判断 35: ★ MEDIUM —— **mac の host triple を CI ログで実測し直した**

- ⚠️ 指摘: 決定 3 (`targets` を書かない) の安全性は **gse-mac が arm64 であること**に
  全面的に依存するのに、★ 実測 #5 は **`ci.yml` を読んだだけ**だった。
- ⚠️★★★ **Intel mac なら `--target aarch64-apple-darwin` が `can't find crate for core` で即死する**
  (★ `dtolnay` の `targets:` は **stable にしか入らない**ので救わない)。
- ★ **CI ログで実測した** (PR #193 / mac レグ): **`host: aarch64-apple-darwin`**。
  → ✅ 決定 3 は安全。⚠️ ただし**根拠を一次資料へ差し替えた** (判断 32 の一般化の適用)。

## 判断 36: ★ 残りの MEDIUM / LOW の扱い

| 指摘 | 対応 |
|---|---|
| ⚠️ `build-*` の注記が「`working-directory: src-tauri` の cargo step」と書くが、**当 job にそれは無い** (実経路は `npx tauri build`) | ✅ 各 job の実経路を書く形へ訂正 |
| ⚠️ 「action は **rustup を用意する**」の根拠が未確認 (★ 実際は rustup が既に在る前提) | ✅ 射程を狭めた ——「保証されるのは **`rustup default` が立つこと**」 |
| ⚠️ runbook の「手元の rustc が新しいから CI と違う結果になる は起きない」が**無条件に読める** | ✅ 「**rustup 管理下の cargo に限る**」を明記。★ `rustup show active-toolchain` で確かめる 1 行を追加。⚠️ かつ「消えるのは rustc 版差だけで **OS 差と `--features package` 差は残る**」を併記 |
| ⚠️ 版上げ手順 4 に**どの機械で uninstall するか**が無い | ✅ `gse-win` / `gse-mac` / 手元の **3 か所**を名指し。★ 手順 2 も実機名を明記 |
| ⚠️ 同一 8 行の注記が **3 箇所に複製** (★ disk-guard を composite 化した教訓と同型) | ✅ `check` を**正典**にし、他 2 箇所は **1 行参照**へ縮めた |
| ★ 版上げ手順に「CI ログで版を確認する」step が無い | ✅ **手順 5** として追加 |

## 判断 37: ⚠️★★★ **判断 15 / 30 の検証指示を訂正する** (★ ただしレビューの提案とは別の形で)

- ⚠️ レビュー指摘 (security M-2 / code H-2): ★ 判断 15 は「**初回 CI で `free before:` を見よ**」と
  書いたが、⚠️ **暗黙 auto-install はディスクガードより *後* に起きる**ので、
  **初回の `free before:` は DL 前の数字**であり、**測りたい増分を測る前に測っている**。
- ★ レビューの提案は「**2 回目以降**の run を見よ」。
- ⚠️★★★ **私はそれを採らなかった。** ★ 判断 33 で **install step をディスクガードの *前* へ置いた**
  ので、⚠️ **初回から guard が DL 後の真値を測る**ようになった。
  → ★ **「2 回目以降を見る」という運用で回避するのではなく、順序そのものを直した。**
  ⚠️ 回避策は「次からは正しく測れる」だけで、**初回の数字が嘘である事実は消えない**。
- ★ **したがって正しい検証指示はこうなる**:
  > ★ **初回 run の `free before:` を見る。** ⚠️ install step が guard より前にあることを
  > step 順で確認したうえで読む (★ 順序が崩れたら数字は無意味になる)。
- ⚠️ **他の計器で外挿しない** (★ `df -h` と guard の `df -Pk` が 1 GiB 食い違った前科)。

## 判断 38: ★ レビューが補強した「実測 #1 の交絡が無い」こと

- ★ security-checker の実測: `~/.rustup/settings.toml` の **`[overrides]` が空**。
- → ⚠️ `rustup show active-toolchain` の `overridden by ...rust-toolchain.toml` は
  **`rustup override set` (ディレクトリ override) による交絡ではなく、本当にファイル由来**である。
- ★ **実測 #1 はこの点で正しかった**ことが独立に確認された。

## 判断 39: ★ M-1 の射程を正確化する (★ レビューの自己訂正を採用)

- ⚠️ security-checker は当初「std CVE の 2 クラスが live」と読める書き方をし、**自ら訂正した**:

  | CVE クラス | GSE での出現 | 射程 |
  |---|---|---|
  | `std::process::Command` (**CVE-2024-24576 critical**) | ★ **製品コード 20 箇所** (`lib.rs` / `g1.rs` / `bin/submit.rs` / `hook_macos.rs`) | ⚠️ **本当に直撃するのはこちら** |
  | `std::fs::remove_dir_all` (CVE-2022-21658 high) | ★ **テストコードのみ 10 箇所** | 射程は狭い |

- ★ **どちらも 1.98.1 では修正済み** (⚠️ 1.94.1 でも修正済みだった)。
- ⚠️★★★ **論拠の形はこう読む**: 「toolchain 由来の脆弱性は **年 1 件弱**と低頻度だが、
  ★ **唯一の critical (CVE-2024-24576) が GSE の製品コードのクラスに当たった**」。
  → ⚠️ 「低頻度だから無視してよい」ではなく「**低頻度だが当たれば自分のコードに当たる**」。
  → ★ だから版上げ手順 0 (advisory 点検) を**人の手順として明文化**した。

## 判断 40: ★★★ **1.98.1 での再検証** — ⚠️ 固定先を変えたので全ゲートを回し直した

★ 本機を 1.98.1 へ切り替えて実測 (2026-09-12・Windows 実機):

```
1.98.1-x86_64-pc-windows-msvc (overridden by 'C:\GSE-prototype\rust-toolchain.toml')
rustc  1.98.1 (48a229cea 2026-09-01)
cargo  1.98.1 (797e8a9bc 2026-08-05)
clippy 0.1.98 (48a229ceae 2026-09-01)
```

| ゲート | 結果 |
|---|---|
| `cargo fmt --check` | ✅ exit **0** |
| ⚠️★★★ `cargo clippy --all-targets --features package -- -D warnings` | ✅ exit **0** (4m51s) |
| `cargo test --features package --workspace` | ✅ **11 スイートすべて ok**・FAILED 0 |
| ゴールデン | ✅ `OK: 15 snapshots match` |
| schema | ✅ **byte-equal** |

- ⚠️★★★ **clippy が要点だった** —— ★ 1.94 と 1.98 では lint 集合が違うので、
  **1.94 で緑だったことは 1.98 で緑であることを保証しない**。→ **実際に回して確かめた。**
- ★ 併せて **ローカルと CI の lint 集合が初めて一致した**
  (⚠️ 従来はローカル 1.94 / CI 1.98 で別物を検査していた・判断 31)。
- ⚠️ `HMM_VERSION` は **bump しない** (★ ゴールデン 15 が byte-equal = 挙動不変)。

---

# ★★★ PR #194 (PR-A) の CI 実測 — ⚠️ **「緑だった」で終わらせずに 4 点を測った**

★ run `34679690117` / 2026-09-12。**check 両レグ ＋ frontend-check すべて pass**
(mac 7m18s / win 6m19s / frontend 48s)。

## 判断 41: ✅ **① 固定が効いた証拠が CI ログに残った** (★ H-3 の狙いどおり)

```
[win] 1.98.1-x86_64-pc-windows-msvc (overridden by 'C:\actions-runner\_work\GSE-prototype\GSE-prototype\rust-toolchain.toml')
      rustc 1.98.1 (48a229cea 2026-09-01) / cargo 1.98.1 (797e8a9bc 2026-08-05)
[mac] 1.98.1-aarch64-apple-darwin (overridden by '/Users/johnd/actions-runner/_work/.../rust-toolchain.toml')
      rustc 1.98.1 (48a229cea 2026-09-01) / cargo 1.98.1 (797e8a9bc 2026-08-05)
```

- ⚠️★★★ **これが無ければ「どの版で緑なのか」は永久に分からなかった。**
  ★ 従来 `ci.yml` に `rustc --version` を出す step は **0 件**だった。
- ★ **mac の host triple も改めて確定**した: `1.98.1-**aarch64**-apple-darwin`
  → ✅ 決定 3 (`targets` を書かない) は安全 (判断 35 の再確認)。

## 判断 42: ✅ **② step 順が正しい** (★ H-2 の狙いどおり)

`3. Env precondition` → `4. dtolnay` → **`5. Install pinned toolchain`** → **`6. Disk guard`**

⚠️ **install が guard より前**にあるので、guard は **DL 後の真値**を測る。

## 判断 43: ✅ **③ ディスクの実増分を guard 自身の計器で測れた**

| run | `free before:` | `wiped=` |
|---|---|---|
| PR #193 (★ 固定前・DL なし) | **20 GiB** (threshold=15 floor=8) | false |
| ⚠️ **PR #194** (★ 固定・初回 DL 後) | **19 GiB** (threshold=15 floor=8) | false |

- ★ **減少は約 1 GiB**。⚠️ threshold 15 GiB に対し **4 GiB の余裕**が残る。→ ✅ **掃除は走らない。**
- ⚠️★★★ **`du` の見かけ値 (default 1.3 GiB / minimal 見込み 0.6 GiB) で外挿しなかったのが正解だった** ——
  ★ 実測は **guard 自身の `df -Pk`** で **1 GiB**。⚠️ 2 つの run 間の差なので他の要因も含みうるが、
  **計器と順序は正しい**。
- ★ `profile = "minimal"` を入れたので、⚠️ **default profile のままなら約 2 GiB 減っていた**はず
  (★ 726 MiB の `rust-docs` 分)。→ **判断 34 は効いている。**

## 判断 44: ✅ **④ install step のコストは初回のみ**

| step | win | mac |
|---|---|---|
| `Env precondition (R-4)` | **0s** | **0s** |
| `dtolnay/rust-toolchain@stable` | 6s | 7s |
| ⚠️ **`Install pinned toolchain`** | **97s** | **86s** |
| `Disk guard` | (skip) | 1s |
| `cargo build` | 99s | 129s |
| **job 全体** | **6m19s** | **7m18s** |

- ★ **97s / 86s は初回 DL の代金**である。⚠️ 2 回目以降は toolchain が実機に残るので
  **ほぼゼロになる見込み** (★ 次の run で確認すること)。
- ★ `timeout-minutes: 30` に対し **約 23 分の余裕**。→ ✅ 問題なし。

## 判断 45: ⚠️★★★ **「緑だった」で終わらせない** —— ★ この 4 点は *事前に* 決めてあった

- ★ PR の本文に「**初回 CI で必ず見るもの**」として **4 項目を先に書いてから** CI を回した。
  ⚠️ **後から「何を見るか」を決めると、都合のよい数字だけを見ることになる。**
- ★ 4 点すべてが**期待どおり**だった。⚠️ もし ③ が「DL 前の数字のまま」だったら、
  **緑でも H-2 が閉じていない**と判定するつもりだった。

---

# `/cross-review` (Codex 独立レビュー) — PR-A

## 判断 46: ★★★ **R-5 の 3 回目の成功** (⚠️ 切り分けは依然として未了)

- ★ `scripts/run-codex-review.sh` が **exit 0** で完走。⚠️ **1312 は再現しない** (3 回連続)。
- ★ 予算は自動計上 (`142,909` → 本レビュー分)。⚠️ 3 回とも **codex-cli 0.152.1** なので、
  **版差か権限差かの切り分けは依然として未了**である (★ 実務上は「使ってよい」で足りる)。

## 判断 47: ⚠️★★★ **Codex 指摘 1 (HIGH) を採用 —— 不変条件を「コメント」から「step」へ移した**

- ⚠️ 指摘: `dtolnay` の `targets:` が入れるのは **stable 側にだけ**。
  ★ その後 cargo は固定版へ切り替わるので、⚠️ **固定版の側に target std が無い**と
  `--target` が `can't find crate for core` で落ちる。
  → ★ **いまは host == `matrix.target` なので成立しているが、コメント頼みの壊れやすい設計**。
- ★ **これは正しい**。⚠️ 判断 35 で「Intel mac なら即死する」と自分で書いておきながら、
  **その不変条件を強制する仕掛けは置いていなかった** (★ 注記に書いただけ)。
- ★ **対応**: install step へ `--target "${{ matrix.target }}"` を明示。
  ⚠️ **決定 3 とは矛盾しない** —— ★ ファイルに `targets` を書くと**相手 OS の std を両機に**
  入れるが、**step 側はレグごとに 1 つだけ**入る。
- ★ **実機で動作を確認した** (⚠️ 「書いたから動く」で済ませない):
  `rustup toolchain install --target x86_64-pc-windows-msvc` → **exit 0** /
  `rustup target list --installed` → `x86_64-pc-windows-msvc`。

## 判断 48: ⚠️★★★ **実行して副作用を見つけた —— この step は rustup 自身を self-update する**

- ⚠️ 上の検証を回したとき、**予期しない出力**が出た:

  ```
  info: checking for self-update (current version: 1.29.0)
  info: downloading self-update (new version: 1.29.1)
  ```

- ⚠️★★★ **`rustup toolchain install` は既定で rustup 本体を更新する。**
  → ★ **self-hosted 実機のツールを黙って書き換える**うえ、
  ⚠️ **所要時間が読めなくなる** (= `timeout-minutes` の見積もりが揺れる)。
  ★ PR #194 の install step が **97s / 86s** かかったのも、一部はこれの可能性がある。
- ★ **対応**: `--no-self-update` を **3 job すべて**に付けた。
  ⚠️ rustup の更新は**意図して別途行う**。CI の副作用でやらない。
- ★ **教訓**: ⚠️ **レビュー指摘を直したら、直したものを動かして出力を読む。**
  ★ この副作用は**誰の指摘にも無く、実行して初めて見えた**。

## 判断 49: ⚠️ Codex 指摘 2 は **false positive** (★ diff しか見えないことに起因)

- ⚠️ 指摘: 「runbook は clippy を必須化しているが、CI 側に同等条件の step がある保証が
  **diff から読めない**」。
- ★ **反証 (一次資料)**: `ci.yml:543` に実在する ——
  `cargo clippy --all-targets --features package --target ${{ matrix.target }} -- -D warnings`
  → ⚠️ **runbook と同条件** (★ `--target` の有無だけが違い、これは意図的)。
- ★ Codex 自身が「**diff 外に該当 step があるなら問題なし**」「誤検知可能性: 中」と留保していた。
- ⚠️ これは `post-mac-sync-cleanup` 判断 13 の `is_ime_active_check` と**同型の FP** である
  (★ **Codex は repo を読めない**ので、削除/未変更の行の存在を確認できない)。

## 判断 50: ★ Codex 指摘 3 / 4 の扱い

| 指摘 | 判定 |
|---|---|
| ⚠️ **指摘 3**: 固定版運用に**セキュリティ更新の検知ゲートが無い** (CI / 定期チェック) | ★ **既知・裁定済み** (決定 2 / 判断 39)。⚠️ 緩和は `rust-toolchain.toml` の**版上げ手順 0** と runbook。⚠️★★★ **ただし security-checker と Codex が *独立に* 同じ点を挙げた** → ★ **研究者へ follow-up として挙げる** (下記) |
| ★ **指摘 4** (LOW): 将来 `cargo test` の shell/default が変わると検査と実行環境が乖離しうる | ★ **既に注記済み** (⚠️ `defaults:` が無いことを実測し、変わったら再確認する旨を ci.yml に記載)。⚠️ 「`cargo test` step 側で検証する方が堅い」案は、★ **既存の緑の step を触る**代償に見合わないので採らない |

## 判断 51: ★★★ **cross-review 反映後の CI 実測** — ⚠️ 直したものを動かして確かめた

★ run `34680342872` (head `f71d72a`) / 2026-09-12。**全 job pass** (mac 5m39s / win 4m25s)。

### ★ install step の「証拠ブロック」の実出力

```
[win] 1.98.1-x86_64-pc-windows-msvc (overridden by 'C:\actions-runner\_work\...\rust-toolchain.toml')
      cargo 1.98.1 (797e8a9bc 2026-08-05) / clippy 0.1.98 (48a229ceae 2026-09-01)
      x86_64-pc-windows-msvc                    ← ★ rustup target list --installed
[mac] 1.98.1-aarch64-apple-darwin (overridden by '/Users/johnd/actions-runner/_work/...')
      cargo 1.98.1 (797e8a9bc 2026-08-05) / clippy 0.1.98 (48a229ceae 2026-09-01)
      aarch64-apple-darwin                      ← ★ rustup target list --installed
```

→ ✅ **固定版に `matrix.target` の std が入っていることが CI ログで確認できる** (判断 47)。
⚠️ これで「host == matrix」という不変条件は**コメントではなく step とログ**で保証される。

### ⚠️★★★ `--no-self-update` の効果 (★ 判断 48 の検証)

| 項目 | 前 run (`b82d411`) | ⚠️ 今 run (`f71d72a`) |
|---|---|---|
| `Install pinned toolchain` | win **97s** / mac **86s** | ✅ win **0s** / mac **1s** |
| rustup self-update | ⚠️ (ローカル実測で 1.29.0 → 1.29.1 の DL を確認) | ✅ **発生なし** |
| disk guard `free before:` | 19 GiB (wiped=false) | ✅ **19 GiB** (wiped=false)・安定 |

- ★ **97s / 86s は初回 DL の代金だった** —— ⚠️ 2 回目以降は toolchain が実機に残るので **ほぼゼロ**。
  → ✅ 判断 44 の見込みが当たった。**定常状態での固定のコストは実質ゼロ**である。
- ★ ⚠️ **新しく分かったこと**: `dtolnay/rust-toolchain` 自身のコマンドラインは
  `rustup toolchain install stable --target ... --component clippy --profile minimal --no-self-update`
  → ★ **action は既に `--no-self-update` と `--profile minimal` を使っていた**。
  ⚠️ **自己更新を起こしていたのは私が足した step だけ**だった (★ 判断 48 の副作用の出所が確定)。
  ★ 併せて ci.yml の既存注記「dtolnay は `--profile minimal` で入れる」も**実ログで裏が取れた**。
