# 次セッション — issue 004（`T1c`）/ 006（`T1d`）★ タスク 2 の再開順 ④

> 作成: 2026-09-20。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/issues/004.md` / `006.md`（**本文の「推奨」表**）／
> 同 `decisions.md`（**判断 25 #9 / #10 / 判断 26**）／
> `docs/theory/` の `definitions-restop-t1d-t1c.md` ／ `src-tauri/src/analysis/feat_offline/`。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-issues-004-006-arbitration.md を読んで、issue 004（T1c）/ 006（T1d）を実施してください。
⚠️ まず「未裁定」9 論点（U1〜U4 / V1〜V5）を裁定してください。★ すべてに「推奨」が既に書いてあるので、
裁定は「推奨を承認するか、対案に倒すか」を 9 回答えるだけです（新しい設計をゼロから起こす作業ではありません）。
裁定が終わり `grep -c 未裁定` が 0 になってから実装に入ってください（判断 26 の着手条件）。
状態は一次（issues/004.md・006.md の本文／feat_offline/ の実装）で確かめ直すこと。台帳も引き継ぎも未検証メモとして扱う。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ⚠️ なぜこれが次なのか（★ 2026-09-20 に一次で確かめた）

★ タスク 2 の**再開順は研究者が確定済み**（判断 25）:

```
① 理論レビュー        ✅ 完了（.steering/20260918-theory-critical-review/）
② Loop 基盤の修正     ✅ 完了（.steering/20260920-loop-foundation-fixes/）
③ 封筒 issue（起票 2 / 5）  ✅ **完了**（.steering/20260920-envelope-issues/）
④ 004（T1c）/ 006（T1d）  ← ★ ここ
⑤ capability matrix（ADR-032 M7）
⑥ P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）
```

★ **③ が終わったので、全 acceptance の前提はもう動かない** ——
⚠️ 封筒（`{ provenance, config, rows }`）は **8 本すべてを 1 度だけ書き換え済み**で、
`004` / `006` の acceptance も**配列前提は解消してある**。
→ ★ **いま 004 / 006 が赤いのは「自分の Tier が未実装」だからだけ**である（2026-09-20 実測）:

```
004  NG: 全行に revision の必須フィールドが揃っていない
006  NG: 全行に restart の必須フィールドが揃っていない
```

## §2 ⚠️ 着手条件（★ 判断 26。満たすまでコードを書かない）

```bash
grep -c 未裁定 .steering/20260914-mhd-feature-offline-tiers/issues/004.md   # → 0 になるまで着手しない
grep -c 未裁定 .steering/20260914-mhd-feature-offline-tiers/issues/006.md   # → 同上
```

★ 2026-09-20 時点の実測: **004 = 6 件 / 006 = 5 件**。

⚠️★★★ **すべてに「推奨」が既に書いてある。** ★ 裁定は
**「推奨を承認するか、対案に倒すか」を 9 回答えるだけ**である。
★ 裁定したら、各行の「推奨（⚠️ 未裁定）」を **「★ 裁定: …（判断 N・日付）」へ書き換える**
（⚠️ 見出しの「（未裁定・2026-09-19）」も外す）。

### ★ issue 004（`T1c` = 削除と挿入の遷移の形）U1〜U4

| # | 論点 | 推奨 | 対案 |
|---|---|---|---|
| U1 | 削除の走りを**切る press**（挿入でも削除でもない press = `navigation` / 修飾キー） | 削除系以外の press は**すべて切る** | 挿入系だけが切る |
| U2 | `category_bigram_repeat_rate` の**式**（例 AA, AA, AB） | **1 − 種類数 ÷ 総数**（= 1/3） | 2 回以上現れる種類に属する出現の割合（= 2/3） |
| U3 | 走り・burst 単位の値を載せる **tick** | **閉じが確定した時点の tick**（causal・未来が漏れない） | 最後の press の tick ／ 次の burst の最初の press の tick |
| U4 | 走りの**最小の長さ** | **1 から** | 2 から |

⚠️ U2 はどちらの式でも `Alphabetic` が大半のため **burst 長と強く相関する**。

⚠️★★★ **呼び名に注意**: `T1c` の旧ブロック名「revision topology」は **2026-09-19 に廃止**され、
★ **「削除と挿入の遷移の形」**と呼ぶ（ADR-030 補訂 1 項目 9・`docs/glossary.md`）。
⚠️ **コードの識別子 `revision` を改名するかは実装フェーズの未決**（★ acceptance は `revision` を見ている）。

### ★ issue 006（`T1d` = 再開）V1〜V5

| # | 論点 | 推奨 | ⚠️ なぜ決まらないか |
|---|---|---|---|
| **V1** ★★★ | **E1 の集計窓と実装順** | 検出列は変えず、E1 は `recovery` と同時に**別層**で入れる。それまでは E2 の窓で数え、後から感度分析 | ⚠️ `recovery` が `feat_offline` に**未実装**。このまま E1 を検出列に入れると**同じ観測区間で最初の onset しか立たない** |
| V2 | **条件 A の辺の取り出し方** | `stall_onset.rs` から `pub(crate)` で出す（Allowed Files に追加）。右端ちょうどは `t0 <= b` と対称に | ⚠️ 条件 A は `stall_onset.rs` の**非公開関数**。現状の Allowed Files だと**定義が二重になる** |
| V3 | **fixture** | `stall_onset_observed.ndjson` へ差し替え、正解値を参照実装で確定 | ⚠️ `deep_silence.ndjson` は issue 008 以後 onset が立たず **AC6 が原理的に通らない**（起票 17） |
| V4 | **打ち切りの指標** | 生存解析に使うなら `censored` フラグを足す | `null` が「打ち切り」と「再開が無い」を区別しない |
| V5 | **集計窓が無いとき**の `post_t0_*` / `resumption_count` | **`null`**（観測できなかったものを 0 で埋めない） | ⚠️ `o = t0 + B` が右端 `b` を越える場合。一次の `definitions-restop-t1d-t1c.md` §3.2 が**書き切っていなかった** |

⚠️★★★ **V1 が最も重い** —— ★ 研究者の指示（2026-09-19・逐語
「**E1の箇所は具体的に設計議論などが実行後での実装フェーズにて実装する形にしましょう**」）で
実装フェーズ送りになった**本体**である。

## §3 ★ 封筒（③）が残した前提 —— ⚠️ **実装前に読むこと**

★ `--features` の出力は **`{ provenance, config, rows }`** である（2026-09-20・起票 2）。

- ★ acceptance は**取得時に `jq -e '.rows | arrays'` で剥がす**。⚠️ この行を消さないこと。
- ★ `rows[].quality` に **`capabilities` は無い**（封筒の `provenance.capabilities` が持つ）。
- ⚠️ **`001-acceptance.sh` の最上位キー集合は完全一致検査**である
  （現行: `["activity","boundary","dispersion","quality","stall_onset","t_ms"]`）。
  → ★ **`revision` / `restart` を足したら、004 / 006 の実装と同じコミットで
  `001-acceptance.sh` のこの 1 行へ語を足す**（⚠️ 忘れると 001 が赤くなる。★ 判断 18 の先例）。
- ★ `config` は**事前宣言値の受け皿**である。⚠️ 新しい閾値を足すなら
  `FeatureConfigDto` と `envelope-acceptance.sh` AC7 の両方を同じコミットで直す。
- ⚠️ **新しい数値定数を `feat_offline/` に宣言しない**（★ `001-acceptance.sh` AC6 が 3 本で見ている）。

## §4 ⚠️ 先に確かめること（★ 推測で始めない）

1. `issues/004.md` / `006.md` の**本文**（★ 推奨表は本文にある。本メモの表は写しである）。
2. `src-tauri/src/analysis/feat_offline/stall_onset.rs` の**非公開関数**（V2 の対象）。
3. `src-tauri/src/analysis/feat_offline/mod.rs` の `FeatureRow`（★ いま `revision` / `restart` は**無い**）。
4. `004-acceptance.sh` / `006-acceptance.sh` の jq 式（★ どのフィールド名を要求しているか）。
5. `docs/theory/definitions-restop-t1d-t1c.md` §3.2（V5 が指す「書き切っていない」箇所）。

## §5 ★ 並行して残っているもの（⚠️ 本タスクでは触らない）

| # | 何 | 状態 |
|---|---|---|
| A | **起票 18**（Loop の `--cleanup` が逸脱 worktree を撤去できず「完了」と嘘をつく） | ⚠️ **開いたまま** |
| B | 起票 7（`T1a` の分位点が構造的に退化） | ⚠️ **開いたまま**。★ 判断 25 #11「事前宣言と一緒に決める」 |
| C | ⚠️ `issue_status_key` の語彙（`unblocked` / 日本語で始まる Status） | ★ **未決**（判断 9）。⚠️ 判断 4 の領域なので研究者が決める |
| D | G1 収集開始ゲートの赤 6 件 | ⚠️ **研究者判断 5 件が律速**。→ `next-session-after-g1-collection-gate.md` |
| E | ★ **`gse-dataset` 側に共有の門を置く**（③ の残り） | ⚠️ **開いたまま**。★ 向こうに `.github` が無く CI が無い。`scripts/check_no_feature_output.sh --root <クローン>` を**手で**回す運用（`docs/verification-runbook.md` §1 (i)）。★ workflow を新設するかは**別リポの作業**として研究者判断 |

## §6 ⚠️ 守ること

- ★ `/start-task` から。判断は `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ ADR 本文・事前登録 `§3`・被験者向け文書は書き換えない。
- ★ 完了時に `code-reviewer` ＋ `security-checker`（並列・opus）と `/cross-review` **2 巡**（パス限定）。
  ⚠️ レビュー系 subagent には **範囲 / 作業ツリー不可 / クローン不可 / 長い検査を回さない / N 分で結論**
  を明記する（★ 契約は `subagent-delegation` Skill）。
  ★ ⚠️★★★ **パス限定の副作用に注意** —— 2026-09-20 に Codex が
  「`sha2` が diff に無いのでコンパイル不能」と誤検知した（★ `Cargo.toml` を範囲に入れていなかっただけ）。
  → ★ **範囲に入れないファイルがあるなら、その旨をプロンプトに書く**。
- ⚠️ `.codex/budget.json` の当日残量を**先に見る**（★ 2026-09-20 は 420,548 / 300,000 で超過した）。
- ⚠️ `git add -A` / `git add <dir>` 禁止。`.codex/budget.json` を `git checkout --` で戻さない。
- ⚠️★★ **python でスクリプトを書き戻さない**（★ Windows で CRLF が混入する）。
  → `Write` / `Edit` を使い、`tr -cd '\r' | wc -c` が 0 であることを確認する。
  ★ ⚠️ **bash heredoc の中の python も危ない** —— 2026-09-20 に `\\n` が壊れて置換が 2 度空振りした。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
