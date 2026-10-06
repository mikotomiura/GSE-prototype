# 次セッション — IME 論文 M12 の続き: 公開 repo の push → Mac・Surface で書庫と書き出しの確かめ → G-GEAR で Zenodo に上げてリリース D → 公開の確認

> ⚠️★ **2026-10-06 夜に `next-session-ime-paper-manuscript-9.md` で置き換えた**（PR #316・#317 の merge と datasheet の後）。次のセッションは -9 を読む。以下は記録。
> 作成: 2026-10-06 夜（G-GEAR）。判断 206〜211 の後。枝 `docs/ime-m12-release`。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 207〜212**、`tasklist.md` の M12 の小項目、`papers/ime-observation/kit/export/README.internal.md`（公開の履歴と手順）、`experiment/data.md` の寄託の手順。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を測る（PR #316〔枝 docs/ime-m12-release〕が main に merge 済みか）。未 merge なら §2.0 から。⚠️ main は別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/main から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-8.md を読んで §2 を、このセッションの機械（G-GEAR / Mac / Surface）の節から実行してください。
一次は decisions.md の判断 207〜212、tasklist.md の M12、kit/export/README.internal.md、experiment/data.md と data.windows.md の寄託の手順。
Skill: git-workflow・verify-before-claiming・data-privacy（書庫・--pack）・subagent-delegation・browser-verification（GitHub と Zenodo を Chrome で見るとき）。応答は日本語。コミットは git add パス指定。
⚠️ 公開（GitHub の repo を public に・Zenodo の publish）は取り消せない → その場で研究者に確かめる。Zenodo の下書き 2 つ（23183438・23183441）を消さない（予約した DOI が失われる）。token（C:/zenodo/）は表示・委譲しない。
⚠️ 公開 repo の履歴 A〜C は組み直さない（C の hash cb29a1a9… が原稿に入っている）。正本は C:/wt/ime-conversion-logging.git（bare）と、push した後の GitHub。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ 判断の番号は 213〜、逸脱は D13。heredoc でバックスラッシュを 2 本重ねない（python に渡ると壊れる）→ 置換は Edit か Write で書いたスクリプトで。
```

## §1 状態（2026-10-06 夜）

- ✅ 原稿の attack-me は round 2 で閉じた（round 3 は回さない・判断 206）。`round-1/tmp/`・`round-2/tmp/` は消した。
- ✅ M12 の進め方（判断 207）: リリースの DOI は手で上げて予約（判断 183-4 を覆した）・公開 repo は `mikotomiura/ime-conversion-logging`・履歴は A〜D・非公開の commit の参照は置き換え・書庫は G-GEAR に集める。
- ✅ Zenodo の下書き（判断 208）: データセット deposition `23183438`（**DOI 10.5281/zenodo.23183438**）・ソフトウェア deposition `23183441`（**DOI 10.5281/zenodo.23183441**）。どちらもファイルなし・説明は仮（"Draft. …"）。
- ✅ GitHub の repo を非公開で作った。push は自動モードの判定で拒まれたので、研究者が A〜C を push した（§2.1）。
- ✅ 公開の履歴 A〜C を手元で組んだ（`C:/wt/ime-conversion-logging.git`・bare）:
  - A `bf137ffec0549ddb699e02e1efd6c88202230764`（タグ `ime-observation-prereg-macos`・一覧 `29b183ba…` 98 ファイル）
  - B `32a5e18076884bb2e4aea59606726a3faeecac7b`（タグ `ime-observation-prereg-windows`・一覧 `f61af353…` 108 ファイル）
  - C `cb29a1a9086e77c89cb66c05e39ba4fc8091e074`（B に `ffd315a4` の外枠を足した・原稿の Open Practices に入れた）
- ✅ 書き出しの道具を原稿・SVG・`.gitattributes` に対応させた。`rv@` → `rv:`。著者のアドレスだけを通す（判断 208・210）。
- ✅ 非公開の commit の参照 12 か所の置き換え・`\tbd` 18 → 8・README（Identifiers・History・一覧を計算し直す手順）・ライセンスの全文・`.gitattributes`・CITATION.cff・.zenodo.json（判断 209）。
- ✅ README の先頭にロゴ（ライトとダーク）と動く SVG（判断 210・研究者の求め）。⚠️ GitHub での見え方は push の後に確かめる。
- ✅ 作業中の点検（code-reviewer ∥ security-checker）の指摘 14 件を一次で確かめて直した（判断 211）: アドレスの例外の境界（`@`）と範囲（`manuscript/` だけ）・SVG の能動的な要素を止める `check_svg`・入れ子の `.gitattributes` が root の強制 `text` を上書きしていたのを戻す・長い行・図の説明（`nav` は矢印キーの押下の数）・表 1 は「This logger 0.1.0, in release 1.0.0 of the code」。
- ✅ 本番の形の書き出し（ライセンスあり）が G-GEAR で exit 0・194 ファイル・その木で `kit/check.sh` 31 本が緑。
- ✅ 2026-10-06 夜（G-GEAR）: PR #316 を /cross-review の直しの後に merge（`c77e324f`・判断 212）。続けて datasheet を下書きした（枝 `docs/ime-m12-datasheet`・判断 213・未 PR）。研究者の確認（`.steering/20260927-ime-observation-paper-eval-design/datasheet-reading-ja.md`）と /cross-review（その日の Codex は上限超え）が残る。書き出しは datasheet を含めて 195 ファイル。
- 残る `\tbd` 8 か所: `dataset.tex` の `confirmed at deposit`（working の観測ログ）と `written at deposit`（datasheet）、試行の表（`results-agreement.tex`）の `at deposit` 6 か所。

## §2 やること

### 2.0 ✅ 済み（2026-10-06・G-GEAR・判断 212）: PR #316 の /cross-review と merge

- /cross-review は Codex をパスで絞って 3 回（1 巡目はコードと公開の文書を分けて 2 回・2 巡目は直しの境界）。真の指摘 7 件を再現してから直した（SVG を XML として読む層・文字参照を戻した走査・`<text>` の中の `<title>`・凍結の一覧の手順が期待値と比べる・`xml:base`・入れ子の復号・引用符の中の `>`）。偽陽性 2 件。変異 21 本すべて赤。きれいな clone で本番の形の書き出し exit 0・194 ファイル・`kit/check.sh` 31 本が緑。⚠️ merge したかは `git fetch` の後に `gh pr view 316` で確かめる。
- 以下は当時の手順（記録）。PR #316 は作業中の点検（判断 211）まで済み、/cross-review（Codex）は未実施。⚠️ 差分は `values.tex` だけで 2,600 行あり fail-closed になる → `run-codex-review.sh origin/main..HEAD -- <paths>` で、コードのパス（`kit/export/export.internal.py`・`issues/_style_check.py`・`assets/make_assets.py`）と公開の文書の主な変更（`README.md`・`.gitattributes`・`manuscript/sections/declarations.tex`）に絞る。1 巡目＝自文書・他文書の矛盾、2 巡目＝足した規則の境界条件（memory）。回す前に origin/main の台帳（`.codex/budget.json`）も見る。
- 指摘を一次で確かめて直す（判断 212〜）→ CI 緑なら merge（git-workflow ルール 6）→ main の CI を確かめる。

### 2.1 ✅ 済み（2026-10-06）: 研究者が公開 repo に A〜C を push した

`git ls-remote` で main = `cb29a1a9086e77c89cb66c05e39ba4fc8091e074`、タグ `ime-observation-prereg-macos` → `bf137ffe…`・`ime-observation-prereg-windows` → `32a5e180…`。repo は非公開のまま。⚠️ ロゴと動く図はリリース D の README に入るので、GitHub での見え方は D を push した後に確かめる。以下は当時の手順（記録）。

G-GEAR で（`!` を付けるとこのセッションで実行される）:

```
! git -C C:/wt/ime-conversion-logging.git push https://github.com/mikotomiura/ime-conversion-logging.git main ime-observation-prereg-macos ime-observation-prereg-windows
```

push の後、`git ls-remote https://github.com/mikotomiura/ime-conversion-logging.git` が main = `cb29a1a9…` と 2 つのタグを返すことを確かめる。⚠️ repo は非公開のまま。

### 2.2 Mac（macOS の書庫と書き出しの確かめ）

1. `data.md` の寄託の手順 1〜5 で、まだ書庫にしていないものを束ねる: macOS の E3 の `working` の run（Run checks の行 `macos-e3-working` は点検済み）、較正パイロットの run のうち寄託の条件を満たすもの（外枠 DS1・判断 183-3・封印したセッション行は寄託のためだけに開け、解析しない）、E3 の標本（`samples.tsv`・`idle` と `working`）。`--pack` に `--also-user`・`--also-home` を渡す（値は書かない）。SHA-256 を `data.md` の Deposits と「Machine that ran the deposit check」に記録する。
2. 公開物の書き出しを Mac で回して、Mac の値（ホーム・ログイン名・ホスト名）が入っていないことを確かめる: 2 つの凍結のタグのきれいな worktree でタグ自身の `export.internal.py --allow-missing-license`（一覧が `29b183ba…`・`f61af353…` と一致）、`origin` から取った最新の枝で本番の形の書き出し（exit 0）と、その木で `bash kit/check.sh`。
3. 書庫を G-GEAR に移す（研究者・Windows の書庫と同じ道）。
4. ★ datasheet のために（判断 213）: 各 run の `run.json` の `git_commit` と `git_dirty` **だけ**を読んで記録する（ログは開かない・値は commit の 40 桁か `null`）。各条件の `conditions.txt` を `samples.tsv` と一緒に移す（寄託する）。寄託したパイロットの run の名前と、寄託しなかった候補とその理由を `data.md` に書く。

### 2.3 Surface（Windows の書庫と書き出しの確かめ）

1. 2.2 の 1 と同じことを Windows で: E3 の `working` の run、較正パイロットの run（⚠️ 2 つ目の参照入力欄のものは寄託しない・`dataset.tex`）、標本。`data.windows.md` に記録。Windows のセルの書庫 `windows-msime-tsf-2.zip` は G-GEAR の `Downloads` にもある（SHA-256 `f2287a74…cd06` を照らす）。
2. 2.2 の 2 と同じ確かめを Surface で。
3. 書庫を G-GEAR に移す。
4. ★ datasheet のために（判断 213）: 2.2 の 4 と同じ（`git_commit`・`git_dirty`・`conditions.txt`・寄託したパイロットの run）。加えて、**§10.8 の確かめの run（パイロットの `verify` 計画 39 試行・2026-10-04 00:27〜00:37 JST）と、その最初の開始（runner が鍵を送る前に中止）もパイロットの部の候補として `--pack`** する（研究者の選択・判断 213-3）。runner が中止した Windows のパイロットの 3 つの試みは、`--pack` の前に `run.json` の `abort_reason` の文字列にアプリ名や窓の題が入っていないかを確かめる（security-checker の残し・`run_cell.py` の前面の窓の確かめの失敗の文を一次で読む）。管理者権限で拒まれた計測の開始（oracle のヘッダだけ）は、寄託の規則（`dataset.tex` §11.3）で決めて `data.windows.md` に書く。

### 2.4 G-GEAR（すべての書庫がそろってから）

1. 書庫の SHA-256 を `data.md`・`data.windows.md` と照らし、Zenodo のデータセットの下書き（23183438）の bucket に上げる（API・token はプロセスの中で読むだけ）。datasheet・`FORMATS.md`・コーパス・計画の設定と seed も（表 13 のとおり）。
2. ✅ datasheet は 2026-10-06 に下書きした（判断 213・`experiment/datasheet.md`・枝 `docs/ime-m12-datasheet`）。ここでは「(to be filled in at deposit)」の印（ファイル名・SHA-256・寄託したパイロットの run・working の観測ログ・macOS の `git_commit`・管理者権限で拒んだ開始・公開日）を埋める。⚠️ 研究者が全文を確かめたか（`datasheet-reading-ja.md`）と、その枝が merge 済みかを先に見る。
3. `\tbd` の残り 8 か所（試行の表の `at deposit` は寄託の規則で決まる・`confirmed at deposit`・datasheet）を埋め、`data.md`・`data.windows.md` の Deposits の場所と日付を埋める。`build.sh --submission`・文体の検査。
4. リリース D: 最新の枝の本番の形の書き出しを C の上に commit（`README.internal.md` の手順・`#!` に実行ビット）→ タグ `v1.0.0` → `git archive` の zip をソフトウェアの下書き（23183441）に上げる。Zenodo の説明を書き直す（"Draft." を消す）。
5. **研究者に確かめる**: GitHub の repo を public に・Zenodo の 2 つを publish（取り消せない）。公開の後、README の図とロゴ（ライト・ダーク）と DOI のリンクを Chrome で確かめる。
6. その後は `next-session-ime-paper-manuscript-7.md` §2 の 3〜5（PsyArXiv・投稿の前の確かめ・OSF のプロフィール名）。

### 2.5 この枝の残り

- 作業中の点検の指摘は判断 211 で直した。/cross-review は §2.0。
- ⚠️ M12 の完了時（D を作った後）にも、D までの変更に /cross-review を回す。

## §3 気をつけること

- ⚠️ 書き出しは、それを回す機械の値しか探さない（ほかの機械の値は `--also-user`・`--also-home` で渡す）。判断 207 の段取りでは、3 台それぞれで書き出しを回して確かめる。3 台とも通るまで公開に切り替えない。
- ⚠️ `git archive` は `core.autocrlf=true` だと CRLF で書き、凍結の一覧が別の値になる（実測 `ce8bfefe…`）。README の手順は `-c core.autocrlf=false`。
- ⚠️ 書誌の型（sn-apa）は `@misc` の `doi` を出さず、`url` を "Retrieved from" で出す。データとリリースの項目は `url` に `https://doi.org/…` を入れた。
- ⚠️ Zenodo の旧来の API はライセンスが 1 つ（データセット CC BY 4.0・ソフトウェア Apache-2.0）。データ・文書の CC BY 4.0 は README と同梱の LICENSE-DATA に書いてある。
- ⚠️ Windows の Python が標準出力に書く行には CR が付く（`while read` で使うなら `${f%$'\r'}`）。
- ⚠️ `pkill` は Windows の git-bash で効かない → 立てたサーバは PowerShell でそのポートのプロセスだけを止める。
- Codex の台帳: 2026-10-06 は 505,404 / 16 回（PR #316 の /cross-review 3 回の後・上限は 300,000 に戻した）。
