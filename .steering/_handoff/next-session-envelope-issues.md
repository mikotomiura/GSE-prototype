# 次セッション — 封筒 issue（起票 2 / 5）★ タスク 2 の再開順 ③

> 作成: 2026-09-20。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/blockers.md`（**起票 2 / 5**）／
> 同 `decisions.md`（**判断 25 #14 / 再開順**）／ `src-tauri/src/bin/replay.rs` /
> `.steering/20260914-mhd-feature-offline-tiers/issues/*-acceptance.sh` / `docs/glossary.md:233`。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-envelope-issues.md を読んで、封筒 issue（起票 2 / 5）を実施してください。
まず /start-task を起動し、grill で「封筒に何を載せ、何を載せないか」「共有の門をどこに置くか」を確定してから進めてください。
状態は一次（bin/replay.rs の --features 経路・各 *-acceptance.sh・docs/glossary.md:233 の実物）で確かめ直すこと。台帳も引き継ぎも未検証メモとして扱う。
⚠️ 研究者判断 2026-09-18（判断 25 #14）の逐語は「封筒を足す小 issue」です。★ 出力を { provenance, config, rows } にし、全 acceptance の前提（配列）を 1 度だけ書き換えます。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ⚠️ なぜこれが次なのか（★ 一次で確かめた事実）

★ タスク 2（`20260914-mhd-feature-offline-tiers`）の**再開順は研究者が確定済み**（判断 25）:

```
① 理論レビュー        ✅ 完了（.steering/20260918-theory-critical-review/）
② Loop 基盤の修正     ✅ 完了（.steering/20260920-loop-foundation-fixes/）
③ 封筒 issue（起票 2 / 5）  ← ★ ここ
④ 004（T1c）/ 006（T1d）
⑤ capability matrix（ADR-032 M7）
⑥ P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）
```

⚠️★★★ **④ を先にやらない理由**（★ 2026-09-20 に一次で確認）:

- ★ `issues/004.md` に **「未裁定」が 6 件**、`issues/006.md` に **5 件**残っている
  （`grep -c 未裁定`）。⚠️ 判断 26 が定めた着手条件
  「**『未裁定』の語が 1 つでも残っていれば着手しない**」に当たる。
- ★ かつ **封筒は全 acceptance の前提を書き換える**ので、
  ⚠️ **004 / 006 を回した後に入れると、走り終えた issue の検査が全部無効になる**
  （★ 起票 2 の逐語「途中で変えると走り終えた issue の検査が全部無効になる」）。
  → ★ **封筒が先**である。

## §2 ★ 対象（★ 2 件。2026-09-20 に一次で再確認した）

### (1) 起票 2 —— `--features` の出力に「由来の封筒」が無い

- ★ 現状: `bin/replay.rs:824` 逐語「**Tier 別 1 Hz tick 単位特徴行を JSON 配列で出力**」。
  → ⚠️ トップレベルが **`FeatureRow` の配列**で、
  **セッション単位の事実（`capabilities` / `app_version` / OS / fixture 名）を持たない**。
- ⚠️ **複数セッションの出力を結合すると、どの行がどの計器条件で取れたか失われる。**
- ★ 判断 25 #14 の逐語: **「封筒を足す小 issue」**。出力を **`{ provenance, config, rows }`** に。

⚠️★★★ **起票 1（`meta` に `os` が無い）と混ぜない。**
★ 起票 1 は**計器変更**（`logger.rs` / `schema_dto.rs`）で **ADR-032 の領域**であり、
本タスクの範囲外。→ ★ 封筒に載せられるのは **いま NDJSON から読めるもの**だけである
（⚠️ **`os` は読めない**。★ `capabilities` は issue 007 が既に行ごとに載せている）。

### (2) 起票 5 —— 「`--features` 出力を共有しない」に機械的な門が無い

- ★ 規約は在る: `docs/glossary.md:233` 逐語
  「★ **中間成果物であり `gse-dataset` へは共有しない**」。
- ★ 実装も規約どおり（`--features` は **stdout に書くだけ**でファイルを作らない）。
- ⚠️ **問題は門が無いこと**（★ 2026-09-15 に実測）: `feat.json` / `features.json` /
  `src-tauri/rows.json` / `experiments/x/feat.json` は **4 つとも NOT ignored**。
  ⚠️ **`out.ndjson` も NOT ignored**（★ パターンは `gse_*.ndjson` / `P[0-9]*_*.ndjson`）。
- ★ 判断 25 #14: **「共有しない」を封筒に刻む**。
- ⚠️ 未実施の本筋: **`gse-dataset` 側に feature row 形の JSON が無いことを CI で見る**。
  ⚠️ **`.gitignore` に慣用ファイル名を足すのは名前依存なので代替にならない**（★ 起票 5 の逐語）。

## §3 ★ 受け入れ条件（★ このプロジェクトで何度も踏んだ型を避ける）

- [ ] **全 acceptance を 1 度だけ書き換える** —— ★ **8 本すべて**が配列を仮定している
      （2026-09-20 実測・`all(.[]; …)` 系が計 **28 箇所**）:
      `001`(2) / `002`(1) / `003`(3) / `004`(1) / `005`(2) / `006`(2) / `007`(8) / `008`(9)。
      ⚠️ **1 本でも取り残すと、その issue の検査は「配列が来ない」で赤になる**。
- [ ] **既に merge 済みの issue の acceptance も通ること**を実測する
      （★ 001 / 002 / 003 / 005 / 007 / 008 の 6 本。⚠️ 004 / 006 は blocked のまま）。
- [ ] **封筒に載せる項目を grill で確定する**。⚠️ **推測で足さない**
      （★ 載せられるのは NDJSON から読めるものだけ。**`os` は読めない**）。
- [ ] ⚠️ **「共有しない」の門は、名前依存でない形で置く**
      （★ `.gitignore` にファイル名を足すのは**代替にならない**）。
      ⚠️ 置けないなら**置けない理由を書いて未決として残す**（★ 黙って諦めない）。
- [ ] ⚠️ **検査が「見ていないもの」を検査自身のコメントに書く**。
- [ ] ⚠️ **突然変異で検査が赤くなることを確かめる**
      （★ `.steering/20260920-loop-foundation-fixes/measurements.md` の M-a〜M-h が手本。
      ⚠️ **本プロジェクトは「検査があるつもりで検査していない」を 3 回踏んでいる**）。
- [ ] `decisions.md` に判断を残す。★ `blockers.md` の起票 2 / 5 を**閉じる**（⚠️ 消さない）。

## §4 ⚠️ 先に確かめること（★ 推測で始めない）

1. `src-tauri/src/bin/replay.rs` の `--features` 経路（`:1061` 付近）の**実際の出力組み立て**。
2. `issues/*-acceptance.sh` **8 本すべて**の jq 式（⚠️ `all(.[]; …)` 以外の配列前提も探す）。
3. `docs/glossary.md:233`（**規約の逐語**）と、`src-tauri/src/bin/replay.rs` の usage に
   既に書いた注記（★ 起票 5 の「安価な側」は**実施済み**）。
4. ⚠️ `scripts/build_analysis_db.py` が読むのは `.metrics.json` **だけ**であること
   （★ 封筒を足しても解析 DB は壊れない、の裏取り）。
5. ⚠️ `emit_schema` / `check_schema_parity.py` の対象に `--features` が**入っていない**こと
   （★ memory「OutcomeMetrics の外部契約」と同じ型の**無音の破壊**が起きないか）。

## §5 ★ 並行して残っているもの（⚠️ 本タスクでは触らない）

| # | 何 | 状態 |
|---|---|---|
| A | **004（T1c）/ 006（T1d）** | 🔴 `blocked`。★ 算出式は判断 26 で確定・転記済み。⚠️ 残るのは**実装フェーズの設計議論 9 論点**（下表）。★ **裁定セッションが先**（⚠️ `grep -c 未裁定` が 0 になるまで着手禁止） |
| B | **起票 18**（Loop の `--cleanup` が逸脱 worktree を撤去できず「完了」と嘘をつく） | ⚠️ **開いたまま**。★ 2026-09-20 に実測で発見。⚠️ ブランチ検査が入ったので到達確率は下がったが**経路は残る** |
| C | 起票 7（`T1a` の分位点が構造的に退化） | ⚠️ **開いたまま**。★ 判断 25 #11「事前宣言と一緒に決める」 |
| D | ⚠️ `issue_status_key` の語彙（`unblocked` / 日本語で始まる Status） | ★ **未決**（判断 9）。⚠️ 判断 4 の領域なので研究者が決める |
| E | G1 収集開始ゲートの赤 6 件 | ⚠️ **研究者判断 5 件が律速**。→ `next-session-after-g1-collection-gate.md` |

### ★ A の中身 —— 「未裁定」9 論点（★ 2026-09-20 に一次から起こした）

⚠️★★★ **すべてに「推奨」が既に書いてある。** ★ 裁定は
**「推奨を承認するか、対案に倒すか」を 9 回答えるだけ**である（⚠️ 新しい設計をゼロから起こす作業ではない）。

**issue 004（`T1c` = 修正トポロジー）U1〜U4**

| # | 論点 | 推奨 | 対案 |
|---|---|---|---|
| U1 | 削除の走りを**切る press**（挿入でも削除でもない press = `navigation` / 修飾キー） | 削除系以外の press は**すべて切る** | 挿入系だけが切る |
| U2 | `category_bigram_repeat_rate` の**式**（例 AA, AA, AB） | **1 − 種類数 ÷ 総数**（= 1/3） | 2 回以上現れる種類に属する出現の割合（= 2/3） |
| U3 | 走り・burst 単位の値を載せる **tick** | **閉じが確定した時点の tick**（causal・未来が漏れない） | 最後の press の tick ／ 次の burst の最初の press の tick |
| U4 | 走りの**最小の長さ** | **1 から** | 2 から |

⚠️ U2 はどちらの式でも `Alphabetic` が大半のため **burst 長と強く相関する**。

**issue 006（`T1d` = 再開）V1〜V5**

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

★ 裁定したら、各行の「推奨（⚠️ 未裁定）」を **「★ 裁定: …（判断 N・日付）」へ書き換える**
（⚠️ 見出しの「（未裁定・2026-09-19）」も外す）。★ `grep -c 未裁定` が **0** になったら ④ に入れる。

## §6 ⚠️ 守ること

- ★ `/start-task` から。判断は `decisions.md`。`verify-before-claiming`（状態の断定は一次で）。
- ⚠️ ADR 本文・事前登録 `§3`・被験者向け文書は書き換えない。
- ★ 完了時に `code-reviewer` ＋ `security-checker`（並列・opus）と `/cross-review` **2 巡**（パス限定）。
  ⚠️ レビュー系 subagent には **範囲 / 作業ツリー不可 / クローン不可 / 長い検査を回さない / N 分で結論**
  を明記する（★ 契約は `subagent-delegation` Skill）。
- ⚠️★★★ **`/cross-review` は架空のトークン名で fail-closed する** —— ★ 2026-09-20 に 2 回踏んだ。
  ★ **フィクスチャ側を寄せる**（⚠️ `--ack-filtered` は人が目視確認したときだけ。自動では付けない）。
  ★ 先に `git diff <range> -- <paths> | bash scripts/secrets-filter.sh; echo $?` が **0** になるか見る
  （⚠️ `git diff <range>` は**コミット済み**を見るので、作業ツリーを直しただけでは変わらない）。
- ⚠️ `.codex/budget.json` の当日残量を**先に見る**（★ 2026-09-20 は 341,548 / 300,000 で超過した）。
- ⚠️ `git add -A` / `git add <dir>` 禁止。`.codex/budget.json` を `git checkout --` で戻さない。
- ⚠️★★ **python でスクリプトを書き戻さない**（★ Windows で CRLF が混入する）。
  → `Write` / `Edit` を使い、`tr -cd '\r' | wc -c` が 0 であることを確認する。
- ★ コミット: `[type]([scope]): [説明]` ＋ 本文 ＋ `Refs:` ＋
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`。
