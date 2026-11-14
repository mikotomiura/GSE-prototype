# 設計 —— ADR-052

## アプローチ

grill の判断 1〜9 を ADR-052 の D1〜D9 に写し、各 D の根拠を一次資料に降ろす。ADR-043・ADR-051・ADR-039 の本文は書き換えず、「上書きの範囲」の表と README の注記で読み替える（ADR-043 の作法と同じ）。

## 変更対象

| ファイル | 変更 |
|---|---|
| `docs/adr/ADR-052-stage1-pre-adoption-confirmatory-n3.md` | 新規 |
| `docs/adr/README.md` | 一覧に 1 行・ADR-031/032/039/043/051 の行に注記 |
| `docs/preregistration-stage1.md` | §0・S1-G1・S1-G2 に ADR-052 への参照（値は埋めない） |
| `docs/glossary.md` | 「採択前の確認の群 / 採択後の再現の群」（済み） |

## ADR-052 の骨格

- Context: 研究者の方針（2026-11-14）・ADR-043 D3/D8・ADR-039 D1 と 10-12 の注・ADR-014 判断 3・ADR-051 D1
- D1 採択前の n=3 を事前登録つきの確認とし、採択後の審査済みの群を直接の再現にする（判断 1・3）
- D2 審査なしの根拠: ADR-014 判断 3 の 4 根拠を段 1 の構成に当て直す表（判断 1）
- D3 ADR-039 D1 の範囲を 2 本目の論文に限ると読む（判断 1）
- D4 本人の段 1 から n=3 へ進む 4 つの関門（判断 4）と、集計の出力だけを見る手順（判断 5）
- D5 両 OS で募り、Windows 版の手跡が通るまで始めない（判断 6）・通ったとする範囲（判断 7）
- D6 同意に入れるもの: 参加・問い・手跡の後期・個人ごとの集計値と図の公表（判断 8）
- D7 ADR-031・ADR-032 は n=3 の同意文書の承認で Accepted（判断 9）
- 上書きの範囲・Alternatives（grill で退けた案）・Consequences・Migration（引き継ぎ 2〜4）

## 確かめ方

- 根拠の行番号は origin/main の版で引く。ADR 本文の不変は `git diff --stat origin/main -- docs/adr/ADR-0{14,31,32,39,43,51}*` が空であること。
- /cross-review（code-reviewer＋Codex）。送る diff は docs だけで、記録の本文を含まない。
