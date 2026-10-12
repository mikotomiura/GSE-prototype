# 次のセッション: 公開データでの照合の論文 —— 取得の後の検査 1〜7

作成 2026-10-13。前の引き継ぎ `next-session-public-keystroke-matching-code-fixes-then-acquire.md` の 1（コードの直し）と 2（取得）は済んだ。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。機械は G-GEAR。10/26 の催促は `next-session-public-keystroke-matching-1026-reminder.md`。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-checks-1-7.md を読んで、取得の後の検査 1〜7 を進めて。
```

## 今の状態（2026-10-13）

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`。PR #364（凍結と本計算のコードと凍結の後の直し）は CI 緑で main に merge した（merge commit `1753696e`）。その後の 2 コミット（ENJA15・KLiCKe の取得の記録）は push 済みで PR はまだ。
- コードの直し: `notes.md`「凍結の後・データの前の直し」。自己検査 PASS・変異 21 個すべて狙った検査で落ちる。レビューは code-reviewer 1 回・Codex 2 巡（陰性対照の R3-u の A3 の版の選び直し HIGH を含め直した）。security-checker は今回の差分では回していない（集計と自己検査だけ）。
- 取得（中身はまだ 1 行も開いていない）:
  - KLiCKe: `raw/klicke/WritingTask.zip`（SHA-256 `ffa4d753…`）。展開は `raw/klicke/extracted/WritingTask/`（`keystrokelogs/csv` 4,992・`texts` 4,992・`holistic_scores.csv`・`writing_prompts.docx`）。人口統計は取らず、zip にも無かった。
  - ENJA15: `raw/enja15/`（SVN r649・T のセッションだけ・`enja15-manifest-r649.sha256`）。ライセンスは CRITT のページで CC BY-NC 4.0 と CC BY-NC-SA が食い違う（[P484]・厳しい方に従う）。T の意味は [P483]。
  - KeyTAR: `raw/keytar/keytar.zip`（2026-10-12T21:56:20Z に取得を終えた・大きさと md5 が Zenodo の値と一致・SHA-256 `d2fe250a…` を `data.md` と `config.json` に記録）。まだ展開していない。
- 検査 2 の最初の項目（列名）だけ見た:
  - 記録の CSV: `"",DownEventID,UpEventID,DownTime,UpTime,ActionTime,DownEvent,UpEvent,CursorPosition,PauseTime,WordCount,TextChange,Activity`（4,991 本は引用符つき、1 本は引用符なし）。先頭の名無しの列は行の番号と見られる（確かめる）。
  - `holistic_scores.csv`: `ID,Prompt,Text,Score`。本文の列 `Text` を含む（11 MB）。
  - pip-audit 2.10.1（使い捨ての venv）で `requirements.txt` に既知の脆弱性なし。

## やること

### 1. `load_klicke.py` と検査 1・2

- 列の対応（Kaggle の名へ）: `DownEventID` → `event_id`、`DownTime` → `down_time`、`UpTime` → `up_time`、`ActionTime` → `action_time`、`DownEvent` → `down_event`、`UpEvent` → `up_event`、`CursorPosition` → `cursor_position`、`WordCount` → `word_count`、`TextChange` → `text_change`、`Activity` → `activity`。`UpEventID`・`PauseTime`・先頭の番号の列は表に無い列なので、事前登録の規則（R0 以外で削除）どおり使わない（本計算の行は Kaggle の列だけなので、どの形でも出ない）。検査 2 で「表に無い列」として一覧に書く。`DownEventID` と `UpEventID` が違う行の数を数える（`down_event` と `up_event` が違う行と並べる）。
- 課題・採点: `holistic_scores.csv` の `ID`・`Prompt`・`Score`。`Text` の列は読まない（配布の本文は `texts/<ID>.txt` を使う。README の "~5,000 persuasive texts" のファイル）。`Text` と `texts/` の照合は事前登録の検査に無いので計算しない（「ここに無い量は計算しない」）。どちらを本文とするかは notes の「実装で決めたこと」に書く。
- 例外に行の断片を出さない（書き手の ID と例外の型名だけ）。`Move From` の書式が合わない行は除外の理由に回す（security-checker LOW 2）。
- 検査 1: 各ファイルの SHA-256（済み）・行の数・書き手の数・課題ごとの数・除外の数（理由ごと）・複数の課題に現れる ID の数。
- 検査 2: 列名（上）・`Activity` の値の一覧・押したキーの値のうち `config.json` の `key_categories` の対応（`synthetic_logs.category`）に無い値の一覧・模擬の仮定を確かめる数（事前登録の検査 2 の列挙どおり）。値の一覧は押したキーの値と `Activity` の値に限る（`text_change` の値は出さない）。
- 結果は `notes.md`「データの検査」に。手順を直すときは直す前と後を「逸脱」に。

### 2. 検査 3〜7

- 3: R0 の再生（`corpus.replay_origins`）の最終稿と配布の本文の一致の割合（空白の正規化の後の完全一致・正規化編集距離の分布）。
- 4: 区間の規則で数えた区間の値と、R0 の真の対応から数えた値の一致の割合。
- 5: ENJA15 の数（セッション・訳文・原文ごとの訳者・訳者ごとの原文の数 → 交差か入れ子か・`Type` と `IMEtext` の値の種類）。読み込みの前に Translog-II の XML の構造を、要素と属性の名前だけで確かめる。訳文は Translog-II の XML か `Alignment/*.tgt` のどちらかで、決めたら notes に書く。IME の経路の検査（R3j の後に文字列が残らない）もここ。
- 6: KeyTAR の取得の後。`model_licenses`・`ethics.txt`・`limitations.txt` を読む（合わなければ A4 を行わない）。RTX 5060 Ti に合う PyTorch と CUDA の版を `env.md` に固定（本計算の venv とは別の venv）。種で引いた 1 本で推論の時間と GPU のメモリだけ（復元と照合の値は見ない）。既定の設定を `data.md` に。
- 7: 配布に Inputlog の値（作文の過程の指標）があるかを、ファイルの一覧と列名だけで確かめる。`WritingTask.zip` には IDFX（Inputlog の形式の記録）しかなく、指標の値のファイルは見当たらない。無ければ検査 7 は行わず、その旨を報告する（Inputlog を自分で回さない）。あわせて、削除・挿入の連なりが修飾の行で切れる点の読み方（[V264] Table 5 の "one deletion activity"）は、検査 7 が行えないなら直す機会が無いので、登録の字面どおりのまま限界に書く。

## 守ること（大事な順）

- 記録と本文の中身を、Claude 自身も読まない。生の行・本文・抜粋を `cat`・`head`・`Read` で開かない。スクリプトは数・ハッシュ・集計だけを出す。書き手の ID の一覧も出さない（8 桁の数字）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ（`raw/` を範囲に入れない）。
- 凍結の後の変更はすべて `notes.md` の「逸脱」に（変える前の結果も残す）。
- 応答は日本語。★・⚠️ を多用しない。
- `git add -A`・`git add <dir>` を使わない。置換のスクリプトは Write で作る。config を書き換えたら重複キーを検出する形で JSON を読む。
- 状態を変える操作（push・PR・merge・取得）は出力をファイルに保存して 1 回だけ。
