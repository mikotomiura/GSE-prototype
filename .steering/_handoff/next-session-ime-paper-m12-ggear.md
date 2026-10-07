# 次セッション（G-GEAR）— IME 論文 M12: Mac と Surface の枝を合わせ、照合して Zenodo に上げ、datasheet を埋め、リリース D → 公開の確認

> 作成: 2026-10-06 夜（G-GEAR・判断 215 の後）。`next-session-ime-paper-manuscript-9.md` の §2.3 を、機械ごとの引き継ぎに分けて具体にしたもの（研究者の求め）。**Mac（`next-session-ime-paper-m12-mac.md`）と Surface（`next-session-ime-paper-m12-surface.md`）の両方が済んでから**始める。
> ✅ **§2.1〜2.5 は済み（2026-10-07・G-GEAR・判断 218・PR #318 merge `62cacbe5`）**: 3 台の枝を合わせ、`C:/ime-deposit/` の 30 ファイルで照合が通り（保留 0）、datasheet と `\tbd` 8 か所を埋め、点検と /cross-review（Codex 3 回）の指摘を直した。
> ✅✅ **すべて済み（2026-10-07 昼・G-GEAR・判断 218〜220）**: 38 ファイルの寄託・README の仕上げと日本語訳（PR #319・`428a13bd`）・リリース D `48caf9ef`（タグ `v1.0.0`）・Zenodo の 2 つを publish（`10.5281/zenodo.23183438`・`…23183441`・2026-10-07）・GitHub の repo を public。**残りは `next-session-ime-paper-manuscript-7.md` §2 の 3〜5**（PsyArXiv・投稿の前の確かめ・OSF のプロフィール名）。下の途中経過は記録として残す。
> ⏳ **2026-10-07 未明の途中経過（判断 218・219）**: (1) データセットの下書きへの `--upload`（`62cacbe5` の新しいクローン・job の tmp の `clone-main`）は 33 ファイルまで済み、残り 5 つ（大きい書庫）を送り直し中（回線は毎秒 73 KB ほど・1 回目は 55 MB で HTTP 0）。途中で止まっても、同じ命令を回し直せば既にあるものは飛ばす。(2) 研究者の求めで README を仕上げ、日本語訳 `README.ja.md` を足した（枝 `docs/ime-m12-readme`・PR はまだ）。上げが済んだら同じ枝で記録（`data.md`・`data.windows.md`）の寄託先と日付を埋めて PR → merge。(3) リリース D は 1 回目（`12dc813f`・研究者が GitHub に push 済み・非公開）を、README の後の main から**作り直して置き換える**（force push は研究者）。(4) 研究者は「Zenodo は用意ができたら publish してよい」と許した → 説明と日付（文案は job の tmp の `dataset-description.html`・`software-description.html`・`zenodo_update.py`）→ ソフトウェアに D の zip → 2 つを publish。GitHub を public にする許可はまだ無い。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/decisions.md` の**判断 207〜218**、`tasklist.md` の M12、`papers/ime-observation/kit/export/deposit.internal.{json,py}`（docstring が照合と上げの仕様）、`kit/export/README.internal.md`（公開の手順と履歴）、`experiment/data.md`・`data.windows.md`、`experiment/datasheet.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → origin/docs/ime-m12-mac-conditions と origin/docs/ime-m12-surface-deposit が push されているか（判断 216・217）を確かめる。どちらか無ければ止まって研究者に聞く。
⚠️ G-GEAR では main を別の worktree（C:/wt/p321-submission）が使っているので git switch main はしない。origin/docs/ime-m12-deposit-prep から枝 docs/ime-m12-deposit を切り、2 つの枝を merge する（decisions.md・tasklist.md は末尾の追記どうしの衝突になる → 両方を残す）。
.steering/_handoff/next-session-ime-paper-m12-ggear.md を読んで §2 を実行してください。
一次は decisions.md の判断 207〜217、tasklist.md の M12、kit/export/deposit.internal.json と deposit.internal.py の docstring、kit/export/README.internal.md、experiment/data.md・data.windows.md・datasheet.md。
Skill: git-workflow・verify-before-claiming・data-privacy・subagent-delegation・browser-verification（GitHub と Zenodo を Chrome で見るとき）。応答は日本語。コミットは git add パス指定。
⚠️ 公開（GitHub の repo を public に・Zenodo の publish）は取り消せない → その場で研究者に確かめる。Zenodo の下書き 2 つ（23183438・23183441）を消さない（予約した DOI が失われる）。token（C:/zenodo/）は表示・委譲しない。
⚠️ 公開 repo の履歴 A〜C は組み直さない（C の hash cb29a1a9… が原稿に入っている）。
⚠️ 新しい計測はしない。凍結のタグのコードと事前登録は変えない。生ログ・キーコードを原稿や外部の LLM に出さない。
⚠️ 研究者のメールアドレスを Codex に送らない（/cross-review は §3 の「伏せた写し」で）。
⚠️ 判断の番号は 218〜。heredoc でバックスラッシュを重ねない → 置換は Edit か Write で書いたスクリプトで。
```

## §1 状態（2026-10-06 夜）

- ✅ 判断 214（Mac）・215（G-GEAR）。寄託は **1 ファイルずつ**（研究者の選択）。一覧 `kit/export/deposit.internal.json`（39 項目: 計測 3・working 2・標本 8・パイロットと確かめの run・共有 8）と道具 `kit/export/deposit.internal.py`（照合・`--remote`・`--upload`・`--table`・selftest。点検 code ∥ security の指摘 17 件を直した・変異で selftest が赤になることを確かめた）。
- ✅ `--remote`（GET）で下書き 23183438 を読んだ: 予約の DOI 一致・`unsubmitted`・バケットは API のホスト・ファイル 0（2026-10-06）。
- ✅ この枝の新しいクローンで本番の形の書き出し exit 0・195 ファイル（Mac の `data.md` の追記を含む・internal の 2 ファイルは入らない）・その木で `kit/check.sh` 31 本緑・共有の 8 ファイルは書き出しとバイト一致（`--export`）。
- ⏳ Mac（判断 216 の予定）: `conditions.txt` の SHA-256 を `data.md` と一覧に・macOS の 15 ファイルを `C:/ime-deposit/` へ。
- ⏳ Surface（判断 217 の予定）: Windows の書庫と標本・`data.windows.md` と一覧・書き出しの確かめ・`C:/ime-deposit/` へ。
- 残る `\tbd` 8 か所: `dataset.tex` の `confirmed at deposit`（working の観測ログ）と `written at deposit`（datasheet）、試行の表（`results-agreement.tex`）の `at deposit` 6 か所。datasheet の「(to be filled in at deposit)」。
- ⚠️ 判断 215 で見つけた点: 研究者が採った datasheet の「Files of the deposit」の表（7 行）は、datasheet 自身を含む行の SHA-256 を「寄託のときに埋める」としていたが、自分自身の値は書けない。→ 1 ファイルずつの表に広げ、datasheet の行は `not given (this file)`。**研究者が採った版からの差なので、埋めた後に伝える。**

## §2 やること

1. **合わせる**: §0 のとおり枝 `docs/ime-m12-deposit` に Mac と Surface の枝を merge。`python -I papers/ime-observation/kit/export/deposit.internal.py --selftest` と `bash papers/ime-observation/kit/check.sh`（作業ツリー・34 本）。
2. **集める**: `C:/ime-deposit/` に macOS の 15 ファイル・Windows の書庫と標本（Surface から）・`windows-msime-tsf-2.zip`（Downloads から写す）。名前は何でもよい（道具は SHA-256 で探す）。
3. **照合**: `python -I papers/ime-observation/kit/export/deposit.internal.py --from C:/ime-deposit` → **保留 0・MISSING 0・FAIL 0**（`--allow-pending` を付けない）。`unlisted` が出たら何かを確かめる。続けて `--remote`（GET だけ）。
4. **datasheet を埋める**: 「Files of the deposit」の表の本体を `--table` の出力で置き換える（1 行 1 ファイル・datasheet の行は `not given (this file)`）。ほかの「(to be filled in at deposit)」を `data.md`・`data.windows.md` の記録から埋める（寄託した working の観測ログ・寄託したパイロットの run・各 run の `git_commit`・管理者権限で拒んだ開始・公開日）。`\tbd` の残り 8 か所、`data.md`・`data.windows.md` の Deposits の場所（`https://doi.org/10.5281/zenodo.23183438`）と日付。`build.sh --submission`・文体の検査（違反 0）。⚠️ datasheet を変えたら、研究者が採った版からの差を伝える（表の形・埋めた値）。
5. **点検と PR**: code-reviewer ∥ security-checker → /cross-review（§3 の伏せた写しで・パス限定）→ PR → CI 緑で merge（git-workflow ルール 6）。
6. **データセットを上げる**（merge の後の main と同じ commit で）: `python -I papers/ime-observation/kit/export/deposit.internal.py --from C:/ime-deposit --upload`（最終の状態を求める・小さい順・送る前にハッシュを取り直す・公開はしない）。出力の `source commit` を記録に残す。Zenodo のデータセットの説明を書き直す（"Draft." を消し、datasheet と合わせる）。
7. **リリース D**: 最新の main の本番の形の書き出しを C の上に commit（`README.internal.md` の手順・`#!` に実行ビット）→ タグ `v1.0.0` → `git -c core.autocrlf=false archive` の zip をソフトウェアの下書き（23183441）に上げる（⚠️ `deposit.internal.py` はデータセット用。D の zip は判断 208 と同じく手で・API で上げる）。説明を書き直す。D の後に D までの変更に /cross-review（伏せた写しで）。
8. **研究者に確かめる**: GitHub の repo を public に・Zenodo の 2 つを publish（取り消せない）。公開の後、README の図とロゴ（ライト・ダーク）と DOI のリンクを Chrome で確かめる。
9. その後は `next-session-ime-paper-manuscript-7.md` §2 の 3〜5（PsyArXiv・投稿の前の確かめ・OSF のプロフィール名）。

## §3 気をつけること

- ⚠️ **/cross-review で研究者のメールアドレスを Codex に送らない**（判断 213）: 差分に datasheet の連絡先や書き出しの道具の定数が入るときは、worktree で**基点と頭の両方**のアドレスを伏せた写しの commit（push しない）を作り、伏せた同士の範囲を `run-codex-review.sh <base>..<head> -- <paths>` に渡す。送る前に `git diff <base>..<head> | grep -ci 'mmiura\|gmail'` が 0。終わったら worktree を消す。
- ⚠️ `--upload` は一覧・記録・datasheet が HEAD と同じでないと止まる（作業ツリーの未コミットの変更があれば先に commit）。下書きに一覧に無いファイルや中身の違うファイルがあれば何も送らずに止まる（ウェブ画面で消してから回し直す）。途中で止まったら、回し直すと既に上がったファイルは飛ばす。
- ⚠️ `git archive` は `core.autocrlf=true` だと CRLF で書き、凍結の一覧が別の値になる（実測 `ce8bfefe…`）。
- ⚠️ 書誌の型（sn-apa）は `@misc` の `doi` を出さず、`url` を "Retrieved from" で出す。データとリリースの項目は `url` に `https://doi.org/…` を入れた。
- ⚠️ Zenodo の旧来の API はライセンスが 1 つ（データセット CC BY 4.0・ソフトウェア Apache-2.0）。
- ⚠️ `run-codex-review.sh` が台帳を書き戻すと `.codex/budget.json` が CRLF になる（中身は壊れない）。台帳は回す前に origin/main のものも見る（memory「Codex ledger split by branch」）。
- ⚠️ 別の job の一時ディレクトリに token の写しが残っている（判断 215 に書いた・研究者に消すかを確かめる）。
