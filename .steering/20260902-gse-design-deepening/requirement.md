# 要件定義 — GSE 設計の深掘り（表現チャネル → 身体回帰 → Mh-D 再定義）

- **日付**: 2026-09-02
- **ブランチ**: `docs/mitou-doc-split`（★ `stale-sweep` / `runbook-wall-cleanup` / `research-positioning-fix` を **祖先として含む**ことを実測で確認済み）
- **入口**: `.steering/_handoff/next-session-gse-design-deepening.md`
- **入力**: `.idea/20260901-smartphone-state-externalization-and-physical-return.md`（814 行・GPT との議論記録）

## 背景

`.idea` メモは GPT との大まかな議論の記録であり、**検証済みの設計ではない**。
2026-09-01 のセッションで、同種のサーベイ記録に一次資料照合で誤りが 3 件見つかっている
（主題の取り違え / 筆頭著者の別人 / 数値の誤読）。

## ゴール

1. **B**: `.idea` §9 のサーベイ 5 系統の真偽を一次資料で確認する（DOI を Crossref raw JSON で検算）
2. **A**: §7 の未決事項 8 件を、既存 ADR との衝突を検査したうえで研究者と詰める
3. **C**: §11–15 の Mh-D / ML 段階の再定義を、既存 ADR・glossary との衝突を検査したうえで詰める
4. 確定したものを **ADR-019 以降**に起票する（既存 ADR の本文は書き換えない）
5. `docs/` の SSOT を更新する
6. **最後に**未踏提出資料（`docs/mitou_submission/` 5 本）へ反映する

## スコープ外（やらないこと）

- `src-tauri/` / `src/` のコード変更（★ 本タスクは設計の議論）
- `docs/preregistration-v0.3.md`（凍結文書）
- 過去 ADR（001–018）の本文改訂（★ 追補は新規 ADR で行う）
- `docs/design-history.{md,ja.md}`（履歴文書）
- `.steering/` の過去の記録

## 受け入れ条件

- [ ] `.idea` §9 の各文献に「一次確認済み / 未取得 / 誤り」の判定が付いている
- [ ] `docs/references.md` への append が `[P219]` / `[V89]` から連番で行われている（★ 着手時実測値）
- [ ] A / C の各論点に研究者の判断が記録されている（`decisions.md`）
- [ ] 確定事項が ADR として起票されている
- [ ] `scripts/check_doc_lexicon.py` が提出 5 本すべてで通る
- [ ] 詳細資料の 10 ページ規約を悪化させていない

## 運用メモ

- /reimagine 適用: **No**
- 理由: 本タスクは既存の確定事項（ADR-001〜018）との整合を取りながら未決事項を閉じる作業であり、
  ゼロから代替案を生成する性質ではない。個別論点は `AskUserQuestion` で研究者に選択させる。
