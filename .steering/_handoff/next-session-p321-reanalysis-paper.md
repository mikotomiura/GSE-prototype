# 次セッション — 2 本目の論文: [P321] ＋ [P434] の再解析（成果を要求しない自己解決指標のずれ）

> 作成: 2026-09-28（IME 論文の議論セッションで判断 16 を下した直後）。
> ⚠️ **このメモを一次資料にしない。** 数字・状態は着手時に一次で測り直す。
> ★ IME 論文（`next-session-ime-paper-issues.md`）とは触るファイルが別なので**並行可能**。

## §0 打ち込む用

```
.steering/_handoff/next-session-p321-reanalysis-paper.md を読んで、2 本目の論文（[P321] ＋ [P434] の再解析）を始めてください。
まず /start-task で .steering/<日付>-p321-reanalysis-paper/ を作る（実験は experiments/ 側・論文の作業記録は .steering/ 側）。
一次資料: .steering/20260927-ime-observation-paper-eval-design/decisions.md 判断 16 ／
experiments/20260906-p321-resumption-baseline/notes.md（★ §4 と §9 を必ず読む）／docs/references.md の [P321] [P433] [P434]。
最初の作業は §2 の 1（投稿先の確認）と 2（正式版の replication package をブラウザで取得）。
Skill: verify-before-claiming・reproducibility-discipline・citation-ssot・browser-verification（figshare を開く時）・
subagent-delegation（サーヴェイを投げる時）・literature-review / literature-card（位置づけのサーヴェイ）。
応答は日本語。コミットは専用ブランチ（例: docs/p321-reanalysis-paper）で、git add はパス指定（-A 禁止）。
```

## §1 状態（2026-09-28）

- ★ **判断 16**（`.steering/20260927-ime-observation-paper-eval-design/decisions.md`）: 研究者の指示「機関に関係なく使えるもの（論文などで公開されたもの）で、機が熟しているなら並行して進める」を受け、**2 本目を並行で進める**と決めた。
- ★ 使うデータ（**どちらも CC BY 4.0・機関に属さずに使える**）:
  - [P321] Alaboudi & LaToza の figshare パッケージ（`experiments/20260906-p321-resumption-baseline/raw/`・SHA-256 は `data.md`）—— 解析済み（R₀ = 70/89・R₁ = 60/73・R₀′ = 60/89）
  - [P434] Li & Coblenz（FSE 2026・doi:10.1145/3797077）の **論文の Table 4（Resolved Y/N）と Table 5（手法 × task）** —— task 単位 n = 17（R₀ = 11/17・R₁ = 9/13・R₀′ = 9/17）。⚠️ GitHub の補足データは **LICENSE が無い**ので使わない
- ★ 論文の芯（案）: **「解決と中止を同じ終端に束ねた episode 定義のもとで、成果を要求しない自己解決指標がどれだけずれるか」**。分子の効果 R₀ − R₀′（＝ 未解決かつ参照なしで終わった割合）が **[P321] +11.2pt / [P434] +11.8pt**。
- ⚠️ **弱点（先に固定）**:
  - R₀ そのものは原著が既報（arXiv v1 の補集合 21%・正式版 [P433] は 33%）→ 新規性は R₀ ではない
  - 「未 fix ほど参照が多い」は **defect の起点で交絡**（`notes.md` §9.2）
  - [P321] の 89 episode は第一著者 1 名のコーディング・N = 11 名（`notes.md` §4）
  - [P434] は n = 17・単位が task・外部資源の時刻なし
  - 正式版 [P433] は数え直している（参照 33%・活動 2135）。GSE の入力は arXiv v1 側と一致
- 暫定の投稿先: **EASE 2027 Short Papers and Emerging Results**（6 頁・abstract 2027-02-22 / paper 2027-03-01 AoE・double-anonymous）。次点 ICPC 2027 RENE（12-18）。⚠️ **研究者の最終確認が未了**。

## §2 次セッションでやること（順番）

1. **投稿先を研究者に確認する**（EASE 2027 Short / ICPC 2027 RENE / arXiv プレプリントの併用）。⚠️ 締切は着手時に CFP を一次で開き直す。⚠️ EASE は double-anonymous → 自著（GSE）の引用は三人称で。
2. **正式版 [P433] の replication package を取得する**: `https://figshare.com/s/0e9eac98b8ddd54c384c`（⚠️ curl / WebFetch は bot 対策で失敗する。★ `data.md` §2 と同じく**実ブラウザで**。ダウンロードはファイル名・サイズを示して研究者の承認を取ってから）。
   → v1 のデータ（`raw/replication_package_FSE2021/`）と比べ、**何が数え直されたか**（参照 21% → 33%・活動 2137 → 2135）を特定する。★ 論文ではどちらの版で数えたかを必ず書く。
3. **新しい実験ディレクトリ**（例: `experiments/<date>-self-resolution-measure-two-datasets/`）: `reproducibility-discipline` に従う。
   - 入力: [P321] の `rowData.json`（SHA-256 固定）＋ [P434] の表を**転記した CSV**（転記元の頁・表番号を列に持つ・二重転記で照合）
   - 解析: R₀ / R₁ / R₀′・分子と分母の効果・起点での層別（[P321]）・区間は開発者単位のクラスタ・ブートストラップ（seed 固定）
   - ★ 陽性・陰性対照（`notes.md` §6 の型）と、[P434] の転記ミスを検出する検査
4. **位置づけのサーヴェイ**を `/literature-review` で 1 ラウンド（help-seeking・debugging の観察研究・outcome の定義と中止の混入）。⚠️ 前回（2026-09-28）のサーヴェイは 20 分で、academic help-seeking と impasse 研究は**要旨どまり**。
5. 6 頁の外枠（主張 ↔ 根拠の対応表）を書く。

## §3 書いてよいこと / 書いてはいけないこと

- ✅ 「成果を要求しない指標は、2 つの独立な公開データで同程度（約 11pt）ずれる」（⚠️ 区間を必ず併記）
- ✅ 「参照と結末の関連は起点で交絡しうる」「コーディングの版で参照率が 21% → 33% と動く」
- ⚠️ 「R₀ は新しい指標」とは書かない（既報）
- ⚠️ 「再現した」とは書かない（n = 17・単位が違う）→「同程度だった」
- ⚠️ 「先行が存在しない」とは書かない（`docs/glossary.md` 禁止用語）

## §4 やらないこと

- ⚠️ [P321] / [P434] の値を **GSE の期待値**として使う（`notes.md` §4）
- ⚠️ IME 論文と同じ論文に混ぜる（判断 6）
- ⚠️ [P434] の GitHub 補足データ（LICENSE 無し）を使う・再配布する
- ⚠️ 人の打鍵データ・Phase1 / G1 / O1 のデータを使う
