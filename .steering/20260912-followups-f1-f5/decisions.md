# decisions — 申し送り F-1 / F-2 / F-3 / F-5

> ★ 書式は `.steering/_template/decisions.md` に従う (決定 / 理由 / 却下案)。
> ⚠️ 前タスクの判断番号 (1〜54) とは独立に **D1 から振り直す**。

---

## D1: ★ 検知経路は **単一 workflow** に集める (F-1 + F-2 を一体で解く)

- **決定**: `.github/workflows/supply-chain.yml` を新設し、**toolchain / Rust 依存 / npm の 3 層**を
  1 job で検査する。
- **理由**: ⚠️ F-1 (toolchain) と F-2 (依存) を別々に足すと検知経路が 2 系統に割れ、
  「どちらを見れば足りるのか」が分からなくなる。★ grill で研究者が「単一 CI job で両層」を裁定。
- **却下**: ⚠️ **docs だけに手順を書く** —— ★ 判断 20 の M4 でまさにこれを直した
  (`Cargo.toml` のコメントにしか無かった MSRV 検査を runbook へ移した)。
  **回す場所が無い手順は回らない**。

## D2: ★ `ci.yml` に足さず**独立したファイル**にする

- **決定**: 新規 workflow ファイルにする。
- **理由**: ⚠️ 本 workflow の要は `schedule` (★ 新しい advisory は**コード差分ゼロで現れる**ので
  PR 発火だけでは永久に気づかない) だが、`ci.yml` に `schedule:` を足すと
  **ci.yml の全 job が週次で発火**する。⚠️ `check` / `build-macos` / `decide-win-runner` は
  **self-hosted 実機**であり、週次で占有するのは割に合わない。
- **却下**: 各 job の `if` に `github.event_name != 'schedule'` を足す ——
  ⚠️ 既に長大な `if` 群をもう一段複雑にする。

## D3: ⚠️★★★ 「非ブロッキング」は**設定で作らない** —— 既に構造的に成立している

- **決定**: `continue-on-error` を**書かない**。
- **理由**: ★ 実測 (2026-09-12) —— `gh api repos/mikotomiura/GSE-prototype/branches/main/protection`
  → **`404 Branch not protected`**。⚠️ required check は 1 つも無く、本 job が赤でも
  マージは機械的に止まらない。→ ★ **すでに非ブロッキングである**。
  ⚠️ その上で `continue-on-error` を書くと「赤」が「緑」に見え、**唯一の信号が消える**。
- ★ 本 job の役割は **門ではなく信号**であると workflow 冒頭に明記した。

## D4: ★ F-3 = `stop-check.sh` に `--features package` を**足さない**

- **決定**: `.claude/hooks/stop-check.sh` は変更しない。
- **理由**:
  - ★ **実測でわかった構造**: `src-tauri/` に `cfg(not(feature = ...))` は **0 件**なので、
    `--features package` は**ソース上は default の上位集合**である。
    ⚠️ **しかし lint 結果は上位集合にならない** —— `submission.rs` の共有ヘルパのように
    package OFF でのみ `dead_code` になりうる項目があるため、**両形は互いを覆わない**。
  - → ⚠️ **片方だけをローカルに足しても非対称は消えない**。向きが変わるだけ。
  - ★ 構造的に正しいのは **CI に両形を置く (F-4)** ことであり、
    ローカル hook は「速い部分検査」と割り切る (⚠️ そもそも `WARN` を出すだけでブロックしない)。
  - ★ コスト: Windows 実測 (warm・1.98.1) で **10s → 14s** (+4 秒/Stop)。⚠️ mac は未測定。
- ⚠️ **申し送りに残る**: ★ F-4 が入るまで「CI は `--features package` だけ」の状態は続く。
- **却下**: 両形をローカルで回す (⚠️ 推定 +14 秒/Stop・mac 未測定)。

## D5: ⚠️★★★ `cargo audit` は**今日すでに赤**だった —— 足す前に緑にした (R-1 と同じ順序)

- **実測** (2026-09-12・cargo-audit 0.22.2・G-GEAR): **exit 1** / vulnerability **3 件** / warning 13 件。
  ★ 確かめずに CI へ足していたら、**新 job は初日から赤**だった。

| ID | crate | 経路 (`cargo tree -e normal --target all -i`) | 決定 |
|---|---|---|---|
| RUSTSEC-2026-0258 | `h2 0.4.15` | `reqwest` ← ⚠️ **`--features package` のみ** = `gse-submit` | ★ **直す** (0.4.19) |
| RUSTSEC-2026-0194 | `quick-xml 0.38.4` | `plist 1.8.0` ← `tauri 2.10.2` (⚠️ **macOS 経路**) | ⚠️ **明示除外** |
| RUSTSEC-2026-0195 | 同上 | 同上 | ⚠️ **明示除外** |

- ★ `quick-xml` を直せない根拠 (実測): 修正版は **0.41.0** だが `plist 1.8.0` が `0.38` 系を要求し、
  `cargo update -p quick-xml` は **`Locking 0 packages`** を返す (= semver 内に解が無い)。
- ★ 露出評価: 当該 advisory は**未信頼 XML に対する DoS** であり、GSE が `plist` に渡すのは
  **自前バンドルの `Info.plist`**。⚠️ 「当たらない」とは断定せず、再点検期日 (**2026-12-12**) を置いた。

## D6: ⚠️★★★ `cargo update -p h2` は **h2 以外も書き換えた** —— 最小差分に戻した

- **決定**: `cargo update` の出力をそのまま採らず、`Cargo.lock` の **h2 の 2 行だけ**を当てた。
- **実測**: `cargo update -p h2` は h2 に加えて **7 crate の `windows-sys` 依存辺**を
  0.61.2 → 0.52.0 / 0.59.0 へ**巻き戻した** (arboard / dirs-sys / errno / nu-ansi-term /
  rustix / tempfile / winapi-util)。⚠️ `cargo update --dry-run` は「Locking 1 package」としか
  言わず、**この副作用を予告しない**。
- ★ 原因: 7 crate はいずれも**広い範囲**を宣言しており (例 `rustix`: `>=0.52, <0.62`)、
  再解決時に cargo が **lock に既にある最小の版**を選び直したため。
  → ⚠️ 「不正」ではないが、**h2 の脆弱性修正と無関係な巻き戻し**であり、
  Windows の FFI バインディングを後退させる。
- ★ 検算: 最小差分を当てた後に `cargo metadata --locked` が **exit 0**
  (= cargo 自身が「変更不要」と認める)。⚠️ さらに `cargo metadata` の解決グラフを
  更新前後で突き合わせ、**h2 の辺だけが動いた**ことを確認した。
- ★ この教訓を `check_dependency_audit.py` の赤メッセージと runbook §1 (g) に書き込んだ
  (⚠️ 次に踏む人が `git diff` を見る理由を持つように)。

## D7: ⚠️★★★ `cargo-audit` は除外を**黙って消す** —— ラッパーを噛ませた

- **実測** (cargo-audit 0.22.2): `[advisories] ignore` に入れた advisory は
  **人間向け出力から跡形もなく消える** —— 件数も ID も出ない。
  → ⚠️ **「緑」と「除外したから緑」が出力上まったく区別できない**。
  ★ これは R-4 が `panic!` に倒した無音 skip と**同じ失敗様式**である。
- ⚠️ **初稿の `.cargo/audit.toml` に「cargo-audit は除外件数を毎回出力に出す」と書いたが、
  それは誤りだった。** ★ 検証して訂正した。
- **決定**: `scripts/check_dependency_audit.py` を通して回す。同 script は
  (a) cargo-audit を **config の無い一時ディレクトリ**で回して生の検出集合を得る、
  (b) 除外 ID を**毎回必ず印字**する、
  (c) ⚠️ **stale な除外** (もう報告されない ID が config に残っている) を **exit 2 で赤にする**。
- ★ (c) は cargo-audit 単体では不可能 —— ⚠️ 何にも当たらない除外は**見えないまま永久に残る**。
- **却下**: workflow の中で `--ignore RUSTSEC-... ` を並べる ——
  ★ コマンドラインには出るが、⚠️ **手元で素の `cargo audit` を叩いた人と結果が食い違う**。

## D8: ⚠️ npm は **`--omit=dev` だけを門にする**

- **決定**: `npm audit --package-lock-only --omit=dev` を門にし、**全体も必ず出力**する。
- **実測** (2026-09-12): 全体 **7 件** (high 4 / moderate 1 / low 2) は**すべて devDependencies**
  (vite / postcss / nanoid / browserslist / esbuild / @babel/core / baseline-browser-mapping)。
  ★ `--omit=dev` は **0 件**。
- **理由**: ⚠️ dev 依存は**被験者に配る Tauri バイナリの実行時経路ではない**。
  ★ しかし「無い」ことにはしないので、情報として毎回出す
  (⚠️ 緑だから dev 依存に問題が無い、と読ませない)。

## D9: ★ F-5 は **top-level `permissions`** で解く

- **決定**: 4 job への個別付与ではなく `ci.yml` の top-level に `permissions: contents: read`。
- **理由**: ★ 直したい失敗様式は「**job を足したとき `permissions:` を書き忘れる**」であり、
  個別付与は**今ある 4 job しか直さない**。⚠️ top-level なら今後足す job も既定で最小になる。
- ★ 既存 2 job の job 側宣言が上書きするので挙動は不変 (yaml パースで実効値を検算)。
- ⚠️ **検証の限界を先に書いた**: `build-windows` / `build-macos` / `release` は
  tag か `workflow_dispatch` でしか走らず **PR 実行では検証できない**
  → ★ `workflow_dispatch` を**ブランチ指定**で発火して `build-windows` を実機確認した
  (⚠️ tag を選ぶと `build-macos` が実機を占有し `release` が GitHub Release を作る)。

## D10: ⚠️★★★ 変異テストが**実バグ**を出した —— cp932 で出力が落ちていた

- **実測**: `check_dependency_audit.py` の「脆弱性あり」経路に `⚠️` を含む出力があり、
  Windows の cp932 コンソールで `UnicodeEncodeError` を出して**落ちていた**。
  ⚠️★★★ **しかも Python の未捕捉例外は exit 1** なので、
  **「脆弱性を検出した」と外形上まったく区別が付かなかった**。
  ★ 期待した exit code が**間違った理由で**出ていた。
- **決定**: 両 script の冒頭で `sys.stdout/stderr` を UTF-8 に `reconfigure` し、
  ★ 出力文字列自体からも非 ASCII を落とした (⚠️ 呼び出し側の `PYTHONUTF8=1` に依存しない)。
- ★ 回帰として `test_check_dependency_audit.py` に **`text.encode("cp932")`** を置いた。
- **教訓**: ⚠️ 「緑になった」ではなく「**赤になるべきときに、正しい理由で赤になる**」を確かめる。

## D11: ⚠️ 旧手順のコマンドは**本機で動かなかった**

- **実測**: `rust-toolchain.toml` 手順 0 の `gh api /repos/rust-lang/rust/security-advisories` は、
  git-bash (MSYS2) が**先頭スラッシュ**を Windows パスへ書き換えるため
  `invalid API endpoint: "C:/Program Files/Git/repos/..."` で落ちる。
- **決定**: 手順 0 を script 呼び出しへ差し替えた (★ script は先頭スラッシュ無しで呼ぶ)。
  ⚠️ さらに「一覧を目で見て判断する」形をやめた —— ★ 範囲が `>= 1.87.0, < 1.89.0` のような
  **閉区間**のとき「修正版より新しいから安全」は成り立たず、**人が誤りやすい**。

## D12: ★ dependabot は**入れない** (⚠️ 申し送りに残す)

- **決定**: 今回は導入しない。
- **理由**: ★ 検知は D1 の workflow に一本化する (⚠️ dependabot を足すと経路が再び 2 系統になる)。
  ⚠️ 2-3 人チームに自動更新 PR のノイズが勝る。
- ⚠️ **ただし別論点が残る**: ★ `ci.yml` / `supply-chain.yml` が使う **GitHub Actions の版は
  タグ参照 (`@v4`) のままで SHA 固定していない**。→ ★ 申し送り (F-8) として残す。
