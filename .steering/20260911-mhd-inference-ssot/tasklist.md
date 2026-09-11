# タスクリスト

⚠️★★★ **`_survey-inference-architecture.md` は索引であって原本の代替ではない。**
2026-09-11 の調査で、48KB のメモを 250 行に要約したら 40 見出し中 9 節しか残らなかった実例がある。
**着手時に原本の該当節を必ず読む。**

## §0 準備 — ★ `.idea` 原本の熟読（**省略しない**）

`.steering/_handoff/idea-coverage-20260911.md` を開き、本タスク担当分（T3）の状態を確認する。

- [ ] **`20260910-mhd-criterion-practice-trace-and-g-o-validation.md`**（20KB）— ✅ 深掘り済み。
      ★ `grep -n "^#\{1,3\} " ` で見出し一覧を出し、`_survey` が拾った節と**突き合わせる**
- [ ] **`20260910-mhd-feature-work-behavior-literature-gap-survey.md`**（35KB）— ✅ 深掘り済み。同上
- [ ] **`20260911-mhd-growth-personalization-and-gse-overview-roadmap.md`**（18KB）— ✅ 深掘り済み。同上
- [ ] ⚠️★★★ **`20260801-architecture-signal-and-online-learning.md`**（28KB）— 🔶 **要約のみ・未検証**。
      「ADR-008/009 ＋ `personalization-and-online-learning.md` へ昇格済み」と**報告されただけ**。
      ★ **統合先がこの文書なので、何が既に昇格済みで何が落ちたかを原本で確かめる**
- [ ] ⚠️★★★ **`20260801-behavioral-context-online-latent-ml-design.md`**（24KB）— 同上
- [ ] **`20260901-smartphone-state-externalization-and-physical-return.md`**（54KB）— 🔄 深掘り実施。
      ★ **層・段の呼称（`L1〜L4` / `Stage1-4` / `M1〜M4`）は ADR-019 D2 / ADR-021 D11 が却下済みだが、
      呼称を剥がした中身は生きている可能性がある**。結果ファイルの有無を確認し、無ければ投げ直す
- [ ] **`20260819-user-validation-workspace-behavior-and-mhd.md`**（22KB）— 🔶 要約のみ。
      ★ 本文が「ほぼ決着済み」と自己申告。**残 open item 5 件だけ**確認すればよい
      （⚠️ `KeyCategory` の `Punctuation` 追加は**既に main にマージ済みで解決**）
- [ ] 読んだ結果で `idea-coverage-20260911.md` を更新する

## §1 T1 の完了を確認

- [ ] ⚠️★★★ **T1（`20260911-intake-arbitration-branch`）が完了している**こと
- [ ] 取り込み後の `docs/architecture/personalization-and-online-learning.md` の差分を確認
- [ ] 取り込み後の `docs/research-positioning.md`（+16 行）の差分を確認
- [ ] ⚠️ **上記と `_survey` の A 区分を突き合わせ、重複を除く**

## §2 ⚠️★★★ 最大の争点を先に裁定する

- [ ] **`ADR-008 D8` と `WP5 I2` の衝突**を裁定する
      - D8: 「③どの信号が効くかの癖には**専用の特徴選択機構を作らない**
        （1 人あたりラベル 20〜100 件では確実に過学習するため、②の係数の大きさとして吸収させる）」
      - I2: 「十分な過去 episode を持つ人だけ、限定候補から**個人別 feature subset** を選ぶ」
      - ★ **I0/I1 は D8 と両立する。I2 だけが正面衝突する**
      - ⚠️ **新規 ADR で D8 を明示的に部分改訂しない限り SSOT 化できない**
- [ ] ⚠️ **`/reimagine` を設計段階で起動する**（`requirement.md` の運用メモで Yes と決定済み）。
      オンライン学習の境界そのものを動かす判断なのでやり直しが効かない

## §3 issue 分解

- [ ] `issue-slicing` skill を読む（**Opus** で実行）
- [ ] `_survey-inference-architecture.md §11` の A / B 区分から縦切り issue を作る
- [ ] `issues/00X.md` ＋ `_issue-plan.md`（DAG・Allowed Files 交差表）を出力
- [ ] ⚠️ **`acceptance.sh` を書く**
- [ ] `/clear` して新セッションで実行する

## §4 実行（A 区分）

- [ ] 段別モデル候補と昇格判定表 → `gse-v2-overview.md` または ADR-019 への補遺
- [ ] **三つの時間**・**三つの出力を混ぜない** → `personalization-and-online-learning.md §7.2`
- [ ] **hyperparameter tuning 対象 / 禁止リスト 5 項目** → 同 `§6` または新設節
- [ ] auto-tuning の offline global tuning
- [ ] WP5 **I0**（共有特徴 + 個人別縮約係数）
- [ ] **feature importance の四層** → 同 `§8.1`
- [ ] ⚠️ **用語整理**: `Mh-D` → **`MhD`** / `M1〜M4` → **実体名**
      （固定 baseline / criterion 直結 / 個人・タスク適応 / 時系列）

## §5 実行（B 区分・統合が要る）

- [ ] ⚠️ **registry 11 項目と `ADR-008 D5` の pinning リストの一本化**
      （`seed` ↔ `random_seed`、`profile_version` 系 vs `dataset_version`/`split_manifest`）
- [ ] ⚠️ **Tier 名の衝突解消** — 既存 Tier 0/1/2 は「**収集済みか否か**」の軸、
      `.idea` の T0/T1a-d/T2/Q は「**認知の跡がどこにあるか**」の軸。**同名だが軸が違う**

## §6 検証

- [ ] `PYTHONUTF8=1 python scripts/check_doc_lexicon.py` が exit 0
      （★ **`M1〜M4` と `Mh-D` が残っていないこと**）
- [ ] `PYTHONUTF8=1 python scripts/check_citations.py` が exit 0（★ 緑になるまで繰り返す）
- [ ] `code-reviewer` + `security-checker` を**並列**起動
- [ ] ⚠️ **`/cross-review`**（skip した場合は理由を明記）

## §7 完了処理

- [ ] `idea-coverage-20260911.md` を最終更新
- [ ] `design.md` / `decisions.md` の最終化
- [ ] `/finish-task`
- [ ] git commit（⚠️ `git add -A` 禁止。パス明示）
