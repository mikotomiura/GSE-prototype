# practice-portrait-ssot

> ⚠️ **本タスクは issue 未分解。** 下記 2 本の `_survey-*.md` を読んでから
> `issue-slicing` skill で分解すること。
> ⚠️ **T1（`20260911-intake-arbitration-branch`）の完了後**に着手する。
> 取り込み後の `expression-channel.md`（+337 行）に既に書かれている可能性があり、重複判定ができないため。

## 背景

`.idea/` の 9/8〜9/9 の 3 本（`20260908-measurement-terminating-practice-portraiture.md` 48KB /
`20260909-content-evanescent-context-portraiture.md` 63KB /
`20260909-pigment-fluid-practice-portrait-synthesis.md` 14KB）が、表現層を
「推定された認知状態の表示装置」から **「実践生成肖像（Practice Portrait）」というメディアアート**へ
拡張する構想を、理論・造形・OS 制約・評価設計まで含めて展開している。

調査結果は本ディレクトリの 2 本に保存済み（★ **これが一次資料**）:
- **`_survey-20260908-claims-and-evaluation.md`** — 研究主張・先行系譜・評価 8 軸・主張しないこと 9 項目
- **`_survey-20260908-form-and-os-constraints.md`** — 造形・レンダリング設計・OS 制約・自前化の限界

### ★ 研究主張の核（`20260908 §5.3` の最小命題・逐語）

> **日常の知的作業が暗黙に共同制作するセッション固有の生成肖像が、普段は周縁に留まり、
> 必要時には同じ作品の内部から画面外への開口を作る。その先の身体を測定・達成判定・報酬化せず、
> 作品が自らの計測権限を終える。**

⚠️ メモ自身が「これは『要素の組合せが見つからなかった』だけでは研究貢献にならない」と明記し、
形式化すべき 6 項目を挙げている。

### ⚠️ 判明した最重要の事項

1. ⚠️★★★ **第一候補が入れ替わっている**
   `Semantic Reagent`（意味試薬）は第一候補から**降格**し、「本人が任意の語を渡した場合の比較条件」に後退。
   代わりに **`Palimpsestic Practice Membrane`（書き換わる実践膜）**が第一候補。
   ★ content-free が構造的に保証される（力学系の入力が `feature_trajectory`（F1/F3/F4/F5/F6・X/Y・invitation）と
   `session_seed` だけで、**生テキストも意味処理経路も持たない**）。

2. ⚠️★★★ **`Temporal Primitive` の定義が同一メモ内で食い違う**
   `§3.4` は 7 項目（`pace, continuity, revision, suspension, tension, persistence, observability`）、
   `§4.8` は 6 項目（`persistence` と `observability` が消え `cohesion` が新規）。**実装前に一本化が必須**。

3. ⚠️★★★ **`§4.8–4.10` に層ラベルが無く、`§4.12` まで読まないと Layer A 契約と衝突して見える**
   実装者が `§4.8` 単体を読むと「`level`/`invitation` 以外を載せない」契約を破る設計に見える。
   **SSOT 化の際は各節に層ラベルを付け直す必要がある**。

4. ⚠️★★★ **`§4.14` が設計上の不変条件を明らかにした**
   - **iOS のロック画面実行権限は、どの自前化の範囲でも増えない**
   - **secure lock screen と全 OEM の AOD は Android でも所有できない**
   - 専用端末化すれば技術的には解けるが、**研究対象の生態学的妥当性を失う**
   → ★ ADR-022 は技術的根拠を持つが、「**自前システムでも解けない**」という設計判断の結論文は本文に無い。

5. **`embedding inversion` が `data-privacy` Skill に無い**
   `[P1]` Morris et al. 2023 が「32-token 入力の 92% を完全復元、臨床記録から氏名も回復」。
   現行 SKILL ルール 3 は「VK コード → キー種別カテゴリ」レベルの匿名化しか想定していない。

## ゴール

`.idea` の Practice Portrait 構想のうち **A 区分（規約・境界・禁止事項・主張範囲）**を SSOT へ昇格する。
⚠️ **造形そのものは凍結しない**（試視が先）。

## スコープ

### 含むもの（A 区分）
- **`§10` 主張しないこと 9 項目** → `research-positioning.md` の主張範囲節
- **却下記録**（全文/全画面の受動取得を入れない・**二重非保存原則**・**Stop 条件 9 本**）→ 新規 ADR の Alternatives 節
- **避ける造形 7 モチーフ**（花・樹木／雲・天気／心臓・脳・顔／ペット・目／炎・電池・ゲージ／結晶／大規模流体）
- **`§3.2` 第一の肖像材料にしないもの 6 件**（`keys`/`bs_keys` / `paste` / `focus transition` /
  `pointer bin` / IME 状態 / `intervention response`）
- **`§4.14` の「自前化の限界」表** → `expression-channel.md §3.5.1b` ＋ ADR-022 の Consequences 節
- **`§4.11 #10` 視聴時間を成功指標にしない** → `expression-channel.md §7`
- **`embedding inversion`** → `data-privacy` Skill ルール 3 への追記
- 色を state へ直接マップしない規約 / 周縁開口型表現の 3 条件トレードオフ / PC 制作環境は母型であること
- **`§4.1〜4.5` の否定形の禁止事項**（派手さ・赤・警告を増やさない / 点滅・報酬を伴わない /
  無入力比例の成長を作らない）→ 既存禁止リストとの重複確認の上で

### 含むもの（B 区分・実装着手前に凍結）
- ⚠️ **`Temporal Primitive` の定義の一本化**（7 項目 vs 6 項目）
- ⚠️ **`§4.8–4.10` への層ラベル付け直し**
- **`§4.10` の 1Hz 意味更新 / 60fps 描画分離**・臨界減衰ばね・固定 dt・accumulator・clamp
  → `expression-channel.md §3.5.2`。⚠️ ADR-022 は OS 制約のみで**端末内補間アーキテクチャは未規定**
- ⚠️ **`semantic parity`** の用語定義（メモ内の造語で他文書に定義なし）
- 履歴の有限圧縮・セッション終了時消去（ADR-020 の長期プロフィール禁止の実装要件として）

### 含まないもの
- ⚠️ **造形候補の確定** → `§18.8` の最小比較試作（20〜30 秒 loop・3 案比較）が先（**C 区分**）
- ⚠️ **`§4.9` 流動エンジンの技法選定**（ばね格子 + curl-noise + パリンプセスト）
  → `experiments/20260902-expression-layerA-visual/` のハーネスで検証してから（**C 区分**）
- ⚠️ **`§6` 先行系譜の `[Pn]` 採番** → メモ自身が「予備調査であり体系的レビューではない」と自己申告。
  **scoping review が先**
- ⚠️ **`§9` 評価 8 軸の実施** → 形成的試視の実施待ち。⚠️ **被験者数・比較群が未確定**
- ⚠️ **`§5.1〜5.3` 新規性の主張の確定** → scoping review と評価設計を経てから
- ⚠️ **`§8` 横展開**（Coding / 音楽練習 / 手仕事 / 学習 / ケア）→ **D 区分**。
  メモ自身が「イベント意味が異なり単純転移できない」と明記
- ⚠️ **本人提供 seed の opt-in パイプライン** → メモ自身が「別 ADR・同意文・privacy audit・
  倫理審査判断が必要」と明記
- Pi Zero + LCD / フリップカバーのハードウェア試作（`.idea/20260909-physical-foreground-*`）

## 受け入れ条件

- [ ] A 区分が docs / ADR に反映され、`check_doc_lexicon.py` が exit 0
- [ ] ⚠️ **`Temporal Primitive` の定義が 1 つに確定している**
- [ ] ⚠️ **各節に層ラベル（層 A / 層 B / 将来拡張）が付いている**
- [ ] `data-privacy` Skill に `embedding inversion` が追記され、`[P1]` が `references.md` に採番済み
- [ ] ⚠️ **A 判定の項目が既存の一次資料（ADR-017/018/021/022・`expression-channel.md`・
      `glossary.md` 禁止用語）と突合されている**（★ **`.idea` の記述を無条件に正としない**）
- [ ] `/cross-review` を通している

## 関連ドキュメント

- ★ **`_survey-20260908-claims-and-evaluation.md` / `_survey-20260908-form-and-os-constraints.md`（本ディレクトリ）**
- `docs/architecture/expression-channel.md`（⚠️ **T1 で +337 行される**）
- `docs/adr/ADR-017` / `ADR-021` / `ADR-022`（層 A/B の契約）
- `docs/adr/ADR-025` / `ADR-026` / `ADR-027` / `ADR-028`（⚠️ **T1 で main に出現**）
- `docs/glossary.md`（禁止用語 15 件）
- `.claude/skills/data-privacy/SKILL.md`

## 運用メモ

- **/reimagine 適用: No**
- 理由: 本タスクの A 区分は「既に出ている結論を既存 docs の正しい節へ置く」作業であり、
  設計の再生成を要さない。⚠️ ただし **B 区分（`Temporal Primitive` の一本化）は
  どちらの定義を採るかの判断**を含むので、その issue だけは設計段階で選択肢を明示すること。
