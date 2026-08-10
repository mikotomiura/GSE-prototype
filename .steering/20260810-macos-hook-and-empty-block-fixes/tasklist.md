# タスクリスト

## 【4】Input Monitoring を必ず要求する

- [x] 「要求」と「先に試す tap の順序」を分ける (`hook_macos.rs`)
- [x] 成功時のログを実態 (実際に付いている権限) に合わせる
- [x] `USING_ACCESSIBILITY_FALLBACK` を実態に合わせる
- [x] `cargo build --target aarch64-apple-darwin` が通る
- [x] ★ 判断を純関数に切り出し、**2 方向の変異で赤を確認**
- [ ] ⚠️ ★ **実機で再現 → 修正 → 再実機は未実施** (`decisions.md` D-5)

## 【1】空ブロックを提出しない

- [x] ⚠️ 案 B は**却下** (`decisions.md` D-1: `SessionStart` は `let _ = try_send` で落ちうる)
- [x] 案 A: `has_any_data_row` の除外に `ime_state` を足す
- [x] テスト: 実物と同じ 4 行を fixture 化。★ 変異で赤を確認
- [x] テスト: `feat` / `key` があるセッションは従来どおり包む
- [x] `cargo test --workspace --features package` = **350 passed**
- [x] ⚠️ ★ `--features package` を付けないと packaging のテストは **1 件も走らない**と実測

## 【3】レビュー

- [x] `code-reviewer` 起動
- [x] `security-checker` 起動
- [ ] ⚠️ `/cross-review` (Codex) は**未実施**
- [x] 指摘を `review-findings.md` に記録 (HIGH 2 / MEDIUM 5 / LOW 6)
- [ ] ⚠️ ★ **指摘の修正は未着手** (配布済みバイナリのため研究者の判断待ち)

## 【2】macOS のフック生存検知

- [x] `liveness.rs` の macOS 経路を `CGEventSourceSecondsSinceLastEventType` で埋める
- [x] ★ 揺れを C で実測 (離席 12 秒 / 60 サンプル → 55.5 ms)
- [x] ⚠️ 秒量子化は**自分のテストで赤**になり却下 → ms + 許容幅 250 ms へ
- [x] 比較規則を `liveness::system_input_seen()` に集約 (Windows = 等値 / macOS = 許容幅)
- [ ] ⚠️ 実機で hook_health を確認 (未実施・`decisions.md` D-5)

## 共通

- [x] `gse-replay --snapshot` 4 本すべて一致
- [x] ⚠️ ★ `OK:` は **stderr** に出る。`2>/dev/null` で一度自分の測定結果を捨てた
- [x] `HMM_VERSION` bump は**不要** (HMM 不変・ゴールデン 4 本一致・schema drift なし)

## 【3-b】レビュー指摘の修正 (v0.1.26)

- [x] HIGH-1 レシートの断定文を `unsent === 0 && last_error === null` のときだけ出す
- [x] HIGH-2 番兵を `emit("g1-block-ended")` の **前**で立て、ブロック終了時にレシートを捨てる
- [x] MED (sec) `resolve_submit_bin` の画面文言から絶対パス (= OS ユーザー名) を落とす
- [x] MED (sec) 参加者 ID が変わったらレシートの根拠を捨てる
- [x] MED 梱包フェーズの無表示を埋める (`unsent > 0` ゲートを外し、起動時スキャンだけ除外)
- [x] MED 「数秒かかります」を 30 秒で切り替え、未送信カードの抑制も解除する
- [x] MED 数え損ね (`counted: false`) のときは緑の ✅ を出さない
- [x] LOW `SUBMIT_IN_FLIGHT` の ordering を Release/Acquire に、`unwrap_or(0)` を `1` に
- [x] LOW 「この回…3 件」の文言を件数で分岐
- [x] `cargo test --workspace --features package` = **353 passed** (3 回連続で緑)
- [x] ⚠️ ★ 新テストが既存テストと同じ Atomic を踏み、**単独で緑・全体で赤**になった → 直列化
- [x] `tsc --noEmit` / clippy / ゴールデン 4 本 / schema drift
- [x] バージョンを **v0.1.26** に上げる
- [ ] ⚠️ CI で本番バイナリを作り、**実機で 5 項目を再確認**する
- [ ] ⚠️ 配布 zip を作り直して Drive を差し替える
