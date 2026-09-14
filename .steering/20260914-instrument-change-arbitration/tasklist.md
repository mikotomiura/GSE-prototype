# タスクリスト

## 準備
- [x] ハンドオフ `next-session-mhd-instrument-change-arbitration.md` を読む（★ ただし**一次にしない**）
- [x] `verify-before-claiming` / `citation-ssot` Skill を参照
- [x] ★ `.idea/…survey.md`（**551 行**）を**全文**読む（⚠️ ルール 7）
- [x] ★ `.idea/…criterion.md`（**349 行**）を**全文**読む
- [x] `ADR-030 D10 / D11` / `ADR-014 判断 6・D4 禁止表` / `ADR-009 D2` / `ADR-031` を読む
- [x] `data-privacy` ルール 7 / 判断 12 / 起票 6・16・17・18 を読む
- [x] ★ **一次（コード）で実測**: `hook_windows.rs` / `hook_macos.rs` / `schema_dto.rs` /
      `anonymize.rs` / `observe_windows.rs` / `lib.rs` / `consent-draft-o1.md`
- [x] ★ ベースライン取得（`check_citations` 緑 / `check_doc_lexicon` 緑 / o1 readiness **19 / 2**）

## 裁定
- [x] ★ **① / ② / ⑤ を研究者に問う**（3 択 × 3・⚠️ §5 Stop Condition）
- [x] ★ `docs/adr/ADR-032-instrument-change-arbitration.md` を書く（① 〜 ⑦）
- [x] ⚠️ 各項目に「**解く / 解かない**」→「**破れる約束 / 測れなくなるもの**」の順で書く
- [x] ★ 引用（`[Pn]` / `[Vn]`）を付ける（⚠️ **既存 active のみ**・append しない）
- [x] ★ `ADR-031 §Migration` に **M9** を足す（⚠️ 本文の *決定* は書き換えない）
- [x] ★ `docs/adr/README.md` に索引行を足す
- [x] ★ `data-privacy` **ルール 1** に D2 の 9 条件を明文化（★ ADR-032 M3・⚠️ 自己点検で見つけた穴）

## 検証
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` → ★ **違反なし**（初回から緑）
- [x] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` → ★ **違反なし**（⚠️ ADR は検査対象外なので自分で `glossary` を確認した）
- [x] `git diff --stat` で **`src-tauri/` が 0 行**（AC 6）—— ★ `git status -- src-tauri/` が空
- [x] `bash scripts/check-o1-release-readiness.sh` が **19 / 2** のまま（★ 着手前と同じ）

## レビュー
- [x] `code-reviewer` ＋ `security-checker` を**並列**起動（★ HIGH 9 / MEDIUM 10 / LOW 8）
- [x] HIGH を消化（★ **7 か所で裁定を狭めた** —— `decisions.md` 判断 7）
- [x] ⚠️ レビューの主張 1 件を**一次で確認して訂正**（★ 判断 8 —— 「既に破れている」は**未配布ドラフトの話**だった）
- [x] ★ **自分の実測発見を起票**（★ 起票 19 / 20）
- [ ] `/cross-review` を**パス限定**で（⚠️ `docs/mitou_submission/**` を送らない）
- [ ] 2 巡目（★ 自分が足した規則の境界条件）

## 完了処理
- [x] `requirement.md` / `design.md` / `decisions.md` を作る
- [ ] `decisions.md` の最終化（★ レビューで出た判断を追記）
- [ ] `git commit`（⚠️ `git add -A` を使わない・**明示的に staging**）
- [ ] 次セッションの引き継ぎを `.steering/_handoff/` に作る
