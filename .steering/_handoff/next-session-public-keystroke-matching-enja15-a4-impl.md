# 次のセッション: 公開データでの照合の論文 —— ENJA15 と A4 の実装、そして本計算

作成 2026-10-13。前の引き継ぎ `next-session-public-keystroke-matching-checks-1-7.md` の検査 1〜7 は済んだ（`experiments/20261012-public-keystroke-matching/notes.md` の「データの検査」・逸脱 D1）。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。機械は G-GEAR。KLiCKe の著者（Dr. Tian）からは 2026-10-13 に返事が来た（懸念なし・MIT・IRB・集計で報告する勧めは事前登録と同じ・判断 54）。10/26 の催促は要らない。研究者が 10-13 に送った 2 通（Dr. Tian への審査機関の問い・PoPETs の program chairs への録画と発表の要否の問い）の返事を待つ（`next-session-public-keystroke-matching-1026-reminder.md`）。PoPETs から「録画か発表が必須」と返ってきたら投稿先を考え直す。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-enja15-a4-impl.md を読んで、研究者の判断 2 つを聞いてから ENJA15 と A4 を実装して。
```

## 今の状態

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`。検査のコミットは `0f226c2f`・`f3986a2d`・`d0dafd81`・`cafaef95`（レビュー: code-reviewer・security-checker・Codex 2 巡）。
- 検査の要点: KLiCKe 4,992 人・除外 0。配布の CSV は `\n`・`\t`・`\"`・`\\` でエスケープしており、読み込みで戻す（D1。直す前は最終稿の一致 1.4%・後は 97.0%）。検査 4 の区間の一致は 80.3%（空の区間を除くと 77.1%）。ENJA15 は 76 セッション・訳者 39・原文 6・交差。IME の経路の検査は PASS。KeyTAR は利用条件に合い A4 を行う。検査 7 は配布に Inputlog の値が無く行わない。
- 本計算の読み込み: `run_main.py` の `load_writers` はまだ `--source synthetic` だけ。`load_klicke.load` と `fill_rows` をつなぐ（全員の行をメモリに載せると 17M 行で重いので、作業のプロセスの中で読む形に）。

## 研究者に聞くこと（AskUserQuestion・推奨と理由を添える）

1. A4 の人数: 500 人で GPU 約 150 時間（約 6 日・CPU の本計算と並行できる）。推奨は 500 人のまま（登録どおり・締切まで 7 週ある）。減らすなら A4 の行だけを課題ごとに同数ずつ減らし逸脱に書く。
2. A4 の `max_new_tokens`: 既定の 50 では 20 区間の塊（間隔 70〜144 個）を復元しきれない。選択肢は (a) 既定のまま（登録の「成果物の既定」の字面どおり・復元は途中で切れる）、(b) 塊の大きさに合わせて延ばす（逸脱・時間は増える）。どちらも notes の逸脱か限界に書く。

## やること

1. ENJA15 の実装（`scripts/enja15.py` を広げる）: 区間の規則（英字の押下は IME の行の `[A]`〜`[Z]` と insert の行の英字 1 字・`[Back]` は IME と delete の両方を数えるのが字面の読み・句読点の確定で閉じる）・R0j・R3j・R3j-t(w)・R4(w)・A0・A2・訳文の区間（SudachiPy の読みと `romaji_table.py`）・おとりと交差のブートストラップ。R3j の種類の対応（`[Space]`・`[F7]`〜`[F10]` を変換、IME の `[Return]` と insert の文字列を確定）と `[PageUp]`・`[Next]`・`[Prior]` の扱いを、照合の値を見る前に「実装で決めたこと」に書く。変えたら IME の経路の検査を回し直す。
2. A4 の実装（KeyTAR の venv `~/.venvs/pkm-keytar`・`scripts/check6_keytar.py` の読み込みと入力の形を使う）: 間隔の上限 1,023・前の往復なし・比べる 1 本（既定の出力の先頭）・R0〜R3 は入力が同じなので使い回す。
3. 本計算: `run.sh` に実データの段を足す。主な表（500 人）→ 補遺（全員・約 22 時間）。

## 守ること

- 記録と本文の中身を Claude 自身も読まない（数・ハッシュ・分布だけを出す。値を書くのは閉じた一覧だけ）。打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex にはコードと文書の差分だけ（`raw/` と結果の JSON を範囲に入れない）。
- 凍結の後の変更はすべて `notes.md` の「逸脱」に（変える前の結果も残す）。
- 応答は日本語。★・⚠️ を多用しない。`git add -A`・`git add <dir>` を使わない。バックスラッシュを含む置換は Write か Edit で（heredoc は壊す）。
- 状態を変える操作（push・PR・merge）は出力をファイルに保存して 1 回だけ。
