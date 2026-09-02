# tasklist — `.idea` §7 の未決事項 8 件

## Phase 0: 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-expression-channel-open-items.md` を読む
- [x] `/start-task` で `.steering/20260902-expression-channel-open-items/` を作成
- [x] 必須 Skill を参照（`verify-before-claiming`）
- [x] 一次実測: ADR-017 / ADR-018 / ADR-019 / ADR-010 / `expression-channel.md` / `data-privacy` / コード
- [x] 採番の実測 → **次番 `[P239]` / `[V112]`**（`check_citations.py` 緑・P1..P238 / V1..V111）
- [x] 研究者ヒアリング（スコープ / PreReg / PS-Q5）

## Phase 1: サーヴェイ（★ 全 7 系統をサブエージェント並列）
- [x] A 媒体の置き場所 → 未決 #1
- [x] B 他者可視性・THAT/WHAT/HOW → 未決 #2（PS-Q5）
- [x] C 抽象表現の個人化 → 未決 #3
- [x] D 招待の面と framing → 未決 #5 / #6
- [x] E ≤4 秒の可読性 → ★ §4.3 の層 A の穴
- [x] F 可読性・俯瞰・自律性の最小プロトコル → 未決 #8
- [x] G 逐語照合（`[P219]`–`[P238]` / `[V89]`–`[V111]`）→ ★ 繰り越し 2

## Phase 2: 一次照合（メイン）
- [x] `.idea` §0–8 の一次照合 → `idea-0-8-audit.md`
- [x] ★ 新規発見 B1 `level` に「わからない」が無い
- [x] ★ 新規発見 B2 「音の有無」が ADR-017 D5 と衝突
- [x] ★ 新規発見 B3 「表示場所」の自由化が ADR-017 D6 を壊す
- [x] ★ 新規発見 B4 スマホ側「層 0」の実体が未定義
- [x] ★ 新規発見 B5 §5.2 の上位 2 項目は content-free 制約に抵触
- [x] ★ 新規発見 B7 §3.1 が契約の 3 フィールドを落としている
- [x] ⚠️★★★ 新規発見 D1 `M1〜M4` が WBS `M0〜M5` と衝突 → 研究者判断で**実体名へ**

## Phase 3: 裁定（`decisions.md`）
- [x] 判断 4: `intervention_active` を `level` から外し直交フィールドへ
- [x] 判断 7: 双方向通信は開かない（★ 問いを書き直して閉じる）
- [x] 判断 9: 「わからない」を足さず、証拠不足は層 0 へ縮退
- [x] 判断 10: モデル成熟の呼称を実体名へ（ADR-019 D1 の追補）
- [x] 判断 1: 第一媒体（← サーヴェイ A）
- [x] 判断 2: 本人 / 他者（← サーヴェイ B・★ 設計制約のみ確定）
- [x] 判断 3: 固定 / 可変の境界（← サーヴェイ C）
- [x] 判断 5: 出口を出す境界（← サーヴェイ D）
- [x] 判断 6: 招待を差し出す面（← サーヴェイ D）
- [x] 判断 8: 最小プロトコル（← サーヴェイ F）
- [x] 判断 11: 層 A の設計要件 ＋ 視覚側「層 0」の定義（← サーヴェイ E）

## Phase 4: 文書化
- [x] `docs/adr/ADR-021-*.md` を起票
- [x] `docs/adr/README.md` に追加（⚠️ ADR-019 行に呼称改訂の注記）
- [x] `docs/architecture/expression-channel.md` を追随（§2.1 / §3 / §6 / §7.5 / §8）
- [x] `docs/glossary.md` を追随
- [x] `docs/references.md` へ append（`[P239]` / `[V112]` から）
- [x] `docs/preregistration-v0.3.md` に addendum 1 段落（★ 本文不変）
- [x] モデル成熟の呼称を 5 ファイル 7 箇所で是正 ＋ 提出資料を再生成

## Phase 5: 検証
- [x] `python scripts/check_citations.py`
- [x] `python scripts/check_doc_lexicon.py`
- [x] 提出資料の再生成（`md2docx.py` / `md2pptx.py`）
- [x] `/cross-review`（★ **両系統完走**・指摘 7 件はすべて採否を判断し是正済み → `decisions.md` 判断 12）
- [ ] `/finish-task`

## Phase 6: 追加で行ったこと（★ 当初の計画に無かったもの）
- [x] ⚠️★★★ **重複登録 4 件を検出・是正**（`check_citations.py`）——
      `[P251]`→`[P85]` / `[P262]`→`[P148]` / `[V120]`→`[V24]` / `[V122]`→`[V26]` を **tombstone ＋ 内容を統合先へ merge**
- [x] ★ **`[P92]` を `superseded` にした** —— ★ 本行は「一次を読めていない二次引用。根拠に使ってはならない。
      **全文入手が次ラウンド最優先**」と自認していた。★ **`[P267]` がその宿題を果たした**
- [x] ★ **提出資料の生成が決定的であることを実測で確認**（★ md5 が 2 回とも一致。⚠️ 機械検査が緑なだけでは信じない）
- [x] ★ **pptx の 1 枚あたり字数を実測** —— **非表スライドで 400 字超はゼロ**
