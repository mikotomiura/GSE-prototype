# 新セッション冒頭に**そのまま打ち込む**プロンプト — issue 001 の pause 閾値裁定（Opus）

> 作成: 2026-09-15 / ★ **下のコードブロックの中身をコピーして、新セッションの最初の発話に貼る。**
> ⚠️ このファイル自体は一次資料ではない。★ 詳細な経緯・3案・裁定後の手順は
> `.steering/_handoff/next-session-issue001-pause-const-arbitration.md` にある。

---

## ★ 貼り付ける本文（ここから）

```text
issue 001（gse-replay --features / T0 activity）が Stop Conditions で止まった。
pause 閾値の扱いを裁定する。

## 実行条件（⚠️ 守る）
- 応答はすべて日本語で。
- モデルは Opus（設計判断のため）。
- ブランチは docs/adr-030-stall-onset-definition。main へ switch しない
  （ADR-030 / 031 / 032 はこのブランチにしか無い）。
- git add -A / git add <dir> を使わない。

## まず読む（★ 一次資料・再導出しない）
1. .steering/_handoff/next-session-issue001-pause-const-arbitration.md  … ★ 詳細版(経緯・3案・裁定後の手順)
2. worktree(証拠保持中) の Execution Result:
   C:/wt/GSE-prototype-001-issue/.steering/20260914-mhd-feature-offline-tiers/issues/001.md
   … worker の調査結果の原文（⚠️ main 側の同名ファイルは queued のまま更新されていない）
3. .steering/20260914-mhd-feature-offline-tiers/_issue-plan.md
4. docs/adr/ADR-030-stall-onset-and-decision-episode.md の D1 / D3 / D10 / D11
5. docs/loop-engineering.md

## 前セッション(2026-09-14/15)までに分かっていること(⚠️ やり直さない)
- issue 001 を Loop モード C で実行 → 6 attempt すべて acceptance_fail → abandoned
  (_loop-run-report.md: cost $3.528222 / 7,792,190 tokens)。
- worktree にコード変更ゼロ（feat_offline/ ディレクトリ自体が存在しない）。
- worker は features.rs に pause 閾値の named constant が無いことを理由に、
  issue 001 の Stop Conditions 3 番目に該当すると判断して停止した
  （issue.md の Execution Result に調査結果あり・worktree 側にのみ存在・未コミット）。
- ★ 前セッションでの推奨は案1（features.rs の既存リテラル 2000（4 箇所）を
  pub const に一本化する先行 issue を切り、Allowed Files に features.rs を加えて
  issue 001 を再発行する）。他に案2（intervention.rs::SHORT_PAUSE_MIN_MS の転用を
  ADR-030 に一文追記して裁定）／案3（AC 6 を撤回・改訂）がある。3 案とも詳細版 §3 に
  比較して並べてある。
- worktree（C:/wt/GSE-prototype-001-issue）は証拠として残してある（cleanup していない）。

## やること
1. 3 案（推奨=案1）を読み、ADR-030 D1 の射程（命名だけの最小リファクタまで禁じているか）
   を本文で確認したうえでどれを採るか裁定する。
2. .steering/20260914-mhd-feature-offline-tiers/decisions.md に裁定を記録する。
3. 裁定に応じて issue 001（または新規先行 issue）を改訂する。
4. worktree を cleanup する: bash scripts/loop-spawn.sh --cleanup 001-issue
5. issue を Loop モード C で単独再実行する:
   bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001
   （案1 なら先に --issues 000）

## ⚠️ 実行条件（継続・変更なし）
- allowed_tools を null にしない。
- .gitignore の _loop-events.jsonl / _loop-board.md / _loop-run-report.md を外さない。
- HMM_VERSION を bump しない／ゴールデン snapshot を再生成しない。
- schema_dto.rs / logger.rs / capabilities.rs を触らない。
- features.rs / engine.rs / loop_step.rs の変更は原則禁止（★ 案1 の例外可否は
  ADR-030 D1 本文で確認してから裁定する）。

まず詳細版と worktree の Execution Result を読み、読めたことと 3 案の要点を
報告してから裁定に入ること。
```

## ★ 貼り付ける本文（ここまで）
