# 引用の良い例 / 悪い例（citation-ssot）

SSOT: `docs/references.md`。本文を書きながら [n] を付け、末尾に append する。

## ✅ 良い例

### 例 1: 主張に inline [Pn]/[Vn] を付け、その場で append
本文:
> GSE は不便益 [P6] の思想を、生産的苦闘 [P12] の保護へ、行動プロキシ [P7][P11] で結びつける。

references.md（該当名前空間の末尾に追加、既存番号はそのまま）:
| [P6] | proc:design-society-2019 | Kawakami & Naito — Benefit of Inconvenience | Proc. Design Society 2019 | — | research-positioning §1,§4 | — | active |
| [P12] | doi:10.1080/07370000802212669 | Kapur — Productive Failure | Cognition and Instruction 2008 | — | research-positioning §1,§4 | — | active |

### 例 2: 名前空間と重複の扱い
同じ文献が理論(P)・方法論(V)両方で要るとき（例 Oppezzo 歩行研究）は両 ID を維持し「重複」列で相互リンク:
| [P8] | doi:10.1037/a0036577 | Oppezzo & Schwartz — Give your ideas some legs | JEP:LMC 2014 | <https://doi.org/10.1037/a0036577> | Physical Anchor | =V8 | active |
→ 片方を tombstone にしない。新規方法論引用は V 名前空間の末尾へ append。

### 例 3: 書誌未確定は provisional / 撤回は tombstone
- 未確認: 状態を `provisional` で登録し、確認後に key/URL を埋め `active` へ（捏造 URL を書かない）。
- 撤回: 行を残し `~~[Vk]~~ ... (撤回: 理由)` + 状態 tombstone。番号 [Vk] は二度と再利用しない。

## ❌ 悪い例

### アンチ 1: 出典なし主張 → 最後にまとめ書き
> ...先行研究では困難が学習を促す。（本文に [n] なし）
> ## 参考文献（末尾に手作業で列挙）
→ SSOT が二重化し、本文との対応が崩れる（drift）。**書きながら [n] を付ける。**

### アンチ 2: renumber
[2] を削除して [3]→[2], [4]→[3] と詰める
→ 既に各設計書に散った inline [2][3][4] が全部ずれる。**append-only / tombstone を厳守。**

### アンチ 3: 番号の再利用
撤回した [3] を別文献に振り直す
→ 過去の本文 [3] が別物を指す。**再利用禁止。**

### アンチ 4: URL/DOI の捏造
未確認なのに DOI をでっち上げる
→ **provisional で登録し確認に回す。** 確認できない書誌を active にしない。

## セルフチェック（編集後に grep）

- 本文の `[n]` を抽出し、references.md に全て実在するか
- references.md の各 `active` 行に「使用箇所」列が埋まっているか
- key 列に重複がないか（同一 DOI/arXiv/URL の二重登録）
