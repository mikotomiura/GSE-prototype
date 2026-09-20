# 次セッション — ⑤' 理論の回: サーヴェイ **S3 → S4** → **J-2（名称ゲート）の裁定**

> 作成: 2026-09-21。⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260918-theory-critical-review/survey-plan.md`（**「★ 実施状況と残りの予定」節**）／
> `.steering/20260918-theory-critical-review/questions-batch-1.md`（**J-2**）／
> `.claude/commands/literature-review.md` ／ `docs/references.md`（採番 SSOT）。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-survey-s3-s4-and-j2.md を読んで、⑤' を実施してください。

【1】サーヴェイ S3（生成芸術論・メディアアート）を /literature-review で 1 ラウンド。
【2】続けて S4（data portrait / self-tracking art）を 1 ラウンド。
【3】S3 の結果を見て J-2（「生成的返権論」の名前を残すか）を裁定する。

⚠️ ラウンドごとに即コミット（references.md / _index.md / positioning に複数ラウンドを同居させない）。
★ 探索は subagent、docs/references.md への追記はメイン直列。
⚠️ check_citations.py は「違反なし」が出るまで是正→再実行を繰り返す（1 回で全件出ない）。

状態は一次（survey-plan.md・questions-batch-1.md・references.md）で確かめ直すこと。
設計判断は Opus。サブエージェントは既定 sonnet、レビューとセキュリティだけ opus（model を毎回明示・入れ子禁止）。
応答は日本語。git add -A / git add <dir> は使わない。.codex/budget.json を git checkout -- で戻さない。
```

## §1 ★ 直前のセッションで何が終わったか（2026-09-21）

| ブランチ | 中身 | 状態 |
|---|---|---|
| `fix/loop-spawn-cleanup` | ★ 起票 18（`--cleanup` の嘘の完了報告）の是正 ＋ 回帰テスト（**9 群 29 件**・変異対照つき）＋ CI 配線 | ⚠️ **main へ未マージ** |
| `docs/capability-matrix` | ★ `docs/architecture/offline-replay-capability-matrix.md`（**M7**）＋ **ADR-036**（Proposed）＋ 起票 24 | ⚠️ **main へ未マージ** |

⚠️★★★ **どちらも PR を出していない。** ★ 次セッションの最初に**研究者の判断を仰ぐ**こと
（★ そのまま PR → merge するか、先に手元で追検証するか）。

★ タスク 2 の再開順（`.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25
＋ ★ **2026-09-21 の研究者判断で 1 つ挿入**）:

```
① 理論レビュー          ✅
② Loop 基盤の修正        ✅
③ 封筒 issue            ✅
④ 004 / 006             ✅
⑤ capability matrix     ✅（2026-09-21・本 PR）
⑤' 理論の回: S3 → S4 → J-2 の裁定   ← ★ ここ
⑤'' 起票 23（resolve_base）の是正    ← ★ 2026-09-21 に研究者が挿入
⑥ P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極（ポインタ・修飾キー）
```

⚠️★★★ **起票 23 は ⑥ の実施前に *必ず* 解決させる**（★ 研究者判断 2026-09-21）——
★ ⑥ は **Loop で回す**ので、⚠️ `resolve_base` が古い枝を選ぶと
**worktree が 38 コミット前から切られ、全 issue が誤った base の上で走る**。

## §2 ★ なぜ S3 が先なのか（★ 一次で確かめた）

⚠️★★★ **J-2（「生成的返権論」の名前を残すか）が S3 待ちで止まっている唯一の未回収**である。
★ `questions-batch-1.md:27` 逐語:

> 「**S1 / S3 の結果（先行と衝突するか）を見てからでないと判断材料が無い**」

★ **S1 は 2026-09-19 に完了**している（`docs/literature/20260919-authority-return-burden-precedents.md`・
[P368]–[P379]）。→ ★★★ **残る閂は S3 だけ**である。

## §3 ★ 実施の作法（⚠️ 省略しない）

- ★ **`/literature-review` 1 ラウンド ＝ 1 問**。⚠️ S3 と S4 を 1 ラウンドに混ぜない。
- ⚠️★★★ **ラウンドごとに即コミット**（★ memory「Commit each survey round」——
  `references.md` / `_index.md` / `research-positioning.md` に複数ラウンドが同居すると
  **`git add -p` で分離できなくなる**）。
- ★ 探索は **subagent**、`docs/references.md` への **append はメイン直列**
  （★ memory「Survey via subagent」／ 手順は `/literature-review` Step 2）。
- ⚠️★★★ **`check_citations.py` は「違反なし」まで繰り返す** ——
  ★ 重複検出は **1 回で全件出ない**（memory「check_citations は違反を隠す」）。
- ⚠️ **PDF は `pypdf` で読む**（★ `WebFetch` は PDF を読めないが原本をローカル保存する。そのパスを開く）。
- ⚠️ **長い一次資料を 1 節だけで代表させない**（★ `verify-before-claiming` ルール 7）。

## §4 ⚠️ 残りのサーヴェイ 2 本（★ この回では回さない）

| ID | ★ いつ | ⚠️ 何が待っているか |
|---|---|---|
| **S5**（計測しない身体） | ★ **Physical Anchor の PC 面の実装設計タスク**（ADR-035 の未決 3 つと同じ回） | ★ J-14 は裁定済み。⚠️ 残るのは **PM-Q7**（復帰後の差分を表現へ結合するか） |
| **S6b**（罪悪感・応答義務等の既存尺度） | ★ **EH3 を設計する回**（⚠️ 走らせる前） | ⚠️ EH3 は研究用の**別計器**で、まだ設計されていない |

## §5 ⚠️ 本セッションで新しく開いた / 閉じた起票

| 起票 | ファイル | 状態 |
|---|---|---|
| **18**（`--cleanup` の嘘） | `20260914-mhd-feature-offline-tiers/blockers.md` | ✅ **是正済み** |
| **21**（単独キー用の門） | `20260914-instrument-change-arbitration/blockers.md` | ✅ **解決**（`ADR-036 D3`） |
| **23**（`resolve_base` が config を `tail -1` で選ぶ） | `20260914-mhd-feature-offline-tiers/blockers.md` | ⚠️ **未解決**（★ 実測: 38 コミット古い枝から worktree が切られた） |
| **24**（`check` job の `permissions:`） | `20260914-mhd-feature-offline-tiers/blockers.md` | ❌ **取り下げ**（⚠️ 一次で成立しなかった。★ 番号は再利用しない） |
| **24**（ライブ変換の層を識別できない） | `20260914-instrument-change-arbitration/blockers.md` | ⚠️ **未解決**（★ 研究者判断「起票だけ」） |

> ⚠️★★★ **起票 24 は 2 つのファイルに在り、片方は取り下げ済みである。**
> ★ **必ずファイルとセットで呼ぶ**（★ 起票 21 と同じ注意）。

## §6 ★ 研究者判断（2026-09-21・★ **裁定済み。次セッションで蒸し返さない**）

| 論点 | ★ 裁定 |
|---|---|
| 2 本のブランチ | ★ **push → PR → CI 緑なら merge**（★ PR **#216** / **#217**） |
| **ADR-032 / ADR-036** | ★★★ **Proposed のまま据え置く。** ⚠️ **Migration の実施は「必要になったタイミング」で行う** —— ★ いま予定タスクに積まない（⚠️ どちらも実データ待ちの項目を持つ） |
| **起票 23**（`resolve_base`） | ★★★ **⑤' の *後* に実施する。⚠️ ⑥ の実施前には *必ず* 解決させる**（→ §1 の ⑤''） |

⚠️★★★ **したがって次セッションで ADR-036 を Accepted にしに行かない。**
★ 承認が要るのは「**その ADR の Migration を実際に動かすとき**」である
（⚠️ `ADR-036 M4a` は **O1 の実データの後**、`ADR-032 M5` は **Accepted 後**）。
