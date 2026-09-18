# 草案の引用文献 × `docs/references.md` 照合（2026-09-18）

> サブエージェント（Sonnet・読み取り専用）の照合結果をメインが要約した。⚠️ 推測で番号を埋めていない（Grep 実地照合のみ）。
> 対象: B §6.3 / §15、A §5、C §15、D の `core-cs` §15・`core-art` §15・`bridge-dn` §5・`measurement-dictionary` §13・`gr-h4…` §4.5。

## 集計

| 区分 | 件数 | 中身 |
|---|---|---|
| 登録済み・書誌一致 | 15 | [P361]〜[P367]（AI 疲労系 7）/ [P127]=[V37] Buçinca / [P183] Sengers / [P45] Gaver / [P261] Pousman / [P249] Mankoff / [V75] Epstein / [P77] Etkin / [P100] Consolvo |
| 登録済みだがキー形式に注意 | 1 | ⚠️ **Horvitz 1999** —— [P42] が `proc:chi-1999-mixed-initiative` キーで登録済み。草案は DOI `10.1145/302979.303030` で引く → **DOI キーで新規登録すると二重登録事故**（citation-ssot ルール 4） |
| 未登録 | 約 32 | Galanter×2 / Boden & Edmonds / Eco / LeWitt / Cage / Lozano / Hsieh / Offenhuber / Xiong & Donath / Fairclough / Ewing / Chalmers & Galani / Höök / Pierce / Baumer & Silberman / Satchell & Dourish / Zong & Matias / Scerri et al. / Fogarty 2005 / Orseau & Armstrong / Hadfield-Menell / NIST AI RMF / Amershi / OECD / Donath Data Portraits / de Montjoye / Ochiai×2 / Weiser / Weiser & Brown / Abowd & Mynatt / Dourish 2004 / Nardi & O'Day / Star & Ruhleder / Bødker & Klokmose / Crabtree & Rodden |
| 名前のみ・書誌なし | 13 | Forms of Vitality / Laban Effort / process art・rule-based morphogenesis / embodied・enactive cognition / phenomenology of embodiment / somaesthetic interaction design / attention and action-readiness / micro-break・walking・creativity / construct・criterion validity / dynamic prediction / survival analysis・competing risks / calibration・temporal validation / micro-randomized trials（A §5） |
| 研究計画の運用 URL | 8 | IPA 未踏・DIS 2027・IUI 2027・OSF・Zenodo（C §15）—— ⚠️ 主張の根拠ではない。citation-ssot の対象にするかは運用判断 |

★ SDT は [P178]〜[P182] として既登録（P178 / P182 active、P179〜181 provisional）。

## 書誌の不一致（昇格前に直す）

1. **Horvitz 1999** —— 上表のとおり [P42] に寄せる（新規登録しない）。
2. **Offenhuber** —— B L602 は IEEE TVCG 2020（doi:10.1109/TVCG.2019.2934788）、`core-art` L233 は arXiv:1907.05454（2019）。同一論文の版違いの疑い。一次で同一性を確認してから 1 件に寄せる。
3. **Eco, *The Open Work*** —— B L595 は年・DOI なし、`core-art` L231 は 2021 reader chapter（doi:10.7312/hayo18620-025）。版の表記を統一する。

## `scripts/check_citations.py`（docs/ 側の現状）

- `=== 違反なし ===`。P1..P367 / V1..V150、欠番なし。tombstone は撤回説明の文脈での参照。
- 登録済み・本文未引用 19 件に **[P361]〜[P367]** が含まれる（★ 引き継ぎメモの「本文未引用」と一致）。
- ⚠️ 本スクリプトは `docs/` と `experiments/` だけを走査する → **`.idea` 草案の引用は検査されていない**（本表が代替）。

## 帰結（レビューへの反映）

- 草案の引用の **約 2/3 が未登録**。⚠️ SSOT へ昇格する単位ごとに、`citation-ssot` の手順（DOI 重複検査 → 末尾に append → provisional の扱い）で登録してからでないと昇格できない。
- ⚠️ 特に B §6 の「先行概念との衝突」表は、**衝突相手の大半が未登録**のまま新規性の範囲を論じている。→ 体系的レビュー（段 2）の前提。
