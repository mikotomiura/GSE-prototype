# 次セッション — G1 / O1 の残タスクの棚卸し（★ 判断 4 の反映の次）

> 作成: 2026-09-20。前段: `.steering/20260920-decision4-reflection/`（判断 4 の反映・完了）。
> ★ 順序は `.steering/_handoff/next-session-decision4-reflection.md` §5 の案（2026-09-20 の相談で合意・研究者が変えてよい）のとおり。
> ⚠️ 本メモは一次資料ではない。★ 書いてある「状態」は 2026-09-20 時点のもので、**着手時に一次で確かめ直す**。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-g1-o1-inventory.md を読んで、G1 / O1 の残タスクの棚卸しをしてください。
まず /start-task を起動し、grill で範囲（棚卸しだけか・どこまで片づけるか）を研究者と確定してから進めてください。
既存の引き継ぎはどれも段 3 より古いので、状態は一次（コード・スクリプトの実行・ADR・事前登録）で確かめ直すこと。
設計判断は Opus、機械的な作業は Sonnet。サブエージェントは実装・操作は sonnet、レビュー・企画は opus で起動する（model を毎回明示・操作系は入れ子にしない）。
応答は日本語。ブランチ docs/adr-030-stall-onset-definition のまま、main へ switch しない。git add -A / git add <dir> は使わない。
```

## §1 ★ 研究者への質問（判断 4 の反映で起票・4 件・★ 推測で埋めない）

★ 一次は `.steering/20260920-decision4-reflection/decisions.md` **判断 8**（Q1〜Q4）。

| # | 問い | 締切 |
|---|---|---|
| Q1 | G1 の収集開始の前提条件 7（途中でやめた人の途中までの記録の数え方）に、(i) 本人の申し出以外で完了しない人（技術的な中断・連絡の途絶）、(ii) やめた後 / 完了後に削除を求めた人、(iii)「中断」と「やめる」の区別・申し出の取り消し、を含めるか。★ 前提条件 7 の中身（(a) §3.6 の同意撤回に当たるか・(b) n に数えるか・(c) 補充するか）と一緒に決める。★ 計器の現在の挙動（`validate_blocks.py` は一部だけ記入を FAIL・`analyze.py` は 8 本未満を `skipped` にし名簿の人数では数える）と突き合わせる | G1 の収集開始の前 |
| Q2 | ADR-034 D3 の「G1 の最初の配布」はどの配布か（★ リブート前の P-1 = `v0.1.22`・P007 / P014 / P016 = `0.1.29` を含むか）。★ Migration 3（タグの記録先）と一緒に決める | G1 の次の配布の前 |
| Q3 | CORE-CS の「テストの中の陽性対照」（判断 4 #8 で EH1 の支持に数える）は `#[cfg(test)]` に限るか。`gse-replay` のフラグや cargo の feature を含むか | `OnlineUpdater`（ADR-008）の実装時 |
| Q4 | 研究者本人のパイロット（`EH2`）や開発者の日常利用で Nudge を出すことは、IDE の見直し候補 R-1 の「Nudge を被験者に出す研究」に入るか | R-1 を決めるとき |

## §2 棚卸しの対象（★ 状態は未確認 —— 一次で確かめ直す）

### G1
- 収集開始の前提条件 **1〜7**（事前登録 第 17 版 1〜4・第 18 版 5〜6・第 19 版 7）。⚠️ **どれも `run.sh` では機械検査していない**（`run.sh` の緑は「技術的な準備だけ」）。
- ADR-034 **Migration 3**（G1 の最初の配布のタグの記録先）＋ Q2。
- ⚠️ **ADR-034 D1 の律速 4**: 案内日の分離（D6）が **G1 の募集の手順にまだ入っていない**（`experiments/20260801-controlled-friction-task/README.md` §6.3 は 2026-08-03 の順序図）。確認の置き場も無い（`check-o1-release-readiness.sh` に D6 の検査は 0 件）。
- ⚠️ **`run.sh` は Windows の既定のエンコーディング（cp932）で赤になる**（`[1]` の `json.load(open('config.json'))` に `encoding` が無い・`check_g1_emails.py` も同じ）。`PYTHONUTF8=1` で全項目通過。この要件はどの文書にも無い。
- ⚠️ `config.json` の `status` が `CONFIRMATORY_IN_PROGRESS_1_OF_3` のまま（実際は 0/3 名・読むコードは無い）。
- G1 モードでも週の選択画面が出て、コードでは第 1 週（介入なし）を強制しない（手順と既定値だけ・IDE R-1 の注記）。

### O1
- ADR-031 / ADR-032 の Accepted（同意文書 §3 の改訂 = 研究者承認）・`scripts/check-o1-release-readiness.sh` の緑。
- ADR-034 **Migration 6**（O1 の事前登録に「G1 のログを入力に取ったら止まる」検査を、O1 の最初の配布より前に書く）。
- ⚠️ 募集と配布のゲートが分かれた（ADR-034 D2 / D1）ので、**配布できない間に募集した O1 の参加者へ何を約束するか**が書かれていない（Codex 2 巡目 X3・⚠️ 被験者向け文書は契約）。

### 共通
- ⚠️★ ブランチ `docs/adr-030-stall-onset-definition` は main より大きく先行している（2026-09-20 に 132 コミット・判断 4 の反映で +8）。★ 配布物はリリースタグ（`v*` の push）から作るので、G1 / O1 の配布の前に **main へのマージの計画**が要る。
- ⚠️ schema parity: `activity_label` が gse-dataset 側に無い（drift）。★ 既知の保留（`.steering/20260913-esm-audit-criterion-gate/decisions.md` 判断 3「同期は本ブランチのマージ後」）。★ マージの計画と一緒に扱う。
- 既存の引き継ぎ（★ どれも段 3 より古い）: `g1-o1-precollection-findings.md`（2026-09-01）・`next-session-post-adr032-approvals-and-parallel-tracks.md`（2026-09-14）・`next-session-o1-consent-secondary-use.md`（2026-09-13）。

## §3 その後（★ `next-session-decision4-reflection.md` §5 のまま）

- 文献ラウンド（1 本）: SR の Semantic Scholar 取得失敗 7 本の再実行 ／ 差分の候補（未検証）4 つの補足の検索（判断 4 #10 —— 外部の文書で差分を主張する締切が先なら前に出す）／ S3 → 理論名（判断 4 #9）。
- 任意: SSOT の本体（ADR-033 / 034 / 035・RP §4）を Codex で 1 巡。

## §4 ⚠️ 守ること

- ★ `/start-task` から。判断は `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ ADR の本文・事前登録 §3 は書き換えない。被験者向け文書（同意文書・`participant-setup-guide.md`）は契約 —— 変える必要が出たら研究者へ返す。
- ⚠️ 配布（`make-distribution.sh` / `make-common-app-zip.sh`）はモードとタグを確かめてから（ADR-034 D3・Q2）。
- ★ 完了時に `/cross-review` 2 巡（`scripts/run-codex-review.sh <range> -- <paths>` でパス限定。Codex は repo を読めない）。`.codex/budget.json` を `git checkout --` しない。
- ⚠️ `git add -A` / `git add <dir>` 禁止。NDJSON 生ログ・キーストローク内容を外部 LLM に送らない。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋ `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
