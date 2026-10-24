# 引き継ぎ: C（TRACE）—— 第一著者の段 2・3 の残り（共著者に net1・h1 を渡している間）

作成 2026-10-24（Mac）。前提は判断 88（共著者の 2 割の取り込み・一致・2 回目の冊を置いた）。共著者が net1・h1 を返した後の手順は、別の引き継ぎ `next-session-ai-fatigue-c-after-net1-h1-return.md` にある（この引き継ぎが済んだことを前提に書いてある）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 引き継ぎの文を一次資料の代わりにしない。手順の一次資料は `registration-day.md` の「人 2 人の形」の「段 2・3」の 1〜2 と、道具 `~/TRACE/scripts/c_screening.py` の止まりの文。

## 始め方

研究の物は `~/TRACE`（main は `0376625` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 88 まで）。道具は `~/TRACE/scripts` で `uv run -q --with openpyxl python c_screening.py <命令>`（この Mac の素の `python3` には openpyxl が無い）。始める前に `git -C ~/TRACE status` で main が origin と同じかを見る。

## 1. 今の状態

- 第一著者の段 2・3 は b01〜b19（171 件）が書き出し済み（判断 86）。
- 全文の段に回っていて、第一著者の段 2 の判定がまだ無い記録は 35 件: 監査の 30 件（`screening/coauthor/audit.ids`）、共著者だけが段 1 で含めた 2 件、束になっていない端数の 3 件（CS02953・CS04223・CS03205）。35 件はすべて h1 の冊に入っている。
- 監査の 30 件の全文は判断 88 で取れるものをすべて取った。全文の無い 10 件（CS06058・CS08421・CS06394・CS08944・CS06384・CS09120・CS05115・CS02828・CS00978・R15）は、取り寄せを試して無料の版が無かった記録で、E6 の保留にする（判断 85・86 の決まり）。
- DB（Drive の `TRACE/TRACE_database.xlsx`）は判断 88 で作り直してあり、35 件の行は『段2・3』にある。

## 2. やること（この順）

### 2.1 束を切る

1. `next --stage 2` を 3 回 → b20・b21・b22（9 件ずつ・27 件）。束の記録の順は道具が決める。
2. 4 回目は「8 records ready for stage 2; cut a smaller batch with --short only when no more are coming …」で止まるはず。ここで `--short` を使わない。共著者の net1 が戻ると、共著者だけが含めた記録が増えて、この 8 件と束になる（引き継ぎ `after-net1-h1-return` の 2.3）。止まりの数が 8 でなければ、数え直してから研究者に伝える。
3. `screening/batches.csv` を名指しで add・コミット・push。
4. 束ごとの ID と全文の有無を `~/Documents/TRACE/段2の束-<日付>.txt` に書く（前の回の `段2の束-20261021.txt` と同じ形）。全文の有無は Python で数える（zsh のループは変数を空白で分けない・判断 82）。CS03205 が b20〜b22 に入ったかも書く。

### 2.2 研究者が判定する

- 判定の前に DB の控えを取る: `~/Documents/TRACE/TRACE_database.段2判定前-<日付>.xlsx`。Excel が閉じていることを確かめてから写す。
- 研究者が『段2・3』の束の行に、判定・除外理由・中心・読んだ範囲・根拠メモを入れる。含める記録には中心も付ける。全文が無ければ保留＋E6（読んだ範囲は抄録か題名のみ）。
- CS03205 は今「保留・E7」で、保留に付けられるのは E6 か理由なし。束に入ったら、研究者に直してもらう（判断 85）。
- Codex が DB に入力したときは、Drive の DB に保存されたことと、同期フォルダに降りてきたことを確かめてから読む（降りる前に読むと未判定に見える・判断 80・81）。Drive の API（`get_file_metadata`）の更新時刻と大きさを、同期フォルダの版と比べる。

### 2.3 照らして書き出す

1. 照合: `uv run -q --with openpyxl python -I .steering/20261017-ai-fatigue-c-outline/scripts/compare_stage2_db.py <控え> <今の DB> <段2の束.txt>`。違いが『段2・3』の束の行の判定の欄だけかを見る。値は出ない。束の外の違いがあれば、研究者に確かめる。全文の段では、読んだ範囲と E6 の決まりも数える（道具は止めない）。
2. 書き出し: `bash .steering/20261017-ai-fatigue-c-outline/scripts/export_stage2.sh b20 b21 b22`（束ごとに `export-author --stage 2` → CSV を名指しで add・コミット）。止まったら止まりの文に従う（E7 の保留など）。研究者に直してもらったら、控えを取り直してから照らし直す。
3. `git -C ~/TRACE push`。CSV の段 2 の行の数が DB の判定の数と一致することを確かめる。
4. 記録: 判断 89 として、束・判定の数（含める・保留（E6 と理由なし）・除外と理由）・照合の結果・端数の 8 件が待っていることを書く。worktree のブランチにコミット・push（名指しで add）。

## 3. この回でやらないこと

- 端数の 8 件の束（`--short`）。net1 の取り込みの後に切る。
- `import-coauthor --stage 2 --book h1`。206 件すべてで第一著者の段 2 の判定が要るので、端数の 8 件が済むまで止まる。
- 共著者の冊の中身を開くこと（戻っていても）。

## 4. 守ること

- OSF の登録の下書きや欄を手で直さない。
- 抄録・全文・訳・AI の出力（網の答えを含む）・検索の書き出し・共著者の判定の値を repo や査読者に渡すファイルに写さない。網の答えと共著者の判定の値は開かない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
