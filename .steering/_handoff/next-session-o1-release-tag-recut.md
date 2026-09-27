# 次セッション — O1 リリースタグを切り直す

> 作成: 2026-09-27（`.steering/20260927-precondition8-t3-and-consent/` 完了直後・main=`02272e0`）。
> ⚠️ **このメモを一次資料にしない。** 数字・状態は着手時に測り直す。
> ★ **`.steering/_handoff/next-session-loop-run-progress-flag-bug.md` と並行実行可能**
>   （触るファイルが完全に別: 本タスクはリリース/ビルド系のみ・loop-run.sh には触れない）。

## §0 打ち込む用

```
.steering/_handoff/next-session-o1-release-tag-recut.md を読んで、次を進めてください。
O1 リリースタグを切り直し、bash scripts/check-o1-release-readiness.sh の
「リリースタグが古い」失敗を解消してください。
⚠️ まず git pull --ff-only。/start-task（task 名: o1-release-tag-recut）を実行し、
   grilling skill で残りの判断分岐（バージョン番号・G1/O1 どちらのタグにするか等）を閉じる。
★ タグ push は研究者承認が要る（v0.1.36 のときと同じ手順）。
Skill: verify-before-claiming・git-workflow。
応答は日本語。
```

## §1 現在の状態（2026-09-27・測り直し済み）

| 何 | 値 |
|---|---|
| main | `02272e0`（PR #237 merge 直後） |
| O1 ゲート | 通過 22 / 未達 2（`bash scripts/check-o1-release-readiness.sh`） |
| G1 ゲート | 通過 23 / 未達 3（記録票 A/B/C のみ・研究者の実地確認待ち・本タスク対象外） |

## §2 課題（一次で確認済み）

`bash scripts/check-o1-release-readiness.sh` の未達 2 件のうち 1 件がこれ:

```
❌ ⚠️★★★ リリースタグ v0.1.36 は **古い**。★ タグ以降にコードが 5 コミット動いている
   （★ 配るバイナリにその修正が入らない）:
      53e98b6 fix(reconcile): 2 巡目レビューを反映する
      a94e0ac docs(reconcile): 所有確認の限界を正直に書き直す
      914e88f fix(reconcile): ロックに所有印を持たせる
      016b5f2 fix(reconcile): レビュー指摘を反映する
      a819f0d fix(reconcile): ロックの stale 判定を heartbeat にする
   → ★ 再ビルドして新しいタグを切ること。
```

★ この 5 コミットは PR #233「fix(reconcile): O1 の滞留でロックを奪われないようにする
（heartbeat ＋ 所有印）／v0.1.36 を G1 の配布タグとして記録」で **main に merge 済み**
（`.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md` に実装・2 巡レビュー
・Codex cross-review 2 巡の記録あり）。★ **実装は完了しており、タグを切り直すだけ**でよい。

もう 1 件の未達（同意文書の「未了」項目＝6択ESM追補の採否）は**別件・研究者判断待ち**。
本タスクの対象外（触らない）。

## §3 手順（v0.1.36 のときと同じ・`experiments/20260801-controlled-friction-task/distribution-tag.md` が記録形式の型）

1. 状態を測り直す: `bash scripts/check-o1-release-readiness.sh` / `bash scripts/check-g1-collection-readiness.sh`（両方回して他に何か増えていないか確認）。
2. バージョン番号を決める（研究者に確認: 0.1.37 が妥当か。4 ファイルの整合を確認する手順は
   `.steering/20260927-g1-o1-release-and-o1-resilience/` の T1 節を参照）。
3. 研究者承認のもとタグを push（`git tag vX.X.XX <sha> && git push origin vX.X.XX`）。
4. CI（`build-macos` / `build-windows` / `release`）が全部 success になるまで待つ。
5. Release 成果物の実体検証（署名・バージョン文字列・対照の有無を byte レベルで確認。
   `distribution-tag.md` の「実体で確かめたこと」節と同じ厳密さで）。
6. ⚠️★★★ **O1 用の配布物を作る**（G1 用とは別）。`distribution-tag.md` の注記
   「O1 の配布物は O1 用の別タグで作り直す（ADR-034 D3・ADR-031 M9）」に従う。
   `make-common-app-zip.sh --mode o1 --tag vX.X.XX` のような形になるはず
   （⚠️ 実際のスクリプトのフラグ名は一次で確認すること。記憶で書かない）。
7. `docs/o1-deletion-ledger.md` や `distribution-tag.md` に相当する O1 側の記録ファイルへ
   append-only で記録する（★ 型は `distribution-tag.md` を参照。O1 専用の記録ファイルが
   無ければ新設が必要かもしれない — 一次で確認）。
8. `bash scripts/check-o1-release-readiness.sh` を再実行し、「リリースタグが古い」が消えたことを確認する。

## §4 やらないこと

- 同意文書の「未了」（6択ESM追補）の採否判断（別件・研究者へ）。
- G1 側の記録票 A/B/C（研究者の実地作業）。
- `20260927-g1-o1-release-and-o1-resilience/` の T3（GAS プロジェクト管理提案）— 別タスク。
- reconcile.rs のコード変更（既に完了済み・触らない）。

## §5 一次資料（読む順）

1. `bash scripts/check-o1-release-readiness.sh` を実際に実行して現状を測り直す
2. `experiments/20260801-controlled-friction-task/distribution-tag.md`（v0.1.36 の記録・型）
3. `.steering/20260927-g1-o1-release-and-o1-resilience/decisions.md`（T1・T2 の実装記録）
4. `.steering/20260927-g1-o1-release-and-o1-resilience/tasklist.md`（T1 の手順の実績）
5. `scripts/check-o1-release-readiness.sh`（ゲートが何を見ているか）
