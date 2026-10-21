# 引き継ぎ: C（TRACE）—— 共著者の段 1 の冊が戻った後

作成 2026-10-21（Mac）。`next-session-ai-fatigue-c-stage2.md` を置き換える（そこの 2.1・2.2 は判断 84〜86 で済み、2.3 をここで詳しくした）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。手順の一次資料は `registration-day.md` の「人 2 人の形」（段 1 の 2〜6、段 2・3 の 1〜7）と、道具 `~/TRACE/scripts/c_screening.py` の止まりの文。

## 始め方

研究の物は `~/TRACE`（main は `e91b2e6` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 86 まで）。道具は `~/TRACE/scripts` で `uv run -q --with openpyxl python c_screening.py <命令>`（この Mac の素の `python3` には openpyxl が無い）。

## 1. 今の状態（2026-10-21）

- 第一著者の段 1: 564 件（63 束）すべて書き出して push、網も 63 束すべて済み（判断 80・81）。含める 174・除外 390。
- 第一著者の段 2・3: b01〜b19（171 件）を書き出して push（判断 86）。含める 87・保留 56（E6 38）・除外 28。`export-final --stage 2` はまだ（共著者の段 2・3 の判定が要る）。
- 段 2 の端数 3 件（CS02953・CS04223・CS03205）は束になっていない。研究者は DB に判定を入れてあり、残すと決めた（判断 85）。CS03205 は「保留・E7」で、保留に付けられるのは E6 か理由なしなので、束になったときに `export-author` が止まる。そのとき研究者に直してもらう。
- 共著者の段 1 の冊: Drive の `AI-fatigue/TRACE/TRACE_Co-Author/TRACE_Co-Author_judge-sheet/TRACE_co-author_stage1.xlsx`（113 件・2026-10-19 に `--hold` で作った冊を、判断 76 でそのまま使うと決めた）。配った時点の版は 2026-10-19 13:34:59・228,317 バイト・SHA-256 `0aae57a0…`。案内（`coauthor-guide.md`）は「ファイル名を変えずに、このフォルダに戻してください」と頼んでいるので、戻った冊はこの同じ場所を上書きする。
- TRACE の `screening/coauthor/` はまだ無い（共著者の冊を 1 つも取り込んでいない）。

## 2. 次にやること（この順）

### 2.1 戻った冊を確かめる（中身は開かない）

- 研究者に、共著者から戻ったと連絡があったか、置き場所が上の場所かを聞く。
- 冊の大きさ・更新時刻・SHA-256 が配った版から変わったこと、Drive の API（`get_file_metadata`）の更新時刻と、この Mac の同期フォルダの版が同じことを確かめる。降りる前に読むと配った版のままに見える（判断 80・81 と同じ型）。
- 研究者は取り込むまで冊を開かない。メインも判定の値を読まない（取り込みの道具だけが読む）。冊はまず `~/Documents/TRACE/` に日付つきで写し、写しを `--file` に渡す（取り込みの後に Drive の冊が書き換わっても、取り込んだ物が残るように）。

### 2.2 段 1 の 2 割を取り込み、一致を出す（`registration-day.md` 人 2 人の形・段 1 の 2〜3）

1. `import-coauthor --stage 1 --book sample --file <写した冊>` → `screening/coauthor/` の出た物を名指しで add・コミット・push。止まったら、止まりの文に従う（冊の記録が 113 件と違う、選び肢の外の値、など。第一著者の段 1 は全部 push 済みなので、その止まりは出ないはず）。
2. `coauthor-agreement` → `coauthor/sample-agreement.csv` をコミット・push。追加候補 53 件と確かめの標本 60 件を、群ごとに別々に 80% と照らす。80% に届かなかった群は、その群の段 1 の残りの全部を共著者に頼むことになる。結果（群ごとの一致・kappa・80% に届いたか）を研究者に伝える。

### 2.3 網・混ぜる記録・監査を抜いて、2 回目の冊を作る（段 1 の 4、段 2・3 の 3）

1. `coauthor-ids --stage 1 --book net1` → `coauthor/net1.ids`・`coauthor/mix.ids`・`coauthor/audit.ids` をコミット・push。80% に届いた群は網の記録と同じ数（最低 5・seed 20261026）の未判定の記録を混ぜる。届かなかった群は網ではなく残りの全部。監査は、届いた群で第一著者だけで除いた記録から 30 件（seed 20261024）。
2. 監査の記録は全文の段に回る記録として扱われ、第一著者の段 2・3 の束に印なしで入る。確かめの標本の記録が当たったら、全文を取り寄せる（`scripts/fetch_fulltext.py` → ブラウザ・判断 82・83 と同じ手順 → `update_trace_db.py` で DB を作り直す。Excel が閉じていることを確かめてから）。
3. `make_coauthor_db.py --stage 1 --book net1 --ids ../screening/coauthor/net1.ids --out <置き場所>` で段 1 の追加の冊を作る。
4. 段 2・3 の冊: `coauthor-ids --stage 2 --book h1` → `coauthor/h1.ids` をコミット → `make_coauthor_db.py --stage 2 --book h1 --ids ../screening/coauthor/h1.ids --out <置き場所>`。全文の無い監査の記録は警告で出るので、全文を取り寄せてから冊を作る。
5. 案内の流れの表では、2 回目は「AI が拾い直した記録の段 1 と、全文の段」を同時に渡す。冊を Drive の `TRACE_Co-Author/TRACE_Co-Author_judge-sheet/` に置く前に、冊の名前・置き場所・案内の文を変えるかを研究者に聞く（共著者に見せる文には、ルールの明示と日付を書かない）。

### 2.4 第一著者の段 2・3 の束を続ける

- 監査の記録と、共著者の段 1 で含められた記録が全文の段に回ると、`next --stage 2` が端数の 3 件と合わせて新しい束を切る（9 件たまれば切れる）。研究者が『段2・3』で判定 → `scripts/export_stage2.sh` は b01〜b19 専用なので、束の番号を合わせて同じ形で回す（照らすのは `scripts/compare_stage2_db.py`。束の一覧のファイルを新しく作って渡す）→ コミット・push。
- `import-coauthor --stage 2 --book h1` は、冊のすべての記録（監査の記録も）で第一著者の段 2 の判定がコミット・push されていないと止まる。h1 が戻る前に、第一著者の束を済ませておく。

### 2.5 共著者の冊が戻ったら（3 回目以降・ここでは手順だけ）

- 段 1 の追加の冊: `import-coauthor --stage 1 --book net1 --file <戻った冊>` → コミット・push → 束ごとに `export-final --stage 1 --batch bNN`（2 人とも除いて理由が違う記録は、2 人で決めた理由を研究者が『最終の除外理由』に書く）→ コミット・push。
- 段 2・3 の冊: `import-coauthor --stage 2 --book h1` → `differences --stage 2` → 2 人で決めて研究者が『最終』を記入 → `export-final --stage 2` → `differences --stage 3` → 『最終の中心』→ `export-final --stage 3`。E5 の 2 件（S04-21→S04-28・CS05713→S04-17）は、研究者が『同じ標本の相手（E5）』を判定の時に入れてある（判断 86）。

## 3. 守ること

- OSF の登録の下書きや欄を手で直さない。
- 抄録・全文・訳・AI の出力（網の答えを含む）・検索の書き出し・共著者の判定の値を repo や査読者に渡すファイルに写さない。網の答えは開かない。
- Codex が DB に入力したときは、Drive の DB 本体に保存されたことと同期フォルダに降りてきたことを確かめてから、判断 84 の照合（`compare_stage2_db.py`）で違いが判定の欄だけかを見る。全文の段では、読んだ範囲と E6 の決まり（無料の全文が無ければ保留・E6、判断 85・86）も数える。道具はどちらも止めない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
- シェルは zsh で、変数を空白で分けない（束の ID のループは bash の脚本か Python で回す・判断 82）。
