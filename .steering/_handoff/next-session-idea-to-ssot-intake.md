# 次セッション開始プロンプト — **`.idea` → SSOT の取り込みと昇格（4 タスク構成）**

> 作成: 2026-09-11 / ⚠️★★★ **このメモを一次資料にしない。** 実体は各タスクの `issues/00X.md` と
> `_survey-*.md` にある。*issue ファイルだけを読んで実行が成立しないなら、分解が失敗している*。

## §0 ⚠️★★★ タスクは 4 本に分かれている（★ 1 セッション 1 タスク）

```bash
git status && git branch --show-current      # clean / main か
ls .steering/20260911-*/
```

| # | task | 内容 | 状態 | 依存 |
|---|---|---|---|---|
| **T1** | `20260911-intake-arbitration-branch` | ブランチ取り込み（案 C）・**issue 001–006 分解済み** | ★ **次はこれ** | — |
| **T2** | `20260911-outcome-arbitration-and-o1-preflight` | 転帰定義の一本化 ＋ O1 配布前の実装 2 件・**issue 007–009 分解済み** | 待機 | T1 |
| **T3** | `20260911-mhd-inference-ssot` | MhD の推論アーキ・tuning 規約・特徴量 Tier・⚠️ **ADR-008 D8 との衝突裁定**。★ **調査済み・issue 未分解** | 待機 | T1 |
| **T4** | `20260911-practice-portrait-ssot` | Practice Portrait の SSOT 化。★ **調査済み・issue 未分解** | 待機 | T1 |

★ **T2〜T4 がいずれも T1 を待つ理由**: 取り込み後の `expression-channel.md`（+337 行）/
`glossary.md`（+27 行）/ ADR-023〜028 に**既に書かれている可能性があり、重複判定ができない**ため。

⚠️ **T3 / T4 は issue 未分解。** それぞれの `_survey-*.md`（調査済みの一次資料）を読んでから
`issue-slicing` skill で分解する。分解と実行は別セッションにする。

## §1 ★ 次のセッションでやること = T1

`.steering/20260911-intake-arbitration-branch/` を開き、この順に読む:

1. `requirement.md` — 背景とゴール
2. `_issue-plan.md` — **DAG・交差表・実行ウェーブ・引き継ぎ事項**
3. 着手する `issues/00X.md` — **これが SSOT**
4. `decisions.md`（判断 6 件・蒸し返さない）/ `blockers.md`（起票 3 件）

| ウェーブ | issue |
|---|---|
| **W1** | **001 単独**（⚠️ ゴールデン・schema の前提を変えるので並列にしない） |
| W2 | 002 / 003 / 004（002 は 001 完了後） |
| W3 | 005 / 006（006 は 002 完了後。005 は依存ゼロで前倒し可） |

⚠️★★★ **着手前に `blockers.md` 起票 3 を処理すること** —— issue 002/003/005/006 は
**何も取り込まなくても** `check_doc_lexicon.py` が exit 0 になる。`acceptance.sh` を書かないと
「客観に見えて無意味な緑」を量産する。

## §2 ⚠️★★★ 絶対にやらないこと

1. ⚠️★★★ **`git checkout` / `git switch` でブランチ `feat/resumption-outcome-arbitration` へ切り替えない。**
   main で作業し、`git checkout <branch> -- <path>` か `git show <branch>:<path>` を使う。
2. ⚠️★★★ **ブランチを丸ごとマージしない**（200 files / +26,924）。研究者が**案 C を採択済み**。
3. ⚠️ **`git add -A` / `git add <dir>` を使わない。**
   ⚠️★★★ **作業ツリーには常に別ブランチの未コミット作業がある。** パスを明示する。
4. ⚠️ **Proposed の ADR（003 / 005 / 008 / 009 / 010）を Accepted にしない。**
5. ⚠️ **ADR 本文を書き換えない。** 改訂は後続 ADR 側に書き、README の重ね書き注記で追跡する。
6. ⚠️ **`check_doc_lexicon.py` の `HISTORICAL` 許可パターンを勝手に緩めない。**
7. ⚠️ **既存のテストを無断で削除しない。**

## §3 ⚠️ 実行時に効く前提（忘れると空振りする）

- ⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**
  `cd src-tauri` するか `--manifest-path src-tauri/Cargo.toml` を付ける。
- ⚠️ **`check_citations.py` は違反を 1 回で全件出さない。**「違反なし」まで是正 → 再実行を繰り返す。
- ⚠️ **`metrics.rs` の識別子改名は `scripts/build_analysis_db.py` も同時に。**
  schema drift check の対象外で**無音で壊れる**。
- ⚠️ **OS ごとに規則が違うロジックは両 OS に対のテストを置く。**
- ⚠️ Hook はすべて bash 前提。Windows では **git-bash 必須**。

## §4 ⚠️ 作業規約（CLAUDE.md より・省略しない）

- Skill を先に読む: `architecture-rules` / `rust-standards` / `hook-constraints` / `data-privacy` / `git-workflow`
- サブエージェントへ委譲: 探索 → `file-finder` / 影響範囲 → `impact-analyzer` /
  テスト → `test-runner` / ビルド → `build-executor`。
  レビューは **`code-reviewer` + `security-checker` を並列**起動。
- ⚠️★★★ **`/cross-review` は各タスク完了時に必須**。skip した場合は**理由を完了報告に明記**。
  ⚠️ 無関係な未コミット変更で BLOCKED になるので
  `scripts/run-codex-review.sh -- <paths>` でパス限定して回す。
- ⚠️ **キーストローク内容・NDJSON 生ログを Codex（外部 LLM）へ送らない。**
- コミット: `[type]([scope]): [説明]` + 本文 + `Refs: .steering/20260911-<task>/`
- 応答は**日本語**で。

## §5 ⚠️★★★ 決着済み（★ 蒸し返さない）

1. **ADR-023〜028 は既に書かれている**（未マージブランチ）。新規に書かない。
   `.idea/20260907` の **`W-2` は ADR-027 が**、`.idea/20260908` の **`W-3` は ADR-028 が**既に閉じた。
2. **`KeyCategory` の `Punctuation` 追加は既に main にマージ済み**（`e14b6bd` PR #113）。
   `boundary-conditioned pause` は現行記録から計算できる。
3. **`HMM_VERSION` bump は不要**（ADR-024 が意図的に回避・実測確認済み）。
4. **特徴量の新 Tier は置換ではなく追加**（shadow feature として記録）。
5. **`M1〜M4` は撤回済み**（ADR-021 D11）。実体名で呼ぶ:
   **固定 baseline / criterion 直結 / 個人・タスク適応 / 時系列**。表記は **`MhD`**（ハイフン無し）。
6. **一般理論構想（`.idea/20260905`）は昇格させない**（研究者本人が明記・後続メモへの波及なしを確認済み）。
7. **O1 はまだ開始していない**（2026-09-11 時点）。だから T2 の issue 008/009 が間に合う。
8. **学習しているコードは現在 0 行**（`train(`/`.fit(`/`gradient`/`optimizer`/`linfa`/`smartcore` で 0 件）。
   ADR-008 の「β は母集団定数ハードコード」は 2026-09-11 現在も正しい。

## §6 ★ T3 / T4 に進むとき（T1 完了後）

⚠️ **issue が無いので、まず `_survey-*.md` を読んで `issue-slicing` で分解する。**

### T3 `20260911-mhd-inference-ssot`
一次資料: `_survey-inference-architecture.md`
⚠️★★★ **最大の争点は ADR-008 D8 と WP5 I2 の正面衝突**
（D8「専用の特徴選択機構を作らない」vs I2「個人別 feature subset を選ぶ」）。
新規 ADR で D8 を部分改訂しない限り SSOT 化できない。
⚠️ 受け皿は**新規ファイルではなく `personalization-and-online-learning.md`（1401 行）への統合**
（`Layer 4` 専用文書が存在せず、新規作成すると重複して曖昧になる）。

### T4 `20260911-practice-portrait-ssot`
一次資料: `_survey-20260908-claims-and-evaluation.md` / `_survey-20260908-form-and-os-constraints.md`
⚠️ **`Temporal Primitive` の定義が同一メモ内で食い違う**（§3.4 の 7 項目 vs §4.8 の 6 項目）。
⚠️ **§4.8–4.10 に層ラベルが無く、Layer A 契約と衝突して見える**ので各節に層ラベルを付け直す。
⚠️ **造形は凍結しない**（試視が先）。A 区分は規約・境界・禁止事項・主張範囲のみ。
