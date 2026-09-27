# 次セッション — 2 本目の論文: [P321] ＋ [P434] 再解析の原稿を書く（EMSE 研究論文）

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
  - D1 [P321]/[P433]: R0 − R0′ = +11.2pt（開発者ブートストラップ 95% [6.8, 15.7]）・参照の定義で +9.0〜+11.2pt
  - D2 [P434]: +11.8pt（[0.0, 31.2]）・本文の参照を足すと +5.9pt
  - [P433] の報告値（参照 33% など）は公開データから単一規則では再現できない（パッケージは v1 とバイト同一）
- ⚠️ **新規性として主張しない**: R0 そのもの（原著が既報）・「参照なし ≠ 自力解決」（[P436]）・成果で条件づけること（[P435]）

## §2 次にやること（順番）

1. **EMSE の査読方式**（single / double-anonymous）と、プレプリント・再現一式の扱いを公式ページで一次確認（⚠️ 出版社のページは curl / WebFetch が 403 → 実ブラウザで）。
2. **[V178] の本文**（OA）を読む → 妥当性の節の書き方（7 つのガイドライン）。
3. 原稿の骨組み（`outline.md` の構成）→ Results（表 1: R0 / R1 / R0′ / 差 / 区間）から書く。
4. 再現一式の保存先（Zenodo の DOI 付きアーカイブ）と Data availability 節。

## §3 やらないこと

- ⚠️ [P321] / [P434] の値を GSE の期待値として使う（`experiments/20260906-p321-resumption-baseline/notes.md` §4）
- ⚠️ IME 論文と同じ論文に混ぜる
- ⚠️ [P434] の GitHub 補足データ（LICENSE 無し）を使う
- ⚠️ OA オプションを選ぶ（費用が発生する）・登壇が要る場に出す
- ⚠️ 他タスク: IME 論文の判断 8（CHI 2027 Posters）は「登壇なし・費用ゼロ」に当たりうる → IME 論文のタスクに戻るときに見直す（本タスクでは触らない）
