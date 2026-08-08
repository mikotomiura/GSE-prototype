# タスクリスト

## 【B】ログのファイル出力

- [x] `logger.rs`: `session_log_dir()` / `log_dir_for()` / `app_log_path()` を足す
- [x] `applog.rs` を新規追加（bounded channel + 書き込みスレッド + 世代交代）
- [x] `lib.rs:1943` の `tracing_subscriber::fmt::init()` を tee 構成に差し替える
- [x] 単体テスト T1〜T5 + 親ディレクトリ作成（6 本）
- [x] ★ **6 変異すべてで赤を実測**（下表）
- [x] 統合テスト `tests/applog_subscriber.rs`（★ 本物の購読者を通す）
- [x] ★ **旧挙動（stdout だけ）に戻す変異で統合テストが赤になることを実測** = 直したバグを再現できる
- [x] `cargo test --workspace` 297 + 23 + 1 passed / 0 failed
- [x] ゴールデン回帰 `gse-replay --snapshot` = 15 snapshots match
- [x] `emit_schema` byte-equal / `cargo fmt --check` / clippy 新規警告なし
- [ ] ⚠️ ★ **Finder 起動の `.app` での実測**（★ 未実施。CI 本番バイナリが要る → 研究者の操作）

### 変異テストの結果（★ すべて赤を実測）

| 変異 | 赤になったテスト |
|---|---|
| M1 `Drop` が空を送る | T1 / T2 / T3 |
| M1b 親ディレクトリを作らない | T1b |
| M2 `append` → `truncate` | T2 / T3 |
| M3 上限判定を消す | T3 |
| M4 `try_send` → `send` | T4（★ 120 秒でハング = フックを待たせる） |
| M5 捨てた件数を報告しない | T5 |
| M6 購読者を stdout だけに戻す（= 元のバグ） | ★ 統合テスト |
| M7 ファイル側の `with_max_level` を外す | ★ 統合テスト（`VK=0x41` が出て赤） |

## 【follow-up】beforeunload

- [x] `writing-pad.html` に `started` を足す
- [x] `build_task_pages.py` の検査に**条件そのもの**を追加（`"beforeunload"` だけでは空回り）
- [x] ★ 検査が空回りしていないことを変異で確認（旧条件に戻すと赤）
- [x] `pages/` 208 枚を作り直し（208/208 にガードあり）
- [x] `dist/_drive` 150 枚を作り直し（`prepare-subjects.sh --range P006 P020`）
- [ ] ⚠️ `dist/PILOT-win/` の 8 枚は**作り直していない**（実施済みパイロットの成果物なので触らない）
- [ ] ⚠️ ★ **Drive への再アップロードは未実施**（上げるのは人）

## 【C】後片付け

- [x] ★ 残っていた `gse-next`（PID 84943・3 時間・CPU 157 分）を停止
- [x] `~/.gse/g1_participant_id`（P009）→ ゴミ箱
- [x] `~/Desktop/G1_実施用_macOS` → ゴミ箱
- [x] `cleanup-record.md` に消す前の状態を記録
- [ ] ⚠️ `~/Documents/GSE-sessions/*.ndjson` 3 本は**消していない**（承認外・研究者判断）

## 【A】Windows 新品端末（★ 本セッションでは実施不可）

- [ ] 引き継ぎに「B の後に何をやり直すか」を書く

## 【追加】G1 管理シートにセッション提出トラッキングタブ

- [ ] Phase1 `buildSubmissionTab_` を読む
- [ ] G1 版を実装（★ 参加者ロスターは作らない = 明文の設計判断を守る）
- [ ] 実シートで確認

## 仕上げ

- [x] 自己レビュー（★ 2 件の誤りを自分で見つけて直した: README の主張 / ID 解決の副作用）
- [ ] `/cross-review`（Codex）
- [ ] 引き継ぎメモの更新
