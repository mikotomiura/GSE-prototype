# expression-adr023 — 最終サーヴェイ 1 ラウンド → ADR-023 の起票

> ★ 入口: `.steering/_handoff/next-session-expression-final-survey-and-adr023.md`
> ⚠️★★★ **引き継ぎメモは三次資料である**（`verify-before-claiming` ルール 1）。
> ★ 当たりを付けるためだけに使い、**手を動かす前に一次で裏を取る**。
> ★ 実際、本タスクの着手直後に **引き継ぎの記述 1 件が一次と食い違った**（→ `decisions.md` 訂正 1）。

## 背景

`.idea/20260905`（メディア表現の理論案）の逐条照合は **2026-09-06 に完了**した
（記録: `.steering/20260906-expression-transform-theory/`）。その過程で
**判断 (a)〜(i)** が立ち、**サーヴェイを 2 ラウンド**（RQ0/2/3/4/5-6 → RQ A〜E・計 10 系統）回した。

★ 中心は **判断 (i)** である —— **測る対象を「可読性」から「出口への結合」へ移し、
可読性を manipulation check へ降格する**。⚠️ しかしこの立て方には **未実証の急所**が 1 つ残っている:

> 「可読性は合否を決めない。**が、落ちると結果が解釈不能になる**」という *関係そのもの* を
> 検証した先行が、2 ラウンド回しても **ゼロ**である
> （`.steering/20260906-expression-transform-theory/decisions.md` §RQ-A〜E-7.5）。

★ また、2 ラウンドで確定した **9 件の留保**（過大主張の禁止事項）が `decisions.md` に散在しており、
⚠️ **ADR として一箇所に固定されていない**。★ 現状、次の実装者・執筆者はこれを 1264 行の
`decisions.md` から拾わねばならない。

## ゴール

1. ★ **最終サーヴェイを 1 ラウンド回す**（RQ α/β/γ/δ ＋ 一次取得 5 件）。
2. ★★★ **ADR-023 を起票する** —— 判断 (i) ＋ その精緻化を主軸に、2 ラウンドで確定した留保と
   「主張してはいけないこと」を **ADR の本文として固定**する。

## スコープ

### 含むもの
- サーヴェイ 1 ラウンド（**サブエージェント 5 系統並列**・予算 15〜20 ソース/系統）
- `docs/references.md` への append-only 登録（★ **採番と append はメインが直列**）
- `docs/literature/` のカード 1 枚 ＋ `_index.md` 追記
- **`docs/adr/ADR-023-*.md` の新規起票** ＋ `docs/adr/README.md` の一覧追記
- 影響を受ける SSOT の訂正（★ **一次で裏が取れたものに限る**）
- `code-reviewer` + `security-checker` 並列 → `/cross-review`（パス限定）→ `/finish-task`

### 含まないもの
- ⚠️★★★ **`experiments/` の設計**（★ 中断 → 再開の観測設計は **次セッション**）
- ⚠️ **コード変更**（★ 本 ADR は **コード変更ゼロ**。指標の実装是正は別タスクへ割る）
- ⚠️ **ADR-017/018/020/021/022 の本文書き換え**（★ ADR 本文は書き換えない規約。参照するだけ）
- ⚠️ **凍結済み `docs/preregistration-v0.3.md` の書き換え**
- ⚠️ 判断 (h) を理論的新規性として書くこと（★ 2 ラウンドで「工学的統合」へ降ろし済み）

## 受け入れ条件

- [ ] サーヴェイ 5 系統の生出力が `surveys/` に残っている（★ **全損 0 件**）
- [ ] 各系統が **ゼロの検算表**（条件を 1 つずつ落とす）を含む
- [ ] `references.md` の新規行が **すべて key（DOI/arXiv/正規化 URL）付き**で、
      **既存行との重複照合をメインが実施**済み
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が **「違反なし」まで**回っている
      （⚠️ **1 回で全件出ない**ので繰り返す）
- [ ] `docs/adr/ADR-023-*.md` が **Context / Decision / Alternatives / Consequences / Migration** を持つ
- [ ] ADR-023 に **9 件の留保**と **9 件の「主張してはいけないこと」**が漏れなく入っている
- [ ] ADR-023 の各断定に **一次の典拠 `[Pn]`/`[Vn]` か repo の実測（`file:line`）**が付いている
- [ ] `docs/adr/README.md` の一覧に ADR-023 の行がある
- [ ] `code-reviewer` / `security-checker` / `/cross-review` の **HIGH 指摘を本タスクで消化**済み
      （⚠️ backlog へ punt しない）

## 関連ドキュメント

- `docs/architecture/expression-channel.md`（★ §5 / §7.1 / §7.5 / §8）
- `docs/adr/ADR-017` / `ADR-018` / `ADR-020` / `ADR-021` / `ADR-022`
  （⚠️★★★ **ADR-017 単独で読むと古い契約を掴む。番号の大きい方まで読む**）
- `docs/research-positioning.md` §4 / §5（H-Y / H-PA / H-EXPR）
- `.steering/20260906-expression-transform-theory/decisions.md`（判断 (i) と §RQ-A〜E）
- `src-tauri/src/analysis/metrics.rs`（★ 機会保存の 3 指標の **実装**）

## 運用メモ

- **/reimagine 適用: No**
- 理由: ★ 本タスクは **設計案の生成ではなく、既に確定した判断の *記録*** である。
  2 ラウンドのサーヴェイで代替案（判断 (e) 差分の主座 / 判断 (h) 理論的新規性）は
  **既に検討され、証拠によって降ろされている**。★ ゼロから再生成しても同じ証拠に当たるだけで、
  ⚠️ **むしろ確定済みの留保を落とす risk のほうが大きい**。
