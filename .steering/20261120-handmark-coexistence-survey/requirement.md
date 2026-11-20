# handmark-coexistence-survey（S-CX）

## 背景

2026-11-20、研究者と Windows 機で手跡の文献ラウンド（S-TG・S-TN・S-TN2・S-CO・S-NW）と S-EA の「やり残し」を整理した。0 件の穴が重なる所から、次の組み合わせを候補にした（Claude の見立て・文献で確かめていない）。

- 主役（概念）: 共存感覚 —— 自分の手つきから生まれたのに、自分ではないものとしてそばにいる感じ（S-CO・S-NW の 0 件の穴）
- つまみ: 由来を速さを除いたリズムで運び、慣性の時定数で「自分」と「別のもの」のあいだを動かす（S-TN/TN2 の 0 件の穴）
- 守り: 系の判断を運ばない（S-EA の差 1・差 2・予測器 A と B の漏れの検査）

一言の案は「由来は自分だと分かるが、判断は読まれない、自分から生まれた他者」。研究者は、共存感覚を新しい概念として立てる方向を面白いとし、詰め込まずにいいとこ取りで組むことに同意した。概念の文章を書く前に、同じものが別の名前で既にあるか（名前の衝突）を確かめる。

## ゴール

共存感覚という構成概念と、その組み合わせが、既存の概念・研究と衝突しないかを根拠つきで判断できる材料を作る。新しさの証明ではない。概念を採るか・名前をどうするかはこのラウンドでは決めない。結果の向きを先に決めない。

## 下位の問い（2026-11-20 研究者が承認）

1. 自分由来のものを「自分ではない存在」として感じる構成概念は、既にあるか（所有感と主体感の分離・分身・social presence の周辺）
2. 慣性・遅れ・自律性を振ったとき、自分のものという感じと「別のものらしさ」が入れ替わる点を測った研究はあるか（S-CO の続き）
3. リズムのような時間の構造で由来を感じさせる表現と、その評価（S-TN/TN2 の続き）
4. 反証の向き: 共存や生き物らしさの表示が、慣れで消える・煩わしくなる・監視と感じられる証拠

## スコープ

### 含むもの
- 文献のラウンド 1 回（/literature-review）・カード・references.md への append（P594〜）・_index.md の 1 行

### 含まないもの
- 概念の文章・名前の決定・research-positioning への還元・ADR・実装・未踏の提案書の文
- S-EA の枝の内容の変更（土台として使うだけ）

## 受け入れ条件

- [x] docs/literature/20261120-handmark-coexistence-concept.md（落合 6 項目・3 票の検証・否決リスト・名前の衝突の表）
- [x] references.md に append-only（P594〜P616）・check_citations.py が「違反なし」
- [x] _index.md に 1 行
- [ ] /cross-review（Codex を含む・送るのはカード・索引・references の diff だけ）
- [ ] push と PR は研究者に確かめてから（S-EA の PR の後に merge）

## 関連ドキュメント

- docs/literature/20261017-handmark-coexistence-sense.md（S-CO）・20261018-handmark-nature-world.md（S-NW）
- docs/literature/20261016-tangibility-self-recognition-and-leak.md（S-TN）・20261017-tangibility-recognition-leak-followup.md（S-TN2）・20261015-tangibility-agency-trace-replay.md（S-TG）
- docs/literature/20261117-expression-audit-precedent.md（S-EA）
- docs/adr/ADR-048（手跡は行為の性質だけを返す・共生は日の終わりに尋ねる）・ADR-051 D3（漏れの検査）

## 運用メモ
- /reimagine 適用: No
- 理由: 文献のラウンドで実装の設計判断を伴わない
