# ADR-037: O1 の宣言に 5 つ目の値 `other`（「その他・細切れの作業」）を足す

- **ステータス**: **Accepted**（★ 2026-10-02 研究者承認。D3・D4・見直しの閾値「過半」を含む）
- **日付**: **2026-10-02**
- **決定者**: 研究者 ＋ Claude Code
- **関連**:
  **ADR-016 判断 4 / 4b-2 / 4b-3**（★ 本 ADR が覆す「新 enum 値は足さない」）/
  **ADR-006 Migration 5**（「task_kind enum は 4 変種維持」）・**下位決定 #3**（Creative に打鍵 β を持たせない）/
  **ADR-010 D1 / D3**（out-of-scope を head にしない／観測から `task_kind` を推定しない）/
  **ADR-005**（additive versioning）/ **ADR-014**（O1）/ **ADR-031**（6 択 ESM・⚠️ 本 ADR とは別の軸）
  ⚠️★★★ **本 ADR は既存 ADR の本文を 1 文字も書き換えない。** ★ 覆す決定は番号の大きい側に置く。
- **作業記録**: `.steering/20261002-o1-task-kind-other/`
- ★ **外部の理論・文献には依拠しない**（根拠はすべて repo 内の決定と実装）。

---

## ⚠️★★★ 最初に固定する切り分け

| # | ★ 本 ADR が **する**こと | ⚠️ 本 ADR が **しない**こと |
|---|---|---|
| 1 | ★ `task_kind` に 5 つ目の値 `other` を足す（O1 の宣言 UI にだけ出す） | ⚠️ G1 の開始画面（argumentative lock）に出す（⚠️ ただし **backend では閉じていない** —— `record_session_meta` は G1 / 通常運用でも `TaskKind::parse` の 5 値を受け付ける。G1 を論述に固定しているのは frontend の lock だけで、`creative` などでも以前から同じ状態である） |
| 2 | ★ `other` を **Writing fallback** で採点する | ⚠️ 新しい head を作る ／ 推論・特徴量・HMM の数値を変える ／ `HMM_VERSION` を上げる |
| 3 | ★ 同意フォームの宣言の列挙を 5 択に直す | ⚠️ ADR-031（6 択 ESM）の同意改訂を承認・実装する |
| 4 | ★ 「未設定」（`session_meta` の不在）は**そのまま残す** | ⚠️ `unknown` を足す（★ ADR-016 判断 4b-3 は維持） |
| 5 | — | ⚠️ 観測から `other` を推定して埋める（★ ADR-010 D3） |

---

## Context

### 1. 4 択には「どれとも決めづらい時間」の受け皿が無い

O1 は自然な作業を常時記録する（ADR-014・ADR-016 判断 4b-0）。宣言は
**論述 / 通信文 / デザイン・映像・制作作業 / vibe coding** の 4 択である（ADR-016 判断 4b-2・
`src/components/RecordingControls.tsx` の `O1_TASK_KINDS`）。
自然な作業には、**メールを読む・調べもの・細かな事務**のように 4 つのどれとも決めづらい時間が多く含まれる。

★ そのとき被験者に残るのは次の 2 つだけである:

1. **当てはまらない値を無理に選ぶ** → 4 つの値のラベルが汚れる
2. **前の宣言を出しっぱなしにする** → ⚠️★★★ ADR-016 判断 4b-3 が「**原理的に検出できない**」として
   事前登録 §11 の限界に回した**陳腐化した宣言**を、⚠️ **制度の側で誘発している**

⚠️ 「未設定」（判断 4b-3 の `session_meta` 不在）は**逃げ道にならない**。
★ 一度宣言した後に未設定へ戻す経路は無く、仮にあっても **「忘れた」と「どれでもない」を区別できない**。

### 2. O1 は未配布である

★ 2026-10-02 に研究者が確認した。★ 同意フォームの改訂・事前登録（`preregistration-draft.md`・**未凍結**）の
追記・schema の追加の代償が**最も安い時点**である。⚠️ 配布後なら再同意の判断が要る。

### 3. ⚠️ 本 ADR とぶつかる既存の記述（★ 全文 grep で拾った）

| # | 記述 | 場所 |
|---|---|---|
| a | 「★ **新 enum 値は足さない**（D7-iii のまま）」 | ADR-016 判断 4 |
| b | 「★ 既存 4 値をそのまま出す。⚠️ **新 enum 値は足さない**」 | ADR-016 判断 4b-2 |
| c | 「`schema_dto.rs` は additive のみ（**task_kind enum は 4 変種維持**）」 | ADR-006 Migration 5 |
| d | ⚠️★★★ 「鍵を増やすと**鍵あたりのデータが減る**。**task_kind は 4 変種を超えて増やさない**」 | `docs/architecture/task-adaptation-and-scope-gating.md` §3.2 |

★ a〜c は「schema を動かさない」ための**運用上の制約**で、O1 未配布の今は代償が小さい（D4）。
⚠️ **d だけは実質の反論である** —— 個人ベースライン（個人 × `task_kind`）の鍵が 1 つ増える。→ **D3** で答える。

---

## Decision

### D1. ★ `task_kind` に `other` を足す。画面の語は「その他・細切れの作業」

- 値名: **`other`**（`TaskKind::Other` / `TaskKindDto::Other`・snake_case で `"other"`）
- 画面の語と補足 1 行:
  > **その他・細切れの作業** —— メールを読む・調べものなど、どれとも決めづらいとき。メールを書くのは「通信文」
- ★ **逐語一致の範囲**: UI の補足（`O1_TASK_KINDS` の `note`）は、同意文書の雛形
  `consent-draft-o1.md` §2 の表の右列と**逐語一致**させる（既存 4 値と同じ規則）。
  ★ 同意フォームの正本（`Form_O1/GSE_O1_Form_Builder.gs`）は**語（ラベル）を逐語**にし、補足は**同じ意味の別文**で書く
  （⚠️ 機械検査 `o1_form_builder_test.cjs` が見ているのはラベルだけである）。
- ★ 補足の括弧は **「通信文」との境界**を閉じるためにある（メールを *読む* = other、*書く* = 通信文）。
- ★ 出すのは **O1 の宣言 UI だけ**。G1 の開始画面は argumentative に固定したまま（交絡統制・`research-positioning §9`）。
- ★ 「未設定」は残す。→ **ログ上の 3 状態が分かれる**: 4 つの領域のどれか ／ `other`（本人が「どれでもない」と言った）／
  宣言なし（忘れた・まだ選んでいない）。

### D2. ★ `other` は **Writing fallback** で採点する。推論は変えない

- 振り分け: `TaskKind::Creative | TaskKind::Other => TaskDomain::WritingFallback`（`logger.rs` の `From<TaskKind> for TaskDomain`）
- ★ `head_id = writing_fallback` の定義は「**適合する head が無いまま Writing head で採点した**セッション」
  （`analysis/heads/mod.rs` の `HeadId::WritingFallback`）であり、`other` にそのまま当てはまる。
  ⚠️ `head_id` だけでは Creative と区別できない。★ **区別は `session_meta` の `task_kind` で行う**。
- ★ ADR-010 D1 に反しない —— `other` は**宣言の値**であって head ではない（`NullHead` は作らない）。
- ⚠️ 推定を止める案は採らない（→ Alternatives B）。

### D3. ⚠️ 個人ベースラインの鍵を増やさない —— **`other` はベースラインの鍵にしない**

★ 反論 d への答え。`task-adaptation-and-scope-gating.md` §3.2 が懸念するのは
**意味のある領域が細かく割れて鍵あたりのデータが痩せること**である。

- ★ `other` は領域ではなく「**どの領域とも言えない**」という申告である。→ ⚠️ **独立した鍵として個人ベースラインを推定しない**。
  ★ 個人ベースライン（未実装・ADR-008 / ADR-009）を実装するときは、`other` の区間を
  **ベースラインの推定から除外する**か、**未宣言と同じ扱い**にする（どちらにするかは実装時に決める。⚠️ 鍵にする案だけを禁じる）。
- ★ むしろ逆向きの利得がある: 決めづらい時間が 4 つの鍵に**誤って流れ込まなくなる**ので、
  **4 つの鍵のほうのデータが汚れにくくなる**。
- ⚠️ この利得は**予想であって実測ではない**。パイロットで `other` の比率を見る（→ Consequences）。

### D4. ★ schema は additive に 1 値足す。`HMM_VERSION` は上げない

- `TaskKindDto` に `Other` を足し、`emit_schema` で `schema/current.json` を再生成する（ADR-005 の additive の範囲）。
  ★ gse-dataset の `schema/current.json` も同じ版に揃える（`scripts/check_schema_parity.py`）。
- ★ `HMM_VERSION` を上げない根拠: `analysis/engine.rs` の版の規約は、既存ログの確率列が変わらなくても
  「新しい入力クラスに対して**挙動の分岐条件が増える**」なら MINOR とする。
  ★ `other` は既存の fallback 経路に乗るだけで、出力は `writing` と**同一**である（分岐は増えない）。
  ログ上の新しい値は **schema の版**が記録する。
- ★ 既存ゴールデンは `argumentative` / `vibe_coding` だけなので **byte-equal のまま**であることを acceptance にする。

### D5. ★ 同意フォームの改訂は `other` の 1 点だけ

- ★ 文面の上流 `consent-draft-o1.md` §2 を先に 5 択へ直し、それを正本 `Form_O1/GSE_O1_Form_Builder.gs` の「4 つの選択肢」の 2 か所へ写す
  （★ `.gs` 冒頭の規則「先にあちらを直してからここへ写す」）。
  ★ 既存の約束「何を選んでも、記録する内容は 1 つも変わりません」は **`other` でも真のまま**である（D2）。
- ⚠️ ADR-031 の同意改訂（6 択 ESM）とは束ねない（ADR-031 は Proposed で承認待ち）。
  ⚠️ その結果、**同意フォームの再配備が将来もう 1 回要る可能性**を受け入れる。

---

## Alternatives

| 案 | 内容 | 却下の理由 |
|---|---|---|
| A | 現状維持（4 択） | ⚠️ Context-1 の 2 つの失敗（誤った選択・陳腐化した宣言）を制度が誘発し続ける |
| B | `other` の間は推定を止める（`feat` を出さない） | ⚠️ R3-a（`task_kind` に依存しない `left_observation` の内訳）の入力から、自然作業の大きな部分が抜ける。★ 除外は解析側で `task_kind = other` によっていつでもできる |
| C | 「未設定に戻す」ボタンだけを足す（schema 不変） | ⚠️ 「忘れた」と「どれでもない」を区別できない。★ 本人の明示ラベルが残らない |
| D | 値名を `free_task`（「フリー作業」）にする | ⚠️ 境界の補足は同じだけ要る。★ 汎用の `other` のほうが後の解析で誤読されにくい |
| E | ADR-031 の同意改訂と束ねる | ⚠️ 本 ADR が ADR-031 の承認に縛られる |

## ⚠️ 却下した主張（★ 本 ADR が足す禁止リスト）

1. ⚠️ 「`other` を足したので**陳腐化した宣言の問題は解けた**」—— ★ 誘発の 1 経路を減らすだけで、切り替え忘れは残る（ADR-016 判断 4b-3 の限界は維持）。
2. ⚠️ 「`other` の区間は**推定の対象外**である」—— ★ 推定は走っている（D2）。対象外にするかは**解析の判断**である。
3. ⚠️ 「`other` が増えれば 4 つの鍵のデータが**きれいになった**」—— ★ D3 の利得は予想。実測するまで書かない。
4. ⚠️ 「`writing_fallback` は Creative のこと」—— ★ 本 ADR 以降は Creative と Other の両方を含む。

## Consequences

- ★ ログ上で「どれでもない」と「宣言なし」が分かれる。
- ⚠️ `head_id = writing_fallback` に 2 つの宣言が同居する（`task_kind` で分ける）。
- ⚠️ `other` が**何でも入れられる箱**になり、4 つの領域のデータが減る可能性がある。
  ★ **見直しの条件**: パイロットで宣言時間のうち `other` が過半を占めたら、語と補足を見直す
  （⚠️ 閾値はパイロット前に事前登録ドラフトに書く）。
- ★ 旧バイナリで `other` を含むログを replay すると、`bin/replay.rs` が警告して Writing に倒す（落ちない）。
  ⚠️ そのとき刻まれる `head_id` は `writing_fallback` ではなく `writing` になる（数値は同一）。新旧の replay を突き合わせるときは `task_kind` で揃える。
  ★ O1 の配布は本 ADR を含む新しいタグから行う（`docs/o1-distribution-tag.md` に新しい節を足す・別タスク）。

## Migration

1. `logger.rs` / `schema_dto.rs` に `Other` を足し、振り分けを D2 のとおりにする。`schema/current.json` を再生成する。
2. `HeadId::WritingFallback` / `HeadIdDto::WritingFallback` / `heads/writing.rs` の説明を「Creative と Other」に直す（★ 型と数値は不変）。
3. O1 の宣言 UI（`RecordingControls.tsx`）と `probeTypes.ts` に `other` を足す。
4. `consent-draft-o1.md` §2 を 5 択に直し、`Form_O1/*.gs` の 2 か所と `o1_form_builder_test.cjs` へ写す。
5. 現行仕様を述べる docs（`glossary.md`・`workspace-behavior-observation.md`・`task-adaptation-and-scope-gating.md` §3.2・
   `functional-design.md`）を追随させる。⚠️ ADR 本文は直さない。
6. O1 の事前登録ドラフト（未凍結）に、`other` の扱い（D2・D3）と見直しの閾値を書く。
7. gse-dataset に schema の対 PR を出す。
8. ⚠️ 配布前の別タスクで: 新タグを切る・GAS フォームを再配備する・`docs/o1-distribution-tag.md` に節を足す。
