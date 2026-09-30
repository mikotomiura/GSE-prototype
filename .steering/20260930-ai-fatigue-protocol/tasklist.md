# タスクリスト

## 準備
- [x] 引き継ぎ・S-11 と S-09 の見立て・issue（N-05・S-01・S-06・S-07・S-10）・評価プロトコル v1.0・判定基準のシートを読む
- [x] 引き継ぎ §2 の 3 つの論点と N-05 の範囲の論点を聞く（判断 1・2）
- [x] worktree（`C:\wt\ai-fatigue-judge-file`）で origin/main から `docs/ai-fatigue-protocol` を切る
- [x] 方法論の文献の書誌を Crossref で確かめる・GSRR の 65 項目を一次（PMC10514995）で確かめる
- [x] 登録前の段の年表の材料（サブエージェント・読んでいない範囲あり → 次の段で一次で裏取り）
- [x] design.md §2 を試しの検索の前に固定し、コミットする（5d33a7da・23:21）

## 間引き（判断 3〜7 で追加）
- [x] design.md §7（観点・閾値・分け方）を検出の前に固定（5e3b981d・23:33）
- [x] `evidence/dedup.py`・`test_dedup.py`（13 本緑・変異 7 件がすべて赤）
- [x] 書誌 255 件（Crossref・DataCite）→ 組 159 → 姓＋名の頭文字で 45（判断 4）→ メインが抄録で分けた
- [x] 独立の第 2 の読み（Sonnet）と突き合わせ（判断 7）→ `classification_2026-09-30_final.json`
- [x] 内容の群（§7.6・判断 5・6）: 機械の分類 → 不明 52 件と抜き取り 30 件をメインが確かめた（20/30 が正しい）
- [x] `dedup-259.md`（事実）
- [x] 内容の群の全件の確かめ（§7.7・判断 9・10: 独立の読み 3 本・食い違い 98 件の裁定・抜き取り 20 件は誤り 0 → 判定者用ファイルを作り直した 48af51d3…）
- [x] 判定者用ファイルの作り直し（寄せる 5 件を外す・「同じ研究の群」「内容の群」の列・『寄せた記録』シート・`check_judge_xlsx.py`。直前に Downloads の写しの SHA-256 を確かめた・判断 8。内容の群は判定者 1 のファイルだけ＝判定者 2 は研究者の確認待ち）

## 検索式の開発
- [x] ERIC・arXiv・Zenodo の検索の構文を一次で確かめる
- [x] `evidence/search_dev.py` と `test_search_dev.py`（11 本緑・変異 5 件がすべて赤）
- [ ] 種 25 件が各情報源に記録されているかを DOI で確かめる
- [ ] v0 を回す（件数・種の再現）→ 必要なら版を上げる（`evidence/search-dev.md`・判断）

## プロトコル
- [ ] 登録前の段の年表を一次（ノート・コミット時刻）で裏取りして付録 A に書く（間引きも含める）
- [ ] `protocol-ja.md` §0〜§6・付録 B〜E（重複除去の節に §7 の規則）
- [ ] `scripts/check_protocol_here.py`（禁止語・GSRR の 65 項目）

## 理論の文献（S-09）
- [ ] 書誌を Crossref で取る → `evidence/theory_rows.py` で xlsx
- [ ] `scripts/check_theory_rows.py`（変異で赤）→ archive と Downloads

## 検査とレビュー
- [ ] issue-status.md
- [ ] code-reviewer・security-checker（並列）
- [ ] `/cross-review` 2 巡（Codex の当日の実消費を先に確かめる）

## 完了処理
- [ ] 引き継ぎ（次の段: 研究者の確認 → attack-me → 英語の登録版）
- [ ] コミット → push → PR → CI 緑なら merge → main の CI 発火確認
