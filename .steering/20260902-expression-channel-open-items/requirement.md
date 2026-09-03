# requirement — 表現チャネル `.idea` §7 の未決事項 8 件を裁く

- 日付: 2026-09-02
- 前タスク: `.steering/20260902-gse-design-deepening/`
- 入力: `.idea/20260901-smartphone-state-externalization-and-physical-return.md` §0–8
  （⚠️ **追跡外＝ SSOT ではない**）
- 引き継ぎ: `.steering/_handoff/next-session-expression-channel-open-items.md`

---

## 背景

前セッション（2026-09-02）で `.idea` §9–15 を裁き、**ADR-019 / ADR-020** を起票した。
併せて §9 のサーヴェイ記録に **重大な誤りが 5 件**あることを一次確認で暴いた
（`survey-verification.md`）。⚠️ **§0–8 も同じ精度で疑う必要がある。**

`.idea` §7 は未決事項を 8 件挙げているが、`conflict-audit.md` F7–F10 の実測により、
**そのうち複数は既に ADR-017 / ADR-018 で決まっているか、問いの立て方自体が成立しない**
ことが分かっている。→ ★ **「裁く」の中身は、まず *問いを正しく立て直すこと* である。**

## ゴール

1. `.idea` §7 の 8 件それぞれについて、**(a) 既決か / (b) 問いの再定義が要るか / (c) 本当に未決か**
   を一次資料（ADR / SSOT docs / コード）で判定し、`decisions.md` に記録する。
2. 本当に未決なものを裁き、**ADR-021** を起票する（★ ADR-020 の次番）。
3. ⚠️★★★ **`.idea` §4.3 の穴（層 A の設計が欠けている）を埋める** —— ADR-017 D6 は
   層 A（強制曝露・≤4 秒）と層 B（任意閲覧・数十秒）を別に設計せよと決めているが、
   §4.3 は層 B しか書いていない。
4. `docs/architecture/expression-channel.md` を ADR-021 に追随させる。
5. 新規に引く文献を `docs/references.md` へ append する（★ 次番 `[P239]` / `[V112]`・2026-09-02 実測）。
6. **繰り越し 2**: `docs/references.md` の新規「逐語」引用のサンプル照合（`literature-card`）。
7. **繰り越し（研究者判断済み）**: `docs/preregistration-v0.3.md` に addendum を 1 行足す
   （★ 2026-06-28 の先例に倣う。★ **本文は変えない**）。

## 受け入れ条件

- [ ] 8 件すべてに判定と根拠（一次資料の実測）が付いている
- [ ] ADR-021 が起票され、`docs/adr/README.md` に載っている
- [ ] 層 A の設計要件が `docs/architecture/expression-channel.md` に書かれている
- [ ] 新規引用がすべて `docs/references.md` に登録され、`scripts/check_citations.py` が緑
- [ ] `scripts/check_doc_lexicon.py` が緑（提出資料に触れた場合）
- [ ] `/cross-review` をパス限定で実行済み

## スコープ外（やらないこと）

- ⚠️ **`docs/preregistration-v0.3.md` の本文改変**（★ addendum ブロックへの 1 行追記のみ）
- ⚠️ **過去 ADR（001–020）の本文改変** —— 改訂は新規 ADR の追補で行う
- ⚠️ **`.steering/` の過去の記録の改変**
- ⚠️ **`docs/design-history.{md,ja.md}`**
- ⚠️ **wire protocol の決定**（W-1・実装着手時の別 ADR）
- ⚠️ **コード変更**（`src-tauri/**` / `src/**`）—— 表現チャネルは未実装
- 繰り越し 1（`.pptx` / `.docx` の実地確認）/ 繰り越し 3–6 —— ★ **今回のスコープ外**（研究者判断）

## 運用メモ

- **/reimagine 適用**: No
- 理由: 本タスクは**設計判断の裁定と文書化**であり、実装案の複数候補を比較する局面ではない。
  ★ ただし未決 #1 / #6 は選択肢の比較を含むため、`decisions.md` の「却下案」欄で同等の比較を行う。
- **研究者判断（2026-09-02・ヒアリングで確定）**:
  1. スコープ = 8 件 ＋ 繰り越し 2（逐語照合）
  2. PreReg = **2026-06-28 の先例に倣い addendum を 1 行足す**
  3. PS-Q5 = **設計制約だけ確定し、最終判断は試視へ送る**
