# 設計 v2（/reimagine 1 回目・requirement.md だけから作り直した案）

## 実装アプローチ

v2 の軸は 2 つ。「押すたびに 1 行を書いて終わる（途中の答えを誰も持たない）」と、「キーの登録はカードの部品の生き死にに結びつける」。

### 1. 押すたびに書く（追記だけ・途中の状態を持たない）

- Q3 を押したら、その場で今と同じ 2 行（`realtime_label` answered・`activity_label`）を書く。`realtime_label` の q1・q2 は段 1 では常に null（Q1・Q2 は別の行で持つ）。
- Q1・Q2 は新しい行種 `s1_scale_label { probe_id, scale: "friction" | "progress", value: 1..=5, latency_ms }` を押すたびに 1 行書く。
- 押した分はその時点で記録に入っているので、カードがどの経路で閉じても書き足すものが無い（判断 3 の「押した分を残す」が構造で成り立つ）。
- driver の `ProbeCard` には「Q3 を答えた」「Q1 を答えた」の 2 つの印だけを持たせる。印のあるカードが閉じる経路（閉じる・superseded・一時停止・終了）では、skipped の行を書かない（すでに answered を書いた）。
- 新しい行種なので `capabilities` の行種の一覧に載り、「計器が無かった版」と「聞かなかった・答えなかった」を行種で分けられる（ADR-031 D4 が `activity_label` を新しい行種にしたのと同じ理屈）。

### 2. キーの登録は frontend のカードの部品が持つ

- `@tauri-apps/plugin-global-shortcut` を npm に足し、`S1ProbeCard` が描かれたら（`useEffect` の mount）その段のキーを `register` し、消えたら（unmount・段の替わり）`unregister` する。カードが消える全経路は「部品が消える」に集まるので、backend の閉じる経路を数え上げなくてよい。
- キーの callback はクリックと同じ関数を呼ぶ。キーとクリックが 1 本の道になる。
- 登録に失敗したら（Promise の reject）キーの表示を消し、クリックで答える。
- backend の共通ハンドラ（`lib.rs:6051`）は変えない（数字の組には当たらない）。
- 修飾キーは macOS ⌥・Windows Ctrl（判断 2）。frontend が OS を知る手段は backend の `S1ModeDto` に足す。

### 3. 読み手

- `realtime_label` は段 1 では answered でも q が null になる。`bin/replay.rs`・`calibration_eval.rs` は「q がそろった answered」で数え、q の無い answered を破損と扱わない（較正の既存の記録は変わらない）。
- 段 1 の Q1・Q2 の解析は `s1_scale_label` を `probe_id` で突き合わせて読む。`s1_replay.rs` に集計を足す。

### 4. 答えの打鍵

- 判断 5 のとおり、フックは変えず、カードの区間で除く（事前登録 S1-B3）。

### 5. 画面

- Q3 は 7 つの大きなボタン（キーの表示つき）、Q1・Q2 は 5 つのボタン（初期値なし）、下に「思い出せない」「閉じる（⌥0）」。「回答する」は無い。優先の規則は初回の説明（`S1ConsentPanel.tsx`）へ。

## 変更対象

- `src-tauri/src/logger.rs`・`schema_dto.rs`・`schema/current.json`・`capabilities.rs` — 新しい行種 `s1_scale_label`、段 1 の `realtime_label` の q null
- `src-tauri/src/s1_driver.rs` — カードの 2 つの印、印のあるカードを閉じるときに skipped を書かない
- `src-tauri/src/lib.rs` — `answer_s1_probe_q3`・`answer_s1_probe_scale` のコマンド、`S1ModeDto` に OS
- `src-tauri/src/bin/replay.rs`・`analysis/calibration_eval.rs`・`s1_replay.rs` — 数え方と新しい行の集計
- `package.json`・`package-lock.json` — `@tauri-apps/plugin-global-shortcut`、`Cargo.toml` の版との整合
- `src/components/S1ProbeCard.tsx`・`src/probeTypes.ts`・`src/components/S1ConsentPanel.tsx`
- `docs/adr/`・事前登録・同意文書・フォーム・`data-privacy` ルール 7・glossary・functional-design・gse-dataset の schema・削除保証の対象の行種（`o1.rs:183` の一覧）

## 既存パターンとの整合性

- 新しい情報は新しい行種で持つ（ADR-031 D4）。
- 画面は描くだけ（ただしキーの登録は画面の部品が持つ。backend が真実を持つ作法からは外れる）。

## テスト戦略

- 単体: 押すたびの行の形、印のあるカードを閉じる全経路で skipped が出ないこと、新しい行種の往復と capabilities の網羅のテスト（`capabilities_covers_every_line_type`）。
- 単体（frontend）: 段の替わりで登録・解除が対になること（モックで）。
- 回帰・schema・実機（macOS の目視・tap が答えのキーを見るか）は v1 と同じ。

## リスク

- 行種が増えるので、gse-dataset の schema・削除保証・capabilities・同意文書の「記録するもの」の表に足す箇所が多い。
- 段 1 の Q1・Q2 の解析が 2 行の突き合わせになる。
- overlay の webview が global shortcut を登録する権限を使い始める（今は権限だけあって使っていない）。webview が任意の組を登録できる状態が実際に使われる面になる。
- JS の callback は overlay の webview が生きていることが前提（`hide()` で JS が休む問題は `show_s1_overlay` が避けている）。
