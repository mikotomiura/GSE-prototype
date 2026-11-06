# 検証テスト ランブック (回帰 + 機能 + フォーム)

開発者・研究者向けの **動作検証手順** を一箇所にまとめる。リリース前・PR マージ前・実機配布前に
ここを上から実行する。データ収集パイロットの運用は `docs/calibration-smoke-runbook.md` /
`docs/pilot-runbook.md` を、被験者スモークは `.steering/*/smoke-test-runbook.md` を参照。

- **対象**: macOS 13+ (Apple Silicon) / Windows 11。`analysis/` は OS 非依存、`input/`・overlay は OS 固有。
- **プライバシー**: 検証で生成する NDJSON にもキーストローク**内容**は含まれない (VK コード列のみ)。
  外部 LLM・外部サービスへ NDJSON 生ログを送らない (`data-privacy`)。

---

## 1. 自動検証 (OS 非依存・CI 相当・必須)

`src-tauri/` で実行する。**全部 green でなければ先に進まない。**

> ⚠️★★★ **toolchain は `rust-toolchain.toml` (repo 直下) で固定されている**（2026-09-12・R-2）。
> ★ repo の中で cargo を叩けば **rustup がその版へ切り替える**（未導入なら自動 DL）。
> → ★ **rustc の版差に由来する食い違いは消える。**
>
> ⚠️★★ **ただし成立するのは「rustup 管理下の cargo を使っている」場合だけ**である。
> ★ Homebrew / apt / MSYS 由来の cargo や、下記の shim 破損時は **ファイルが無音で無視される**。
> → ★ **まず `rustup show active-toolchain` を叩き、`overridden by .../rust-toolchain.toml` が
> 出ることを確かめる**（⚠️ 出なければ以下の結果は CI と比較できない）。
>
> ⚠️★★★ **これは「手元の検証が CI の代替になる」という意味ではない。**
> ★ 消えるのは **rustc の版差だけ**で、⚠️ **OS 差**（`*_macos.rs` は Windows で 1 行も
> コンパイルされない）と **`--features package` の有無**は残る
> （`docs/agent-shared.md`「手元の検証は CI の代替にならない」）。
>
> ★ 版を上げるときは **`rust-toolchain.toml` を書き換える単独 PR** を立てる（手順はファイル内に記載）。
> ⚠️ `rust-version`（`src-tauri/Cargo.toml`）とは**別物** —— ★ あちらは利用者に約束する下限。

> ⚠️ ★ **`~/.cargo/bin/cargo` が動かない環境がある**（2026-08-06 に macOS で実測）。
> `~/.cargo/bin/*` は rustup の shim（symlink）で、`rustup` 本体が消えると**全部 dangling** になり
> `no such file or directory` で落ちる。⚠️ ★ `ls` ではリンクが見えるので**壊れていると気づきにくい**。
> → 実体は `~/.rustup/toolchains/<toolchain>/bin/cargo`。`cargo --version` が通らなければそちらを使う。
> ★ これを踏むと `run.sh` の cargo ゲート 4 本が「飛ばした」と言って**素通り**する。

```bash
cd src-tauri

# (a) 単体・統合テスト
~/.cargo/bin/cargo test --workspace
#   macOS で素早く回すなら: cargo test --lib --target aarch64-apple-darwin

# (b) リプレイ回帰 (背骨): FeatSnapshot 列が byte-equal で一致すること = HMM 不変の証明
~/.cargo/bin/cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson \
  --snapshot tests/snapshots/minimal.json
#   期待: "OK: N snapshots match ..."。差分が出たら HMM 挙動が変わっている。
#   意図的変更なら HMM_VERSION を bump → ゴールデン再生成 → .steering/ に根拠を記録。

# (c) Schema drift 検査 (gse-dataset 整合)
~/.cargo/bin/cargo run --bin emit_schema    # 出力を src-tauri/schema/current.json と byte-equal 比較

# (d) フロント型チェック
cd .. && npx tsc --noEmit

# (e) 整形・lint (⚠️ CI は -D warnings の門を持つので任意ではない)
cd src-tauri && ~/.cargo/bin/cargo fmt --check
cd src-tauri && ~/.cargo/bin/cargo clippy --all-targets --features package -- -D warnings

# (f) ⚠️★★★ MSRV 検査 —— ★ **依存を更新したとき / 新しい std API を使ったときだけ**回す
#   ★ 継続検査する CI job は**存在しない** (2026-09-12 の研究者裁定: 足さない) ので、
#     ⚠️ **ここを回さなければ誰も気付かない**。
#   ★ <MSRV> は `src-tauri/Cargo.toml` の `rust-version` の値 (2026-09-12 時点で 1.88)。
cd src-tauri && cargo +<MSRV> check --all-targets --features package
#   ⚠️ 落ちたら: 宣言が実態より低い。★ エラーが名指しする crate の要求まで `rust-version` を上げる
#     (⚠️ 下げてはならない —— 下げると「古い toolchain で動く」という嘘の契約になる)。
#   ⚠️ `+<MSRV>` は `rust-toolchain.toml` を**上書きする**ので、toolchain 固定と両立する (実測済み)。

# (g) ⚠️★★★ supply chain 点検 (F-1 / F-2・2026-09-12 追加) —— ★ **repo 直下から**回す
#   ★ 週次で `.github/workflows/supply-chain.yml` が同じコマンドを回すが、⚠️ **依存・toolchain を
#     動かした回は手元でも回す** (CI を待たずにその場で分かる)。
#   ★ 検査する 3 層:
#     | 層 | 固定の仕方 | 手段 |
#     |---|---|---|
#     | toolchain (rustc/std/cargo) | `rust-toolchain.toml` に**名前のみ** | 下記 1 本目 |
#     | Rust 依存 630 crate | `Cargo.lock` に **checksum 付き** | 下記 2 本目 |
#     | フロント npm | `package-lock.json` | 下記 3 本目 |
cd <repo> && python3 scripts/check_toolchain_advisories.py
cd <repo> && python3 scripts/check_dependency_audit.py     # 要 `cargo install cargo-audit --locked`
cd <repo> && npm audit --package-lock-only --omit=dev
#   ⚠️★★★ **`cargo audit` だけでは足りない** —— ★ cargo-audit が見るのは `Cargo.lock` の依存だけで、
#     **toolchain 同梱の cargo / rustc / std は見ない**。⚠️ RustSec DB に `std` の advisory は 1 件も無い。
#   ⚠️★★★ **`cargo audit` を直接叩かない** —— ★ 実測 (0.22.2): `.cargo/audit.toml` の
#     `[advisories] ignore` に入れた advisory は**出力から跡形もなく消える** (件数すら出ない)。
#     → ⚠️ 「緑」と「除外したから緑」が区別できない。★ ラッパーは除外 ID を毎回印字し、
#     **stale な除外** (もう当たらないのに残っている ID) を **exit 2 で赤にする**。
#   ⚠️ npm の門は **`--omit=dev` (本番依存) だけ**。★ 全体の 7 件は全て devDependencies で
#     被験者に配る Tauri バイナリの実行時経路ではない (⚠️ 「無い」わけではないので CI は全体も出力する)。
#   ⚠️ 赤が出たら: `cargo update -p <crate>` を先に試す。★ semver 内に解が無いときだけ
#     `.cargo/audit.toml` に **ID + 理由 + 依存経路 + 再点検期日**を書いて除外する。
#     ⚠️ `cargo update -p <crate>` は**無関係な依存辺も張り替えることがある** (2026-09-12 実測:
#     `-p h2` が `windows-sys` を 7 crate ぶん巻き戻した)。→ ★ `git diff` を見て意図した
#     crate だけに絞ること。

# (h) ⚠️★★★ workflow の不変条件 ＋ third-party action の版上げ (F-8 / F-9・2026-09-13 追加)
#   ★ 検査そのものは CI (`frontend-check`) で毎回走る。手元では workflow を触ったときに回す。
cd <repo> && python3 scripts/check_workflow_invariants.py
#   ★ 検査する 4 点: (1) 全 job が実効 permissions を持つ (2) third-party action が
#     **40 桁 commit SHA** で固定 (3) `supply-chain.yml` が self-hosted へ向いていない
#     (4) ⚠️ 走査 0 件は exit 2 (= 「違反なし」と読ませない)
#
#   ⚠️★★★ **third-party action の版上げは人が回す** (★ dependabot を入れない裁定 = D12)。
#     ⚠️ 固定したまま放置すると上流のセキュリティ修正が**自動では来ない**。
#     ★ 手順 (⚠️ 先頭スラッシュ無しで `gh api` を呼ぶ —— git-bash が書き換えるため):
#       1. 新しい SHA を引く (⚠️ **annotated tag はタグオブジェクトの SHA で、commit ではない**):
#            gh api repos/<owner>/<repo>/git/ref/tags/<tag> --jq '.object.type, .object.sha'
#          → `type` が `tag` なら さらに:
#            gh api repos/<owner>/<repo>/git/tags/<その sha> --jq '.object.sha'
#          ★ `dtolnay/rust-toolchain` は**ブランチ**なので:
#            gh api repos/dtolnay/rust-toolchain/branches/stable --jq '.commit.sha'
#          ⚠️ その際 **`action.yml` の `toolchain` 既定が `stable` のまま**かを確認する
#            (★ 意味が変わると toolchain が黙って切り替わる)。
#       2. `uses:` 行だけを書き換え、⚠️ **版名コメントを必ず付ける** (`# v2.9.2` 等)。
#          ★ コメント中の言及や過去の CI ログ引用は**書き換えない** (2026-09-13 に一度壊した)。
#       3. `python3 scripts/check_workflow_invariants.py` が exit 0 であること。
#       4. ⚠️ `build-macos` / `release` は **tag でしか走らない**ので PR では検証できない。
#          ★ `workflow_dispatch` を**ブランチ指定**で発火し `build-windows` を実機確認する
#            (⚠️ tag を選ぶと Release ができる)。
#   ⚠️ `actions/*` は**意図的にタグのまま**である (★ 理由は `.github/workflows/ci.yml` の注記)。

# (i) ⚠️★★★ G1 の**新コホートの収集を始める前**だけ回すゲート (2026-09-20 追加)
#   ★ 事前登録の逐語「⚠️ 1〜7 が終わるまで新コホートの収集を始めない」(`preregistration.md:69`)
#     を機械が持つ。⚠️ **今は赤いのが正しい** (前提条件 3 / 5 / 7 が未達)。
cd <repo> && bash scripts/check-g1-collection-readiness.sh
#   ★ ゲート自身が空回りしていないかを測る (⚠️ 数分かかる。実物の repo は 1 バイトも変えない):
cd <repo> && bash scripts/check-g1-collection-readiness.sh --selftest
#   ⚠️★★★ **(a)〜(h) が全部緑でも、このゲートが緑になるまで収集を始めてはならない。**
#     ★ 逆に、このゲートは**開発の門ではない** (★ 収集を始めるときだけ通す)。
#   ⚠️ **ゲートが見ていないもの**: 配布したバイナリの実行時挙動 / 外部サービスの状態
#     (配布済み同意フォーム・Drive の実物・CI の両 OS の run)。
#     → ★ 後者は `experiments/.../collection-readiness-record.md` の**人手の記録票**が受ける。
#       ⚠️ 検査 [8] が見ているのは「**人が確かめたと書いたこと**」だけである。
```


合格条件:
- [ ] `cargo test --workspace` パス
- [ ] `gse-replay --snapshot` が一致 (HMM 不変)
- [ ] `emit_schema` 出力が `schema/current.json` と一致 (drift なし)
- [ ] `tsc --noEmit` エラー 0
- [ ] `cargo fmt --check` クリーン・**`clippy --all-targets --features package -- -D warnings` が exit 0**
- [ ] ★ **依存を更新した回のみ**: `cargo +<MSRV> check --all-targets --features package` が exit 0
- [ ] ★ **依存 / toolchain を動かした回のみ**: (g) の 3 本がすべて exit 0
      (⚠️ `check_dependency_audit.py` は **exit 2 = stale な除外**でも落ちる)
- [ ] ★ **workflow / composite action を触った回のみ**:
      `python3 scripts/check_workflow_invariants.py` が exit 0
      (⚠️ **exit 2 = 走査 0 件**＝検査が動いていない。★ 緑として扱わない)
- [ ] ⚠️★★★ **G1 の新コホートの収集を始める回のみ**:
      `bash scripts/check-g1-collection-readiness.sh` が exit 0
      (★ 開発の門ではない。⚠️ **今は赤いのが正しい** —— 前提条件 3 / 5 / 7 が未達)
- [ ] ⚠️★★★ **`gse-dataset` へ何かを push する回のみ**（★ 下記 (i)）:
      `bash scripts/check_no_feature_output.sh --root <gse-dataset のクローン>` が exit 0
- [ ] ⚠️★★★ **`gse-replay --features` の出力を作る回のみ**（★ 下記 (j)）:
      `bash scripts/run-features-all-poles.sh <session.ndjson> <outdir>` が exit 0 で 3 ファイルを出す
      （⚠️ **極を 1 つずつ手で叩かない**。`pole_applicable == false` は失敗ではない）
- [ ] ⚠️★★★ **P1 の再現を回す回のみ**（★ 下記 (k)）:
      `bash scripts/p1-repro.sh <ndjson-root> <workdir>` が exit 0 で `provenance.json` を出す
      （⚠️ **既定は PG-1 の手前で止まる**。`--stage search` は PG-1 を宣言してから）

### (i) ⚠️★★★ `gse-dataset` 側の共有の門（★ 手動。CI では走らない）

`gse-replay --features` の出力（**特徴行**）は**中間成果物**であり、`gse-dataset` へ共有しない
(`docs/glossary.md`「特徴行」の逐語)。⚠️ `t_ms` は**絶対 epoch ms** で **`anonymize.rs` を
一度も通っておらず**、`T1a` 以後は ms 粒度の pause 長とセッション横断の個人統計が載る ——
`gse-dataset` へ出してよい唯一の共有物と定めた `metrics.json`（集計値・約 1KB）より
遥かに粒度が高い。

★ 本リポ側は CI で自動的に見ている（`ci.yml` の `frontend-check`）。
⚠️★★★ **`gse-dataset` 側は見ていない** —— ★ 向こうには `.github` が無く **CI が存在しない**
(2026-09-20 実測)。→ **push の前に手で回す**:

```bash
# ★ 先に門そのものが閉まることを確かめる (⚠️ 陽性 4 / 陰性 3。★ 既定枝の対照を含む)
bash scripts/check_no_feature_output.sh --self-test

# ★ gse-dataset のクローンを走査する (⚠️ 本機は C:\gse-dataset)
bash scripts/check_no_feature_output.sh --root /c/gse-dataset
```

- exit 0 = 緑 / exit 1 = 違反あり / ⚠️ **exit 2 = 走査できなかった**（★ 緑として扱わない）
- ⚠️ **この門が見ていないもの**: リポジトリの外（Slack / メール / USB）／
  圧縮・暗号化された中身（`.zip` / `.age` / `.gz`）／ CSV・NDJSON へ変換された行。
  → ★ script 冒頭に同じ一覧がある。

### (j) ⚠️★★★ `gse-replay --features` の出力を作る回のみ: **3 極を必ず回す**（★ 手動・2026-09-25 追加）

`--features` の**極**（ADR-030 D3）は **別モード（`--pole`・1 実行 1 極）** で出す（判断 3）。
⚠️ その代償は「**3 極のどれかを回し忘れる**」ことである。→ **極を 1 つずつ手で叩かず**、次で回す:

```bash
# ★ repo 直下から。3 極 (baseline / pointer_b / modifier_m_plus) を回し、<outdir> に 3 ファイルを出す
bash scripts/run-features-all-poles.sh <session.ndjson> <outdir>
#   ★ 長いセッションは release で（⚠️ 相対パスは呼び出し元の cwd から解決する）:
#     GSE_REPLAY_BIN=src-tauri/target/release/gse-replay bash scripts/run-features-all-poles.sh <session.ndjson> <outdir>
#   ★ 設定を振る（探索格子 `scripts/p1_run_grid.py` が使う）: `--` の後ろの `--set <key>=<value>` を 3 極すべてへ渡す（⚠️ `q` は `warmup_count` と対で・同じ key の 2 回指定は exit 2）:
#     bash scripts/run-features-all-poles.sh <session.ndjson> <outdir> -- --set q=0.995 --set warmup_count=200
```

- ★ 出るのは `<outdir>/baseline.json` / `pointer_b.json` / `modifier_m_plus.json` の 3 つ。
  各ファイルの `config.pole` は**ファイル名と一致する**（⚠️ 食い違う出力は出さない）。
- ⚠️★★★ **極を Cartesian（直積）に組まない**（ADR-030 D3 の囲み「他の極と Cartesian に組まない。独立に報告する」）。
  ★ 出す組は上の 3 つだけで、`pointer_b` と `modifier_m_plus` を**掛け合わせた出力は作らない**。
  ⚠️ 3 ファイルは**互いに独立の報告**である（★ 極 B が baseline の部分集合になるとは限らない・判断 25）。
- ⚠️ **fail-closed**: 1 極でも失敗したら**全体が非 0 で止まり、`<outdir>` には 1 ファイルも置かない**。
- ⚠️★★★ **`pole_applicable == false` は失敗ではない**（★ 「その極は判定できない」という正しい報告）。
  修飾キー行の無い入力の `modifier_m_plus`、ポインタの宣言も行も無い入力の `pointer_b` がそうで、
  **exit 0 のまま 3 ファイル出る**。★ 読む側は `config.pole_applicable` を**必ず見る**
  （⚠️ `false` の極の行は baseline と恒等なので、「その極でも onset が同じだった」と読まない）。
- ⚠️★★★ **`<outdir>` は使い回さない**（2026-09-25 追加）: `baseline.json` / `pointer_b.json` /
  `modifier_m_plus.json` の**いずれかが既にあれば exit 2 で拒否**される（★ fail-closed が
  「古い 3 ファイルが残った outdir」では破れるため。前回の失敗の跡が残っていても、今回の失敗時に
  古い 3 ファイルが「3 極そろった」と誤読される／成功時は黙って上書きされる、の両方を防ぐ）。
  上書きしたいときは**空の `<outdir>` を新しく指定する**。
- ⚠️★★★ **`<outdir>` は git 管理下に置かない**（2026-09-25 追加）: `git -C <outdir> rev-parse
  --is-inside-work-tree` が成功すると **exit 2 で拒否**される。GSE repo の中・`gse-dataset` の
  クローンの中の両方を弾く（★ 出力（特徴行）は共有禁止 (`sharing: prohibited`) で、repo 内に書くと
  誤って `git add` で stage されうるため）。⚠️ この判定自体が「`not a git repository`」以外の
  エラー（所有権チェック失敗等）で失敗した場合も、**「管理外」として素通りさせず exit 2 で拒否**
  される（fail-closed）。
- ⚠️★★★ **二重起動は排他される**（2026-09-25 追加）: `<outdir>/.all-poles.lock` を `mkdir`
  （atomic）で取り、取れなければ **exit 2**（★ 同じ `<outdir>` への同時実行を防ぐ）。
- ⚠️★★★ **入力は最初に staging へ固定コピーされる**（2026-09-25 追加）: 3 極すべてがそのコピーに
  対して回るので、3 回の実行の間に元の入力ファイルが変わっても極間で入力が食い違わない。
- ⚠️★★★ **既知の限界（構成は変えない）**: 3 極は `baseline.json` / `pointer_b.json` /
  `modifier_m_plus.json` の **3 ファイル構成**なので、`mv` で outdir へ移す**最中**に SIGKILL 等で
  プロセスが強制終了されると、1〜2 ファイルだけが outdir に揃ってしまう部分出力は**原理的に防げない**
  （★ ディレクトリ単一 rename への構成変更はしない。通常の失敗・fail-closed の経路は上記のとおり
  outdir を空に保つ）。
- ⚠️ 出力は**中間成果物**で `gse-dataset` へ共有しない（上の (i) の門が見る）。`<outdir>` は repo の外に置く。
- ★ 計算量の門は **1 極あたり 20 秒**（`.steering/20260914-mhd-feature-offline-tiers/issues/008-acceptance.sh` の
  AC18 / AC18b。★ 門の入力は onset が 100 本立つ）。⚠️ 3 極を回すと時間は**約 3 倍**になるが、門は 3 倍を織り込まない
  （★ 1 極が遅いのか 3 回回しているのかを混ぜない）。
  ⚠️★★★ **この門が保証する範囲**: `R`（onset 数）に比例する経路を実際に踏むことと、`N`・立ち上がり数に
  対する **二乗**への退行の検出まで。★ `R=100` では `O(R·C)` や `O(R²)` への退行は 20 秒に届かず検出できない。
  `R` 経路そのものの正しさ（愚直走査との一致）は `restart::tests::many_onsets_match_a_naive_scan` が持つ。

### (k) ⚠️★★★ P1 の再現を回す回のみ: **既定は PG-1 の手前で止まる**（★ 手動・2026-09-26 追加）

P1 の実データが届いた日に、**1 コマンドで「3 極 → PG-1 に渡す分布 → episode DB」まで**を回し、刻印を残す
（`reproducibility-discipline` ルール 4）。事前登録の雛形は `scripts/templates/p1-experiment/README.md`
（★ `experiments/<その日の日付>-p1-<名前>/` に写して埋める。実体は本タスクでは作らない）。

```bash
# ★ repo 直下から。<workdir> は repo の外・空か未作成。既定の --stage pg1 は PG-1 の手前で止まる
GSE_DATASET=<gse-dataset のクローン> GSE_REPLAY_BIN=src-tauri/target/release/gse-replay \
  bash scripts/p1-repro.sh <ndjson-root> <workdir>

# ★ PG-1 を宣言（凍結 JSON の新版）して gse-replay を作り直したあとにだけ（<workdir> は新しい空のディレクトリ）:
#   ⚠️ 格子は 31 一式 × 全セッション × 3 極を回すので、GSE_REPLAY_BIN を付ける（無いと debug の `cargo run` で毎回起動して遅い）
GSE_DATASET=<gse-dataset のクローン> GSE_REPLAY_BIN=src-tauri/target/release/gse-replay \
  bash scripts/p1-repro.sh <ndjson-root> <workdir-search> --stage search --labels <labels.csv>
```

- ★ `<ndjson-root>` は `<P-ID>/<session>.ndjson`（`scripts/p1_run_grid.py` と同じレイアウト・同じ検査）。
- ⚠️★★★ **既定では格子（`p1_run_grid.py`）も選択（`p1_select.py`）も呼ばない**。事前宣言 §2.3: PG-1 は探索を
  1 度も回す前に宣言するゲートで、見てよいのは**参加者ごとの episode 数の分布だけ**（`pg1_distribution.json`）。
  PG-1 が宣言されていない凍結 JSON では `--stage search` は **exit 6** で止まる（★ 握りつぶさない）。
- ⚠️★★★ **成果物を repo に置かない**: `<workdir>` が git 管理下なら **exit 2**（`features/` は特徴行で共有禁止・
  `episodes.duckdb` の時刻は絶対 epoch ms で個人を同定しうる）。`<workdir>` が空でない・`<ndjson-root>` の中でも exit 2。
- ★ 出るのは `features/`・`pg1_distribution.json`・`episodes.duckdb`・`provenance.json`（`--stage search` は
  `grid/`・`select_table.json` も）。**`provenance.json` は成功した実行にだけ付く**（★ 無い `<workdir>` は
  完了していない残骸。結果として読まない・使い回さない）。
- ★ 刻印: repo の commit と作業ツリーが clean か／入力の commit（`GSE_DATASET` の `git rev-parse HEAD` の hash だけ。
  中身は開かない。無ければ `null` と理由）／`Cargo.lock` の sha256／凍結 JSON の sha256 先頭 16 桁／
  封筒から取った `hmm_version` と `prereg_version`／seed／実行した stage／開始・終了時刻（UTC・秒）。
- ⚠️ **封筒の identity が 1 通りでなければ exit 3**: 全セッション・全極で `hmm_version` / `prereg_version` が同じで、
  かつ封筒に埋め込まれた凍結 JSON の hash が**いま repo にある凍結 JSON と一致**すること
  （★ PG-1 を宣言して凍結 JSON を新版にしたのに `gse-replay` を作り直していないと、ここで止まる）。
- ⚠️ どの段でも失敗したら**その段の終了コードで止まる**（次の段へ進まない）。テスト:
  `bash scripts/p1-repro-test.sh`（★ 偽 `gse-replay`・合成入力・duckdb 必須。CI `frontend-check` で走る）。

---

## 2. macOS 機能検証 (実機・手動)

開発 dev ビルドを**二重 gate** で起動する (デバッグボタン + backend gate)。

```bash
VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
```

dev ログ NDJSON: `~/Documents/GSE-sessions/gse_*.ndjson`。記録成功は同ファイルに該当エントリが
残ることで客観確認する。

### 2.1 介入カードのクリック受理 + フォーカス非奪取 (v2.22)
1. セッション開始 → Dashboard「プローブを出す」→ 右上のプローブカードが表示される。
2. Q1/Q2 を選び「回答する」を押す → **カードが閉じる** (ボタンが効く)。
3. Dashboard「Nudge を出す」→ Nudge を閉じる → 閉じる。
4. カード表示中に**前面エディタへのタイピングフォーカスが奪われない**こと
   (カードを出したまま別アプリで文字が打てる)。

合格条件:
- [ ] プローブ/Nudge のボタンが**初回クリックで効く** (無反応でない)
- [ ] カード表示中もフォーカスを奪わない (背後アプリで入力継続できる)
- [ ] カード以外の画面領域は背後アプリへ**クリック透過**する (非ブロック)

### 2.2 記録の着地 + 窓反転バグの非回帰 (v2.22)
**起動直後 (5 秒以内)** に「プローブを出す」→「回答する」を試す (旧バグの再現条件)。

合格条件:
- [ ] dev ターミナルに `record_… FAILED` が出ない
- [ ] NDJSON に `realtime_label` が着地する。起動 5s 以内はゼロ幅窓
      (`analysis_window_start_ms == analysis_window_end_ms`)、5s 超は通常窓 (`end > start`)
- [ ] Nudge dismiss で `intervention_response` が着地する

確認例 (NDJSON):
```bash
grep -E '"type":"(realtime_label|intervention_response)"' ~/Documents/GSE-sessions/gse_*.ndjson | tail
```

### ~~2.3 Wall 全画面ブロック (非回帰)~~ — ⚠️★★★ **2026-09-01 削除**

⚠️★★★ **この手順は実行不能である。** Wall・Zen Timer・`wall_server.rs` は
**ADR-015 (2026-08-23) D1 / D2 で全削除**され、`InterventionAction` は
`None / Nudge / Defer` の 3 値になった (実測: `src-tauri/src/analysis/intervention.rs:16-20`)。
★ **発火させる経路が無いので、この節は「必ず落ちる非回帰テスト」として残っていた。**

★ **現行で確認すべき介入は Nudge のみ**であり、§2.2 でカバーされている。
（2026-10-31: ADR-040 D1 で Nudge は既定で無効になったが、§2.1・§2.2 の「Nudge 強制表示 (デバッグ)」は `INTERVENTION_ENABLED` の門より前で処理されるので、手順はそのまま使える。）
⚠️ **代替の手順を新設していない** —— 2026-11-03 時点で Physical Anchor の PC 側の招待は EH3 モードと通常のモードの第 2 週でだけ動き（この節の検証の対象外）、
ADR-018 D1 で完了条件を持たない「方向づけ」に改められたため、
**「解除できるか」という形の検証項目自体が存在しない**。

### 2.4 日本語 IME 合成 (非回帰)
1. 日本語入力でローマ字 → 変換 → 確定を数回行う。
2. 候補ウィンドウ表示中は HMM がポーズする (中間 feat が出ない)。

合格条件:
- [ ] 変換・確定が壊れない (overlay の NSPanel level=Floating が IME をブロックしない)
- [ ] 候補表示中に `force_flow_state` 等のポーズが効く (`hmm-analysis` / メモリ参照)

---

## 3. Windows 機能検証 (実機・手動・差分のみ)

overlay の NSPanel 化は **macOS 限定 gate**。Windows は従来の `set_ignore_cursor_events` 経路。

合格条件:
- [ ] プローブ/Nudge のクリックが効く (`accept_first_mouse` 既定経路)
- [ ] §2.2 と同じく起動直後のプローブ記録が着地する (窓 clamp 修正は OS 非依存)
- [ ] IME (IMM) 合成が非回帰 (⚠️ **旧文の「Wall 全画面ブロック・」は ADR-015 の削除により失効・2026-09-01**)

---

## 4. アンケートフォーム検証 (Google Apps Script)

`Form_Phase1/GSE_Phase1_Form_Builder.gs` を Apps Script エディタに貼り、各関数を実行する。

- `buildForm` … F1 同意・スクリーニング (固定フォーム `FORM_ID`)
- `buildF2` / `buildF3` / `buildF4` … F2-F4 (毎回 `FormApp.create` で新規)
- `buildF5` … F5 事後アンケート (固定フォーム `F5_FORM_ID`)

合格条件:
- [ ] `buildForm` を**2 回以上連続実行**しても `Invalid data updating form` が出ない
      (分岐ナビゲーションを `clearForm` が先に解除してから削除するため)
- [ ] `buildF5` を**単独実行**して事後アンケートが生成される (一括実行で実行時間/クォータに
      当たる場合は単独で回す)
- [ ] F2-B / F5 の GSE-10 項目、F2-C / F5 の `TSE_ITEMS` が pre/post で**完全一致**
      (matched 再測定の前提)
- [ ] 実行ログの編集 URL / 回答 URL を控える

> 注: `buildF2`/`F3`/`F4` は実行ごとに別フォームを量産する設計 (`FormApp.create`)。再実行時は
> 旧フォームを手動で破棄するか、固定 ID 再利用へ寄せる (F1/F5 と同方式)。

---

## 5. トラブルシュート

| 症状 | 切り分け |
|---|---|
| プローブ「記録に失敗」 | dev ターミナルの実 Err を見る。`window_end_ms must be >= window_start_ms` は窓 clamp の回帰 (v2.22 で修正済)。`log channel ...` は logger 経路。 |
| カードのボタン無反応 (macOS) | `capabilities/default.json` の `allow-set-size`/`allow-set-position` を確認。NSPanel 化と Rust 権威 `set_ignore_mouse_events` (overlay_panel.rs)。 |
| 起動時クラッシュ (macOS) | NSPanel 化窓で `maximize()`/`unmaximize()` 禁止 (NSRangeException)。全画面化は明示 `setSize`/`setPosition`。 |
| `Invalid data updating form` | `buildForm` 再実行時の分岐 orphan。`clearForm` 経由で削除しているか確認。 |
| リプレイ snapshot 不一致 | HMM 挙動変更。意図的なら `HMM_VERSION` bump + ゴールデン再生成 + `.steering/` 記録。 |

---

## 関連ドキュメント

- `docs/calibration-smoke-runbook.md` — v0.3 較正スモーク (データ収集・3-5 名)
- `docs/pilot-runbook.md` — M1 パイロット (収集 → 暗号化 → 分析パイプライン)
- `docs/development-guidelines.md` §3 — テスト方針 (Replay-as-Truth)
- `.steering/20260625-macos-overlay-clickthrough-fix/runbook.md` — overlay クリック修正の実機検証
- `.steering/20260627-phase1-1-smoke-verify-closeout/smoke-test-runbook.md` — スモーク検証
