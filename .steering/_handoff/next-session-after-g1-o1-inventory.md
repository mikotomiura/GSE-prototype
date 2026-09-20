# 次セッション — 棚卸しの後（★ 研究者判断 2 件と、マージ → タグ の 2 本）

> 作成: 2026-09-20。前段: `.steering/20260920-g1-o1-inventory/`（棚卸し・完了）。
> ⚠️ 本メモは一次資料ではない。★ 台帳は `.steering/20260920-g1-o1-inventory/inventory.md`、
> その根拠は同 `evidence.md`。⚠️ **着手時に一次で確かめ直すこと**（★ 状態は 2026-09-20 時点）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/20260920-g1-o1-inventory/inventory.md の台帳から続けてください。
まず /start-task を起動し、grill で今回の範囲（下の A / B のどちらを・どこまで）を研究者と確定すること。
状態は一次（コード・スクリプトの実行・ADR・事前登録）で確かめ直す。台帳自体も未検証メモとして扱う。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。ブランチ docs/adr-030-stall-onset-definition のまま、main へ switch しない。
git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ★ 2026-09-20 に研究者が決めたこと（★ 蒸し返さない）

| # | 決定 | 一次 |
|---|---|---|
| Q1 | 前提条件 7 の範囲に **(i)(ii)(iii) を全部含める** | 判断 1 |
| Q2 | 「G1 の最初の配布」＝ **リブート後の次の配布**（P-1 `v0.1.22` と P007/P014/P016 `0.1.29` は含めない） | 判断 2 |
| Q3 | 「テストの中の陽性対照」は **`#[cfg(test)]` に限る**（`gse-replay` のフラグ・cargo の feature は含めない） | 判断 3 |
| Q4 | R-1 の「被験者」に **研究者本人（`EH2`）・開発者は入らない** | 判断 4 |

★ 一次: `.steering/20260920-g1-o1-inventory/decisions.md`。Q3 / Q4 は本文（CORE-CS `:95`・IDE R-1）へ反映済み。

## §2 ⚠️ いちばん重い残り = **研究者にしか決められない 2 件**

1. **G1-1: 前提条件 7 の中身（9 マス）** —— (a) §3.6 の同意撤回に当たるか / (b) n に数えるか /
   (c) 補充するか × (i) 本人の申し出以外で完了しない人 / (ii) やめた後・完了後に削除を求めた人 /
   (iii)「中断」と「やめる」の区別・申し出の取り消し。
   ⚠️ **締切 = G1 の収集開始の前**。★ 記録先は事前登録の**改訂履歴（第 20 版）**＋ `config.json` の
   `revision`（⚠️ **§3 には書かない** = 凍結）。
   ★ 決めるときに突き合わせる計器の挙動（★ 3 つが別々の答えを出している）は
   `evidence.md`「Q1 の材料」に逐語で置いた。
2. **O1-1: ADR-031 / ADR-032 を Accepted にする**（= O1 の同意文書 §3 改訂の承認）。
   ⚠️ 両 ADR とも **Proposed のまま**。承認マーカ `<!-- o1-esm-consent: approved -->` は未挿入。
   ★ これが O1 配布ゲートの赤 ① であり、O1 のすべての律速の先頭。

## §3 ★ 研究者を待たずに走れる 2 本

### A. main へのマージ → 新しいタグ（★ 手順書あり）
`.steering/20260920-g1-o1-inventory/merge-plan.md` のとおり。要点:
- 衝突は **`.steering/_handoff/README.md` の 1 件だけ**（`git merge-tree` で実測）。
- ⚠️ **schema 同期を飛ばさない**（`activity_label` の drift は**本ブランチが生んだもの**）。
- タグを打ったら **G1 の「最初の配布」のタグとして記録**（ADR-034 Migration 3 / 判断 2）。
  ★ 記録先（`data.md` / `config.json` / `notes.md` のどれか）は**配布タスクで決める**。
- ⚠️ 配布スクリプトの既定タグは古い（`v0.1.23` / `v0.1.24`）。`--tag` を必ず付ける。

### B. 前提条件 1〜6 の「確かめ方」を決める（★ 機械検査が 1 つも無い）
⚠️ `run.sh` の緑は**技術的な準備だけ**で、前提条件 1〜7 を 1 つも見ていない（実測）。
→ ★ 1 / 2 / 4 / 6 は機械検査に落とせる可能性がある（3 / 5 / 7 は人手 or 研究者判断）。
★ 落とすなら **置き場は `run.sh` ではない**（run.sh は「技術的な準備だけを見る」と自ら宣言している）。
⚠️ D6 の検査を `check-o1-release-readiness.sh` に置いた判断 7 と同じ考え方で決めること。

## §4 ⚠️ 本タスクで**やらなかった**こと（★ 誤解しない）

- ⚠️ **マージの実行**・**タグの push**・**配布の実行**（すべて計画まで）。
- ⚠️ **事前登録の第 20 版の起草**（★ 中身は研究者の裁定。範囲だけ決まった）。
- ⚠️ **被験者向け文書の改訂**（O1-5「募集してから配布までの間の約束」を含む）。
- ⚠️ `.worktrees/codex-rescue-20260916-theory-review/` の削除（★ 研究者の作業物なので触らない）。
  ★ 残っていてもゲートは緑（判断 6）。

## §5 ★ 本タスクで直したもの（★ 再発したらここを見る）

| 何 | どこ |
|---|---|
| cp932 で `run.sh` が偽の赤 2 件 | `run.sh` の inline python ＋ `check_g1_emails.py` の subprocess（`encoding` 明示）／出力は `PYTHONIOENCODING` |
| 移植性ゲートが入れ子 worktree で rc=2 | `check-shell-portability.sh` の `NESTED` 別枠 ＋ 出力の UTF-8 固定 |
| 上記に隠れていた**本物の違反 1 件** | `007-acceptance.sh:94` の `($OLD・` → `(${OLD}・` |
| ⚠️ selftest の**未定義関数 `clear_pending`**（本タスク以前から・該当ケースが空回りで緑） | `check-o1-release-readiness.sh` の selftest に定義を追加 |
| D6 の確認場所が無い（ADR-034 D1 律速 4） | `check-o1-release-readiness.sh [5]` ＋ G1 README §6.3 ＋ 両文書のアンカー。selftest **7 ケース** |

★ ゲートの現在値（2026-09-20 実測）: `run.sh` = **exit 0** ／
`check-shell-portability.sh` = **exit 0** ／ `check-o1-release-readiness.sh` = **exit 1・通過 21 / 未達 2**
（★ 残り 2 は正しい赤: 同意未承認・タグ陳腐化）／ 同 `--selftest` = **通過 57 / 失敗 0**。

## §5b ⚠️★★ 受けていないレビューが 1 系統ある（★ 先に片づける）

`code-reviewer`（Claude 側の一般的なコード品質レビュー）は **25 分走った末に Bash で停止し、
結果を 1 行も返していない**（★ `.steering/20260920-g1-o1-inventory/decisions.md` 判断 12）。
⚠️ **「指摘なし」ではなく「結果が無い」**。

→ ★ 次セッションの最初に **`/review-changes` を `5b37b3b..HEAD`** に対して回すこと。
⚠️ そのとき **「コミット済みの範囲だけを見る・作業ツリーを触らない・隔離クローンを作らない」**を
プロンプトに明記する（★ 今回の長時間化の原因がそれだった）。

★ 受けている担保: `security-checker`（opus・HIGH 2 点反映済み）／`/cross-review` 2 巡（Codex）／
ゲートの selftest **57 件**。

## §6 ⚠️ 守ること

- ★ `/start-task` から。判断は `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ ADR の本文・事前登録 §3 は書き換えない。被験者向け文書は契約 —— 変える必要が出たら研究者へ返す。
- ★ 完了時に `/cross-review` 2 巡（`scripts/run-codex-review.sh <range> -- <paths>` でパス限定）。
- ⚠️ `git add -A` / `git add <dir>` 禁止。NDJSON 生ログ・キーストローク内容を外部 LLM に送らない。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
