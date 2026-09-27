# 決定記録 — o1-resilience-g1-g2-g5

> grill（2026-09-28・研究者回答）で閉じた分岐。「一次」は私が 2026-09-28 に自分で開いた行。

## 0. grill 前に一次で確かめたこと
| 何 | 実測 |
|---|---|
| `o1.mode` 目印の探索基準 | **実行ファイル基準**（`o1.rs:765` `current_exe()` → `marker_path_for(exe, g1::exe_to_folder_levels())`）。cwd は関係しない → LaunchAgent / Run キーで cwd が変わっても目印は見失わない（handoff §2 G-1 の懸念 2 は起動経路が `.app` 内の同じ実行ファイルである限り成立しない。⚠️ 実機で meta の `o1_mode` を見て裏取りする） |
| 32 MB の出所 | **自前の定数**: `Form_O1/GSE_O1_Submit.gs:176` `MAX_BYTES = 32 * 1024 * 1024`、判定は `decodedLength_(b64) > MAX_BYTES`（`:218`）＝ **`.age` のバイト数で 32 MiB を超えたら拒否**（等号は通る）。Google 側の本文上限は実測で 48.0 MB 通過 / 53.3 MB は 400（`reconcile.rs` の HttpUploader コメント） |
| `ReconcileReason` | `lib.rs:1785`（Startup / BlockEnd / Approval / O1DailyRotation）。フロントの対応は `App.tsx:58` |

## 判断 1: G-1 の方式
- **採用**: `tauri-plugin-autostart`・O1 モードで既定 ON。
- **却下**: 初回ダイアログで同意を取る（UI が増え、断られると起動忘れが残る）／手順だけで案内する（やったか確認できない）／見送り。
- **理由**: 起動忘れを構造的に消せる。告知と解除手順は同意文書・README に書く。

## 判断 2: 被験者が自動起動を切ったとき
- **採用**: 最初の 1 回だけ登録する。実施済みの印をファイルに残し、以後は登録し直さない。
- **却下**: 毎回の起動で ON に戻す（被験者の選択を黙って上書きする＝やめる権利と矛盾する）。

## 判断 3: Mac で TCC が保たれなかったとき
- **採用**: LaunchAgent → 駄目ならログイン項目（AppleScript）方式を同じ実験で測る → それも駄目なら Mac は見送り、Windows だけ入れる。

## 判断 4: 文面の承認
- **採用**: 実装と並行して文面案を作り、研究者が承認してからタグを打つ。

## 判断 5: 既に配った被験者
- `v0.1.37` は**まだ誰にも配っていない**（研究者回答）→ `v0.1.38` を最初の O1 配布物にする。Drive の zip を差し替えるだけでよい。

## 判断 6: G-2
- **採用**: 周期は 6 時間、新しい `ReconcileReason::O1Periodic` を足す（フロントの数値契約も同期）。O1 だけ。
- **却下**: `O1DailyRotation` を流用する（ログで区別できない）／1 時間（送るものが無くても毎回、子プロセス起動・NDJSON の読み込み・ロック書き込みが走る負荷が 6 倍になる）。

## 判断 7: G-5
- **採用**: 送信をやめて隔離フォルダへ移し、applog に記録する。消さない。研究者は受領台帳の途絶・欠番で気づき、手で回収する。
- **却下**: 同じ場所に置いて印ファイルを付ける（再送の判定が 2 か所に分かれる）／分割して送る（GAS と復号側の変更が要り、「doPost を変えない」方針と衝突する）。
- **既定として決めたこと（研究者に確認していない・妥当性をここに残す）**: 送信前のサイズ検査（`.age` > 32 MiB）に加え、**受け口が `too large` を返したときも隔離する**。理由: 上限は GAS 側の定数なので、将来そちらが下がってもクライアントが再送を続けないようにするため。

## 判断 8: タグ番号
- `v0.1.38`。G1 は `v0.1.36` のまま（ADR-034 D3）。

## 判断 9: G-1 はプラグインを使わず自前で登録する（2026-09-28・研究者承認）
- **背景**: `tauri-plugin-autostart` 2.6.0 / `auto-launch` 0.5.0 のソースを一次で読んだ（design.md の表）。
- **採用**: macOS = `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist`（XML エスケープ）／Windows = HKCU Run に引用符つきパス（`windows` crate・`StartupApproved` に触らない）。1 回だけの印は配布フォルダの `o1.autostart`。
- **却下**: プラグイン 2.6.0（tauri 2.12 への版上げ）／2.5.1（引用符なしパス・StartupApproved の書き戻し・未エスケープの plist が残る）。
- **トレードオフ**: Windows の registry 呼び出しを自前で持つ（unsafe 1 か所・CI と実機でしか確かめられない）。
- **grill 判断 1 との関係**: 研究者が選んだのは「OS のログイン時起動を既定 ON で自動登録する」という到達点で、手段の変更は承認済み。

## 判断 10: 小実験の段階 A は Claude が実行する（研究者許可・2026-09-28）
- 段階 A を実施した（結果は `g1-mac-autostart-experiment.md`）。

## 判断 11: README・同意文書の文面（研究者承認 2026-09-28「1-3 ok」）
- README【3】の手動登録手順を削り、自動設定と切り方に差し替え／【4】にやめるときの段落／持ち物に `o1.autostart`。同意文書 §3 に 1 文追加（上流 `consent-draft-o1.md` → `Form_O1/GSE_O1_Form_Builder.gs` の順）。
- ⚠️ 承認後に 1 か所だけ文言を変えた: 「最初に開いたとき」→「**最初に開いて参加の確認を済ませると**」（判断 12 で登録を同意確認の後にしたため、事実に合わせた）。研究者に報告する。
- ⚠️ フォームの文面変更は、研究者が O1 同意フォームを配備し直すまで被験者に届かない。

## 判断 12: レビュー対応（code-reviewer / security-checker・2026-09-28・一次で確かめてから反映）
| 指摘 | 対応 |
|---|---|
| CR HIGH: 同意確認（R-7）より前に自動起動を登録する | ✅ `decide` に `consent_acknowledged` を追加。起動時と `acknowledge_o1_enrollment` の直後の 2 か所で呼ぶ。24 通りのテスト＋変異 |
| SC HIGH / CR MEDIUM: やめても登録が残り、ログインで記録が再開する | ✅ 削除台帳 B-8 と §2 末尾（取りやめでは削除の求めが無くても外してもらう）。README【4】に手順。⚠️ 「`o1.mode` が無いとき自分で外す」は採らない（フォルダを残した人には効かないため） |
| CR MEDIUM: G1 のエラー文言が変わる | ✅ `TooLarge(String)` にして Display は従来の文言。G1 のテストで文字列一致を確認＋変異 |
| CR MEDIUM: G1 の要約行に `quarantined:0` が増える | ✅ 1 以上のときだけキーを足す（G1 は常に 0 → 行は不変） |
| CR MEDIUM: 台帳が欠けると隔離した日の番号が戻る | ✅ `next_o1_day_number` が `oversize/` も数える。台帳なしのテスト＋変異 |
| SC MEDIUM: 失敗時のログにホームのパス（実名） | ✅ エラー文からパスを外した |
| SC MEDIUM: 制御文字で plist が壊れて黙って起動しない | ✅ `path_is_registrable` で拒否（両 OS）＋テスト＋変異 |
| CR LOW: 印を置けない場所で毎回再登録 | ✅ 印を先に書き、書けなければ登録しない。登録に失敗したら印を戻す |
| CR LOW: `anyhow::Result` に揃える | ❌ 採らない: **`anyhow` はこの crate の依存に無い**（`Cargo.toml` に 0 件・実測）。既存の `reconcile.rs` と同じ `Result<String, String>` |
| SC LOW: 誤って隔離されたときの戻し方 | ✅ 台帳 B-4b に 1 行 |
| SC LOW: O1 でもログ接頭辞が「G1 auto-submit detail」 | ✅ O1 のときだけ "O1"（G1 は不変） |
| CR LOW: 置き場の一覧に autostart.rs | ✅ agent-shared 制約 11・repository-structure |
| CR LOW: スリープ復帰で定期とローテートが同じ周回に重なる | 見送り（後着はロックで Busy になるだけ・取りこぼし無し） |
| CR LOW: 端末側に隔離中の状態表示が無い | 見送り（研究者の検知は受領台帳の欠番に頼る設計どおり） |
| SC LOW: 新しい版のフォルダで macOS のオフ状態が残るか | ⏳ 段階 B で確かめる |

検証: `cargo test --workspace --features package` 830 passed／fmt／clippy `-D warnings`（package あり・なし）rc=0／Windows 用コードは最小クレートで clippy rc=0（壊すと E0308 で赤になる陽性対照つき）／フォーム 221 ケース・変異 64/64／`make-common-app-zip.sh --selftest` 19/19。
⚠️ 単体テストで確かめていないもの: ローテートスレッドへの配線（60 秒ループ）・`register_if_needed` の IO（印の先書き）・submit.rs の要約行の条件。→ 実機（段階 B）と CI で見る。
