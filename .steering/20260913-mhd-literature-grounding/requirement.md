# requirement — Mh-D 文献接地の 1 ラウンド（起票 4 / 起票 5）＋ 起票 11 の研究者判断

- **日付**: 2026-09-13
- **ブランチ**: `docs/adr-030-stall-onset-definition`（★ ADR-029 から分岐・**未 push / 未 PR**）
- **入口**: `.steering/_handoff/next-session-mhd-literature-grounding-and-esm.md`
- **コマンド**: `/literature-review`（★ 1 ラウンド）／Skill: `citation-ssot` `literature-card`

## 背景

★ 前セッションは `ADR-030`（`stall onset` / `Decision Episode` の操作的定義）を書いたが、
⚠️★★★ **研究者の指摘で 2 回、同じ型の欠陥が見つかった**:

1. `.idea` の文献サーヴェイ **551 行のうち §6.1（Tier 表・約 25 行）しか読まず**に特徴量の枠を確定した。
   ★ **ADR の引用はゼロ件だった。**
2. `Context-3` で `p_stuck` の循環だけを塞いで「**本 ADR の核心**」と自称した。
   ⚠️ `.idea/survey §5.2` 逐語「**行動だけで criterion を作ると循環する**」——★ **D3 は `key` 行だけで
   onset を決める ＝ まさにそれ**であり、広い循環は **ESM 監査 criterion（起票 11）**が要る。

→ ★ 是正の一部は済んだ（`Context-3b` を追加）が、⚠️★★★ **`.idea/survey §13` の主要文献 33 件中 21 件が
`docs/references.md` に未登録**であり、★ **うち「強い反証」5 本のうち 3 本**が含まれる。

## ゴール

### G1. ★ 起票 11（ESM 監査 criterion）の研究者判断を取り、一次記録に落とす

⚠️★★★ **これは裁定ではなく研究者の意思決定である。エージェントが決めない。**
⚠️ 締切の性質は「O1 配布前」ではなく **「O1 の収集が本格化する前」**（★ 打鍵ログは後から再解析できるが、
その場の自己申告は後から生成できない）。

### G2. ★ 文献接地を 1 ラウンド回す（起票 4 / 起票 5）

★ **最優先は「強い反証」3 本**（★ ADR-030 の `Context-3b` に効く）:

| 優先 | 文献 | ⚠️ 何を示すか | ★ どこに効くか |
|---|---|---|---|
| 1 | **Tabarsi et al. (2022)** | 5 分超 idle が負の感情と関連する一方、成績とは正相関 `r=.507` | ★★★ **D2 / D3 の onset 定義** |
| 2 | **Conijn et al. (2022)** | 回帰は平均予測を超えず、分類は最大 AUC=.57 | ★ D10 の投資順序・`Q`（abstention） |
| 3 | **Zou & Godfrey (2012)** | ラボ約 80% → 実地で 70% 以上の誤差 | ★ `Context-3b (vi)` の外的妥当性 |

★ 次点（★ **原典が無い**）: **Fine & Gray (1999)** / **Nahum-Shani et al. (2018) JITAI** /
**Willett & Singer (1995) multiple-spell**（★ **ADR-030 D2 の反復エピソード規則の出典**）。

★ 起票 5: **Zou & Carl (2026)** ＋ ENJA15 / RUC17 生データ
（⚠️ `.idea §3.1` と `docs/references.md` [P273] が食い違っており **どちらが一次確認済みか未確定**）。

### G3. ★ ADR-030 `Context-3b` へ inline `[Pn]` を足す

⚠️★★★ **ADR 本文の *追記* は規約違反ではない** —— ★ 禁じられているのは **決定の書き換え**である。

## 受け入れ条件

- [ ] **AC1**: 起票 11 の研究者判断が `.steering/20260911-.../blockers.md` に落ち、
      ★ **選ばれなかった選択肢と、選んだ場合の残作業（①〜④）が読める**
- [ ] **AC2**: 「強い反証」3 本が **一次確認**され `docs/references.md` に append 登録された
      （⚠️ 未確認は `provisional`・**捏造 URL ゼロ**）
- [ ] **AC3**: 起票 5 の食い違いに **一次で決着**が付いた（★ または「両方とも一次未確認」と確定した）
- [ ] **AC4**: `docs/literature/<date>-<slug>.md` が落合 6 項目で生成され `_index.md` に 1 行追記された
- [ ] **AC5**: ADR-030 `Context-3b` に inline `[Pn]` が足された（⚠️ **D1〜D11 の中身は 1 文字も変えない**）
- [ ] **AC6**: `PYTHONUTF8=1 python scripts/check_citations.py` が **「違反なし」まで**通った
      （⚠️ **1 回で全件出ない** → 是正→再実行を繰り返す）
- [ ] **AC7**: `docs/research-positioning.md` への還元（★ または「還元不要」の判断）が明示された

## ⚠️ 射程外（★ やらない）

1. ⚠️ **ADR-029 / ADR-030 の承認・push・PR**（★ 研究者判断 2026-09-13 = **保留**）
2. ⚠️ **ADR 本文の *決定* の書き換え** → ★ 改訂が要るなら **ADR-031** を立てる
3. ⚠️ **`docs/preregistration-v0.3.md` の書き換え** / **`HMM_VERSION` の bump** / **`.idea` 本文の書き換え**
4. ⚠️ 起票 11 の **実装**（①〜④）—— ★ 本ラウンドは **判断の記録まで**
5. ⚠️ **ADR-009 を Accepted にしない**（★ G1 が `n = 0/3`）
