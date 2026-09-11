# idea-to-ssot-intake-and-promotion

## 背景

`.idea/` に 17 本・約 500KB の議論メモが蓄積し、直近 1 週間（2026-09-05〜09-11）だけで 6 本が追加された。
これらは Mh-D（特徴量・criterion・検証設計）とメディア表現（Practice Portrait・招待・チャネル）と
GSE 研究全体のコンセプトを論じているが、**どこまでが SSOT へ昇格済みで、どこからが未昇格か**が
把握できない状態になっていた。

2026-09-11 の調査（サブエージェント 6 本）で、前提が 2 つ判明した。

1. ⚠️★★★ **ADR-023〜028 は既に書かれており、未マージブランチ `feat/resumption-outcome-arbitration`
   に存在する**（200 files / +26,924 / −1,707）。`.idea/20260907` と `.idea/20260908` が「正式 SSOT」として
   参照していた ADR-024 / 025 / 028 は**参照切れではなく未マージ**だった。
   → ★ **新規 SSOT 化の前に取り込みが先**。逆順にすると既に裁定済みの論点に重複 ADR を書く。
   → 取り込み計画は `.steering/_handoff/next-session-prompt-intake-windows-and-continue.md §2` に
     「研究者に諮ること」として案 A/B/C が用意済み。**案 B（Windows 実測ぶん）は完了済み**で、
     残るのが **案 C（系統ごとに PR を割る）**。本タスクはその案 C の実行を含む。

2. ⚠️★★★ **転帰（未来アウトカム）の定義が 3 つ並立している**。しかも 1 と 3 で主従が反転している。

   | # | 出典 | 時間原点 | 主イベント | 構造 | 状態 |
   |---|---|---|---|---|---|
   | 1 | ADR-009（main） | stall onset | `recovery`（自力前進の回復） | 4 択・離散時間 hazard | **Proposed・凍結中・着手ゼロ** |
   | 2 | `metrics.rs`（main・実装済み） | stuck エピソード | `p_flow > 0.5` 到達 | 固定窓の二値判定 | 稼働中（2026-06-23 作・ADR-009 より前） |
   | 3 | ADR-024（未マージ） | 離席候補ギャップ明けの初打鍵 | **`receipt`（paste）の発生** | Aalen–Johansen 競合リスク CIF | **Accepted だが main に無い** |

   ★ **ADR-024 が ADR-009 を上書きするのか別トラックなのかが、どの文書にも書かれていない。**
   ⚠️ かつ `.idea/20260910` と `20260911`（ADR-024 の Accepted 日 2026-09-07 より後の日付）は
   なお ADR-009 の 4 択語彙のままで、ADR-024 の再定義を反映していない。
   → ★ **この分岐が閉じていないと、O1 のラベル定義そのものが事後選択の対象になる。**

⚠️★★★ **O1 はまだ開始していない**（2026-09-11 に研究者が明言）。したがって
「収集器を配布した後では原理的に復元できない観測」を確定する最後の機会が今である。

## ゴール

ブランチ `feat/resumption-outcome-arbitration` の内容を **系統ごとに分けて main へ取り込む**（案 C）。
⚠️ **これだけが本タスクのゴールである。** 新規 SSOT 化は後続タスクへ委譲した（下記）。

## ★ 後続タスク（本タスクの完了が前提）

⚠️★★★ 2026-09-11 に**タスクを 4 分割した**（1 セッションに収まる規模を超えたため）。

| task | 内容 | 依存 |
|---|---|---|
| **本タスク** `20260911-intake-arbitration-branch` | ブランチ取り込み（案 C）・issue 001–006 | — |
| `20260911-outcome-arbitration-and-o1-preflight` | 転帰定義の一本化 ＋ O1 配布前の実装 2 件・issue 007–009 | 本タスク |
| `20260911-mhd-inference-ssot` | MhD の推論アーキ・成長軸・tuning 規約・特徴量 Tier（★ 調査済み・issue 未分解） | 本タスク |
| `20260911-practice-portrait-ssot` | Practice Portrait（`20260908` / `20260909`×2）の SSOT 化（★ 調査済み・issue 未分解） | 本タスク |

★ **後続 3 本がいずれも本タスクの完了を待つ理由**: 取り込み後の
`expression-channel.md`（+337 行）/ `glossary.md`（+27 行）/ ADR-023〜028 に
**既に書かれている可能性があり、重複判定ができない**ため。

## スコープ

### 含むもの

**取り込み（案 C）の 6 系統のみ**: ADR-023〜028 ／ `metrics.rs` ほかコード ／ 表現層 ／
ツール ／ サーヴェイ ／ 提出文書図版

### 含まないもの

- ⚠️ **Proposed の ADR 5 件（003 / 005 / 008 / 009 / 010）を Accepted にすること**
  → いずれも「方向は合意・確定は証拠待ち」。ADR-009 は自ら
    「最大の未決は G1 が `n = 0/3` であること」と書いており、**議論では閉じない**。
- ⚠️ **O1 回収後に凍結すべき項目**（Decision Episode 境界・predictor/future window・split 定義・
  G-next / O-holdout の数値）→ データを見る前に決めるのは正しいが、**O1 discovery の結果を
  見てから凍結する**のが出典自身の設計（`criterion §5.3` の Phase A→B→C）。
- ⚠️ **一般理論構想（`.idea/20260905` 社会的表現変換論）** → 研究者本人が「まだ昇格させない」と明記。
  後続メモが暗黙の前提として使い始めていないことを grep で確認済み（0 件）。現状維持。
- ⚠️ **制作・造形の実作業**（TouchDesigner / Substance / After Effects でのシェーダ実装、
  Pi Zero + LCD / フリップカバーのハードウェア試作）→ ADR の粒度ではない。
- ⚠️ **Practice Portrait の造形候補確定** → `.idea/20260909` §18.8 の最小比較試作（20〜30 秒 loop・
  3 案比較）を回してからでないと確定できない（C 区分）。

## 受け入れ条件

- [ ] Wave 0 の 6 系統がすべて main に入り、`cargo test --workspace` / `gse-replay --snapshot` /
      `emit_schema` parity / `check_doc_lexicon.py` / `check_citations.py` / `secrets-filter-test.sh`
      がすべて exit 0
- [ ] `docs/adr/README.md` に ADR-023〜028 が載り、実ファイルと差分ゼロ
- [ ] ⚠️ **`acceptance.sh` を各 issue に書いた**（`blockers.md` 起票 3。取り込まなくても lint が緑になるため）
- [ ] `blockers.md` の起票 1（macOS `secure_input`）と 2（`gse-dataset` 後方互換）を処理した
- [ ] ⚠️ **後続 3 タスクに引き継ぐ差分を記録した** — 取り込み後の `expression-channel.md` /
      `glossary.md` / ADR-023〜028 に**何が既に書かれていたか**。これが無いと後続が重複を判定できない
- [ ] `/cross-review` を通している（skip した場合は理由を明記）

## 関連ドキュメント

- `docs/loop-engineering.md` — issue 単位ループの単一 SSOT（本タスクの issue 分解の基準）
- `.steering/_handoff/next-session-prompt-intake-windows-and-continue.md §2` — 取り込み案 A/B/C
- `.steering/20260910-intake-windows-and-cpu-convention/tasklist.md` — 「残り 3 系統の取り込み＝案 C」が未着手
- `docs/adr/README.md` — ADR-001〜022（main 側）
- `docs/architecture/expression-channel.md` — 表現チャネルの契約
- `docs/architecture/personalization-and-online-learning.md` — `self_directed_recovery_risk` の定義
- `docs/glossary.md` — 禁止用語 15 件・`MhD` の正式表記

## 運用メモ

- **/reimagine 適用: Yes**
- 理由: 転帰定義の一本化（ADR-009 と ADR-024 のどちらを主解析に据えるか）は
  **研究の根幹に関わる設計判断**であり、初回案をそのまま採ると取り返しがつかない。
  該当 issue の設計段階で `/reimagine` を起動し、初回案を破棄して再生成した案と比較する。
  Wave 0 の取り込み系 issue には不要（既に書かれたものを移す作業のため）。
