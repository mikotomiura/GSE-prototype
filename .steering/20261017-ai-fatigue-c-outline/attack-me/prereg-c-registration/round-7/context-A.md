# context A（査読者と監査役に渡す）

## 対象物
- stage: prereg（OSF に GSRR の様式で登録する前の、方法論のレビューの登録の下書き）・round 7（登録の凍結の前の最後の査読）
- 登録の先: OSF Registries（GSRR の様式）。投稿先の雑誌は未定。
- 対象: TRACE リポジトリのコミット 059664b の登録版（草稿 0.19・2026-10-20）。
- round 7 は全文を読み、round 6 の版（草稿 0.11）からの差分を重く見る。差分は全体の 4 割を超える（語数 12,751 → 18,082）。
- 0.11 の後に入った主なもの（どこにあるかは差分のファイルで確かめる。ここに書いたことを根拠にしない）:
  1. 確かめの検索と確かめの標本 300 件（GSRR-25〜27・30〜33・39・57 以降）。
  2. 選別の形の作り替え: 判定するのは人 2 人（著者 1・著者 2）。AI は題名と抄録の段の網で、判定しない。段 1 の 2 割の重ね選別と 80%、束とコミット、第一著者だけの除外の監査、合意できない記録（GSRR-33・34・36〜38・41）。
  3. 符号化: 著者 2 が本体の集合を全部符号化する（GSRR-44・47）。
  4. コードブック第 2 版の改訂と反例集（GSRR-43・44・添付）。
  5. C6c・C7 (ii) をデザイン（AI を操作したか）で分け、問題の型を 3 区分にした（GSRR-16・43・56・57）。
  6. 1 つ前の形にあった感度分析 5（2 人の選別を後で行う）は外した。
- 添付 6 の `instructions.md` は 0.11 の時と同じ版（中身は変えていない）。

## 読んでよいファイルの一覧（これだけ）
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-7/diff-0.11-to-0.19.md
  - 差分。登録版 0.11 → 0.19（word-diff・差分の塊 44）。登録版だけ。
- /Users/johnd/TRACE/registration-en.md
  - 対象物の全文。英語・草稿 0.19・18,082 語・GSRR の 65 項目に 1 対 1。
- /Users/johnd/TRACE/registration-attachments/ai-screening/instructions.md
  - 添付 6。AI に渡す指示の本文（1,199 語）。
- /Users/johnd/TRACE/registration-attachments/ai-screening/call.md
  - 添付 6。束を包む文と呼び出しの設定（639 語）。
- /Users/johnd/TRACE/registration-attachments/ai-screening/README.md
  - 添付 6 の説明（559 語）。
- /Users/johnd/TRACE/codebook-c2b-en.md
  - C2b のコードブック第 2 版（1,779 語）。
- /Users/johnd/TRACE/registration-attachments/validation-cases/cases.md
- /Users/johnd/TRACE/registration-attachments/validation-cases/findings.md
- /Users/johnd/TRACE/registration-attachments/validation-cases/key.csv
- /Users/johnd/TRACE/registration-attachments/validation-cases/key-items.csv
  - 反例集（架空の 12 件）・その所見・キー。
- /Users/johnd/TRACE/registration-attachments/query-strings.md
  - 検索式の一覧（添付・14,811 語）。必要な所だけ参照する。
- /Users/johnd/TRACE/registration-attachments/coverage/search-log.json
  - 確かめの検索の件数の記録（記録の題や抄録は含まない）。
- /Users/johnd/TRACE/manuscript/outline.md
  - 原稿の外枠 10 版・登録の添付 5（8,160 語）。範囲の規則・抄録の規則・方法と結果の計画・主張と根拠の表を中心に参照する。
- /Users/johnd/TRACE/manuscript/draft/main.tex
  - 原稿の草稿（4,430 語）。抄録・方法・限界・宣言を中心に参照する。
- /Users/johnd/TRACE/manuscript/draft/tables.tex
  - 表の枠（3,482 語）。
- /Users/johnd/TRACE/manuscript/draft/figure1.tex
  - 図 1（流れ図）。

一覧に無いもの（読まない）: TRACE の脚本（`scripts/`）・AI の出力（`check-34.csv`）・検索の書き出しと記録の一覧（`coverage/*.csv`・各情報源のログ）・候補の一覧（`dryrun/`）・符号化の様式（`coding-form/`）。登録版がこれらを名指していても、中身は確かめられないものとして扱う。

## 規程の一次の抜粋（GSRR の様式の論文）
- 出典: van den Akker, O. R., et al. (2023). Increasing the transparency of systematic reviews: presenting a generalized registration form. *Systematic Reviews*, 12, 170. doi:10.1186/s13643-023-02281-7。
- 照合: round 7 で Europe PMC の全文 XML（PMC10514995）を取り直した（2026-10-20・SHA-256 は round 1 と同じ c8408c10…）。下の 3 つの文が逐語で在ることを確かめた（照合済み）。
- 逐語 1: "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- 逐語 2: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review."
- 逐語 3: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration"
- 規定なし: 分量の上限（取得した範囲の原文に該当の文が無い）。
- 報告の手引き（対象物が名指す）: Murad & Wang 2017・PRISMA 2020・AMSTAR 2（Shea et al., 2017）。本文は渡さない。

## 測った値（wc -w）

| 対象 | 語数 |
|---|---|
| 対象物（登録版 0.19） | 18,082 語。参考文献 12 本。[at registration] の欄 9 か所 |
| 1 つ前の版（0.11） | 12,751 語 |
| 差分のファイル | 15,568 語・差分の塊 44 |
| 外枠 10 版 | 8,160 語 |
| 草稿 main.tex | 4,430 語 |
