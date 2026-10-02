# 次セッション — IME 論文: M3 の凍結（事前登録の印・タグ・書き出しの一覧）→ OSF の登録（研究者）

> 作成: 2026-10-02（G-GEAR・attack-me round 5 と完了時レビューを終え、PR #289 を main へ merge したセッションの最後に）。
> 前の引き継ぎ `next-session-ime-paper-m3-round5.md` の後継（その §2 はすべて済み）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 125〜129**）・`tasklist.md`（M3）と、事前登録 `papers/ime-observation/experiment/preregistration.md` の **§9 Freeze**・§2.4・§3.1・§3.4。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → main から作業ブランチを切る（G-GEAR では main は別の worktree が checkout している）。
.steering/_handoff/next-session-ime-paper-m3-freeze.md を読んで §2 から始めてください。
一次は decisions.md の判断 125〜129 と、事前登録 §9（凍結の手順）・§2.4・§3.4。
凍結は取り消せない。印を入れる前に研究者に最終の確認を取る。OSF の登録は研究者が行う。
Skill: verify-before-claiming・git-workflow・reproducibility-discipline。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり）

- **PR #289 を merge 済み**（merge コミット `c613bdf5`）。事前登録の下書き・解析一式・attack-me round 1〜5 の記録・完了時レビューの直しが main に入った。**事前登録はまだ凍結していない**（`frozen_at` と `sha256` の行が無い。`experiment/run.sh` は実データで exit 3）。
- attack-me round 5: 判定 minor revision（R1・R2・R3 とも minor・fatal 0・major 0・捏造 0・注入 0）。研究者の採否は判断 125（焦点の規則を行と送出の 1 対 1 の対応で数え S15 の計画した切り替えにも当てる・計画の SHA-256 を解析で照合・感度は §7 に開示・round 6 は回さない）。**attack-me（stage `prereg`）は閉じた**（round 1〜5 の `tmp/` は消した。接地の文献は各 round の `panel.md` の URL と SHA-256 から取り直せる）。
- 完了時レビュー（code-reviewer ∥ security-checker は公開物 24 ファイル・Codex は研究者の選択で直近の `kit/` に絞って 2 巡）→ 判断 127（参照が焦点を得る前と止めた後も喪失として扱う・数える終わりを延ばす・計画をセルのライブ変換の設定と対応させる・残り 12 件）・判断 128（実装）・判断 129（Codex 2 巡目の扱い）。
- 確認（G-GEAR・Python 3.11.9）: `kit/check.sh` 29 本緑・`run.sh --synthetic` 2 回でバイト一致・未凍結の実データは exit 3・文の検査 0 件・引用の違反なし・節の参照はすべて実在・本文 15,469 語。PR の CI（Mac・Windows の self-hosted と frontend）は緑。

## §2 やること

1. **凍結の前の最終の確認を研究者に問う**（`AskUserQuestion`・推奨つき）。⚠️ 凍結は取り消せない。少なくとも次を一次で示す:
   - 未決・既知の限界: 規則の最終形（判断 125・127）はパイロットの生ログ（測定機にある）にまだ当てていない（預けるときに `--check-deposit` が当てる。§3.1 に開示）／規則の感度は selftest でしか確かめていない（§7）／送出の窓 300 ms と余裕 500 ms は設計の選択（§3.4）。
   - 凍結のハッシュの対象（`config.json`・`SEED`・`gt_rules.json`）と、タグで固定されるもの（§9 の表の 5 ファイル・解析のコード）。
2. **印を入れる**（研究者の OK の後）: §9 のとおり `python3 kit/analysis/pipeline.py --freeze-hash --config experiment/config.json --seed-file experiment/SEED` の値を `sha256:` の行に、日付を `frozen_at:` の行に（コメントとコードの囲いの外・各 1 行）。`pipeline.py --check-prereg experiment/preregistration.md --config experiment/config.json --seed-file experiment/SEED` が exit 0 になることを確かめる。§9 の SHA-256 の表の 5 ファイルが今の値と一致することも確かめる。
3. **凍結のコミットとタグ**: タグの名前は研究者に問う（既存のタグの付け方を `git tag -l` で見てから案を出す）。⚠️ タグは push した時点で公開物になる。
4. **書き出しの一覧の SHA-256**（§9）: 公開物の根（`experiment/` と `kit/` を持つディレクトリ）から書き出すファイルの一覧（パスと SHA-256・パスのバイト順・各行 LF）を作り、その SHA-256 を記録する。書き出しの範囲は `papers/ime-observation/.gitignore` と書き出しの道具（`kit/export/`）に従う（⚠️ 一次で確かめる）。
5. **OSF の登録は研究者**: 凍結のファイル・2 つの印・凍結のコミットの 40 桁の識別子・一覧の SHA-256 を渡す。登録の URL と日付は `experiment/notes.md` に記録する（§9）。**登録の日は最初の計測の run より前**。
6. 出荷（git-workflow ルール 6）。M4（Mac での本計測）は登録の後。

## §3 気をつけること

- ⚠️ 凍結の前に ImeShadow と正解を突き合わせない（判断 11）。封印（`sealed/`）は開けない。人の打鍵データを使わない。参照のログのキーコードを表示・転記しない。
- ⚠️ 凍結の後は、事前登録・解析のコード・凍結のハッシュの対象を変えない。変えるなら §8 の逸脱・追補として記録する。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ git-bash で `git show origin/main:<path>` は `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない。Windows の Python に `/c/...` のパスを渡さない。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
