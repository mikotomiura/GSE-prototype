# 次のセッション: 公開データでの照合の論文 —— 本計算のコードの直し → 取得 → 検査 1〜7

作成 2026-10-13（凍結の後）。このメモは `next-session-public-keystroke-matching-research-forward.md` の続きで、その「1. 凍結の残り」は済んだ。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。機械は G-GEAR（16 コア・RTX 5060 Ti）。10/26 の催促は別の引き継ぎ `next-session-public-keystroke-matching-1026-reminder.md`。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-code-fixes-then-acquire.md を読んで、本計算のコードの直しから進めて。
```

## 今の状態（2026-10-13）

- **事前登録は凍結した**: OSF の DOI 10.17605/OSF.IO/Y5R7N（2026-10-12 16:43:33 UTC・「OSF Preregistration」v4・公開）。論文用のリポジトリ `C:\keystroke-log-release-matching`（GitHub `mikotomiura/keystroke-log-release-matching`・private）のコミット `cf5353da` の `preregistration.md`・`config.json`・`SEED`（SHA-256 は OSF の API で一致を確かめた）。**以後の変更は `notes.md` の「逸脱」に書く。**
- 判断の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜53 と凍結）。判断 52: KeyTAR は凍結の後に取得してよい。判断 53: 凍結の前に曖昧さ 3 つ（陰性対照の攻撃者の固定・A3 は A2 の揃え・ブートストラップの標本の名前 `main500`/`all`）を直した。
- 本計算のコード（データの前・合成の記録で通した）: `experiments/20261012-public-keystroke-matching/scripts/`（`align_vec.py`・`seeds.py`・`corpus.py`・`forms.py`・`attackers.py`・`matching.py`・`evaluate.py`・`aggregate.py`・`utility.py`・`run_main.py`・`selftest_main.py`）・`run.sh`・`env.md`・`requirements.txt`。作業記録 `.steering/20261013-public-keystroke-matching-main/`（requirement・design・tasklist）。実装で決めた細部は `notes.md` の「実装で決めたこと」。
- venv: `~/.venvs/pkm-main`（Python 3.11.9・numpy 2.2.6・scikit-learn 1.5.2）。`C:/Users/johnd/.venvs/pkm-main/Scripts/python.exe`。
- 自己検査 `scripts/selftest_main.py` は PASS・変異 6 つすべて落ちる（約 6.5 分）。`run_main.py` は再実行と並列の数でバイト一致。実データの大きさ（約 400 語・候補 1,200 本）で 1 記録 約 256 秒 → 16 並列で主な表 約 3 時間・全員の補遺 約 22 時間。
- ブランチ `docs/public-keystroke-matching-freeze`（worktree `C:\GSE-wt-matching-prereg`・push 済み・PR はまだ）。

## やること

### 1. コードの直し（code-reviewer の指摘・コミット 66721d9d に対して）

一次で裏取りしてから直す（指摘は読んだだけの判断なので、全部が正しいとは限らない）。直したら自己検査に検査と変異を足す（memory「Acceptance self-test」）。

- **HIGH** `aggregate.py` の `contrasts`: config の `["R3","R3-t"]` に対し形の名前は `R3-t(10)` などなので、R3 − R3-t(w) の対比が一度も出ない。w ごとに展開し、事前登録のとおり A3 の差も出す。対が無いときは黙って飛ばさない。自己検査に「config の contrasts が全部出力に現れる」。
- **MEDIUM**（判断 53 で事前登録を直した）`run_main.py` の `negative_control`: 最も強い攻撃者を本計算の点の推定で選ばれた攻撃者に固定する（今は陰性対照の中で選び直している）。攻撃者ごとの値も出す（`cells` は出ている）。
- **MEDIUM** 登録した診断・副次の量の未実装 3 つ: 開いた世界の AUC（N = 1,000・全文。正解を含む候補の最小費用と正解を抜いた候補の最小費用の分けやすさ）／組み立て直しの一致・不一致で分けた正答率（一致の定義は検査 3 の「空白の正規化の後の完全一致」。今の `final_matches_text` は語の並びの一致で、窓の段でしか計算していない）／窓の正解の偏り（正解の窓の位置での A2 の揃えの費用と、記録全体の揃えの費用の分布）。
- **MEDIUM** `aggregate.utility_summary`: 比（中央値・10・90 パーセンタイル）と人の採点との順位相関を課題ごとに出し、4 課題の平均・範囲・区間にそろえる。落ちた数は R0 側と形の側の両方を数える。
- **MEDIUM** `selftest_main.py`: 変異の「killed」を終了コードだけで判定している → 狙った検査名で落ちたことを照合し、traceback は ERROR にする。集計の層（`summarise_cells` の各回の最大・A0 からの上乗せ・`contrasts`・`utility_summary`・本物の `negative_control`）と R4・R7 の窓の切り出しを値で確かめる検査と変異を足す。
- **LOW**: R3-u に表の行としての `A3`（`A3-sum` と `A3-mean` の各回の最大）を合成する／`Cand._codes` を表ごとに鍵づけ／`build_models` の学習の並びを (prompt, writer) で並べる／`need_costs` を B だけにする（今は 500 人全員の費用を親に返し、実データで GB 単位）／ある回で全員 NaN のときの区間と `share_selected`／R0 の削除の連なりが修飾の行で切れる点（検査 7 の前に Table 5 の読み方を確かめる）／R3-u の A3 の和の版が短い候補に有利な点（事前登録どおりだが、合成で偶然の水準を下回らないかを確かめて notes に書く）／A4 の行の置き場。
- 凍結の後なので、コードの直しで事前登録の手順が変わらないかを毎回確かめる。手順に触れる直しは「逸脱」に書く（直す前の結果も出す）。上の直しは、どれも事前登録の文に合わせる方向なので逸脱ではない見込み（判断 53 の 3 つは凍結の前に文を直した）。
- 直したら `code-reviewer`（範囲・禁止・締切を書く）と `/cross-review`（パス限定・`raw/` を入れない）。

### 2. 取得（凍結は済んだので取得してよい）

- **KLiCKe**: 議論文の課題の記録（CSV）・本文・人の採点だけ。人口統計のファイルは取得しない（zip に同梱されていれば展開せず、zip の SHA-256 だけ）。版（取得の日・Drive のファイル ID・各ファイルの SHA-256・GitHub のコミット）を `data.md` と `config.json` の `files` に書く。Drive からの取得は Chrome が要るかもしれない（browser-verification Skill を先に読む）。
- **ENJA15**: 取得の前に、ライセンスの種類と利用条件、T・P・D の意味を [P273] [P359] の本文で確かめる（確かめられなければ ENJA15 の節は行わない）。SVN のリビジョンを固定する。
- **KeyTAR**（Zenodo 17254163・`keytar.zip` 15 GB）: 判断 52 で取得してよい。SHA-256 を記録し、本計算の前に `model_licenses`・`ethics.txt`・`limitations.txt` を読む（合わなければ A4 を行わない）。RTX 5060 Ti に合う PyTorch と CUDA の版を `env.md` に固定する。
- 置き場は `experiments/20261012-public-keystroke-matching/raw/`（git が無視する）。
- `config.json` の `files`・`svn_revision`・`sha256` を埋めるのは、凍結した値の変更ではなく取得の記録なので逸脱ではない（ただし `notes.md` に「取得」として記録する）。

### 3. 取得の後の検査 1〜7

- 事前登録の「取得の後・本計算の前の検査」の 1〜7 だけ。`notes.md` の「データの検査」に書く。
- KLiCKe の読み込み（`load_klicke.py`）を検査 2 の列名で書く。security-checker LOW 2: 例外に行の断片を出さない（書き手の通し番号と例外の型名だけ）・`Move From` の書式が合わない行は除外の理由に回す・処理の前に `pip-audit`。

## 守ること（大事な順）

- **記録と本文の中身を、Claude 自身も読まない。** 取得の後は生の行・本文・抜粋を `cat`・`head`・`Read` で開かない。スクリプトは数・ハッシュ・集計だけを出す。検査 2 の値の一覧は、押したキーの値と `Activity` の値に限る。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ（`raw/` を範囲に入れない）。
- 凍結の後の変更はすべて `notes.md` の「逸脱」に（変える前の結果も残す）。
- 応答は日本語（AskUserQuestion の問いと選択肢も・推奨と理由を添える）。★・⚠️ を多用しない。
- `git add -A`・`git add <dir>` を使わない。ブランチ `docs/public-keystroke-matching-freeze` で続ける。本計算のコードを `experiments/` に入れているので、区切りで PR を出す（計測の run と重ならないか確かめる）。
- 置換のスクリプトは Write で作る（heredoc のバックスラッシュと引用符が壊れる・このセッションで 1 回壊れた）。config を書き換えたら重複キーを検出する形で JSON を読む。
- 状態を変える操作（push・Zenodo・OSF・取得）は出力をファイルに保存して 1 回だけ。
- 論文用のリポジトリに本計算のコードを写すのは、直しとレビューの後（凍結の後のコミットとして）。
- PoPETs は二重盲検。OSF の登録は公開なので、論文での登録の示し方を投稿の段で規程で確かめる。
