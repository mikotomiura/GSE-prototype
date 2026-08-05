# タスクリスト — G1 専用アプリモードとセッションログのローテート

## 0. 先行実践の調査（★ 研究者の指示で追加）
- [x] 「先人はどう対処しているか」を調べてから設計を確定する（R-0）
- [x] ローテート案 → **PsychoPy `Session` API と同型**であることを確認（R-1）
- [x] ブロック長 → **ソフトが強制するのが標準**（jsPsych `trial_duration` 等）。
      ⚠️ **被験者に計らせる実践は見つからなかった**（R-2。「探し方の限界」も明記）
- [x] 二重起動 → **Tauri 公式プラグイン**に差し替え（R-3）
- [x] ⚠️ **D-7 に未計上のリスク 2 件**を発見（R-4 bundle ID 衝突 / R-5 TCC 再許可）
- [x] ⚠️ 配布の**第 3 の道**を発見（機関の Apple Developer アカウントでの公証・R-5-2）

## 1. 実測（★ 二次情報を鵜呑みにしない）
- [x] TCC: コピーを作って起動し、`tccd` の `AUTHREQ_RESULT` を読む
      → ★ **再許可は不要だった**（`authValue=2` / プロンプト無し・R-5 の懸念は棄却）
- [x] LaunchServices: 2 コピー下での `open -a` / パス指定
      → ⚠️★ **`open -a gse-next` は `/Applications` を起こす** → **launcher 廃止**が決まった
- [x] ⚠️★ **二重起動が実測で再現**（2 プロセス共存・NDJSON が 2 本）
- [x] ⚠️ 罠: `log show` を **zsh ビルトインの `log`** で呼んで「0 件」の偽の緑を踏んだ。
      `/usr/bin/log` で 695 行取れた（R-7 に記録）

## 2. 実装（第 1 段）
- [x] `src-tauri/src/g1.rs` を新規作成（判定の純ロジック・OS API 非依存）
- [x] `logger.rs`: `LogEntry::BlockEnd` / `Rotate`、`LogTarget` 共有ハンドル、
      `write_meta_start` / `write_meta_end`、`next_session_path`（★ 秒粒度の衝突ガード）
- [x] `lib.rs`: `G1_MODE`(OnceLock) / `G1_BLOCKS_STARTED`、`start_session` でのローテート
- [x] `lib.rs`: 5:00 でのブロック自動終了スレッド（★ 残り時間は emit しない）
- [x] `lib.rs`: `tauri-plugin-single-instance` を**最初に**登録
- [x] `App.tsx`: ブロック終了の受け取り → スタート画面へ復帰 ＋「終わった」だけの通知

## 3. 実装（第 2 段・第 10 版）
- [x] `g1.rs`: `g1.mode` マーカーの探索（mac 4 階層上 / win 1 階層上）
- [x] `lib.rs`: G1 モードを**プローブ停止の第 2 の引き金**に（★ env 経路は無変更で残す）
- [x] `schema_dto.rs`: `Meta.g1_mode`（加算的）→ `schema/current.json` 再生成（byte-equal 確認）
- [x] `App.tsx`: 「G1 モードで動作しています」の表示（fail-loud）
- [x] `logger.rs`: `meta` 行に `g1_mode` を刻む（★ **G1 でなければ従来と byte-identical**）

## 4. ★ 実測で追加になった 2 件（**設計時に見えていなかった**）
- [x] ⚠️★ **プラグインは旧ビルドとは共存する**（実測）→ G1 モード限定で
      **プロセス名の検査**を追加（`pgrep` / `tasklist`・★ 止めずに画面へ出す）
- [x] ⚠️★ **ブロックされた 2 個目が空の NDJSON を作ってから死ぬ**（私が入れた退行）
      → `find_latest_session_ndjson` が **`meta` しか無いセッションを選ばない**ように
      （★ 起動直後のクラッシュ等にも効く恒久的な堅牢化として入れた）

## 5. テスト
- [x] `g1.rs` 単体 14 本（env の綴り / 両 OS のマーカーパス / 優先順位 / PID 抽出 / `meta` 文字列）
- [x] `logger.rs` 結合 5 本（ローテート / 実時刻の meta / `session_end` 1 行 / byte-identical / 衝突回避）
- [x] `packaging.rs` 1 本（`meta` だけのセッションを提出候補にしない）
- [x] `validate_blocks.py` に `g1_mode` 検査（★ **probe 行 0 とは独立の 2 本目**）＋ selftest 3 ケース
- [x] ★★ **わざと壊して赤を実測** — Rust 5 通り / Python 4 通り / 追加分 3 通り = **12 / 12 が発火**
- [x] `cargo test --workspace` = 268 / `--features package` = 276（緑）
- [x] `gse-replay --snapshot` golden 2 本 = 緑（`replay_snapshot_goldens_byte_equal` も緑）
- [x] `emit_schema` の出力が `schema/current.json` と byte-equal
- [x] `npx tsc --noEmit` = 緑
- [x] `analyze.py --selftest` / `validate_blocks.py --selftest` / `validate_materials.py --strict`
      / `build_task_pages.py --selftest` = すべて緑
- [x] `validate_blocks.py --dataset ~/gse-dataset`（P-1 実データ）= 緑のまま

## 6. 文書
- [x] `preregistration.md` 第 10 版（改訂履歴 ＋ `§5.4-5` / `§5.4-6` ＋ 凍結の記録）
- [x] `config.json` `revision.version` 9 → **10** ＋ `v10_changes` ＋ `execution_environment`
- [x] `analyze.py` `PREREG_REVISION` 9 → **10**（★ selftest が両者一致を検査する）
- [x] `protocol.md`: §1 手順 / §1.1 起動方法（launcher 廃止）/ §4.2 台本 / §4.4 計時の一本化 /
      §4b.1 配布物 / §4b.2 在宅手順 / §6 当日チェックリスト / §6.1 30 秒チェック / §8 関連
- [x] `launch-g1-macos.command` を**廃止スタブ化**（実行すると理由を出して非ゼロで終了）
- [x] `participant-guide.md` / `README.md` / `record-sheet-pilot.md` を追随
- [x] ⚠️ ★ **grep で数え直した**（旧記述が 8 箇所残っていた）

## 7. 実機検証
- [x] `tauri-plugin-single-instance` が **同一ビルド 2 コピーの共存を止める**（実測）
- [x] ⚠️★ **旧ビルドとは共存する**ことを実測 → §4 の対策につながった
- [ ] ★ 新ビルドで **G1 モード表示 / ローテート / 旧ビルド共存の警告** を実機確認
- [ ] ⚠️ **Windows は未実施**（マーカーの階層・二重起動とも）

## 8. 完了処理
- [ ] `/cross-review`（★ 消費量をログで確認する）
- [ ] `run.sh` が GREEN に戻ることをコミット後に確認（★ 現在の RED は**未コミット変更の検査**による）
- [ ] git commit
- [ ] ⚠️ 後片付け: `~/G1-app-test/` と、実測で増えた `~/Documents/GSE-sessions/` の NDJSON
      （★ **key 行 0 = 打鍵内容なし**を確認済み）。**研究者の確認後に削除する**
