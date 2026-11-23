# IMPL_NOTES — 計器を作るときに自分で決めた細部と、設計書との食い違い

設計書（`.steering/20261123-rhythm-stage-person-world/design.md`）は変えていない。ここにあるのは、設計書が決めていなかった実装の細部と、設計書の通りにできなかった所。結果を出す計算（下見・本番・スモーク）は回していない。

## 作ったもの

- `scripts/gen_sessions.py`: `--world person-m|person-r`・`--icc`・`--k` を足した（既存の world はバイトで不変・G0）。
- `scripts/stage.py`: `PC1-id`・`PCp-`・`PC0-id-`・`PC1-pers`・`PCps-`・`PC0p-`（既存の名前の出力は不変）。
- `scripts/person.py`（新規）: (5)・(6)・PC-raw・神託・1 位の当たり・R²・k の較正・各 mode（`--ceiling`・`--pilot-k`・`--pilot`・`--apply-pilot`・`--run [--smoke]`）。`checks.judge` を import して使う。
- `scripts/selftest_person.py`（新規）: design §3.7 の G0〜G5・R1・P1〜P5・Q1〜Q3・J1〜J4 と変異 14 本。`selftest.py` から呼ぶ。
- `config.json`・`run.sh`・`env.md`・`data.md`・`SEED`（20261125）。

## 設計書が決めていなかった細部（自分で決めたもの）

1. **`config.json` の旧 `ceiling.*`・`pc_stall.lam` を残した。** `checks.judge` が `ceiling.main_auc`・`pc_stall.lower/upper/aim/pilot_grid` を読み、前の自己検査（g050/f200 の下見・`apply_pilot` 等）が `ceiling.steps` を読むため。新しい段は `person.steps`。`ceiling.steps` の g050/f200 はこのタスクでは走らせない。
2. **名前の写像で `checks.judge` を再利用した。** `PC1-id`→`PC1`・`PCp-X`→`PCs-X`・`PC0-id-X`→`PC0-X`（(6) は `PC1-pers`・`PCps-`・`PC0p-`）と入れ、出力を逆に写す。理由 `weak_stall_pc` は `weak_person_pc` に書き換える。判定を写し直していない（J1）。役の割り当ては `person.ROLES`／`role_prefixes`（J2・変異の対象）。
3. **変種の名前は `<候補>~ws`、その対照は `PCp-<候補>~ws` など。** 変種の判定は、親の PC1・null・天井をそのまま使い（null は親の値を変種の名前にコピー）、PCp・PC0-id は親の λ の画（同じ stage の系列）の特徴から同じ列を落として当てはめ直す。λ は `person.variant_lam`（親の値）を使い、選び直さない（J3・変異 14）。
4. **p 値のような「null の変種」は走らせない。** null は親の名前（候補・PCp・PC0-id・PC1-id）だけを 20 回回す（design の「親の null の条件」の読み）。
5. **要約の SD は母集団の SD（ddof = 0）。** 窓が 1 つのセッションは SD 0。窓の無いセッションは NaN（hgb は欠損をそのまま扱い、lr は中央値補完）。
6. **要約の基準 A は L300 の表の XA の最初の 11 列（A_NAMES）、A_speed は A ＋ XS の 15〜27 列（WS_NAMES の 13 量）。** design の「A の 11 量」「WS_NAMES の 13 量」の読み。
7. **分割の割り当て**: `derive_rng(seed, "folds")` で人の順列を作り `j % 5`。並べ替えごとの偽の人の分割は `"folds-perm-<r>"`（(6) は `"folds-perm6-<r>"`）。基準と候補で同じ。
8. **ブートストラップの重み**: 人を復元抽出した回数 m_p（多項分布）。同じ人の対は m_p、違う人の対は m_p m_q（P2 が、複写した人の対の AUC と一致することを確かめる）。(6) は人の中の AUC の差の差 D_p の重み付き平均。乱数は `derive_rng(seed, "boot-main" など)`。
9. **偽の人**: 240 本を `derive_rng(seed, "perm", r)` で無作為に並べ、6 本ずつ 40 の偽の人に分ける。偽の人の slot は並びの順（0〜5）。(6) の偽の人は slot 0〜2 で人ごとの読み手を当てはめる。
10. **(6) で除く人**: 学習の側（slot 0〜2）か読む側（slot 3〜5）が 1 クラスの人は、人ごとの読み手・共通の読み手の両方から除く（差の差を同じ人で取るため）。除いた数を `left_out` に記録。
11. **(6) の窓の特徴**: A の 15 列（XA）＋画の窓の特徴 20（`small`）、`full` は前のタスクと同じ 2 窓との差分 40 を足す。(5) の要約とは別。
12. **PC1-id・PC1-pers の画**: 全秒の値（PC1-id は Φ(z'_p)、PC1-pers は 60 秒のブロックの値）で、`r` は 0.5 の定数・止まりの処理は付けない（前の PC1 と同じ位置づけ）。PCp・PCps・PC0 系の候補の画は前の PC-stall と同じ作り（錨は止まり方つき、D は `a_block`）。PC0p は前の `PCs-` とバイトで一致する（自己検査で確認）。
13. **PC1-pers/PCps の s_p**: `derive_rng(seed, "pcsign")` の順列の前半 20 人を +1、後半を −1。`PC0p` は +1 の seam（`stage.pc0p_sign`）。
14. **PC-raw の 12 量の細部**: 間隔 0 ms は対数から除く。6 は隣り合う 2 間隔がどちらも 600 ms 未満の対の |対数の比|の中央値。9・10 は 600 ms 未満の間隔でつながる押下の続きの長さ（個数・秒）の中央値。11 は押下のある秒の数で割る。PC-raw の AUC は `hgb`・`lr` の大きい方、下限はその分類器の区間。
15. **k の格子**: 点ごとに `kgrid_curve` が 240 本をその場で生成して PC-raw を計算する（NDJSON を書かない・`gse-replay` なし）。選び方は `choose_k`（等距離は小さい k・範囲外や 0.02 超は `k_unreached`）。結果は `results/<段>/pilot-k/pilot-k.json`。
16. **下見 0（`--ceiling`）の止まり**: `pilot_gate` が (5)（PC-raw の下限 > 0.53 かつ基準 A が天井でない）と (6)（読み手の A の AUC が天井でない）を別々に判定し、`results/<段>/ceiling/ceiling.json` の `gate` に書く。`--pilot`・`--run` はその `gate` を読み、止まった問いを回さない（(5) は `no_person_signal`）。A_speed だけ天井の段は (5) の副だけ判定不能（`ceiling_kinds` が分類器を外す）。
17. **下見 1 の停止の語**: `ceiling`（使える分類器が無い）・`weak_detector`（PC1-id / PC1-pers の下限が 0.10 以下）・`no_finite_pcs`・`no_person_signal`。これらの基準（問い）の λ は書かない。design §3.7 の「本番・下見 1 の列での配線の検査」のうち PC1 は下見 1 の停止で、PC0-id・PC0p は本番の判定の `stop_path`／`baseline_not_below` として出る。落ちたときの停止（本番へ進まない）は `run.sh` では自動化しておらず、結果を見て研究者に伝える（§8 に書く）。
18. **スモーク**: 40 人 × 6 本は保ち、`--smoke` は人の層の world では長さを 0.05 倍（540 秒）にする（既存の world の `--smoke` の意味は不変）。ブートストラップ 200・並べ替え 2（`person.smoke`）。
19. **`run.sh` の自己検査は `--work` を渡さない。** 前の自己検査の `--work` の部分（旧 e13 の経路）は人の層の列では意味が薄く重いので外し、配線は `person.py` の自己検査（made-up の表）と gse-replay の因果性の検査で見る。
20. **`selftest.py` の `test_unchanged`**: `gen_sessions.py` は写し元と違うので SHA の一致を外し、G0（8 つの world の出力のバイト一致）に替えた。`stage.py` は前から写し元と違い、`test_stage_source` が既存の名前の出力を照らす。
21. **G4 の「長い burst」**: 設計書は「長い burst（作り物・10 万の間隔）」。実際の burst は長い間隔で終わるので、集めた間隔をまとめた中央値には終わりの選択の偏り（約 0.01）が出る。そこで自己検査は burst の長さを 10^7 秒にして 1 つの長い burst から 16×10^6 ms（約 10 万間隔）を集める。
22. **G2 の許容**: ICC 0.2・0.494・0.679 の 3 点を見る（0.494 だけだと、√ICC と √(1−ICC) の入れ替え（0.506）が 0.02 以内に入ってしまい変異 3 が落ちない）。
23. **P5・Q2 は lr のみ**（`person.KINDS` を一時的に差し替える）。配線を見る検査で、分類器の差は見ない。hgb の経路は e2e（下の「確かめたこと」）で通した。
24. **`StageInput` の読みの記録に当たるもの**: 要約は `SummaryInput`（F と G だけ）。`StageInput` は変えていない。R1 は要約・PC-raw の関数のソースに人・manifest・潜在値の語が無いことと、閉じた入力が人の番号を拒むことで確かめる。
25. **記述 (e1)〜(e3)・(e5)** は `run_main` が `summary.json` の `descriptions` に書く（(e4) は (6) の `records` の `d_comm`・`d_pers`・`auc_A`）。(e1) の神託の AUC は全 28,680 対で出す（評価の対ではない）。

## 設計書との食い違い・気づき

- **変異 12（要約の関数に人の番号を渡す）の落ち方**: 閉じた入力が `KeyError` を出すので「例外で落ちた」として数える（design は R1 で落ちると書く）。
- **PC0p の P2 的な余裕は小さい**: Q2 の made-up で PC0p の D の上限は +0.023（0.03 未満・余裕 0.007）。窓の数・人数を変えると超えうる。
- **(5) の `small`・`full` を PC-raw に使い分けない**: 設計の通り同じ 12 量なので、`full/hgb` と `small/hgb` は PC-raw では同一の値になる（`pair_auc_raw` は分類器ごとに 1 回）。
- **`code_fingerprint`** は `scripts/*.py` と `run.sh` 全体（`selftest_person.py` を含む）。
- **n_persons の固定**: `stage.N_PERSONS = 40`・`stage.SLOTS = 6` は定数で、`config.json` の `person.*` と一致することを自己検査が確かめる（変えるときは両方）。
- **設計書通りにできなかった所は無い**。ただし次は、実際に回さないと分からない: 下見 1 の所要（人ごとの読み手の当てはめの数が多い）、(6) の `hgb` の当てはめの安定（窓が少ないとき）、PC0p の上限。

## 確かめたこと（回した範囲）

- `selftest.py` 全体（前の検査 ＋ 新しい検査）と `--mutants`（前の 7 ＋ 新しい 14）。結果は戻り値に書いた。
- 配線の e2e（run の seed を使わず、`SEED` を 4000 にした入れ物の写しで 4001・4002 を使い、540 秒のセッション・`gse-replay` あり）: `--ceiling`・`--pilot`・`--apply-pilot`・`--run --smoke` を通した（結果の値は読まない・捨てた）。
- `run.sh --ceiling/--pilot-k/--pilot/--smoke/--main` は回していない（禁止）。`run.sh` の bash の構文と、`step_args`・`require_prev` は読み合わせただけで、実機では未実行。

## レビュー（code-reviewer・security-checker）の指摘への対応

直したもの
- HIGH 1（fail-open）: `person.py` の `--pilot`・`--run` は `ceiling.json` と `pilot.json` が無い・step／seed／config と instruments の fingerprint／k が違う・gate と pilot と config の λ が食い違う（apply-pilot 未実行を含む）と `SystemExit`（rc ≠ 0）。両方の問いが止まった段も止まる。`run.sh` の `require_prev` は前の段の main が `smoke: false` で五・六の verdicts を持つことを見る。
- HIGH 2（J2）: 期待する名前を文字列で書き（`LIT`）、`ROLES` の中で役を入れ替える変異 15 が落ちる。`stage.person_series`・`run_main` の直書きの名前と `PERSON_NAMES` の一致も検査する。
- MEDIUM 3: `ceiling.json`・`pilot.json`・`summary.json` に `k` を記録し、`record_problems` が config の k と照らす（`check_world` は `world.json` の world・ICC・k を照らす）。`apply_pilot` も pilot の k を照らす。
- MEDIUM 4（G3）: 参照の shift を生の乱数の流れから独立に計算（`indep_shift`）。変異 4 は G3 でも落ちる。
- MEDIUM 5（G4）: 次元 2 を生成の trace で確かめ（burst の長さ × exp(+s2/2)、休止の中央値と上限 × exp(−s2/2)）、AR(1) が burst の境目で引き直されることを境目をまたぐ lag-1 相関で確かめる。変異 16・17 が落ちる（`dim2_scales`・`ar1_reset` を seam にした）。
- MEDIUM 6（G1）: manifest の m_log・x1〜x3・speed_log が同じ z・ε から出ていること（生の流れから独立に計算）、k に依らないこと。ICC 0.679 の k 3 点も見る。
- MEDIUM 7: `run.sh --main` の後に `person.py --wiring`（PC1-id の利得・PC1-pers の D > 0.10、PC0-id・PC0p の上限 < 0.03）を自動で回し、落ちたら rc 3 と「研究者に伝える」を出す（結果は消さない）。コミットされていない変更があれば `--main` は始めない（`--smoke` は警告だけ）。
- MEDIUM 8: `summary.json` に config と code の fingerprint、`provenance.json` に `code_sha256`。`kgrid_run` は目標の m の段の `pilot.json` の step・seed・fingerprint を確かめる。
- LOW 9: 変異 12 は `chk` の失敗で落ちる（`KeyError` を捕まえて失敗にする）。`run_stage` の経路（manifest の潜在値を変えても候補・基準・対照の窓が変わらない）を `test_r1_stage` で確かめる。
- LOW 10: `null6` の分割数を `person.folds` から。
- LOW 11: 下見 1 の止まりの理由を `summary.json` の `pilot_stops` と各 verdict の `reason` に残す。
- LOW 12: `SEED.run` の値が `run_seed(mode)` と違えば止まる。
- LOW 13: `test_raw` で 0・2・4・5 番とそれ以外を手計算で確かめた（この過程で、間隔が一定のとき lag-1 相関に浮動小数のノイズで 1.0 が出る不具合を直した: 標準偏差の下限 1e-9）。P1 は全 fold を見る。
- LOW 14: 自己検査の subprocess の env を `{**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}` に。写し元を実行する前に SHA を照らす（G0）。`test_unchanged` に失敗があれば以降を止める。`run.sh` の `step_args` は world を person-m|person-r に限る。

直さなかったもの
- fail-closed の記録検査（`require_*`・`lam_problems`・`wiring_problems`）への変異は足していない。単体の検査（`test_records`）で落ちることは確かめたが、変異 14 本＋新しい 3 本の枠には入れなかった。
- `run.sh --pilot`／`--smoke`／`--main` の通しは禁止のため実行していない（`--wiring` の呼び出しと `require_prev` の bash の分岐は読み合わせだけ）。

## `/cross-review` 1 巡目（Codex）を受けた直し（design・判断 10 に合わせた）

- (5) の照合の AUC を、検証の組ごとの AUC の 5 つの平均にした（`FoldAuc`・`fold_auc`。ブートストラップ・帰無・PC-raw・k の較正・下見・ceiling の値も同じ量）。P2 を組ごとに作り直し、P6 と変異 18（組の得点を併せる）を足した。
- 変種（`~ws`）は判定の語を付けない記述にした（`summary.json` の `variants` に親と変種の上乗せ・区間。(5)・(6) とも）。変種のための PC の当てはめ・変種の null・`variant_lam`・J3 の旧検査・変異 14 は要らなくなったので外した（J3 は「変種を判定しない・λ の丸めの衝突を拒む」検査に替えた）。`verdicts` に変種は入らない。
- (6) の記述に `last_auc_diff`（AUC(A＋候補|人ごと) − AUC(A＋候補|共通) と 95% 区間・候補ごと・攻撃者ごと）を足した。
- 神託と PC-raw の比べは判定にも確かめにも使わず記述だけ。r の段で `speed_log` だけの距離の AUC を記述に出し、作り物の引きで 0.5 ± 0.03 を確かめる（`test_speed_only`）。
- 相対の型の `k h_j x_j` を [−1.5, 1.5] に切る（`gs.clip_log_scale`・変異 19）。`--k` は 1.0 以下。切った割合は `pilot-k.json` の `clipped_share_any`・`clipped_share_by_dim` と summary の `clipped` に記録（manifest に `clipped`）。k = 1.0 と極端な x で完走する検査（`test_clip`）。k = 0 のバイト一致（G3）は保たれる。
- `world.json` に生成の seed と mode を書き（`--run-mode` は人の層の world で必須）、`--ceiling`/`--pilot`/`--run` が自分の mode と seed と照らして違えば止まる（`check_world`）。
- `apply_pilot` が pilot-k.json・pilot.json の code の指紋も照らす。λ のキー（`.3f`）の衝突を拒む（`lam_key_problems`・下見 1 の格子と `stage_specs`）。
- `--wiring` が合否を `summary.json` の `wiring` に書き、`require_prev` は前の段の `wiring.passed` と、`summary.json` が git で追跡され変更が無いことを見る。
- `test_q1` は読む側の行が人 p の slot 3〜5 の添字の集合と一致することも見る。
- 直さなかった・できなかったもの: `--wiring` を書き込む summary は `dump` で書き直す（公開後の書き換え）。git の追跡の判定は bash の分岐の読み合わせだけで、実行していない。
