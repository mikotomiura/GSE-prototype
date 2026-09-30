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
- [x] 種 25 件が各情報源に記録されているかを DOI で確かめる（Europe PMC 7・Semantic Scholar 22〜23・arXiv 1・Zenodo 4。ERIC は DOI で引く口が無い）
- [x] v0 を回す（件数・種の再現・雑音の見積もり）。取得の直し（Zenodo・ERIC・Semantic Scholar の種の確かめ・途中で切れた応答）を実行の後に入れた（判断 11）。語の欠けによる落ちは無く、版は上げていない（`evidence/search-dev.md`）

## プロトコル
- [x] 登録前の段の年表を一次（判断の記録の行・コミット時刻）で書いた（付録 A・A0〜A30。サブエージェントの材料は使わず、一次から書き直した）
- [x] `protocol-ja.md` §0〜§7・付録 A〜G（重複除去の節に §7 の規則・AI の予備評価の節・確認待ちの一覧）
- [x] `scripts/check_protocol_here.py`（記録の鍵の行の禁止語・内部の語・GSRR の 65 項目と対応表。違反 0・陰性対照 2 と変異 28 がすべて期待どおり・判断 12）

## 理論の文献（S-09）
- [x] 書誌を Crossref で取る → `evidence/theory_rows.py` で xlsx（23 件・判断 15）
- [x] `scripts/check_theory_rows.py`（違反 0・陰性対照 2 と変異 15 がすべて期待どおり）→ archive と Downloads

## 検査とレビュー
- [x] issue-status.md
- [x] code-reviewer・security-checker（並列・範囲 6bf24b59..189b6159）→ HIGH 1・MEDIUM 4・LOW 15 を一次で確かめて対応（判断 17）
- [ ] `/cross-review` 2 巡（Codex の当日の実消費を先に確かめる）→ 1 巡目済み（計 101,900・判断 18）

## 完了処理
- [ ] 引き継ぎ（次の段: 研究者の確認 → attack-me → 英語の登録版）
- [ ] コミット → push → PR → CI 緑なら merge → main の CI 発火確認
