# 段 1 の候補項目と、それを要する数値（issue #333 の「次の一歩」1）

> 作成: 2026-10-10（`.steering/20261010-release-tier1-table-consent-v2/`）。
> 「段 1」は issue #333・ADR-039 D5/D6 の意味（**分析に使った表現**）。段 0 = 集計値とコード、段 2 = 加工した打鍵の記録、段 3 = 生の記録（出さない）。
> ⚠️ O1 の事前登録草案の「段 1」（非打鍵チャネルの凍結表・ADR-014 D4）とは別の語。
>
> 基準にした数値（研究者判断 2026-10-10・判断 1）: 現行の事前登録 —— G1（`experiments/20260801-controlled-friction-task/preregistration.md`・`analyze.py`）、
> P1 の episode（`docs/preregistration-p1-episode.md`・`src-tauri/prereg/p1-episode.json`）、O1 の事前登録草案（`.steering/20261007-o1-preregistration-draft/preregistration-draft.md`・第 0 版・未凍結）、
> 参考に v0.3 の較正スモーク（`docs/preregistration-v0.3.md`）。
> **2 本目の論文の解析計画ができたら、その数値で差し替える。** この表は「現行の解析が、どの表現でどこまで再現できるか」の目安であって、公開する項目の決定ではない（決めるのは研究者・同意文 v2 の【決 v2-a】）。

## この表から先に言えること

1. **公開の対象になりうるのは、2 本目の論文のデータと、ADR-039 D2 の条件（a〜d）がそろった場合の O1 の記録。** G1 は記録を公開しない（ADR-039 D8）。O1 の事前登録草案は、本事前登録の解析としては「記録は公開しない」と書く（草案 `:43`・`:215`）。→ 下の表の G1・P1・v0.3 の行は、2 本目の解析計画が似た数値を使うときの見積もりとして読む。
2. **段 1 だけで再現できる数値と、生の打鍵（段 2 以上）が要る数値がはっきり分かれる。** `feat` 行の 1 Hz の列（とくに `ewma_x/ewma_y` と f1〜f6）と非打鍵の行で足りる数値は多い。打鍵間の間隔の分布（沈黙・連なりの分位点）・キーの数・パラメータを変えた探索の再現には、key 行が要る。
3. **段 1 も無条件に安全ではない。** `feat` 行の `keys` / `bs_keys` は 30 秒窓の個数を毎秒書くので、隣り合う行の差から 1 秒ごとの打鍵数を逆算できる見込みがある（サーヴェイの「GSE への還元」4・未検証）。窓の右端は最後の打鍵の時刻で、沈黙中は同じ値がくり返される（`src-tauri/src/analysis/loop_step.rs:150-180`）。段 1 も ADR-039 D6 の関門にかける。
4. **時刻の基準が表現ごとに違う。** NDJSON（匿名化後）は相対時刻だが、`gse-replay --features` の `t_ms` は絶対の epoch ms で、匿名化を通っていない。出力自身が「gse-dataset へ共有しない」と刻み、CI の門がある（`src-tauri/src/bin/replay.rs:1766-1772`・`scripts/check_no_feature_output.sh`）。段 1 に `--features` の行を入れるなら、この規約の見直しが先に要る。

## 表 A — 段 1 の候補の表現

| # | 表現 | 中身 | 定義（一次） | 使う数値（表 B の行） | 段 1 の候補か |
|---|---|---|---|---|---|
| A1 | `feat` 行の f1・f3・f4・f5・f6 | 30 秒窓の 5 特徴量（飛鍵時間の中央値・修正率・連なりの長さ・2 秒以上の間の数・削除後の停止率）。1 Hz | `src-tauri/src/analysis/loop_step.rs:133-`・`features.rs:157-264`・NDJSON は `logger.rs:595` | G1 の FS-A（B1-1） | 候補。G1 の主判定の半分を担う |
| A2 | `feat` 行の `ewma_x`・`ewma_y` | X/Y 軸の合成値（ヒステリシス EMA 後）。1 Hz | 同上 | v0.3 の PreReg-4 の C-index（B4-1・`AggSpec` の既定） | 候補 |
| A3 | `feat` 行の `p_flow`・`p_inc`・`p_stuck`・`raw_x`・`raw_y`・`obs`・`alpha` | HMM の事後確率・EMA 前の合成値・観測ビン・α | 同上 | 現行の事前登録の数値には使わない（`p_stuck` は O1 草案の【決 6-a】案 A の入力・未凍結） | 出さない候補（2 本目の計画で要るなら足す） |
| A4 | `feat` 行の `keys`・`bs_keys` | 30 秒窓のキー押下数と BS/Del の数（個数・窓の右端は最後の打鍵） | `loop_step.rs:150-180` | G1 の `keys`・`bs_rate` は**この列ではなく** key 行から数える（B1-2） | 出さない候補（差から 1 秒ごとの打鍵数を逆算できる見込み・上の 3） |
| A5 | `paste` 行 | 貼り付けの時刻と文字数 | `src-tauri/src/schema_dto.rs:152` | G1 の `external_paste_chars`（B1-3） | 候補（⚠️ 文字数は長さの並びの手がかり・issue #333 の B の表） |
| A6 | `ime_shadow` 行 | 変換の時刻・`dwell_ms`・候補の移動・取り消し | `schema_dto.rs:315` | G1 の `ime_dwell_med`（B1-3） | 候補（⚠️ 区切りの位置と長さの手がかり） |
| A7 | `focus_transition` 行 | 画面の切り替えの時刻 | `schema_dto.rs:220` | O1 草案の `left_observation`（B3-2） | 候補 |
| A8 | `pointer_bin` 行 | ポインタの 1 秒ビン（動いた量 0..7・ボタン・ホイール・座標なし） | `schema_dto.rs:229`・`src-tauri/src/analysis/pointer_bin.rs:31` | P1 の極 `pointer_b`（B2-4）・idle trim（B2-2） | 候補 |
| A9 | `hook_health`・`secure_input`・`recording_pause` 行 | 計器の健全さ・除外の区間 | `schema_dto.rs:252`・`:245`・`:211` | O1 草案の除外と有効日（B3-3） | 候補（中身は個人の打鍵ではない） |
| A10 | `session_meta`・`session_start`・`meta` の一部 | 作業種別・条件・セッションの開始 | `schema_dto.rs:349`・`:126`・`:52` | G1 の最終セッションの切り出し（B1-5）・O1 草案の作業種別（B3-4） | 候補。⚠️ `meta.o1_install_id` と絶対時刻は必ず落とす（ADR-039 D6） |
| A11 | `probe_assignment`・`probe_response` | 自己申告の割り当てと回答 | `schema_dto.rs:373`・`:396-`（中身は未読） | v0.3 の PreReg-2〜8（B4） | 候補 |
| A12 | `gse-replay --features` の rows | 1 Hz の特徴行（activity・boundary・dispersion・stall_onset・quality・revision・restart） | `src-tauri/src/analysis/feat_offline/mod.rs:162`・`replay.rs:111-` | P1 の凍結値での episode と報告項目（B2-3） | 保留（`t_ms` が絶対時刻・共有しない規約・上の 4）。⚠️ `boundary` は区切りの前後のカテゴリの数を持ち、照合の手がかりに近い |
| A13 | ブロックごとの特徴量表（今は無い） | G1 の FS-A 5 本＋FS-B 9 本・`n_keydowns`・`span_ms` をブロックごとにまとめた表 | `experiments/20260801-controlled-friction-task/analyze.py:443-471` が計算する（ファイルには書き出していない） | G1 の主判定と補助の判定のほぼ全部（B1） | 候補になりうる（段 0 と段 1 の間の粒度）。⚠️ `analyze.py` は NDJSON しか読まないので、この表から判定を再現する入口は今は無い |
| — | `key` 行 | 押したキーのカテゴリと押下・解放の時刻 | `schema_dto.rs:141` | 表 B の「生の打鍵が要る」行 | **段 2**（段 1 ではない） |

## 表 B — 事前登録ごとの数値と、要る表現

「段 1 で可」= 表 A の表現だけで再現できる見込み。「生」= key 行（段 2 以上）が要る。

### B1. G1（主判定は §3.3・`analyze.py`）

| # | 数値 | 要る表現 | 段 1 で可か | 一次 |
|---|---|---|---|---|
| B1-1 | FS-A（f1・f3・f4・f5・f6 のブロックごとの中央値） | A1 ＋ 各ブロックの最初の keydown の時刻 `t0` | 可（`t0` を別の列で渡せば） | `analyze.py:443-449` |
| B1-2 | FS-B Tier 0 の `keys`・`bs_rate` と、適格性の門（各ブロックの keydown ≥ 100） | keydown の数・BS/Del の数 | 生（または A13） | `analyze.py:463-464`（特徴量）・`:54`・`:707-710`（適格性の門） |
| B1-3 | FS-B Tier 0 の `external_paste_chars`・`ime_dwell_med` | A5・A6 | 可 | `analyze.py:465-466` |
| B1-4 | FS-B Tier 1 の `silence_p50/p90/max`・`burst_p50/p90` | 打鍵間の間隔の分布と連なりの長さ | 生（または A13）。閾値 2000 ms を変えた感度分析は生 | `analyze.py:427-441`・`:467-471` |
| B1-5 | 主判定（並べ替え検定・Fisher 法）・補助（OOF AUC）・positive control・最終セッションの切り出し | B1-1〜B1-4 の特徴量行列とラベル・`session_start` | 特徴量の側しだい（FS-A だけなら可） | `preregistration.md` §3.3・`analyze.py:631`・`:674` |
| B1-6 | 操作チェック（強制比較）・`attainable_min_p` | フォームの回答・ラベルの配置 | 打鍵は不要 | `analyze.py:812-842`（操作チェック）・`:658`（`attainable_min_p`） |

### B2. P1 の episode（合否を判定しない・数値は運用パラメータとその結果）

| # | 数値 | 要る表現 | 段 1 で可か | 一次 |
|---|---|---|---|---|
| B2-1 | 凍結値（`w_ms`・`q`・`b_ms`・`hole_gap_ms`・`warmup_count`・`theta_estimator`・`t1a_window_ms`・`net_diff_min`） | 値そのもの（段 0 で出せる） | 段 0 | `docs/preregistration-p1-episode.md:133-140`・`p1-episode.json` |
| B2-2 | idle trim（`idle_trim_min_gap_ms`・`idle_trim_max_ms`） | `feat` 行の時刻・key 行と A8 の最後の入力の時刻 | 生（「最後の入力の時刻」の列を別に出せば可） | 同 md `:298`・`:318-319` |
| B2-3 | 凍結値での episode（`stall_onset.is_onset` の数・`theta_person_ms`・`ime_overlap`・`observed_intervals`） | A12 | A12 を出すなら可（A12 は保留） | 同 md `:154-156`・`:309` |
| B2-4 | 探索空間・選択格子 27 通り・感度の OFAT・極 `modifier_m_plus` | key 行（修飾キーの押下区間を含む）と非打鍵行からの再計算 | 生 | 同 md `:178-205`・`:254-256` |

### B3. O1 の事前登録草案（第 0 版・未凍結・数値の合否はほぼ【決】）

| # | 数値・項目 | 要る表現 | 段 1 で可か | 一次 |
|---|---|---|---|---|
| B3-1 | 主判定: `left_observation` の上下界の幅が介入の判断を反転させない割合 ≤ ε | `left_observation`（focus の喪失・アプリの切り替え = A7・草案 `:67`）と、Nudge の発火の可否の入力（`p_stuck` = A3） | A7 は段 1 で可。発火の可否には A3 が要る（A3 を出さない候補にするなら段 1 では再現できない） | 草案 `:67`・`:135-152` |
| B3-2 | `left_observation` の本数 | A7 の時刻 | 可 | 草案 `:102-104` |
| B3-3 | 有効日・除外の区間 | A9・打鍵と非打鍵の有無 | 有無の判定に key 行が要る見込み（推測） | 草案 `:102`・`:160`・`:173` |
| B3-4 | 作業種別の欠損率・端末の単位・G1 混入の確かめ | A10 | 可（`o1_install_id` は公開物に入れない） | 草案 `:42`・`:114`・`:211` |

### B4. v0.3 の較正スモーク（参考）

| # | 数値 | 要る表現 | 段 1 で可か | 一次 |
|---|---|---|---|---|
| B4-1 | PreReg-4 の個人内の C-index | A11 の回答 ＋ A2 の窓の中央値 | 可 | `docs/preregistration-v0.3.md:75-79`・`src-tauri/src/analysis/calibration_eval.rs:120-170` |
| B4-2 | PreReg-1〜3・5〜8（尺度の理解・回答率・欠測・二軸性・holdout） | A11 とビネットの回答・セッションの順序 | 打鍵は不要（PreReg-6 の Recall の入力の中身は未読） | 同 `:62-101` |

## まとめ（研究者の判断の材料・決定ではない）

- 段 1 の最小の候補は **A1・A2・A5〜A11**（`feat` 行の特徴量と EMA 後の軸、非打鍵の行、自己申告）。これで G1 の FS-A・O1 草案の一部・v0.3 の数値が再現できる見込み。
- **A4（`keys`・`bs_keys`）と A3 は出さない候補**。A4 は逆算の見込みがあり、どの数値にも使われていない（G1 の `keys` は key 行から数える）。
- **A12（`--features` の rows）は保留**。絶対時刻と共有しない規約があり、`boundary` は照合の手がかりに近い。
- 打鍵間の間隔の分布・キーの数・パラメータの探索を要する数値は段 1 では再現できない。2 本目の解析計画がこれらを主要な数値にするなら、**A13 のような集計表**（段 0 と段 1 の間）を作って関門にかけるか、その数値は「申請があればコードをデータ側へ送る方式」（issue #333 の C）で扱う、のどちらかになる。
- 段 1 の各項目も ADR-039 D6 の関門（照合・結び付け・健康状態の推定）にかける。A5（貼り付けの文字数）と A6（変換の時刻）は、照合の手がかり（長さの並び・区切りの位置）を持つので、特に先に測る。

## 読んでいない範囲（Explore の報告・2026-10-10）

- O1 の旧草案（`.steering/20260823-o1-nonkeystroke-gap-and-prereg/preregistration-draft.md`）の本文。
- G1 の `preregistration.md` の §2.1〜§2.4・§2.7〜§2.14・§3.7〜§3.9・§5.3〜§5.4 の本文。
- `calibration_eval.rs` の C-index・Recall・MNAR の計算本体、`probe_response` と vignette 行の schema。
- `OutcomeMetrics`（`metrics.rs:202`）を使う事前登録が、上の 4 つ以外にあるか。
