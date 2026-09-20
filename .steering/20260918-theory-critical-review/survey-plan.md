# 段 2 サーヴェイ候補（review-A〜D の「要サーヴェイ」を集約）

> 1 ラウンド = 1 つの問い（`/literature-review`）。WebSearch はサブエージェントへ並列委譲し、`docs/references.md` への追記はメインが直列（memory「Survey via subagent」）。
> 1 ラウンドごとに即コミット（memory「Commit each survey round」）。`check_citations.py` は「違反なし」まで回す。
> ⚠️ **実施するラウンドは研究者が選ぶ**（`questions-batch-1.md` Q17）。

| ID | 優先 | 問い（RQ） | 何を塞ぐか | 対象の主張 |
|---|---|---|---|---|
| **S7** | **高** | keystroke logging の修正（revision）研究で、**本文・カーソル位置を使わずに**定義された修正の指標（削除の走り・書き直し・再削除・修正の入れ子・局所反復・R-burst 等）はあるか。あるなら定義と名前は何か | ★ issue 004（`T1c`）の算出式と**フィールド名**（`rewrite` / `loop_depth` が本文・位置を持つ構成概念を指さないか）。起票 9 | D の外（MEAS）・`definitions-restop-t1d-t1c.md` §6 |
| **S8** | **中〜高** | 執筆・作業の中断後の**再開と再停止**、pause で区切られる産出の塊（P-burst / R-burst）、再開の安定性はどう操作化されてきたか。2 秒閾値以外の区切り方はあるか | ★ issue 006（`T1d`）の `stable_generation_ms` の定義と、「再停止」の一体定義の外的な接地 | `definitions-restop-t1d-t1c.md` §3-§4 |
| **S1** | **高** | 自動化・適応系が人へ権限（制御・判断）を**返す**とき、監視・検証・例外処理・責任の負担が人へ移ることは、**ironies of automation**（Bainbridge 1983）・**moral crumple zone**（Elish 2019）・自動運転の **take-over request / transition of control**・adjustable autonomy・responsibility gap でどこまで既に記述されているか。「返権の負荷逆説」と「権限・負担の二重台帳」に残る差分は何か | ★ TH-GR の新規性の核（B-24「返権の負荷逆説」・B-23 二重台帳・GR-C1 / GR-C7） | A-05, A-35, B-02, B-23, B-24, B-26, B-32 |
| S2 | 中 | 「非支配的協調」は、共和主義的非支配（Pettit）・関係的自律・nudge 倫理（libertarian paternalism / boosts）・contestability とどう違うか | CORE-NORM の依拠と差分（別トラックの受け入れ条件「依拠と差分を明示」が未充足） | A-07, A-10, B-03, B-04 |
| S3 | 中 | 生成芸術論・メディアアートで「過程」「終端」「撤退」「作者性の移譲」を**作品形式**として扱う議論（McCormack et al. 2014 ほか・process art・ephemeral / withdrawal art・slow technology） | CORE-ART・Galanter 反転（B-09）の新規性 | A-06, A-09, A-14, B-01, B-09, B-25, B-28 |
| S4 | 中 | data portrait / self-tracking art / lived・reflective informatics は、経路依存の「実践肖像」とどう重なるか | SUB-PGP の新規性 | A-13, B-18, B-25 |
| S5 | 低〜中 | embodiment / enactive / somaesthetics で「計測しない身体」を設計対象とした議論 | 「計測なき身体回帰」（A §5.5 が自ら要求）⚠️ J-14 の結論次第 | A-20, A-22, B-30 |
| S6b | 中（EH3 前まで） | 罪悪感・応答義務・不利益予期・放置不安・支援到達可能性の既存尺度（日本語版・弁別妥当性） | 測定辞書の独自 2 項目の置き換え | D-19 |

★ 推奨順: **S7 → S8**（issue 004 / 006 の定義確定に直結・タスク 2 の再開順を進める）→ **S1**（理論の新規性の核）→ S2 → S3 / S4 → S5 → S6b。
⚠️ S7 / S8 は「定義を借りられるか」を問うラウンドであり、**結果が無くても定義案（新しい定数ゼロ）で進められる**（→ 待たずに暫定確定する選択肢もある）。

---

## ★ 実施状況と残りの予定（2026-09-21 追記・研究者判断）

> ⚠️ 本節は**後から足した進捗の記録**である。★ 上の表（問い・対象の主張）は当時のまま。

### 実施済み（2026-09-19・段 2）

| ID | 成果 | コミット |
|---|---|---|
| **S7** | `docs/literature/20260919-content-free-revision-measures.md`・[V151]–[V160]・定義案 §6.2b | `4403763` |
| **S8** | `docs/literature/20260919-resumption-restop-and-bout-segmentation.md`・[V161]–[V169]・定義案 §3.4 | `7860ccb` |
| **S1** | `docs/literature/20260919-authority-return-burden-precedents.md`・[P368]–[P379]・`review-B.md` §5 | `95abd10` |
| **S2** | `docs/literature/20260919-non-domination-and-autonomy-norms.md`・[P380]–[P391]・`review-D.md` §6 | `99c0d60` |
| （補足） | Digital Nature の一次（`20260919-digital-nature-primary-scope.md`・[P392]–[P395]） | 段 2 |

★ S7 / S8 の結果は **issue 004 / 006 に転記済み**で、⚠️ **2026-09-21 に実装まで完了した**
（`.steering/20260920-issues-004-006/`・PR #215 merge）。

### ★ 残り 4 本のタイミング（2026-09-21・研究者判断）

| ID | ★ いつ回すか | ⚠️ 根拠（一次） |
|---|---|---|
| **S3** | ★ **`capability matrix`（ADR-032 M7）の後、理論の回として** | ⚠️★★★ **J-2（名称ゲート ＝「生成的返権論」の名前を残すか）が S3 待ちで止まっている** —— `questions-batch-1.md:27` 逐語「S1 / S3 の結果（先行と衝突するか）を見てからでないと判断材料が無い」。★ **S1 は済んだので、残る閂は S3 だけ**である |
| **S4** | ★ **S3 と同じ回に続けて** | 対象主張（A-13 / B-18 / B-25）が S3 と隣接し、出典が重なる |
| **S5** | ★ **Physical Anchor の PC 面の実装設計タスク**（ADR-035 の未決 3 つと同じ回） | ★ ゲートだった **J-14 は判断 1 #4 で裁定済み**（語を分け、PM-Q7 は別途）。→ ⚠️ 残る論点 **PM-Q7**（復帰後の差分を表現へ結合するか）は PA の実装設計の場にある。★ そこで問わないと S5 の問い自体が揺れる |
| **S6b** | ★ **EH3 を設計する回**（⚠️ EH3 を走らせる前） | 上の表「中（EH3 前まで）」／ `docs/theory/generative-relinquishment-theory.md:496` 逐語「数値マージンと独自項目の妥当性は未確定であり、**EH3 後かつ EH4 の割付前に凍結する**」。⚠️ EH3 は研究用の**別計器**で、まだ設計されていない |

- ⚠️ **外部の締切要因は無い**（★ `docs/wbs-verification-halfyear.md` のマイルストーンは W1 起点の相対表記で、
  逐語「絶対日付は着手時に確定」）。
- ★ 実施は `/literature-review` 1 ラウンド＝ 1 問。⚠️ **ラウンドごとに即コミット**（memory「Commit each survey round」）、
  探索は subagent・`docs/references.md` への追記はメイン直列（memory「Survey via subagent」）、
  `check_citations.py` は「違反なし」まで回す。
