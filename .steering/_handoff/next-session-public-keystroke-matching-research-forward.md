# 次のセッション: 公開データでの照合の論文 —— 凍結 → 取得 → 検査 → 本計算（11 月末の投稿に向けて）

作成 2026-10-12（判断 51 の後）。投稿の目標は PoPETs 2027 Issue 3（締切 **2026-11-30 AoE**・[V271]）。間に合わなければ Issue 4（2027-02-28）。
この機械は G-GEAR（RTX 5060 Ti 16 GB・A4 の KeyTAR はここで回す）。10/26 の催促は別の引き継ぎ `next-session-public-keystroke-matching-1026-reminder.md`。このメモは前の `next-session-public-keystroke-matching-freeze.md` を置き換える。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-research-forward.md を読んで、公開データでの照合の論文の凍結から本計算までを進めて。
```

## 今の状態（2026-10-12 時点）

- 事前登録は**下書き 8（未凍結）**: `experiments/20261012-public-keystroke-matching/preregistration.md`（日本語・作業の記録）・`preregistration.en.md`（英語・凍結すると正の版）・`config.json`・`SEED`。OSF の各欄の文面は `osf-registration-fields.md`。
- 凍結の前の合成の記録の検査は済み（`scripts/`・`notes.md`・`results/synthetic_check.json`。自己検査と変異 5 つ）。PR #358 で main に入った。
- 判断 51（研究者）: **返事を待たずに、凍結 → 取得 → 構築と検証に進む**。ただし事前登録は「データの取得の前に凍結する」ので、**凍結が取得より先**。返事で利用に懸念が示されたら、計算を止め、データを消し、経緯を報告する。
- 判断の記録: `.steering/20261012-public-keystroke-matching-prereg/decisions.md`（判断 6〜51）。

## 日程の目安

| 時期 | やること |
|---|---|
| 〜10/18 | 1. 凍結の残り → 凍結（研究者が OSF に登録） |
| 〜10/25 | 2. 取得 → 3. 取得の後の検査 1〜7。並行して 4. 本計算のコード（合成の記録で先に書いて確かめる） |
| 〜11/9 | 5. 本計算 → 集計・図表 |
| 〜11/27 | 執筆・attack-me（stage `manuscript`）・`/cross-review`（別の引き継ぎを作る） |
| 11/30 | 投稿 |

## やること

### 1. 凍結の残り（データに触れない）

1. 事前登録に判断 51 を入れる（日英の両方・凍結の前なので逸脱ではない）:
   - 「データ」の KLiCKe の表の「取得の開始条件」→「凍結の後に取得する。著者の返事は待たない（利用条件は [V273] で公開）。返事で利用に懸念が示されたら、計算を止め、取得したデータを消し、その経緯を報告する」。`config.json` の `datasets.klicke.acquisition_condition` も合わせる。
   - 「未決」の KLiCKe の返事の行を、上と同じ扱いに書き換える（「凍結の前に閉じる」から外す）。
2. [V281] Menlo Report と [V282] Kerckhoffs を一次で確かめる（無料の原本を取得し、書誌を照合）。`docs/references.md` の状態を active にし、英語の版の References を直す。取れなければ provisional のまま、引用を外すかを研究者に問う。
3. 英語の版と日本語の版の食い違いを確かめる（下書き 8 から変えたところを両方に入れる）。
4. 論文用の git リポジトリの中身を手元で組む（private・GSE への言及なし）:
   - `preregistration.md`（英語の版）・`config.json`・`SEED`・`scripts/align.py`（型の写し・SHA-256 `6c03dc66…`）・`scripts/align_ext.py`・合成の記録の検査の `scripts/`・`results/synthetic_check.json`・ENJA15 の換算表 `romaji_table.py`（SHA-256 は config）。
   - `config.json` に残る GSE の中の参照を直す: `_note` の `.steering/` の文・`romaji_table.py` の `experiments/...` のパス・`alignment.implementation` の `experiments/20261011-g1-copy-self-trial/scripts`。英語の版の本文が参照する `scripts/align.py` と合わせる。
   - 写した後に自己検査（`selftest_synthetic.py`）がそのリポジトリで通ることを確かめる。
5. リポジトリを作る（`gh repo create --private`）。新しいリポジトリへの push は自動モードで止められる（memory）ので、最初の push は研究者に `!` で頼む。
6. 各ファイルの SHA-256 を `osf-registration-fields.md` の「Other」に入れ、研究者が OSF に登録する（Claude はログインしない）。
7. 日英の状態の行を「凍結: <日時>・コミット <sha>・OSF の DOI <doi>」に書き換えてコミットする。以後の変更は「逸脱」。

### 2. 取得（凍結の後）

- **KLiCKe**: 議論文の課題の記録（CSV）・本文・人の採点だけ。人口統計のファイルは取得しない（zip に同梱されていれば展開せず、zip の SHA-256 だけ）。版（取得の日・Drive のファイル ID・各ファイルの SHA-256・GitHub のコミット）を `data.md` と `config.json` に書く。
- **ENJA15**: 取得の前に、ライセンスの種類と利用条件を一次で確かめる（判断 5・7）。T・P・D の意味を [P273] [P359] の本文で確かめる（確かめられなければ ENJA15 の節は行わない）。SVN のリビジョンを固定して `data.md` に書く。
- **KeyTAR**（Zenodo 17254163・`keytar.zip` 15 GB）: **取得の前に研究者に確かめる**（判断 10 の細部「取得の前に研究者に確かめる」・まだ確かめていない）。取得したら SHA-256 を記録し、本計算の前に `model_licenses` と `ethics.txt` を読む（合わなければ A4 は行わない）。RTX 5060 Ti は新しい世代の GPU なので、それに対応した PyTorch と CUDA の版が要る（版は `env.md` に固定）。
- 置き場所は `experiments/20261012-public-keystroke-matching/raw/`（git が無視する・`.gitignore` の `experiments/**/raw/`）。

### 3. 取得の後・本計算の前の検査 1〜7

- 事前登録の「取得の後・本計算の前の検査」の 1〜7 だけを行い、`notes.md` の「データの検査」に書く。ここに無い量は計算しない。
- 検査 2 には、合成の記録の検査の仮定を確かめる数（`down_event` と `up_event` が違う行・`text_change` に " => " が 2 つ以上・`NoChange` の Paste・「Control の次の 1 押下」が外れる数・修飾の `action_time` が 0 でない行・Leftclick の `activity`）が入っている。
- 値を見て手順を変えない。列名や値が想定と違い手順を直すときは逸脱に書く（直す前の結果も出す）。

### 4. 本計算のコード（データの前に、合成の記録で書いて確かめる）

- 加工（R0〜R7・R3-u・R3-t・R4・R5・R6）は `scripts/synthetic_logs.py` の形を本物の列に合わせて使い回す。攻撃者 A0・A1・A1'・A2・A2-b・A3・A4、有用性の 10 指標、候補の抽選、窓、ブートストラップ、陰性対照、ENJA15 の節を、事前登録と `config.json` のとおりに書く。
- 合成の記録で先に通す（memory「Acceptance self-test」: 通して緑でも足りない。判定式が常に真・経路に未到達などを変異で潰す）。
- 環境を固定する: Python 3.11.9・numpy 2.2.6・scikit-learn 1.5.2（`config.json` の `tools`）を venv で入れ、`requirements.txt` と `env.md` に書く。`run.sh` で 1 コマンドで再現できるようにする（reproducibility-discipline）。

### 5. 本計算

- 事前登録のとおりに回し、集計だけを `results/` に置く。個々の書き手の結果・本文と記録の抜粋は出さない。
- 返事で懸念が示されたら、ここで止める（判断 51）。

## 守ること（大事な順）

- **記録と本文の中身を、Claude 自身も読まない**。事前登録は「記録と本文は AI に送らない」と定めている（「記録の扱い」「AI の使用」）。取得の後は、生の行・本文・抜粋を `cat`・`head`・`Read` で開かない。スクリプトは数・ハッシュ・集計だけを出力する形にし、エラーの表示にも本文や行の中身を出さない。列名と値の種類の一覧（検査 2）は、押したキーの値と `Activity` の値に限る（本文の文字列は出さない）。
- 打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。Codex に渡すのはコードと文書の差分だけ（`scripts/run-codex-review.sh` をパス限定で。`raw/` を範囲に入れない）。
- 凍結の前にデータを取得しない。凍結の後の変更はすべて `notes.md` の「逸脱」に書く。
- 応答は日本語（AskUserQuestion の問い・選択肢も日本語・推奨と理由を添える）。★・⚠️ を多用しない。
- docs を先に読む。必須 Skill（`reproducibility-discipline`・`citation-ssot`・`verify-before-claiming`・`subagent-delegation`・`data-privacy`）を参照してから手を動かす。
- 有料の DB と有料の本文は使わない。
- `git add -A` や `git add <dir>` を使わず、ファイルを明示してステージする。並行セッションがあるので worktree で作業する（`C:\GSE-wt-matching-prereg` を origin/main から新しいブランチで切り直す）。
- Codex の予算は、回す前に origin/main の台帳も見る。
- 公開する英語の成果物は学術的な英語・GSE への言及なし・記号や口語なし。
- 置換のスクリプトは Write で作る（heredoc のバックスラッシュが壊れる）。config を書き換えたら、重複キーを検出する形で JSON を読む。
- 状態を変える操作（リポジトリの作成・push・Zenodo・OSF）は出力をファイルに保存して 1 回だけ。
