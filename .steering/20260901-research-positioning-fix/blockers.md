# 詰まり・持ち越し

## 持ち越し 1: ⚠️★★★ Lv2 Wall の陳腐化は `research-positioning.md` の外にも広く残っている

- **発見日**: 2026-09-01（本タスクの影響範囲調査 `verify-before-claiming` ルール 2「消費者を探す」）
- **実測コマンド**:
  ```bash
  grep -rn "Lv2\|Wall" docs/*.md docs/architecture/*.md | grep -v "research-positioning\|glossary\|adr/"
  ```
- **結果**: ★ **Wall を現行機能として書いている docs が本タスクの対象外に多数ある。**

| 文書 | 状態 | 判定 |
|---|---|---|
| `docs/functional-design.md`（L65 / 69 / 71 / 73 / 87 / 95 / 105 / 117 / 248 / 255 / 376 / 378 / 383 / 404 / 405） | ⚠️★★★ **Wall Need 閾値・cooldown・daily cap・Wall Server・Monk Mode を現行仕様として記述** | ★ **要是正（最優先）** |
| `docs/verification-runbook.md`（L92-97 / 117） | ⚠️★★★ **「2.3 Wall 全画面ブロック (非回帰)」という検証手順が生きている** —— 削除済み機能の非回帰テスト | ★ **要是正**（★ 実行すると必ず落ちる） |
| `docs/pilot-runbook.md`（L10 / 146 / 147） | ⚠️★★★ **被験者への手順書が「Wall が出たら案内文に従う」と指示している** —— ★ **被験者向け文書は契約である** | ★ **要是正（最優先）** |
| `docs/wbs-verification-halfyear.md`（L153 / 222 / 223 / 282） | ⚠️ 強 Wall / Wall 閾値を WBS の前提に置いている | 要是正 |
| `docs/development-guidelines.md`（L226 / 248） | ⚠️ Wall Server の性能・セキュリティ要件が残る | 要是正 |
| `docs/repository-structure.md`（L15） | ⚠️ `Overlay.tsx` を「Nudge/Wall 介入オーバーレイ」と説明 | 要是正 |
| `docs/architecture/gse-v2-overview.md`（L112 / 118）/ `intervention-decision-engine.md`（L69-92）/ `personalization-and-online-learning.md`（L638 / 956-957） | ⚠️★★★ `InterventionAction{None,Nudge,Wall,Defer}` を**現行型として記述しているが、実体と食い違う** | ★ **要是正（実測済み）** |
| `docs/architecture.md` / `docs/agent-shared.md` / `docs/glossary.md` | ★ **既に是正済み**（ADR-015 参照つきの過去形） | 対応不要 |
| `docs/design-history.ja.md` / `docs/design-history.md` | ★ **履歴文書。過去の実装を記述するのが役目** | ⚠️ **触らない** |
| `docs/experiment-tracking.md`（L28）/ `docs/architecture/expression-channel.md`（L95-101 / 269） | ★ 過去の事実・既決の引用として言及 | 対応不要 |

- **なぜ本タスクでやらないか**:
  引き継ぎメモのスコープは `research-positioning.md` に限定されており、
  ⚠️ **ADR-018 D7 が「`docs/` の SSOT 20 ファイルの一括改名は本 ADR の範囲外（別タスク）」と明記**している。
  ★ かつ上表は**単なる改名ではなく仕様記述の是正**（閾値・Server・Monk Mode）を含み、
  **コードの実体を実測してから**でないと書けない（`verify-before-claiming` ルール 1）。
- **次タスクの入口**:
  1. ★ **コードの実体は 2026-09-01 に実測済み**（下記）。改めて grep する必要はない。
  2. `docs/pilot-runbook.md` と `docs/verification-runbook.md` を**最優先**で直す
     （★ 被験者・検証者が実際に読む文書であり、契約である）
  3. `docs/functional-design.md` の Lv2 節を ADR-015 参照つきで過去形にする

- ★ **コード側の実測（2026-09-01・`verify-before-claiming` ルール 1）**:
  ```
  $ grep -n -A8 "enum InterventionAction" src-tauri/src/analysis/intervention.rs
  16:pub enum InterventionAction {
  17-    None,
  18-    Nudge,
  19-    Defer,
  20-}
  ```
  → ★ **`Wall` バリアントはコードに存在しない。**
  `grep -rn "Wall\|wall" src-tauri/src src` の 38 ヒットは全て
  (a) `wall-clock`（無関係）/ (b) 削除の経緯を記した**コメント**
  （`intervention.rs:566-571` に削除した 4 テストの名前が記録されている）/
  (c) `replay.rs` の**旧ログ後方互換パース**（`action=wall` の `intervention_response` 行を
  読めることのテスト）—— のいずれかであり、**現行の発火経路は無い**。
  ⚠️★★★ **したがって `docs/architecture/*` の 3 文書は「実装がそうなっている」と読める形で誤っている。**

---

## 持ち越し 2: 生成 AI 群・検証スキップ群の references 登録が未了

- `decisions.md` **判断 2** により、本タスクは「本文が実際に引く分」のみ append した。
- ★ 以下は `.steering/20260830-mitou-2027-proposal-slimming/survey-notes.md` に**逐語つきで揃っているが未登録**:
  - **生成 AI 下の認知的関与**: Burelli 2026 / Lee 2025 (CHI) / Afshar 2025 (NEJM AI) / Lukac 2025 / Feng 2026
  - **検証を飛ばす・主観の乖離**: Skitka 1999 / Parasuraman & Manzey 2010 / Fan 2026 (CHI) / Parry 2021 /
    Murphy-Hill 2021 / Deslauriers 2019 / Khojah 2026（反証側）/ Melumad & Yun 2025 / Peng 2023 / Sandoval 2023
- **入口**: §3 ランドスケープ / §4 差分に AI 関連の本文を書くタスク。
  ★ `survey-notes.md` 結論 2 / 結論 5 の「書ける最強の形」がそのまま本文の素材になる。
- ⚠️ **登録時は引用禁止リスト（`survey-notes.md` 末尾）を必ず参照すること** ——
  特に **Alter et al. (2007) の disfluent font**（Meyer 2015 が 17 実験・N=7,367 で否定）と
  **METR の 19% を現在の事実として**引くことは禁止。

---

## 持ち越し 3: ⚠️ 凍結文書 `docs/preregistration-v0.3.md` とのずれ（★ 直さない・記録のみ）

- **確認日**: 2026-09-01
- ★ 本タスクでは**凍結文書を触らない**方針のため、ずれを発見しても是正しない。
- ★ 発見したずれは本節に追記する（現時点では未調査 —— 本タスクの是正対象 5 件が
  preregistration 側に波及しているかは**未確認**である）。
  ⚠️ **「ずれが無い」ではなく「見ていない」**（`verify-before-claiming`: 未確認は未確認と書く）。

---

## 解消済み 4: ★ 「ただ**消耗**させる摩擦」という中核の言い回しが限定資源モデルの語彙である

- **発見日**: 2026-09-01（本タスクの語彙置換の自己点検 `grep -nE '消耗|リソースの補充|認知リソース'`）
- **場所**: `docs/research-positioning.md` §2 目指す世界（Vision）
  > 「消すべきでない摩擦（自力解決の機会を含む苦闘）」と「ただ**消耗**させる摩擦」を見分け、前者を保護する世界。
- **なぜ問題か**: 「消耗させる」は**有限の資源を減らす**ことを含意し、
  本タスクが §3 (d) で外した **ego depletion / ART の枠組みに乗る**（[P199] d=0.04 / [P200] d=0.06 / [P201] PEESE b=0.003）。
- **対応**: ★ `docs/research-positioning.md` §2 の主文を
  「ただ**関与を削る**摩擦」へ置換した（2026-09-01 code-reviewer 指摘を受けて本タスク内で解消）。
- **残る注意**: `docs/agent-shared.md` 等、research-positioning 外の概要文に同じ語彙が残る場合は、
  持ち越し 1 の **docs 全体の旧仕様是正タスク**で消費者を実測してから直す。

---

## 持ち越し 5: ★ 軽微 —— `docs/references.md` の `[V59]` / `[V72]` 行が 9 列ある（既存の問題）

- **発見日**: 2026-09-01（新規行の列数検算のついでに実測）
- **実測**: 表は 8 列だが、`[V59]`（L316）と `[V72]`（L329）だけ **9 列**ある
  （★ 本文セル内にエスケープされていない `|` が 1 つ混入している）。
- ★ **本タスクの変更ではない**（`git diff --cached -U0 docs/references.md | grep -cE '^\+\| \[V(59|72)\]'` = **0**）。
- **影響**: ★ **`scripts/check_citations.py` は誤動作しない**（状態は `cells[-1]`、重複列は `cells[-2]` で
  末尾から取るため、途中に列が増えても正しく読める）。⚠️ **Markdown のレンダリングで列がずれるだけ**の軽微な問題。
- **直し方**: 該当セル内の `|` を `\|` にエスケープする。
- ⚠️ **本タスクでは直さない** —— 無関係な行の変更は `/cross-review` の差分を汚すため（★ 次の references 編集タスクで拾う）。

---

## 持ち越し 6: ⚠️★★ 「回復」がカテゴリラベルとして未修正箇所に残っている（★ `/cross-review` が発見）

- **発見日**: 2026-09-01（`/cross-review` の Claude 側指摘 #7 → メインが実測で確認）
- **実測コマンド**:
  ```bash
  grep -nE '回復' docs/research-positioning.md \
    | grep -vE '自力回復率|productive_manual_recovery|打鍵再開|訂正|旧文|関与の再開|自力回復リスク'
  ```
- ⚠️ **持ち越し 4（§2 Vision の「消耗させる摩擦」）とは *別の* 見落としである。**
  持ち越し 4 は本文中で自己申告したが、**本件は自己申告していなかった**。

### 区別が要る —— 2 種類ある

| 種別 | 例 | 判定 |
|---|---|---|
| ★ **正当**（否定対象の主張を*名指しで引用*している） | L304 / L307「歩けば認知が回復する」という読み ／ L556「『散歩が認知作業を回復させる』は文献に支持されていない」／ L596 / L621 | ★ **直さない**（★ 直すと何を否定しているのか分からなくなる） |
| ⚠️ **カテゴリラベルとしての用法**（＝ 限定資源モデルの語彙が地の文に残っている） | **L385 / L386**「回復活動そのものを計測せず」／ **L524 / L534 / L791**「『回復の検出』を目的にした系」／ **L537 / L1074**「歩行（**回復**）の計測は害が最大の側」／ **L631 / L634**「停滞からの『回復』の予測」／ **L774**「回復活動を測らないこと」 | ★ **要判断**（下記） |

- **なぜ本タスクで直さないか**:
  ★ 下段は **`.idea` / 過去カード / ADR-017 D10 の判定文からの引き写し**であり、
  ⚠️ **元の文書側の語も同時に直さないと SSOT が割れる**（持ち越し 1 と同じ構造）。
  かつ **L631/L634 の「回復」は ITS 文献（[P33]–[P35] wheel-spinning）の用語**で、
  ★ **ego depletion ではなく「停滞から前進へ戻ること」を指しており、置換すると原典とずれる。**
- **次タスクの入口**:
  1. ★ **まず [P33]–[P35] 系（L631/L634）を「回復」のままにするか決める** —— 原典の用語なので残す判断が妥当と思われる
  2. 残り（L385/L386/L524/L534/L537/L774/L791/L1074）を **「関与の再開」/「離席」/「身体的回帰」**へ置換
  3. ⚠️ **引き写し元**（`.idea/20260806-*`・`docs/literature/20260815-*`・ADR-017 D10）**も同時に見る**
- ★ **本タスクの 5 件の是正の正確性は損なわれていない**（下段はいずれも Physical Anchor の *理論基盤* の主張ではなく、
  観測・計測対象の呼び名である）。

---

## 持ち越し 7: ⚠️★★★ `/cross-review` を回したのに `.codex/budget.json` が更新されていない

- **発見日**: 2026-09-01（コミット直前の `git diff HEAD -- .codex/budget.json` が**空**だったことから）
- **実測**:
  ```
  $ PYTHONUTF8=1 python -c "import json;d=json.load(open('.codex/budget.json'));print(d['today'])"
  {'date': '2026-08-31', 'tokens_used': 154980, 'invocations': 2}
  ```
  → ★ **今日（2026-09-01）の実行が 1 件も記録されていない。**
- **しかし Codex は実際に走っている**: `cross-reviewer` は
  `bash scripts/run-codex-review.sh HEAD -- <5 パス>` が **exit 0** で終わり、
  **6 件の具体的な指摘**を返したと報告した（空振りではない）。→ ★ **トークンは消費されたはずである。**
- **スクリプト側の意図**: `scripts/run-codex-review.sh` は更新する作りになっている ——
  `:194` 逐語「結果を python で parse: 最終 agent_message を stdout、**token を budget.json へ反映**」／
  `:248` `p = os.environ.get('BUDGET_FILE') or '.codex/budget.json'` ／
  `:259` 中断で壊れないよう書き込みを工夫した旨のコメント。
  ★ `:75` には逐語で「**ここで落ちると codex 課金後・budget 更新前に死に、消費が記録されない**」とある。
- ⚠️★★★ **なぜ更新されなかったかは未診断である**（★ `verify-before-claiming`: 未確認は未確認と書く）。
  ★ 候補は (a) `:246` の「`budget records invocation only`」経路に入り token 数が取れなかった、
  (b) サブエージェントの cwd と `BUDGET_FILE` の解決、(c) 例外の握り潰し —— **いずれも未検証**。
- **なぜ重要か**: ★ **予算ガードが実際の消費を過小に数える。**
  memory `silent-failure-in-guard-scripts` の型そのもの（「ゲートが検査しているつもりで素通り」）。
  ⚠️ 今日の残予算は「200,000 全部残っている」と表示されるが、**実際は 1 回分消費済み**である。
- **次タスクの入口**:
  1. ★ **`scripts/run-codex-review.sh` を単体で走らせ、`budget.json` の before/after を実測する**
     （★ 予測しない。走らせる —— `verify-before-claiming` ルール 5）
  2. `:194-260` の python ブロックで **token が取れなかった場合に何が起きるか**を 3 状態（正常 / token 欠落 / 例外）で試す
     （★ ルール 5b）
  3. ⚠️ **`invocations` だけでも必ず加算されることを保証する**（消費を 0 と記録するより、回数だけでも残す方が安全）
