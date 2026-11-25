# 設計（採用: v1 ＋ v2 から 1 点のハイブリッド）

## 実装アプローチ

カードの状態の真実は今と同じく backend（`s1_driver.rs` の `ProbeCard`）が持つ。答えを途中まで持つのも backend にする。そうすると、キーで答えてもクリックで答えても同じ 1 本の処理を通り、カードがどの経路で閉じても（閉じる・次のカードでの置き換え・一時停止・終了）押した分を backend が書ける（判断 3）。

### 1. 答えの段（step）

- `ProbeCard` に途中の答え `partial: Option<Partial>` を持たせる。`Partial { category, q3_latency_ms, q1: Option<u8>, q2: Option<u8>, last_latency_ms }`。
- 画面に出す段は `partial` から決まる: 無ければ Q3、`category` が詰まり・熟考・作業で q1 が無ければ Q1、q2 が無ければ Q2。Q1・Q2 を聞く 3 つは定数 1 か所に置く（`ActivityCategory::asks_scales()`）。
- `S1CardView::Probe` に `step: "q3" | "q1" | "q2"` と `keys: Option<KeyHint>`（登録できたときだけ、修飾キーの表示名）を足す。frontend は `step` で描き分けるだけ。
- 新しいコマンド `answer_s1_probe(probe_id, step, value, latency_ms)` 1 本。step と value が今の段と食い違えば拒む（二重押し・古いカードへの押下）。
  - Q3: `category` を置く。Q1・Q2 を聞かない選択肢なら、その場で 2 行を書いて閉じる。
  - Q1: q1 を置き Q2 へ。Q2: q2 を置き、2 行を書いて閉じる。
- `record_probe_response` は段 1 では使わなくなる（3 問を 1 枚で送る形）。消すか残すかは実装で使い先を確かめて決める（較正の v0.3 は別のコマンド `lib.rs:4582` 以降なので触れない）。

### 2. 書く行

- 完了でも途中で閉じても、`partial` があれば answered の 2 行（`realtime_label` と `activity_label`）を書く。`realtime_label` の q1・q2 は答えた分だけ入り、残りは null。
- `partial` が無いまま閉じたら今の skipped の 2 行（`dont_remember`・`dismissed`・`superseded`）。
- 段 1 用の書き手 `LogEntry::realtime_label_s1_answered(q1: Option<u8>, q2: Option<u8>, ..)` を新しく足す。較正の `realtime_label_answered` は触らない（較正の不変条件を道連れにしない）。`format_realtime_label_line` の debug_assert は「answered でなければ q は null」「q は 1..=5」に緩める。
- `activity_label.latency_ms` は Q3 を押すまで、`realtime_label.latency_ms` は最後に押すまで。
- 同意の取り消しで閉じるときは、`partial` があっても書かない（取り消しの後に `activity_label` を書かない。今の取り消しの扱いを実装で確かめて合わせる）。

### 3. 読み手

- `bin/replay.rs:4519`: answered で q が欠けた行を破損として捨てるのをやめ、q のある・無いを別に数える（`answered_without_scales`）。範囲外（1..=5 の外）は今どおり破損。
- `calibration_eval.rs`: 回答数・`valid_count`・回答率の分母を「q1・q2 がそろった answered」に限る。q の無い answered は別に数える。較正の既存の記録には q の無い answered が無いので、既存の数は変わらない（ゴールデンと fixture で確かめる）。
- `s1_replay.rs`: answered と skip_reason だけを見ているので変えない。Q1・Q2 の欠けの数を集計に足すかは事前登録で決める。
- `schema_dto.rs` の doc（433〜434 行）を直し、`emit_schema` で `schema/current.json` を作り直す。形（型）は変わらない。gse-dataset 側の写しも合わせる（ADR-005 の範囲の確認は ADR に書く）。

### 4. キー（カードの表示中だけ登録）

- 修飾キーは macOS ⌥、Windows Ctrl（判断 2）。Q3 は 1〜7、Q1・Q2 は 1〜5、閉じるは 0。
- 登録と解除は `run_s1_effects`（`lib.rs:2250`・カードの開閉の全経路が通る emit の直前）で、出す view から「あるべきキーの組」を決めて差分だけ登録・解除する。
  - ⚠️ driver のロックを持ったまま OS に登録しに行かない（global-hotkey は macOS でメインスレッドに回す。メインスレッドがロックを待つと止まる）。ロックを離してから行うか、`run_on_main_thread` に投げる。
  - 登録に失敗したら `keys: None` にして、画面はキーの表示を消し、クリックだけで答える形にする（判断 1）。失敗は warn に残す。
- ハンドラ（`lib.rs:6051` の共通ハンドラ）に、修飾キー＋ Digit0〜7 の分岐を足し、`answer_s1_probe` と同じ処理を呼ぶ。段 1 でないとき・同意が無いとき・カードが無いときは何もしない。
- O1 の形で登録しない理由（`lib.rs:7232`: 数週間キーを奪う・同意文書に無い行を書きうる）との関係: 登録はカードの表示中の数十秒だけで、ハンドラが書くのは同意文書にある 2 行だけ。研究者用の 6 本は今どおり登録しない。これを ADR と同意文書に書く。

### 5. 答えの打鍵の扱い

- フックは修飾キーの状態を持たないので、答えのキーは数字の打鍵として `key` 行と段 1 の押下（`s1_send_press`）に入りうる。macOS の tap がホットキーより先に見るかは実機で確かめる。
- 初案: フックは変えない（両 OS のフックに手を入れると Windows の実機確認が要り、G-GEAR は 11 月ふさがり）。代わりに、カードの表示から閉じるまでの区間を記録から特定できることを確かめ、事前登録 S1-B3 に「その区間の打鍵・クリック・フォーカスの移りを除く」と書く。調停器（生きている判定）では、答えの押下が最後の押下になる点を限界として ADR に書く（クリックで答える今の形も同じ性質を持つ）。

### 6. 画面

- Q3: 7 つの大きなボタン（見出しと短い注記・キーの表示「⌥1」）。問いの文は「直前の30秒、何をしていましたか?」だけにし、優先の規則は初回の説明（`S1ConsentPanel.tsx` の同意の説明）へ移す。
- Q1・Q2: 5 つのボタン（1〜5・両端の言葉）。初期値は無い。
- 下に「思い出せない」「閉じる（⌥0）」。「回答する」は無い。Q1・Q2 の段の「閉じる」は、押した分を残して閉じる。
- 押した直後に次の段へ替わる。送り中は押せない（二重押し）。

## 変更対象

### 修正するファイル
- `src-tauri/src/s1_driver.rs` — `ProbeCard.partial`・段の決定・閉じるときの行（partial があれば answered）
- `src-tauri/src/lib.rs` — `answer_s1_probe` コマンド、`run_s1_effects` での登録と解除、ハンドラの分岐、skip のコマンドの partial の扱い、生成コードの門のテスト（8408 行）
- `src-tauri/src/logger.rs` — 段 1 用の書き手・debug_assert の緩和・`ActivityCategory::asks_scales`
- `src-tauri/src/schema_dto.rs`・`schema/current.json` — doc の改訂と再生成
- `src-tauri/src/bin/replay.rs`・`src-tauri/src/analysis/calibration_eval.rs` — q の無い answered の数え方
- `src/components/S1ProbeCard.tsx`・`src/probeTypes.ts` — 段ごとの画面・キーの表示
- `src/components/S1ConsentPanel.tsx` — 優先の規則とキーの説明
- `docs/adr/ADR-057-*.md`（新規）・`docs/adr/README.md`
- `docs/preregistration-stage1.md`（S1-A3・S1-A4・S1-B3・前進）
- `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md`（承認待ちの版の §3）・`Form_O1/GSE_O1_Form_Builder.gs` とそのテスト
- `.claude/skills/data-privacy/SKILL.md` ルール 7（答え方の記述があれば）・`docs/glossary.md`・`docs/functional-design.md`

## 影響範囲

- 較正（v0.3）: 書き手を分けるので記録は変わらない。読み手の数え方を変えるが、既存の記録には q の無い answered が無いので数は変わらない。
- 本人の段 1（v0.1.42）の記録: 読み手は q がそろった answered を今どおり数える。
- capabilities: 行種を増やさないので変わらない。

## 既存パターンとの整合性

- 真実は backend・画面は描くだけ（`S1CardView` の既存の作法）。
- 日の問いの `day_row_for_close` → `commit_day_close` の「行を作ってから状態を変える」作法をプローブの途中の答えにも使う。
- ショートカットのハンドラは既存の共通ハンドラに分岐を足す。

## テスト戦略

- 単体（driver）: 段の遷移（Q3 で聞かない選択肢なら即閉じる／詰まりなら Q1→Q2）、食い違う step の拒否、途中で閉じる全経路（閉じる・superseded・一時停止・終了・取り消し）で書かれる行。
- 単体（登録の差分）: view から「あるべきキーの組」を決める純関数と、差分の計算。カードが消える全経路で空の組になること。
- 単体（logger・replay・calibration_eval）: q の無い answered の往復、replay が捨てず別に数えること、較正の数が変わらないこと。
- 回帰: `gse-replay --snapshot`（minimal）・較正の fixture。`emit_schema` の byte-equal。
- 実機（macOS）: カードを出し、⌥＋数字で答えて記録を確かめる。作業中のアプリに記号が入らないこと・フォーカスが動かないこと・tap が答えのキーを見るか。画面を自分の目で見る。
- Windows: CI でコンパイルとテスト。実機の確認（Ctrl＋数字・メニューバー）は G-GEAR が空いたら（3 名の版のリリース前の条件として残す）。

## ロールバック計画

- 1 つのブランチの中の変更なので、リリース前なら revert で戻せる。記録の形は加える向き（null を許す）だけなので、戻しても既存の記録は読める。

### 7. overlay の webview の登録の権限を外す（v2 から取った 1 点）

- `src-tauri/capabilities/default.json` の `global-shortcut:allow-register` / `allow-unregister` を外す。frontend は 1 度も使っていない（`src/` に用例が無い）。登録は backend だけが行う。外しても backend の `app.global_shortcut()` の登録が動くことを実装で確かめる。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: ハイブリッド（v1 を土台に、v2 から「使っていない webview の登録の権限を外す」を取る）
- 根拠: 研究者が 2026-11-25 に選択。記録は Q1・Q2 を今の `realtime_label` で読める v1 の方が、行種の追加の波及（同意文書の表・削除保証・capabilities・gse-dataset）が無い。キーの登録の真実はカードの真実と同じ backend に置く。v2 の案は `design-v2.md`、比べは `design-comparison.md`。

## 実装中に変わったこと（2026-11-25）

- 答えのキーの登録の更新は、短いスレッドから `run_on_main_thread` へ投げ、走るときに最新の組（`S1_ANSWER_WANT`）にそろえる。メインスレッドのハンドラから直に投げると、その場で走ってプラグインのロックを待って固まった（判断 7・実機）。
- 答えのキーはカードを出してから 2 分で外す（`S1_ANSWER_KEYS_FOR_MS`）。カードとボタンは残る。Windows の修飾キーは Ctrl＋Alt（判断 8）。
- 再生（`s1_replay.rs`）は、途中まで答えた層化のカードが差し替わったとき、記録がその tick に answered で閉じていれば差し替えを照合済みとして扱う（判断 9）。
- 画面のボタンが古い問いへの押下を送ってきたら、捨てて受け付けた扱いにする（判断 9）。
