# 単位 d-2: research-positioning に理論を問いとして入れ、受容の扱いと古い記述を一次へ戻す

> 親タスク: `.steering/20260919-theory-ssot-promotion/`（段 3）。引き継ぎ §2 の単位 **d** のうち、J-1 と S1 / S2 / DN、§5 H-PA / §8（J-15）、SSOT の古い記述 8 件。⚠️ §4 の差分は体系的レビュー（SR）の後（単位 d-3）。

## 背景

- 研究者判断 J-1（前段 判断 1 #1）: 理論は RP §1 の問い（framing）に theory candidate・EH0 として入れる。確証主張は L0 のまま、headline は変えない。
- J-15（同 #11）: 受容率を成功指標にしない（choice symmetry）。RP §5 H-PA・§8 が改訂候補。
- 還元案 `positioning-reduction-draft.md`: S1 / S2 / DN は J-1 と同じコミットで §3 へ。
- `ssot-collision-findings.md`「参考: SSOT 側が古い」8 件（うち 6 件は未検算）→ 一次で確かめてから戻す（memory「Stale doc: revert to primary」）。

## ゴール

- RP §1 に理論の問いを足す（EH0・書いてはいけないこと・既決との対応表）。
- RP §3 に S1（返権の負荷の先行）・S2（非支配と関係的自律）・DN（粒度の違い）を足す。
- RP §5 H-PA / §8 で受容を記述へ移す（ADR-033 D5）。
- 古い記述 8 件を一次で確かめて戻す（ADR 本文は書き換えず README に注記）。

## スコープ

### 含むもの
- `docs/research-positioning.md`・`docs/glossary.md`（(7) 再離席）・`docs/adr/README.md`（(6) ADR-032・(8) ADR-018 の注記）

### 含まないもの
- ⚠️ §4 の差分（SR の後）・事前登録（凍結）・ADR 本文

## 受け入れ条件

- [ ] headline と確証核（L0）を変えていない
- [ ] 理論・返権の負荷逆説・二重台帳を「新しい」と書いていない
- [ ] 古い記述 8 件を 1 件ずつ一次で確かめている（`decisions.md` に記録）
- [ ] `check_citations.py` / `check_doc_lexicon.py` 違反なし
- [ ] `/cross-review` 2 巡

## 関連ドキュメント

- `.steering/20260918-theory-critical-review/`（`decisions.md` 判断 1 / 2・`positioning-reduction-draft.md`・`ssot-collision-findings.md` X-09 / X-12〜X-16・「参考」節）
- `docs/literature/20260919-authority-return-burden-precedents.md`・`…-non-domination-and-autonomy-norms.md`・`…-digital-nature-primary-scope.md`
- `docs/adr/ADR-019` D3・`ADR-023` D1〜D3 / D11-a / D12・`ADR-024` D1 / D2 / D4・`ADR-025`・`ADR-029`・`ADR-031`・`ADR-033`

## 運用メモ

- /reimagine 適用: **No**
- 理由: 中身は研究者判断（J-1 / J-15）と還元案で決まっている
