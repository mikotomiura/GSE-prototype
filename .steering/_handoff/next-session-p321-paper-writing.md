# 次セッション — 2 本目の論文: [P321] ＋ [P434] 再解析の原稿を書く（EMSE 研究論文）

> ✅ **2026-09-28 に実施済み**（`.steering/20260928-p321-paper-draft/`・全節の初稿と /cross-review 2 巡）。→ 次は `next-session-p321-paper-finalize.md`。
> 作成: 2026-09-28（`.steering/20260928-p321-reanalysis-paper/` の完了時）。
> ⚠️ **このメモを一次資料にしない。** 数値は論文用リポジトリの `results/report.md`、判断は `decisions.md` を開き直す。
> ★ IME 論文（`next-session-ime-paper-issues.md`）とは触るファイルが別なので並行可能。

## §0 打ち込む用

```
.steering/_handoff/next-session-p321-paper-writing.md を読んで、2 本目の論文（[P321] ＋ [P434] の再解析）の原稿執筆を始めてください。
まず /start-task で .steering/<日付>-p321-paper-draft/ を作る。
一次資料: .steering/20260928-p321-reanalysis-paper/decisions.md（判断 1–11）・outline.md（主張 ↔ 根拠・書いてはいけないこと）／
論文用リポジトリ C:/self-resolution-measure（private・GitHub mikotomiura/self-resolution-measure）の results/report.md と NOTES.md／
docs/literature/20260928-self-resolution-measure-positioning.md（位置づけ・判定 go）。
Skill: verify-before-claiming・citation-ssot・reproducibility-discipline（論文用リポジトリの run.sh を触る時）・subagent-delegation。
応答は日本語。コミットは GSE 側は専用ブランチで git add はパス指定（-A 禁止）。原稿は論文用リポジトリに置く。
```

## §1 状態（2026-09-28）

- ★ **投稿先 = Empirical Software Engineering の研究論文**（判断 9）。研究者の条件は「**登壇なし・費用ゼロ**」（判断 8）。
  逐語 "The journal does not charge a submission fee or publication fee."（購読型で出す。OA を選ぶと有料なので**選ばない**）。
  desk reject されたら IST の Short Communications（参考文献込み 2,500 語）へ圧縮する。
- ★ プレプリント（arXiv）は**投稿と同時**（判断 10）。ライセンスはコード Apache-2.0 ／ データ・文書 CC BY 4.0（判断 11・論文用リポジトリに LICENSE 済み）。
- ★ 解析は完了: `bash run.sh`（論文用リポジトリ）exit 0。主な値（⚠️ 原稿には `results/report.md` から取り直す）:
  - D1 [P321]/[P433]: R0 − R0′ = +11.2pt（開発者ブートストラップ 95% [6.8, 15.7]）・参照の定義で +9.0〜+11.2pt（DF1）
  - D2 [P434]: 表だけ +11.8pt（[0.0, 31.2]）・本文の参照を足すと +5.9pt（[0.0, 21.4]）（★ 2 つを並べる。⚠️ D2 の未解決は観察期間内の打ち切りを含む＝「観察終了までに解決も参照も記録されなかった割合」）
  - ⚠️ R0 − R1 は「条件づけの効果」＝ 分子の効果 ＋ 分母だけの効果（D1: +11.24 ＋ (−14.78) ＝ −3.54pt）。「分母の効果」「3 倍」とは書かない（判断 12・13）
  - [P433] の報告値（参照 33% など）は、検討した 4 つの参照の定義のいずれでも同時には再現できない（パッケージは v1 とバイト同一・判断 7 追記）
- ⚠️ **新規性として主張しない**: R0 そのもの（原著が既報）・「参照なし ≠ 自力解決」（[P436]）・成果で条件づけること（[P435]）
- ⚠️ [P434] の転記は LLM（メインと独立 subagent）による → 原稿で AI の利用を開示する。★ 研究者が 17 行を PDF と目で照合すると、人による独立の確認になる（任意）
- ⚠️ ADR-024 D7 の根拠文「分母より分子のほうが 3 倍効く」は誤り（判断 12）→ ADR の次の改訂で訂正する（本論文のタスクでは ADR を触らない）

## §2 次にやること（順番）

0. ✅ **研究者の照合は済んだ**（判断 16・2026-09-28・不一致なし・本文 3 文の読みに同意）。論文用リポジトリ `9c73181` に記録済み。★ 原稿の Methods に「転記は LLM の独立な 2 インスタンスで行い、著者が PDF と照合した」と書く（EMSE の LLM 方針・判断 17）。
1. ★ **EMSE の書式は判断 17 で確認済み**（single-blind＝匿名化不要・要旨 150–250 語・キーワード 4–6・著者名と年の引用・Statements and Declarations と Data availability 必須・LLM の使用は Methods に書く・頁数の上限は見当たらない）。→ **テンプレートを選ぶ**（規程ページの LaTeX マクロ zip〔2021 年版・190 kB〕か Springer Nature の LaTeX テンプレートか。Word も可）。⚠️ zip のダウンロードは研究者の承認を取ってから。⚠️ LaTeX はサブフォルダを使わない（図・bib も同じ階層）
2. **[V178] の本文**（OA）を読む → 妥当性の節の書き方（7 つのガイドライン）。
3. 原稿の骨組み（`outline.md` の構成）→ Results（表 1: R0 / R1 / R0′ / 差 / 区間）から書く。
4. 再現一式の保存先（Zenodo の DOI 付きアーカイブ）と Data availability 節。

## §3 やらないこと

- ⚠️ [P321] / [P434] の値を GSE の期待値として使う（`experiments/20260906-p321-resumption-baseline/notes.md` §4）
- ⚠️ IME 論文と同じ論文に混ぜる
- ⚠️ [P434] の GitHub 補足データ（LICENSE 無し）を使う
- ⚠️ OA オプションを選ぶ（費用が発生する）・登壇が要る場に出す
- ⚠️ 他タスク: IME 論文の判断 8（CHI 2027 Posters）は「登壇なし・費用ゼロ」に当たりうる → IME 論文のタスクに戻るときに見直す（本タスクでは触らない）
