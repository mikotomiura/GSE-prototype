# 停滞の定義の候補 C1・C2・C6 を O1 の記録から作って記述する（＋同意文書の改訂案の検討）

## 背景

公開データと O1 の統合（`.steering/20261102-gse-synthesis-redesign/`）で、ADR-030 の停滞（C0 = 文字の正味の産出の止まり）がデスクワーク全体に合わないことが分かり、候補 C0〜C6 を並べた（synthesis §4）。判断 4〜6 で、ADR-031 を Accepted に向けるのを主にし、並行して C1（活動の止まり）・C2（前進なき活動）を主の対、C6（打鍵の空回り）を副として、O1 の見た 14 日から作って記述すると決めた。引き継ぎは `.steering/_handoff/next-session-gse-c1c2c6.md`。

## ゴール

1. C1・C2・C6 の条件の文を記録を開く前にコミットし、陽性対照を通してから 14 日で計算し、`notes.md` に記述だけを書く。
2. 同意文書の改訂案（`.steering/20260913-esm-audit-criterion-gate/consent-revision-proposal.md`）を 9-14 以降の変化と照らし、§4 の論点を研究者に 1 問ずつ聞く。承認されたら (a)〜(f) を別タスクの引き継ぎに書く。

## スコープ

### 含むもの
- `experiments/20261103-stall-candidates-c1c2c6/`（条件・コード・陽性対照・集計・notes）
- 同意文書の改訂案の照合と論点の聞き取り、承認後の引き継ぎ

### 含まないもの
- 11-01 08:30 開始の本とそれ以降の記録（H4a・H5 の確認に残す）
- 検定・判定の閾値・候補の選択・新しい定義の確定（ADR）
- C1・C2・C6 を実行時の契機に使うこと（ADR-014 D4b・ADR-013 D6）
- 同意文書の本文の確定・M5 の配線

## 受け入れ条件

- [ ] 条件の文と陽性対照つきのコードが、計算より前のコミットにある
- [ ] 陽性対照と変異の確かめが通り、K2 の自己検査（C0 の一致）が通る
- [ ] `notes.md` に記述だけ（検定なし・判定なし・詰まりと書かない）
- [ ] code-reviewer と /cross-review（Codex には条件の文とコードだけ）
- [ ] 同意文書の論点を AskUserQuestion で聞き、結果を decisions.md に書く

## 関連ドキュメント

- `.steering/20261102-gse-synthesis-redesign/synthesis.md` §3〜§4・`decisions.md` 判断 4〜6
- `experiments/20261102-stall-decomposition/`（中間と道具）
- `docs/adr/` ADR-030（D3・D4）・ADR-031

## 運用メモ
- /reimagine 適用: No
- 理由: 定義の形は synthesis §4 と判断 5・6 で決まっており、分かれ目は grill（判断 1〜4）で研究者が選んだ。解析だけでコードの設計判断を伴わない。
