# タスクリスト

## 0. 同期（前提）

- [x] `git fetch --all` → `main` を origin/main へ fast-forward（**87 コミット**・`2155a0a` → `00c906c`）
- [x] mac 側の文献更新の着地を確認（`[P45]`–`[P53]` / `[V75]`–`[V78]` が references.md に実在）
- [x] `docs/literature/20260807-self-state-externalization-and-ambient-media.md`（642 行）取得を確認
- [ ] ⚠️ **未処理**: タグ `v0.1.21` のローカル（`a26eafa`）とリモート（`90d86d2`）の食い違い → **ユーザー判断待ち**
- [ ] ⚠️ **未処理**: ローカル stash 1 件（`win-local: gitignore tmp_codex rule + budget.json`）と未追跡 `MEMO`

## 1. サーヴェイ（docs/ へ landing）

- [x] RQ を 4 本に分解（A: 無視のコスト / B: 連続表現の害 / C: 制作者の設計語彙 / D: 感性＝探索仮説）
- [x] 12 検索・**一次資料 5 本取得**（[P54] は **PDF 全文を逐語照合**）
- [x] 敵対的検証 12 主張（3-0: 5 / 2-1: 4 / 1-2: 1 / **0-3 否決 2**）
- [x] `docs/literature/20260810-auditory-modality-and-aesthetic-sensitivity.md` を作成
- [x] `docs/references.md` に **P54–P63 / V79–V80** を append-only 登録（**既存番号の再利用なし**を検証）
- [x] `docs/literature/_index.md` に行を追記
- [x] gate 判定を更新（`音は第 1 版に入れない` を**維持**し、根拠を設計判断 → 文献へ格上げ）
- [x] ★ **対称性**: 案に有利な推論（R-1）と不利な推論（R-2）を**同じ基準で両方 0-3 否決**

## 2. アイディアの深化（.idea/ へ）

- [x] `.idea/20260810-media-expression-sound-and-prototyping.md` を作成
- [x] 段階の骨格を [P54] の notification level 4 段に載せ替え
- [x] 「徐々に介入する」の具体案を 2 つ提示（案 A: 視覚の段＋最上段直前の 1 音 / 案 B: 音を回復側へ）
- [x] 音の具体パラメータを [P58] の**反転**として演繹（★ 実証ではないと明記）
- [x] RQ-D（感性）を **主張しない・測らない・捨てない**の三重扱いで隔離
- [x] ★ **決めていないこと 5 件を明示的に開いたまま残す**（ユーザー指示「具体設計は随時」に対応）

## 3. 制作ツール連携（試作専用）

- [x] 実機の CLI 入口を**全て実行して確認**（TD / Substance / AE / Blender / C4D / Audition / ME）
- [x] ★ `toeexpand` / `toecollapse` の存在とヘルプを確認（TD を Claude Code の射程に入れる鍵）
- [x] TD 同梱 Python が **3.11.15** で uv 側と一致することを実行確認
- [x] ⚠️ **Audition / Media Encoder に CLI が無い**ことを確認（音の生成は Python へ回す根拠）
- [x] 既存 `gse-replay` の出力（`FeatSnapshot` 1Hz・content-free）で足りることを確認＝**GSE 本体の変更不要**
- [x] `design.md` に「やらないこと」を明示（OSC/WS 未実装・被験者環境へ配備しない・`experiments/` に置かない）
- [ ] Step 1（`toeexpand`/`toecollapse` の往復検証）**未実施** → 実施は未定

## 4. 受け入れ条件の確認

- [x] カードに検証票（n-m）と「やり残し」がある
- [x] references.md の追加が **P54 以降 / V79 以降**（重複 ID なしを `uniq -d` で検証）
- [x] 否決リストに理由付きで残っている（有利・不利の両方）
- [x] 「感性が育つ」が探索仮説として隔離され、確証トラックに混入していない
- [x] TD/Adobe 連携が実機確認に基づく（推測で書いた箇所は「未確認」と明記）
- [x] `docs/preregistration-v0.3.md` に変更なし
      （⚠️ **旧記述「git diff は 28 行追加のみ」は本編登録直後の中間確認であり最終形ではない**。
      追補 2〜5・steering・引き継ぎを含む**最終 diff は 8 ファイル・2,311 行の追加**。
      ★ **凍結対象が無傷である主張自体は変わらない**——`git diff --name-only` で
      `preregistration-v0.3.md` / `engine.rs` / `glossary.md` / `research-positioning.md` の
      不在を確認済み。cross-review 指摘 #3 で訂正）

## 1b. 追補 2（同日）: ドローンは別カテゴリである

- [x] 研究者の明確化（アラームではなくメディアアートのドローン系）を受けて再評価
- [x] ★★ **本編カード4 の一般化が誤りであることを特定**（ISE の条件は変化でなく**分節**）[P64]
- [x] `docs/references.md` に **P64–P69** を append-only 登録
- [x] 文献カード冒頭に**訂正の警告**を追加（本編だけを引用させない）
- [x] `.idea` メモに改訂節と**ドローン設計の具体案 α/β/γ** を追加

## 1c. 追補 3（同日）: 最大の空白を埋める

- [x] 9 検索・**一次資料 3 本取得**・6 主張検証（3-0: 2 / 2-1: 2 / **0-3 否決 2**）
- [x] ★ **ドローン直接の ISE 実験は存在しないことを確認**（＝確認済みの空白に変わった）
- [x] ★★ **ISE 文献の steady-state の定義に `legato-music` が入る**ことを発見（ドローン＝legato の極限）
- [x] ★★ **新しい必須要件を確定**: **ユーザーが止められること**（制御不能な連続音は well-being 低下 [P71]）
- [x] ★ **慣化の桁を取得**（30 日・毎日 20 分で約 53% 減衰 [P70]）＝前ラウンド カード12 の穴に数値が入った
- [x] ★★ **[P72] の効果主張を 0-3 否決**（subgroup・統制曲が別楽曲で交絡・Brain.fm との COI）
- [x] ★ **「主観は動くが客観は動かない」が 3 例目**であることを記録（[V35] / [P71] / [P73]）
- [x] `docs/references.md` に **P70–P74** を append-only 登録

## 1d. 追補 4（同日）: 表現層は単独で立つか / 身体的回帰との連動

- [x] ★★ **表現層だけにすると information 系（d=0.00）へ落ちる**ことを 3 経路から導出（[V40] / [P54] / [P6]）
- [x] ★ **自己シグナリングの出典を一次で取得** [P75]（PDF 全文逐語・★ 論文自身の例が「雨の日のジョギング」）
- [x] ★ **本トラック最優先の未取得文献を実質的に閉じた** [P76]（Stusak et al. 2014・abstract 逐語）
- [x] ⚠️ **moral placebo effect** を新しいリスクとして特定（自己像だけが上がる）
- [x] `docs/references.md` に **P75–P76** を append-only 登録

## 1e. 追補 5（同日）: 歩行を計測して MhD に入れるか

- [x] ★ 「MhD」が GSE の既存用語（Mind-house Detector・`glossary.md` 139）であることを確認
- [x] ★★ **前提の訂正**——`.idea/20260801-*` の実測により「打鍵だけで足りている」は崩れている
      （§1.1 X は偶然水準 / §7.2 GATE3 に届かない見込み / §2-4 詰まりは「打鍵しないこと」に現れる）
- [x] ★★★ **歩行だけが特殊な理由を特定**——**defer アームで構造的欠測＝ランダム化が救済にならない**
      （§3.A の他候補は自発的に生じるので救済される）
- [x] ★★★ **[P77] Etkin 2016 を一次取得**（PDF 全文逐語）——**報酬でなくても計測自体が害**。
      opt-in・任意閲覧・本人の希望の 3 防御がすべて論文内で潰れている
- [x] ★★ **境界条件を特定**——**打鍵（作業）の計測は安全側、歩行（回復）の計測は害が最大の側**。
      現行設計（Phase 1 は WoZ + 自己申告）は既に正しい側にいる
- [x] ★★ **生存形を提示**——**合流点を推論層でなく表現層に置く**（MhD 無変更・センサー不要）
- [x] `docs/references.md` に **P77** を append-only 登録

## 1f. セッション終了処理

- [x] 全ラウンドの結論を `.idea/20260810-media-expression-sound-and-prototyping.md` に統合（§9 / §10 追加）
- [x] 次セッション用の引き継ぎを作成: `.steering/_handoff/next-session-prompt-media-expression-layer.md`
      （★ 前セッションの文脈を持ち込まずに成立する形で・CLAUDE.md 制約と落とし穴を埋め込み）
- [x] 追跡ファイルの変更が **追加のみ・削除ゼロ**であることを検証
- [x] **コード無変更**・`preregistration-v0.3.md` / `glossary.md` / `engine.rs` **無変更**を検証

## 2b. 第 2 セッション（2026-08-10）: 引き継ぎ §3 / §3b の 10 問を閉じる

- [x] 引き継ぎ §1 の読む順を実行（`.idea` 本体 / 文献カード**本編＋追補 2–5** / `decisions.md` D1–D11 /
      第 2 版 / `20260801-*` §1・§5・§7）
- [x] ★ 引き継ぎ §1 の指示に従い **`.idea` §2.5–2.6（α/β/γ・M1/M2/M3・設計制約表）を `.steering/` へ複製**
      → `open-questions-decision-material.md` §1
      （★ 正確には **`.idea/*.md` が git 管理外**であり `.idea/` 全体ではない。F1 を参照）
- [x] ★ `verify-before-claiming` を適用し、**引き継ぎ・`.idea`・記憶を根拠にせず一次資料まで降りた**（6 件）
  - [x] **F1**: `.gitignore:40` の実効範囲を `git check-ignore` で実測
        → ★ **引き継ぎ「`.idea` は git 管理外」は過度の一般化**。`.idea/prototypes/` は追跡下に入る
  - [x] **F2**: `intervention_eval.rs:11/:352` + `probe_scheduler.rs` + P000 実測
        → ★ **HIR の分母 labeled-ACT はセッション当たり数件＝もともと低検出力**
  - [x] **F3**: ★★★ **`.idea` §2.5.4 の中心的トレードオフを訂正** — **β は主アウトカムを失わない**
        （セッション間ラグ設計。歩行と違い defer アームで欠測しないのでランダム化が機能する）
  - [x] **F4**: `anonymize.rs` / `packaging.rs:85` / `logger.rs:1808` を読み、副次指標 4 件の算出可否を確定
        → ★ 編集距離は**方針以前に原理的に計算不能**。翌日再開率は**ファイル名経由**で可（要 `data-privacy`）
  - [x] **F5**: `gse-dataset` の confusion matrix を集計 → ★ **Incubation は最頻の予測クラス（42.2%）**
  - [x] **F6**: ★★ **70/30 は β の対比に最適でない**（相対効率 1.190）。**50/50 なら 19% 少ないセッションで足りる**
        ＋ 必要セッション数を逆算（d=0.5・n=5 で **1 人 12.6 セッション**）
- [x] `open-questions-decision-material.md` を作成（判断材料・選択肢・コスト・崩れる条件）
- [x] ★ **研究者に 8 問を確認して確定**（`requirement.md` の温度に従い勝手に決めない）
- [x] `decisions.md` に **D13–D19（確定）＋ D20（未決 2 問の推奨）** を追記
- [x] `reproducibility-discipline` を Read し、D18（`experiments/` 配下）が背負う 8 点を明示
- [x] **コード無変更**・`preregistration-v0.3.md` / `engine.rs` / `probe_scheduler.rs` / `schema_dto.rs`
      / `references.md` **無変更**を検証（次番号は **P78 / V81** のまま）

### 2b-1. cross-review（Codex 第二意見）と、その指摘への対応

- [x] 前提ゲートを実測（codex-cli 0.141.0 / jq 1.8.2 / 予算残 82,445 ≥ per_invocation_max 30,000 /
      proprietary・機密ファイルなし）。diff 915 行 = 警告閾値 500 超・手動承認閾値 2000 未満で進行
- [x] ★ **未追跡ファイルが `git diff` に写らない問題**（memory `cross-review --cached gap`）を
      `git add -N` で回避——主成果物が漏れるところだった
- [x] `bash scripts/run-codex-review.sh` 実行。**指摘 6 件・誤検知ゼロ**
- [x] #1 **50/50 と 70/30 の混在**を訂正（§4 Q7 が旧案のままだった）
- [x] #2 **「`.idea` は git 管理外」の誤前提が tasklist に残存**していたのを訂正（→ `.idea/*.md`）
- [x] #3 **翌日再開率を「保留（`data-privacy` 未通過）」に格下げ**（採用候補に見えていた）
- [x] #4 **「β は主アウトカムを失わない」を限定**——保たれるのは計器と因果チャネルであって検出力ではない。
      **境界の欠測（k → k−1）／持ち越し／慣化／セッション間隔**の 4 要因を明記
- [x] #5 ★ **数値主張の再現手段を追加** → `verify-claims.py`（下記）
- [x] #6 tasklist の章順の崩れを訂正（`## 6` `## 7` → `## 2b` `## 8`）

### 2b-2. 数値主張の再現性（cross-review #5・`verify-before-claiming` ルール 6）

- [x] `verify-claims.py` を追加。F5 / F6 / `stuck_recovery_ms` 集計を**再計算して期待値と突き合わせる**
- [x] **PASS を確認**（`cd /c/gse-dataset && python <repo>/.steering/20260810-.../verify-claims.py` → exit 0）
- [x] ★ ルール 5b（検査自体を複数状態で試す）: **入力不在でも黙って通らないこと**を確認
      （明示メッセージ＋exit 1。当初は `ZeroDivisionError` だったのでガードを追加）
- [x] ⚠️★★ **入力を commit hash で固定できないことが判明**——
      `gse-dataset` の対象 31 本のうち **13 本が未コミット（untracked）**。
      → **入力集合の sha256 `665b56cf9a1ea1fd` を刻む**方式に切り替えた（ドリフトすれば FAIL する）

## 8. 残（第 2 セッション後・優先度順）

- [ ] ★★★ **1 人あたりのセッション数を決める**（研究者「未定」）。D14 の逆算表から
      「検出する価値のある最小の差」を先に決めて逆算する。**≈8/人 のままだと D13（β）は成立しない**
- [ ] ★★ **D20 の 2 問を閉じる**（統合評価の設計 / 副次指標の事前登録）。★ 副次指標は **PreReg-5 の対象**
- [ ] ★★ **Step 1（`toeexpand`/`toecollapse` 往復検証）** — ここが通らなければ TD は扱えず D18 の前提も消える
- [ ] **翌日再開率を採るなら `data-privacy` を通す**（F4: 匿名化が中身から捨てた暦日をファイル名から復活させる）
- [ ] `gse-dataset` に他被験者の metrics が入ったら **F5 を再集計**（D16 の前提確認・1 コマンド）
- [ ] pilot に **Incubation の読み取りを確認する自由記述 1 問**を足す（D16 の未検証部分）

## 9. 残（次セッション以降・文献側）

- [ ] ★★ **`legato-music` を steady-state の例とする記述の一次逐語**（追補 3 の中心的根拠が二次記述水準・**最優先**）
- [ ] ★★ **ドローン ON/OFF を独立変数にした自前の測定**——**文献では埋まらない空白**。
      ⚠️ **G1 は凍結なので別実験**（★ G1 の copy task positive control と打鍵計測は流用できる骨格）
- [ ] **[P71] の一次全文**（N・「制御できない場合」の操作化）
- [ ] **[P65] の "(non-)disturbance impact 過大評価" の向き**（設計目標を fluctuation strength に置けるか）
- [ ] **「自分のための音」の無効化率**の実測研究（[P55] の転移可能性が決まる）
- [ ] **日本語版 soundscape の調整角**（[V79]・音を測定に使うなら前提条件）
- [ ] **執筆課題での背景音の効果**（[P66] は難易度を 154 実験中 17 でしか実測していない）
- [ ] [P62] duplex-mechanism の一次全文（生存形「一瞬のマーカー」の寿命が決まらない）
- [ ] **感性工学（日本語圏）を未探索**（RQ-C が英語圏文献に偏っている）
