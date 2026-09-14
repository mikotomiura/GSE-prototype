# 新セッション冒頭に**そのまま打ち込む**プロンプト — タスク 2 の Loop 実行（モード C 初回・Sonnet）

> 作成: 2026-09-14 / ★ **下のコードブロックの中身をコピーして、新セッションの最初の発話に貼る。**
> ⚠️ このファイル自体は一次資料ではない。★ 詳細な罠と復旧手順は
> `.steering/_handoff/next-session-loop-run-task2.md`（150 行）にある。

---

## ★ 貼り付ける本文（ここから）

```text
タスク 2（MH-D 特徴量のオフライン層分け）の Loop 実行を行う。モード C の初回。

## 実行条件（⚠️ 守る）
- 応答はすべて日本語で。
- 実行制御は Sonnet。/model sonnet になっていることを確認してから始める。
- ブランチは docs/adr-030-stall-onset-definition。
  ⚠️★★★ main へ switch しない。ADR-030 / 031 / 032 はこのブランチにしか無く、
  _loop-config.json の base_branch もこのブランチに pin してある(main から切ると全 issue が即死する)。
- git add -A / git add <dir> を使わない。作業ツリーに別ブランチの未コミット作業がある。
- 実装は自分で書かない。Loop の worker が書く。あなたは実行制御と events の読解を行う。

## まず読む(★ 一次資料・再導出しない)
1. .steering/20260914-mhd-feature-offline-tiers/_issue-plan.md   … DAG / 交差表 / 実行前の前提
2. .steering/20260914-mhd-feature-offline-tiers/issues/001.md     … AC と Stop Conditions の SSOT
3. .steering/_handoff/next-session-loop-run-task2.md              … ★ 罠 5 件と「止まったときの読み方」表
4. .steering/_template/loop-config.README.md                      … ★ 落とし穴集
5. docs/loop-engineering.md                                        … Loop の単一 SSOT

## 前セッション(2026-09-14)までに済んでいること(⚠️ やり直さない)
- 2z(Loop 基盤整備)は実装完了・コミット済み(56d4e58)。
  scripts/loop-worktree-deny.sh 新規 + loop-spawn.sh / loop-run.sh へ配線 + CI 2 箇所 + 24 検査。
  code-reviewer / security-checker / cross-review の HIGH・MEDIUM・LOW を全件反映済み。
- モード C が 1 issue 目で必ず死ぬ実バグを発見・修正済み(29a19c1 / a75bfda)。
  loop-run.sh が作る _loop-events.jsonl が spawn 側の dirty-tree 判定に自分で当たっていた。
  → .gitignore に Loop の実行時生成物 3 件を追加して解消。
- タスク 2 の issue 分解完了(縦切り 7 本 + 各 acceptance.sh + _loop-config.json)。
- コミット 5 本(56d4e58 / a75bfda / 29a19c1 / e326c4f / 365a8a6)。⚠️ push はしていない。
- _loop-events.jsonl は 0 バイト = Loop は一度も走っていない。

## ★★★ 最初にやること — 001 だけを単独で回す

  bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001

SSOT 逐語「新しい実行モードを初めて使う時は、最も安い issue 1 本を parallel=1 で回して基盤を検証する」。

★ 001 は「gse-replay --features の新設 + T0(基本 activity)」で、AC は 10 項目、verify_level は recheck。
★ 同時に これが 2z の実地検証を兼ねる。
  ⚠️★★★ 「注入されていること ≠ 発効していること」は未検証である。
  claude -p が worktree の deny を実際に読んで git push を拒むかは、まだ誰も確かめていない
  (56d4e58 のコミットメッセージが「未検証(隠さない)」として明記している)。
  → 予測しない。events を実際に読んで確かめる。

## 001 が終わったら events を人の目で読む

  cat .steering/20260914-mhd-feature-offline-tiers/_loop-events.jsonl | jq -c .

見るべきもの:
- permission_denials= を含む行            … 何が拒否されたか = allowed_tools の過不足
- WARN: … permissions.deny が失われていた  … worker が安全設定に触ったか(= 毎 attempt 再注入が効いたか)
- issue_done の前に acceptance 段が通っているか … verify が緑でも AC 未充足なら止まる
⚠️ issue_done を自己申告で信じない。recheck の 3 本(001 / 005 / 007)は watchdog の客観再検証を通る。

## 001 が緑なら残りを回す

  bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers

⚠️ --parallel を上げない。交差表(_issue-plan.md §3)のとおり並列可能な組は 1 つも無い。
★ 監視は /loop-status(board の単一書き手)。

## ⚠️★★★ 絶対にやらないこと
1. main から worktree を切らない。
2. features.rs / engine.rs / loop_step.rs を変更しない(ADR-030 D1)。
3. HMM_VERSION を bump しない / ゴールデン snapshot を再生成しない。
4. undo / redo / key.mod を実装しない(ADR-032 が Accepted になり同意 §3 改訂 M4 が通るまで。研究者承認待ち)。
5. schema_dto.rs / logger.rs / capabilities.rs を触らない(= 計器変更)。
6. allowed_tools を null にしない(無人実行がコード 0 行で即死する。実測 2 回・約 $11)。
7. .gitignore から Loop の実行時生成物を外さない(★ 外すと 1 issue 目で全滅する)。
8. --dry-run の結果で権限・cwd 境界・hook 発火を判断しない(観測できない。実測 2 回空振り)。

## ⚠️ 止まったときは
next-session-loop-run-task2.md §4 の表を読む(blocked / no_progress_stop / abandoned の意味と次の手)。
★ issue の ## Stop Conditions に当たったら設計判断が要るということなので、
⚠️ Sonnet の実行セッションで決めない。/clear して Opus で裁定する
(特に 004 の undo/redo と 005 の ADR 曖昧さ)。

## 全緑後
code-reviewer + security-checker を並列起動 → /cross-review(2 巡) → _loop-retrospective.md。
⚠️ main へのマージは研究者判断。

まず上記 1〜5 を読んで、読めたことと 001 の AC の要点を報告してから実行に入ること。
```

## ★ 貼り付ける本文（ここまで）

---

## 補足 — なぜ「2z」ではなく「タスク 2 の Loop 実行」と書いたか

★ 研究者の認識では次が「2z」だったが、一次資料で確認した結果は次のとおり。

| 項目 | 実体 | 根拠（一次） |
|---|---|---|
| 2z の**実装** | ★ **完了・コミット済み** | `56d4e58`（scripts 3 本 / CI 2 箇所 / 24 検査 / レビュー 3 系統反映） |
| 2z の**実地検証** | ⚠️ **未了** | `56d4e58` 本文「未検証（隠さない）… 着手順 4『最も安い issue 1 本を parallel=1 で回す』が担う」 |
| MH-D 特徴量再設計 | ★ **issue 分解まで**完了。実装はこれから | `.steering/20260914-mhd-feature-offline-tiers/issues/001〜007.md` |
| Loop の実行実績 | ⚠️ **ゼロ** | `_loop-events.jsonl` が 0 バイト |

→ ★ **次セッションで 001 を回すことが、そのまま 2z の残り（発効の実測）を閉じる。**
⚠️ 2z を「もう一度実施」してはならない（★ 再導出すると `loop-worktree-deny.sh` を二重に書くことになる）。

## 関連ファイル

- `.steering/_handoff/next-session-loop-run-task2.md` — ★ 詳細版（罠 5 件・復旧表・宿題リスト）
- `.steering/20260914-loop-foundation-worktree-deny/` — 2z の作業記録
- `.steering/20260914-mhd-feature-offline-tiers/` — タスク 2 の作業記録（issues / config / DAG）
