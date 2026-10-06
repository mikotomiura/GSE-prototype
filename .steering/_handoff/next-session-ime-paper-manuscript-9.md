# 次セッション — IME 論文 M12 の続き: Mac・Surface で書庫と書き出しの確かめ → G-GEAR で Zenodo に上げてリリース D → 公開の確認

> 作成: 2026-10-06 夜（G-GEAR）。判断 212・213 の後（PR #316・#317 は main に merge 済み）。`next-session-ime-paper-manuscript-8.md` をこれで置き換える。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 207〜213**、`tasklist.md` の M12 の小項目、`papers/ime-observation/kit/export/README.internal.md`（公開の履歴と手順）、`experiment/data.md`・`data.windows.md` の寄託の手順、`experiment/datasheet.md`。状態は着手時に `git fetch` で測り直す。
> ⚠️ このファイルは枝 `docs/ime-m12-handoff-9` にある（.steering だけの変更なので PR を出していない）。main にはまだ無い → `git fetch` の後、新しい作業はこの枝（＝ main ＋ この引き継ぎ）から切る。

## §0 打ち込む用

```
git fetch → 状態を測る（main = 3e383ccb 以降か・枝 docs/ime-m12-handoff-9 の引き継ぎ）。⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。新しい作業は origin/docs/ime-m12-handoff-9 から枝を切る。
.steering/_handoff/next-session-ime-paper-manuscript-9.md を読んで §2 を、このセッションの機械（Mac / Surface / G-GEAR）の節から実行してください。
一次は decisions.md の判断 207〜213、tasklist.md の M12、kit/export/README.internal.md、experiment/data.md と data.windows.md の寄託の手順、experiment/datasheet.md。
Skill: git-workflow・verify-before-claiming・data-privacy（書庫・--pack・run.json を読むとき）・subagent-delegation・browser-verification（GitHub と Zenodo を Chrome で見るとき）。応答は日本語。コミットは git add パス指定。
⚠️ 公開（GitHub の repo を public に・Zenodo の publish）は取り消せない → その場で研究者に確かめる。Zenodo の下書き 2 つ（23183438・23183441）を消さない（予約した DOI が失われる）。token（C:/zenodo/）は表示・委譲しない。
⚠️ 公開 repo の履歴 A〜C は組み直さない（C の hash cb29a1a9… が原稿に入っている）。正本は C:/wt/ime-conversion-logging.git（bare・G-GEAR）と GitHub。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。run.json は欄を名指して読む（ログは開かない）。
⚠️ 研究者のメールアドレスを Codex に送らない（/cross-review は §3 の「伏せた写し」で）。
⚠️ 判断の番号は 214〜、逸脱は D13。heredoc でバックスラッシュを 2 本重ねない（python に渡ると壊れる）→ 置換は Edit か Write で書いたスクリプトで。
```

## §1 状態（2026-10-06 夜）

- ✅ M12 の進め方（判断 207）・Zenodo の下書き 2 つ（データセット **DOI 10.5281/zenodo.23183438**・ソフトウェア **DOI 10.5281/zenodo.23183441**・どちらもファイルなし・説明は仮）・非公開の公開 repo `mikotomiura/ime-conversion-logging` に研究者が A〜C を push 済み（main = `cb29a1a9…`・タグ 2 つ）（判断 208〜211）。
- ✅ **PR #316 を merge**（`c77e324f`・判断 212）。/cross-review（Codex 3 回）の指摘 7 件を直した: SVG を XML として読む層・文字参照を戻した走査・`<text>` の中の `<title>`・凍結の一覧の手順が期待値と比べる・`xml:base`・入れ子の復号・引用符の中の `>`。変異 21 本すべて赤。main の CI 緑。
- ✅ **PR #317 を merge**（`3e383ccb`・判断 213）。**datasheet** `papers/ime-observation/experiment/datasheet.md`（Gebru らの 7 節・英語・寄託にも同じものを入れる）。点検（code ∥ security）で全面的に書き直し、研究者が日本語の全文（`datasheet-reading-ja.md`）を読んで「このまま採る」。/cross-review 2 巡の指摘 5 件を直した。研究者の答え: 連絡先はメール（書き出しの道具が `experiment/datasheet.md` でもアドレスを通す）・**§10.8 の確かめの run はパイロットの部に入れる**・青空文庫は 12 作品の表と作業履歴・方針の文はこのまま。`dataset.tex` §11.1 と表 13・AI 宣言も直した。⚠️ main の CI（run 37464854917）は引き継ぎを書いた時点で実行中 → 着手時に `gh run view 37464854917` で緑を確かめる。
- ✅ 本番の形の書き出し（ライセンスあり）が G-GEAR で exit 0・**195 ファイル**（datasheet を含む）・その木で `kit/check.sh` 31 本が緑。
- ✅ Windows のセルの書庫 `windows-msime-tsf-2.zip`（G-GEAR の Downloads）は `data.windows.md` の SHA-256 `f2287a74…cd06` と一致。その `run.json` の `git_commit`・`git_dirty` はどちらも `null`（export から回した）。
- 残る `\tbd` 8 か所: `dataset.tex` の `confirmed at deposit`（working の観測ログ）と `written at deposit`（datasheet）、試行の表（`results-agreement.tex`）の `at deposit` 6 か所。datasheet の「(to be filled in at deposit)」の印も寄託のときに埋める。
- Mac・Surface の書庫はまだ作っていない（G-GEAR に届いていない）。

## §2 やること

### 2.1 Mac（macOS の書庫と書き出しの確かめ）

> ✅ **済み（2026-10-06・Mac・判断 214）**: 書庫 9 つは `~/ime-m4/deposit/`（`macos-e3-working-1.zip`・`pilot/`）、標本は `~/ime-m4/deposit/e3-samples/`。SHA-256 と `git_commit` は `data.md`。書き出し 3 種も確かめ済み。残りは 4（G-GEAR へ移す）だけ。

1. `data.md` の寄託の手順 1〜5 で、まだ書庫にしていないものを束ねる: macOS の E3 の `working` の run（Run checks の行 `macos-e3-working` は点検済み）、較正パイロットの run のうち寄託の条件を満たすもの（候補は datasheet の Parts 2: `pilot-1`・`verify-1`・`verify-s5`・`pilot2-on`・`pilot2-off`・`verify-off`・`short-1` と最初のパイロットの前の runner の run。封印したセッション行は寄託のためだけに `seal_obs.py --unseal` で戻し、解析しない）、E3 の標本（`idle` と `working` の **`samples.tsv` と `conditions.txt`**）。`--pack` に `--also-user`・`--also-home` を渡す（値は書かない）。SHA-256 を `data.md` の Deposits と「Machine that ran the deposit check」に記録する。寄託したパイロットの run と、通らなかった候補とその理由も `data.md` に書く。
2. ★ datasheet のために（判断 213）: 各 run の `run.json` の **`git_commit` と `git_dirty` だけ**を読んで `data.md` に記録する（値は commit の 40 桁か `null`。非公開の作業 repo の commit なら datasheet にすでにそう書いてある）。
3. 公開物の書き出しを Mac で回して、Mac の値（ホーム・ログイン名・ホスト名）が入っていないことを確かめる: 2 つの凍結のタグのきれいな worktree でタグ自身の `export.internal.py --allow-missing-license`（一覧が `29b183ba…`・`f61af353…` と一致）、`origin` から取った最新の main で本番の形の書き出し（exit 0・195 ファイル）と、その木で `bash kit/check.sh`。
4. 書庫・標本を G-GEAR に移す（研究者・Windows の書庫と同じ道）。

### 2.2 Surface（Windows の書庫と書き出しの確かめ）

1. 2.1 の 1・2 と同じことを Windows で: E3 の `working` の run、較正パイロットの TSF の入力欄の run（`short-tsf`・`pilot-tsf`・`verify-tsf`・`toolcheck-tsf` と runner が中止した 3 つの試み。⚠️ IMM の入力欄のものは寄託しない）、標本（`samples.tsv`・`conditions.txt`）。`data.windows.md` に記録。
2. ★ **§10.8 の確かめの run**（パイロットの `verify` 計画 39 試行・2026-10-04 00:27〜00:37 JST・計測の cell ファイル）と、その最初の開始（runner が鍵を送る前に中止）を、パイロットの部の候補として `--pack` する（研究者の選択・判断 213-3）。
3. ★ runner が中止した Windows のパイロットの 3 つの試みは、`--pack` の前に `run.json` の `abort_reason` の文字列にアプリ名や窓の題が入っていないかを確かめる（`run_cell.py` の前面の窓の確かめが失敗したときの文を一次で読む・security-checker の残し）。
4. 管理者権限で拒まれた計測の開始（oracle はヘッダだけ）を寄託するかを `dataset.tex` §11.3 の規則で決め、`data.windows.md` に書く。
5. 2.1 の 3 と同じ確かめを Surface で。
6. 書庫・標本を G-GEAR に移す。G-GEAR の `Downloads` にある `windows-msime-tsf-2.zip` はもう照らした（移さなくてよい）。

### 2.3 G-GEAR（すべての書庫がそろってから）

1. 書庫の SHA-256 を `data.md`・`data.windows.md` と照らし、Zenodo のデータセットの下書き（23183438）の bucket に上げる（API・token はプロセスの中で読むだけ）。datasheet・`FORMATS.md`・コーパス・計画の設定（`plan_config.*.json`・`recipes*.json`）・`SEED`・標本も（表 13 と datasheet の Parts のとおり）。ファイル名は datasheet の「Files of the deposit」の表に合わせて決める。
2. datasheet の「(to be filled in at deposit)」をすべて埋める（ファイル名・SHA-256・working の観測ログ・寄託したパイロットの run・`git_commit`・管理者権限で拒んだ開始・公開日）。`\tbd` の残り 8 か所（試行の表の `at deposit`・`confirmed at deposit`・`written at deposit`）を埋め、`data.md`・`data.windows.md` の Deposits の場所と日付を埋める。`build.sh --submission`・文体の検査。⚠️ datasheet を変えたら、研究者が採った版からの差を伝える。
3. リリース D: 最新の main の本番の形の書き出しを C の上に commit（`README.internal.md` の手順・`#!` に実行ビット）→ タグ `v1.0.0` → `git archive` の zip をソフトウェアの下書き（23183441）に上げる。Zenodo の説明を書き直す（"Draft." を消す）。⚠️ D の後に D までの変更に /cross-review（§3 の伏せた写しで）。
4. **研究者に確かめる**: GitHub の repo を public に・Zenodo の 2 つを publish（取り消せない）。公開の後、README の図とロゴ（ライト・ダーク）と DOI のリンクを Chrome で確かめる（ロゴと動く図は D の README に入る）。
5. その後は `next-session-ime-paper-manuscript-7.md` §2 の 3〜5（PsyArXiv・投稿の前の確かめ・OSF のプロフィール名）。

## §3 気をつけること

- ⚠️ **/cross-review で研究者のメールアドレスを Codex に送らない**（判断 213）: 差分に datasheet の連絡先や書き出しの道具の定数（`"mmiura.network" + AT + …` の前後の行）が入るときは、worktree で**基点と頭の両方**のアドレスを伏せた写しの commit（push しない）を作り、伏せた同士の範囲を `run-codex-review.sh <base>..<head> -- <paths>` に渡す（頭だけ伏せると、基点の定数が消した行として出る）。送る前に `git diff <base>..<head> | grep -ci 'mmiura\|gmail'` が 0 であることを確かめる。終わったら worktree を消す。
- ⚠️ 書き出しは、それを回す機械の値しか探さない（ほかの機械の値は `--also-user`・`--also-home` で渡す）。3 台それぞれで書き出しを回して確かめ、3 台とも通るまで公開に切り替えない。
- ⚠️ `--pack` は manifest と 4 つのログだけを束ねる。標本（`samples.tsv`・`conditions.txt`）は束ねず確かめもしない（datasheet に書いてある）→ 移す前に目で中身の形だけ確かめる（パスが無いこと）。
- ⚠️ `git archive` は `core.autocrlf=true` だと CRLF で書き、凍結の一覧が別の値になる（実測 `ce8bfefe…`）。README の手順は `-c core.autocrlf=false`（手順は期待値と比べて exit 1 になる形に直した）。
- ⚠️ 書誌の型（sn-apa）は `@misc` の `doi` を出さず、`url` を "Retrieved from" で出す。データとリリースの項目は `url` に `https://doi.org/…` を入れた。
- ⚠️ Zenodo の旧来の API はライセンスが 1 つ（データセット CC BY 4.0・ソフトウェア Apache-2.0）。データ・文書の CC BY 4.0 は README と同梱の LICENSE-DATA に書いてある。
- ⚠️ Windows の Python が標準出力に書く行には CR が付く（`while read` で使うなら `${f%$'\r'}`）。
- ⚠️ `pkill` は Windows の git-bash で効かない → 立てたサーバは PowerShell でそのポートのプロセスだけを止める。
- ⚠️ `run-codex-review.sh` が台帳を書き戻すと `.codex/budget.json` が CRLF になる（git は LF に直してコミットする・中身は壊れない）。
- Codex の台帳: 2026-10-06 は 555,564 / 18 回（PR #316 の 3 回・#317 の 2 回の後・上限は 300,000 に戻した）。
