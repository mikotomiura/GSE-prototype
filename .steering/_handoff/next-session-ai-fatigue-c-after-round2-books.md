# 引き継ぎ: C（TRACE）—— 共著者の 2 回目の冊を置いた後

作成 2026-10-24（Mac）。`next-session-ai-fatigue-c-after-coauthor-stage1.md` を置き換える（そこの 2.1〜2.3 は判断 88 で済み）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。手順の一次資料は `registration-day.md` の「人 2 人の形」と、道具 `~/TRACE/scripts/c_screening.py` の止まりの文。

## 始め方

研究の物は `~/TRACE`（main は `0376625` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 88 まで）。道具は `~/TRACE/scripts` で `uv run -q --with openpyxl python c_screening.py <命令>`。

## 1. 今の状態（2026-10-24）

- 共著者の段 1 の 2 割: 取り込み済み（`4b1ee45`）。一致は追加候補 94.3%・確かめの標本 100%。両群とも 80% 以上で、段 1 の残りは要らない（`e94fd00`）。
- 戻った冊は Google スプレッドシートを通った `.xlsm` で、『段1』の ID の列が消えていた。リンク先から ID を書き戻した写しで取り込んだ（判断 88）。次に戻る冊でも同じことが起きうる。止まりが「記録が違う」で、extra に `#gid=…` が並んだら、判断 88 の方法（リンク先の『文献DB』の ID で A 列だけを書き戻し、A 列以外の全セルが同じことを確かめ、両方の SHA-256 を記録する）を研究者に確かめてから使う。
- 網 83・混ぜた記録 83（`net1.ids` 166 件）、監査 30（`audit.ids`）、段 2・3 の冊の記録 206（`h1.ids`）をコミット・push 済み。
- 監査の記録の全文: 取れるものはすべて取った。全文の無い 10 件（有料 8・CS09120・R15）は E6 の保留で扱う。
- 2 回目の冊: Drive の `TRACE_Co-Author/TRACE_Co-Author_judge-sheet/` に `TRACE_co-author_stage1_net1.xlsx`（166 件）と `TRACE_co-author_stage2_h1.xlsx`（206 件）を置いた。SHA-256 は判断 88。共有と共著者への連絡は研究者が行う（h1 の全文のリンク先の `TRACE/fulltext` の共有も要る）。

## 2. 次にやること（この順）

### 2.1 第一著者の段 2・3 の束を続ける（h1 が戻る前に済ませる）

- h1 の 206 件のうち、第一著者の段 2 の判定がまだ無いのは、監査の 30 件・共著者だけが段 1 で含めた 2 件・束になっていない端数の 3 件（CS02953・CS04223・CS03205）。`next --stage 2` で束を切る（9 件たまれば切れる）。CS03205 は「保留・E7」で `export-author` が止まるので、そのとき研究者に直してもらう（判断 85）。
- 研究者が『段2・3』で判定 → `export-author --stage 2 --batch bNN` → コミット・push（`scripts/export_stage2.sh` は b01〜b19 専用。照らすのは `scripts/compare_stage2_db.py`）。
- `import-coauthor --stage 2 --book h1` は、冊のすべての記録で第一著者の段 2 の判定がコミット・push されていないと止まる。

### 2.2 共著者の冊が戻ったら

- 戻った冊は開かずに、大きさ・更新時刻・SHA-256 が置いた版から変わったこと、Drive の API と同期フォルダの版が同じことを確かめ、`~/Documents/TRACE/coauthor-returned/` に日付つきで写してから `--file` に渡す。
- 段 1 の追加の冊: `import-coauthor --stage 1 --book net1 --file <写し>` → コミット・push → 束ごとに `export-final --stage 1 --batch bNN`（2 人とも除いて理由が違う記録は、研究者が『最終の除外理由』に書く）→ コミット・push。共著者が net1 で含めた記録は全文段に回るので、3 回目の冊（`coauthor-ids --stage 2 --book h2`）が要る。
- 段 2・3 の冊: `import-coauthor --stage 2 --book h1 --file <写し>` → `differences --stage 2` → 2 人で決めて研究者が『最終』を記入 → `export-final --stage 2` → `differences --stage 3` → 『最終の中心』→ `export-final --stage 3`。

## 3. 守ること

- OSF の登録の下書きや欄を手で直さない。
- 抄録・全文・訳・AI の出力（網の答えを含む）・検索の書き出し・共著者の判定の値を repo や査読者に渡すファイルに写さない。網の答えと共著者の判定の値は開かない。
- 全文の取り寄せでブラウザに見せかける UA を使わない（判断 88 で権限に止められた）。curl は脚本と同じ正直な UA で、ボット対策の無い公開の置き場からだけ。ブラウザでのファイルの保存は研究者の許可を得てから、1 件ごとに新しいタブで。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
- シェルは zsh で、変数を空白で分けない（束の ID のループは bash の脚本か Python で回す）。
