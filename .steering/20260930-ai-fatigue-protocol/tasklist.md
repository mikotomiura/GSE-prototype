# タスクリスト

## 準備
- [x] 引き継ぎ・S-11 と S-09 の見立て・issue（N-05・S-01・S-06・S-07・S-10）・評価プロトコル v1.0・判定基準のシートを読む
- [x] 引き継ぎ §2 の 3 つの論点と N-05 の範囲の論点を聞く（判断 1・2）
- [x] worktree（`C:\wt\ai-fatigue-judge-file`）で origin/main から `docs/ai-fatigue-protocol` を切る
- [x] 方法論の文献の書誌を Crossref で確かめる・GSRR の 65 項目を一次（PMC10514995）で確かめる
- [x] 登録前の段の年表の材料（サブエージェント・読んでいない範囲あり）
- [x] design.md §2 を試しの検索の前に固定し、コミットする

## 検索式の開発
- [ ] ERIC・arXiv・Zenodo の検索の構文を一次で確かめる
- [ ] `evidence/search_dev.py` と `test_search_dev.py`（陰性対照 → 変異）
- [ ] 種 25 件が各情報源に記録されているかを DOI で確かめる
- [ ] v0 を回す（件数・種の再現）→ 必要なら版を上げる（`evidence/search-dev.md`・判断）

## プロトコル
- [ ] 登録前の段の年表を一次（ノート・コミット時刻）で裏取りして付録 A に書く
- [ ] `protocol-ja.md` §0〜§6・付録 B〜E
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
