# TASK-PRE — Codex による issue 独立性の第二意見（2026-09-14）

> ★ 実行: `scripts/run-codex-consult.sh`（read-only）。★ `docs/loop-engineering.md` の Codex ゲート TASK-PRE。
> ⚠️★★★ **これは助言である。採否は人が決める**（★ 逐語）。Codex は文脈の半分しか持たない。

## Codex の応答（原文）

優先度順の盲点です。

1. **独立性はかなり弱い**  
001→007 の完全直列 DAG は安全寄りだが、「mod.rs だけが交差点」以上に、出力行の共通型・tick 生成規則・欠測表現・時刻丸め・lookahead 可否が全 issue の暗黙共有状態になっている。特に T1b/T1d/stall は前後イベントを見るため、T0 の「1 Hz tick に何を帰属させるか」が後で全 Tier の意味を縛る。

2. **最初に切るべき共通基盤が足りない**  
001 に CLI と T0 を同居させるより、`FeatureRow`、tick alignment、window 境界、null/absent/zero の規約、version/schema name、fixture harness を “000 schema/core” として分けた方が後続衝突が減る。今のままだと 002 以降が `mod.rs` と共通 row 構造を毎回触り、直列でもレビュー差分が濁る。

3. **lookahead と因果性の明示が必要**  
offline なので未来イベントを見られるが、tick 行に「その時点で既知の特徴」なのか「後からラベル付けした特徴」なのかが混ざる危険がある。restart は明確に未来依存、stall onset も定義次第で後方確定が必要。`available_at_ms` や `causal=false` 相当の注記を検討したい。

4. **エッジケース不足**  
空ログ、単一イベント、時刻逆行、同一 timestamp 多発、セッション開始直後/終了直前の pause、日跨ぎ、長時間無入力、IME イベント欠落、未知 KeyCategory、破損 NDJSON、複数 app/window 混在、ログ schema version 差、tick 境界ちょうどのキー入力、flush されない最終 pause は AC に入れたい。

5. **順序ハザード**  
002/003/004 が先に「pause」や「baseline」の局所定義を持つと、005 の stall onset が別定義を要求して破壊的変更になりうる。pause extraction は独立 helper として早期固定がよい。

6. **別案**  
Tier ごと PR ではなく、共通 row + fixture + golden-lite を先に作り、各 Tier は `compute_x(events, ticks) -> Vec<Option<X>>` の純関数だけにする。CLI 統合は最後でもよい。

7. **トレードオフの見落とし**  
直列 DAG は衝突回避には強いが、設計誤りの発見が遅い。並列度 1 ならなおさら、早い段階で 005/006 の薄い spike を入れて T0/T1b/T1c の前提を検証した方が、後戻りコストを下げられる。

---

## 採否（★ 2026-09-14）

| # | 指摘 | 採否 | 理由 / 反映先 |
|---|---|---|---|
| **1** | 独立性が弱い。tick 生成規則・欠測表現・時刻丸め・lookahead 可否が**全 issue の暗黙の共有状態**になっている | ✅ **採用** | ★ 指摘のとおり。→ **issue 001 がこれらを明示的に所有する**ことを AC に足した（★ 暗黙にしない） |
| **2** | 001 に CLI と T0 を同居させず、`000 schema/core` を切るべき | ⚠️ **不採用（理由つき）** | ★ `issue-slicing` 基準 1「**層別の横切り分割は禁止**」に当たる。⚠️ かつ `000` は**出力を持たないので `acceptance.sh` が書けない** —— `loop-run.sh` のコメント逐語「**`cargo test` が無条件に緑になる issue では AC 未充足のまま `issue_done` になる**」に直撃する。★ 代わりに **001 が共有規約を所有し、後続がそれを使うことを AC で強制する**形にした（下記 3 / 5） |
| **3** | **lookahead / 因果性の明示**が要る。tick 行に「その時点で既知」と「後から付けたラベル」が混ざる | ✅★★★ **採用（最重要）** | ★ `ADR-030 D2` が検出窓と転帰窓を分けた目的そのもの（`.idea/criterion:66`「**stall onset の検出窓と転帰判定窓を重ねない**」）。→ **001 に「Tier ごとに causal / retrospective を明記する」AC**、**006 に「retrospective が detection 側へ渡らない」AC** を足した |
| **4** | エッジケース不足（空ログ / 単一イベント / 時刻逆行 / 同一 timestamp / tick 境界ちょうど / 最終 pause の未 flush ほか） | ✅ **採用** | ★ tick ループを所有する **001 に境界入力の AC** を足した。⚠️ 「破損 NDJSON」「複数 app/window 混在」は **既存 loader の担当**（★ `ReplayEvent` が未知タグで落ちる既知挙動）なので本タスクの範囲外とし、ここに記録するに留める |
| **5** | **順序ハザード**: 002/003/004 が局所的な `pause` 定義を持つと、005 の stall onset が別定義を要求して破壊的変更になる。pause 抽出は独立 helper として早期固定を | ✅★★★ **採用** | ★ 最も安い対処で最も効く。→ **001 が `pause` / `net` の抽出を共有ヘルパとして所有**し、**002〜005 は独自定義を作らず 001 のヘルパを使う**ことを AC（grep 検査）にした。⚠️ `net` は `ADR-030 D3` が「既存 `OutcomeConfig` の `net_diff_min` をそのまま使う」と決めているので、そこも 001 に集約する |
| **6** | Tier ごと PR をやめ、共通 row ＋ fixture ＋ golden-lite を先に作り、CLI 統合は最後 | ⚠️ **不採用（理由つき）** | ★ #2 と同じ理由。⚠️ CLI を最後にすると **全 issue の `acceptance.sh` が最後まで空振りする**（＝ 「客観に見えて無意味な緑」を 6 本量産する）。★ `docs/loop-engineering.md` 逐語「AC の検証コマンドが `verify` / `acceptance` に載っている」が モードC の客観性の 3 条件の 1 つである |
| **7** | 直列 DAG は設計誤りの発見が遅い。005/006 の薄い spike を早期に入れるべき | ⚠️ **部分採用** | ★ 懸念は妥当。⚠️ ただし「spike issue」は AC を持てないので Loop に載せられない（基準 4）。→ ★ **#5 の共有ヘルパ固定が同じ危険の大半を潰す**（★ 005 が 001 の `pause` / `net` を使う以上、定義の食い違いが起きない）。★ 残る危険（`θ_person` の推定可能性）は **005 の `## Stop Conditions`** が拾う |
