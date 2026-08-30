# 設計

## 実装アプローチ

⚠️★★★ **本タスクはコードを 1 行も書かない。**★ 成果物は **ADR / architecture 文書 / positioning の改訂 /
glossary / Skill の是正**である。

★ 方針は 3 つ:

1. **一次に降ろしてから裁く** —— 2026-08-30 のサーヴェイ 4 ラウンドが出した逐語と実数だけを根拠にし、
   ⚠️ **記憶・過去の引き継ぎ・自分の以前の発言を根拠にしない**（`verify-before-claiming`）。
   ★ 本タスクで再実測したもの: `self_directed_recovery_risk` の**コード内不在**（grep 0 件）／
   `data-privacy` SKILL の**位置情報の規定ゼロ**／`physical-anchor` SKILL:49-50 の **D11 違反**／
   `docs/architecture.md` の **ADR-015 未追随 12 箇所**／`research-positioning.md` §9 の **Wall / Monk Mode 残存**。
2. **既決を覆さず、覆すときは明示する** —— D8 / D9 / D10 / D11 / PM-D11 / PM-D4 / D21 は生かす。
   ★ **ADR-017 D3 は PM-D11 を覆さない**（★ 「測って *よい*」であって「測れ」ではないため）。
3. **研究者確認が要る節は先に確認を取る** —— `research-positioning.md` は §1 / §4 / §5 / §7 が
   研究者確認節。★ **§1 / §4 / §7 は承認を得て適用し、§5 は案提示に留める**（2026-08-30 の 4 択で確定）。

## 変更対象

### 新規作成
- `docs/adr/ADR-017-expression-channel-boundary.md` — ★ **決定の SSOT**（D1–D9）
- `docs/architecture/expression-channel.md` — ★ **設計の SSOT**（§0–§8）
- `.steering/20260830-expression-channel-ssot/decisions.md` — 論点 1〜6 の裁定
- `.steering/20260830-expression-channel-ssot/positioning-section5-draft.md` — ⚠️ **§5 改訂案（未適用）**

### 修正
- `docs/adr/README.md` — ADR-017 を一覧に追加
- `docs/research-positioning.md` — §1（不便益の自己規定）/ §4（差分の焦点化・不便益の実証の薄さ）/
  §7（「測定可能にした」の訂正）/ §8（[P77] 実験 4 の条件＝未計測の限界）/ §9（Wall・Monk Mode・音声の自動開始）
- `docs/architecture.md` — ADR-015 未追随 12 箇所（図 / 依存 crate / スレッド / §4.5 / §4.6 / schema /
  フロー 2 / 外部依存表 / Physical Anchor 項）
- `docs/glossary.md` — 表現チャネル関連 6 語を追加 / Wall・Zen Timer・Monk Mode・Early Unlock を廃止扱い /
  不便益の定義を [P170] の一次へ / 禁止用語 4 件を追加・2 件を失効
- `docs/agent-shared.md` — 概要の介入列 / リンクハブに `expression-channel.md`
- `.claude/skills/physical-anchor/SKILL.md` — ⚠️ **D11 違反の是正 ＋ `wall_server` 依存の除去**（全面改訂）
- `.idea/20260819-smartphone-computational-media-channel.md` — 2026-08-30 追記（★ SSOT への昇格と未決）

### 削除
- なし

## 影響範囲

| 影響先 | 対処 |
|---|---|
| **実装（`src-tauri/**` / `src/**`）** | ★ **差分ゼロ**。⚠️ ADR-017 はコード変更を要求しない |
| **`HMM_VERSION` / `EXPR_VERSION` / NDJSON schema** | ★ **不変**（★ 表現層は MhD に触れない — 既決 D10） |
| **凍結文書**（`preregistration-v0.3.md` / G1 事前登録） | ★ **不変**。⚠️ §8 の限界記述は **Phase1 に計器を足さない**判断とセットである |
| **`research-positioning.md` §5** | ⚠️ **未適用**（★ 案のみ）。研究者の次の承認待ち |
| **`data-privacy` SKILL** | ⚠️ **未着手**（★ 別タスクへ切り出し・ADR-017 D9 がブロッカーとして明示） |
| **他の Skill（`intervention-design`）** | ⚠️ ADR-015 のルール 5（Monk Mode）が無効のまま残っている可能性 → ★ **次タスクの候補** |

## 既存パターンとの整合性

- **ADR の書式**: Context / Decision / Alternatives / Consequences / Migration（`docs/adr/README.md` 凡例）
- **`docs/architecture/` の書式**: `workspace-behavior-observation.md` に倣い、**§0「本文書が何であって、何でないか」**を先頭に置く
- **引用**: `citation-ssot` —— ★ **本タスクは新規登録を行わない**（★ 参照はすべて 2026-08-30 までに
  append-only 登録済みの [P1]–[P191] / [V1]–[V88] の範囲内）
- **glossary**: 「既存用語の意味を変える場合は変更履歴を残す」（用語の追加・変更ルール 2）→
  ★ **削除語は行ごと消さず、取り消し線 ＋ 削除 ADR の参照**で残す

## テスト戦略

- ⚠️ **コード変更が無いのでコードテストは走らせない。**
- ★ **機械検算**: `PYTHONUTF8=1 python scripts/check_citations.py` —— ★ **違反なしを確認済み**
  （未登録参照 / 欠番 / tombstone の引用 / 相互リンク無しの同一 key のいずれも無し）。
- ★ **実装差分ゼロの確認**: `git status --short src-tauri src` が空であること。
- ★ **レビュー**: `code-reviewer` は対象外（コード無し）。⚠️ **`/cross-review` はドキュメント差分に対して
  パス限定で回す**（★ memory: 無関係な未コミット変更でブロックされるため `-- <paths>` を付ける）。

## ロールバック計画

- ★ **すべて追記・置換のみで、削除した情報は無い**（★ 削除語も取り消し線で残している）。
- ★ 単一コミットに閉じるので `git revert` で戻せる。
- ⚠️ **`.idea/` は追跡外**なので git では戻らない → ★ 追記は「2026-08-30 追記」見出しで 1 ブロックに閉じてある。
