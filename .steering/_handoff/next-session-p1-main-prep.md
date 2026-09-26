# 次セッション — D. P1 本体の準備（凍結値で実データを 3 極で回し、解析する段取り）

> 作成: 2026-09-26。⚠️★★★ **このメモを一次資料にしない。** 下の「一次」を開いて状態を確かめ直すこと。
> ★ 研究者と合意した順番（2026-09-26）: A（Loop 基盤・**完了** PR #224 / #225）→ B（事前宣言 v1.1・**完了** PR #227）→ **D（本メモ）** → O1 / G1 の収集中に C ＋ 研究案。
> ★ D の中身は引き継ぎ時点で**ほとんど決まっていない**（一次の記述は「凍結値で実データを 3 極で回して解析する段取り」の 1 行だけ・`next-session-loop-foundation-p1-fixes.md:56`）。→ **範囲そのものを grill で決める**。

## §0 打ち込む用（★ 新しいセッションにこのまま貼る）

```
.steering/_handoff/next-session-p1-main-prep.md を読んで、D（P1 本体の準備）を実施してください。

中身: 凍結済みの P1 事前宣言（docs/preregistration-p1-episode.md v1.1・凍結 JSON 1.0.0）の値で、実データを 3 極（baseline / pointer_b / modifier_m_plus）で回して解析する「段取り」を整える。
  範囲は未確定。引き継ぎメモ §2 の候補から、何を D に入れるか・Loop に分解するかを grill で決める。

⚠️ /start-task が先（grill は Opus・判断分岐が閉じるまで）。実装を含むなら Loop 分解（to-prd → to-issues）の要否も grill で決める。分解したら /clear して別セッションで実行する。
⚠️ 実データ（NDJSON・metrics・--features の出力）の中身を開かない・集計しない。PG-1（一人あたり episode 数の下限の宣言）は「WP1 の yield が出た直後・探索を 1 度も回す前・episode 数の分布だけを見る」ゲート（事前宣言 §2.3）。D はそのゲートを「通れる形にする」までで、ゲートそのものを通すかは研究者判断。
⚠️ 凍結文書（v1.1）と凍結 JSON を書き換えない。値を変える必要が出たら新版（v1.2〜）として別に扱う（§0 の凍結規約）。
⚠️ 長い一次資料（事前宣言全文・ADR-030 補訂 2・roadmap WP1/WP2）を 1 節だけ読んで代表させない（verify-before-claiming ルール 7 / 8）。
★ 完了時は /finish-task → git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 確認）を自動で。
⚠️ git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/（別トラック）は触らない・コミットしない。
⚠️ .codex/budget.json は台帳（git checkout -- で戻さない・記帳はコミットに含める）。/cross-review は Codex gpt-6-astra・パス限定・2 巡。
応答は日本語。
```

## §1 状態（★ 2026-09-26 実測）

- main = `765601f6`（PR #227 merge・main の CI run 発火を確認）。作業ツリーの未追跡は別トラックの `.steering/20260921-media-expression-theory-audit/` だけ。
- 事前宣言: `docs/preregistration-p1-episode.md` は **v1.1**（冒頭の「v1.1 改訂宣言」が本文の 5 点を上書き・追補する）。凍結 JSON `src-tauri/prereg/p1-episode.json` は `1.0.0`（値の版・v1.1 は値を変えていない）。記録は `.steering/20260926-prereg-p1-episode-v1-1/`。
- 実行の道具は揃っている:
  - `gse-replay <入力> --features --pole <baseline|pointer_b|modifier_m_plus>`（凍結 JSON を既定として読む・封筒が `prereg_*` / `overrides` / `pole_*` を自己申告する。ADR-030 補訂 2 項目 2・3）
  - `scripts/run-features-all-poles.sh`（3 極を all-or-nothing で回す）／ 手順は `docs/verification-runbook.md` §1 (j)
  - `scripts/check_prereg_parity.py`（文書と JSON の値の一致だけを検査する）
- ⚠️ **P1 の位置づけ**（一次で確かめること）: `docs/architecture/personalization-and-online-learning.md` §10「**G1（統制タスク実験）は P1 より前**」。roadmap（`.idea/20260911-mhd-growth-personalization-and-gse-overview-roadmap.md`）の **WP1 = O1 natural-work discovery**（完了条件「一人あたり episode 数、転帰 base rate、ICC、欠測率、probe burden」）→ **WP2 = criterion freeze**（完了条件「同じ raw log から第三者が同じ episode table を再生成できる」）。
  → ⚠️ **G1 / O1 の収集がいまどこまで進んでいるか**は本メモで確かめていない。**ファイルの中身を開かずに**（台帳・`.steering/`・`experiments/` の記録から）確かめること。

## §2 ★ D に入れる候補（⚠️ 入れるかどうか・順番は grill で決める。ここは材料の列挙だけ）

| # | 候補 | 一次 |
|---|---|---|
| 1 | **v1.1 の読み方の規則をテストで固定する**: (a) 上下界は軸ごと（ポインタ軸／修飾キー軸）に min / max を取り、軸をまたがない (b) 極 B が非適用なら算出不可として扱い、幅 0 にしない (c) 極 M+ の `not_applicable` は `not_applicable` と報告し、幅への寄与は 0 (d) 探索の実行で `config.warmup_count` が対応表（0.99→100／0.995→200／0.999→1000）と合わない実行を除外する (e) `ime_overlap` を `t0` 時点の特徴量に使わない | `.steering/20260926-prereg-p1-episode-v1-1/design.md` 末尾「検査が届かないもの」・事前宣言冒頭の v1.1 改訂宣言 (3)(5) |
| 2 | **PG-1 を通せる形にする**: 転帰も予測成績も見ずに「参加者ごとの episode 数の分布」だけを出す集計の経路（何を出して・何を出さないかを構造で保証する） | 事前宣言 §2.3「宣言ゲート PG-1」 |
| 3 | **P1 の実行を再現可能にする**: `experiments/<YYYYMMDD>-<name>/`・seed `20260921`・入力の gse-dataset commit・HMM_VERSION・lockfile の刻印・1 コマンド再現 | `reproducibility-discipline` Skill ／ `docs/experiment-tracking.md` ／ 事前宣言 §2.2 |
| 4 | **探索（§2 の 27 通り ＋ OFAT 4 実行）の実行器**: grouped nested CV（outer = leave-one-participant-out・inner = grouped k-fold）。⚠️ **回すのは WP1 の内側・PG-1 の後だけ**。D では「器」だけ作るのか | 事前宣言 §2.1 / §2.2 ／ 凍結 JSON `search_protocol` |
| 5 | 起票 **P1-F**: `--set q=…` が `warmup_count` を連動させない —— CLI に連動を持たせるか（v1.1 は「決めない」とし、探索プロトコルの実装時に裁定すると書いた） | 前タスク `.steering/20260921-p1-prereg-cli-poles/decisions.md` 起票表 ／ ADR-030 補訂 2 項目 2 |
| 6 | 起票 **P1-A**: 凍結既定（`warmup_count=100`）では restart の非退化検査（旧 `006-acceptance.sh` AC6）が走らない —— 既定 config で restop が測れる fixture が要るか | 同 decisions.md 判断 19 |
| 7 | 起票 **P1-G**（security LOW）: `--feature-config` の `id` / `version` を検証せずに封筒へ写す | 同 起票表 |
| 8 | **未裁定の非対称**: `feat` 行が 1 本も無い入力では `T1a` の窓を切らない（値を返す）が、onset は立てない側に倒す —— 向きが違う | ADR-030 補訂 2 項目 6 の「⚠️ 未裁定の非対称」の項 |
| 9 | 解析結合: `--features` の出力を metrics / ラベルと結合する経路（`scripts/build_analysis_db.py`・DuckDB）。⚠️ `--features` の出力は gse-dataset へ共有しない（封筒 `sharing: prohibited`） | memory「Phase C code complete」「OutcomeMetrics の外部契約」（⚠️ memory なので一次で確かめる）／ 事前宣言 §3 規律 5 |

★ grill で閉じるべき分岐の例（固定リストではない）:
- D は「コードとテストの準備」までか、「実データで 3 極を回す」ところまで含むか（⚠️ 後者は PG-1 の手前で止まる設計が要る）
- P1 はいつ回せるのか（G1 の判定・O1 の収集状況）。回せないなら D は何を先に作っておくか
- Loop に分解するか（候補 1〜4 は実装を含む）
- 解析コードの置き場（`experiments/` か `scripts/` か `src-tauri/src/bin/` か）と、`analysis/` のレイヤー規則

## §3 ⚠️ やらないこと

- 実データの中身を開く・集計する・「試しに 1 本回して見る」（★ PG-1 の手前でも forking paths になる）
- 凍結文書 v1.1・凍結 JSON を書き換える
- PG-1 の**値**を決める（WP1 の yield が出た直後の別ゲート）
- ADR-030 D9（壁時計の非単調性）・E1（連結の実装形）を決める（★ どちらも「P1 の実データを見てから」・`recovery` の実装時）
- C（メディア表現の照合・`.steering/20260921-media-expression-theory-audit/`）に踏み込む（★ O1 / G1 の収集中に回す別トラック）
