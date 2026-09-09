# §1 A/B/壊れ/べき等 の実機ログ (2026-09-09)

ビルド: commit `22538ccb5654c6e55a6ac0327cf7ece3b2f9dfd9` の
`src-tauri/target/release/gse-next.exe`（同フォルダに `o1.mode` を配置）。
`cargo test --features package --workspace` は事前に 653 passed / 0 failed。

## A: 正常終了（`Process.CloseMainWindow()` = WM_CLOSE = main窓の× と同一経路）

対象: `gse_o1_20260909_051917.ndjson`

```
最終行: {"type":"meta","session_end":1788931224096}
```

★ `CloseMainWindow()` 送信後 3 秒以内にプロセスが終了し、`session_end` がその場で書かれた。
`lib.rs:4796-4805` の `WindowEvent::CloseRequested -> shutdown_and_exit` の経路と一致。

## B: 強制終了 → 再起動で回収

対象: `gse_o1_20260909_052036.ndjson`（`taskkill` 相当の `Stop-Process -Force` で強制終了、
`session_end` なしのまま放置 → 再起動で回収）

```
gse-app.log:
2026-09-09T05:21:11.939195Z WARN gse_next_lib::o1: O1 orphan sweep: closed
  Some("gse_o1_20260909_052036.ndjson") with session_end=1788931271938
  (the app did not shut down cleanly last time; the 48h deletion window starts now)
2026-09-09T05:21:11.939261Z WARN gse_next_lib: O1 orphan sweep finished closed=1 failed=0
```

ファイル末尾に `{"type":"meta","session_end":1788931271938}` が追記されていることを確認。
★ `session_end` は最終データ行の時刻 (`t`) ではなく検出時刻（決定 A'・`decisions.md` 判断2 通り）。

## 壊れ: 読み取り専用ファイル

対象: `gse_o1_20260909_052111.ndjson`（強制終了直後に `attrib +R` で読み取り専用化 → 再起動）

```
gse-app.log:
2026-09-09T05:21:43.252723Z ERROR gse_next_lib::o1: O1 orphan sweep: cannot close
  Some("gse_o1_20260909_052111.ndjson"): アクセスが拒否されました。 (os error 5)
2026-09-09T05:21:43.252778Z WARN gse_next_lib: O1 orphan sweep finished closed=0 failed=1
```

`grep -c '"session_end"'` = 0（★ 書き込めない = closed に数えられない、を確認）。
検証後 `attrib -R` で読み取り専用を解除済み。

## べき等: 既に閉じたファイルへの再走査

対象: `gse_o1_20260909_051917.ndjson`（A で閉じた）/ `gse_o1_20260909_052036.ndjson`（B で閉じた）

★壊れ状態と同時に行った再起動（3回目のプロセス起動）の後、両ファイルとも
`grep -c '"session_end"'` = **1**（2 行に増えていない = べき等を確認）。

## まとめ

| 状態 | 期待 | 実測 | 結果 |
|---|---|---|---|
| A 正常終了 | その場で session_end | 3秒以内に書かれた | ✅ |
| B 強制終了→再起動 | 次回起動で回収 | closed=1 failed=0、session_end 付与 | ✅ |
| 壊れ(読み取り専用) | cannot close・closed に数えない | ERROR ログ・closed=0 failed=1 | ✅ |
| べき等 | 2 回目の走査で session_end が2行にならない | 1のまま | ✅ |

⚠️ 未検証: C（OS 再起動）はこの後に実施。§0-1c の「時計を戻す」検証は
単体テストで担保済みのため実機では行わない（引き継ぎメモの指示通り）。

## C: OS 再起動（試行1 — 前提不成立で不採用）

対象: `gse_o1_20260909_052143.ndjson`

★ 実機再起動後（`net stats workstation` 実測: システム起動 2026-09-09 14:26:18、
判定コマンド実行 2026-09-09 14:29 頃）に判定コマンドを実行した結果:

```
{"type":"meta","session_end":1788931473562}
```

`session_end=1788931473562` ms を UTC に直すと `2026-09-09T05:24:33.562`。
`gse-app.log` の該当行と突合:

```
2026-09-09T05:24:33.562817Z INFO gse_next_lib: main window close requested -> shutting down
2026-09-09T05:24:33.562841Z INFO gse_next_lib: shutdown requested
2026-09-09T05:24:33.562897Z INFO gse_next_lib::logger: SessionLogger: session closed
```

★★ **これは A と同じ経路**（`lib.rs:4796-4805` の `WindowEvent::CloseRequested ->
shutdown_and_exit`）。つまり 052143 は「GSE を終了せず OS 再起動」ではなく、
**メインウィンドウを閉じて正常終了**していた。しかもその時刻は実際の再起動
（14:26:18）の **約 9 時間前**であり、`gse-app.log` は 05:24:33 から再起動時点まで
一切追記がない（= その間 GSE プロセスは起動していなかった）。再起動後の現在も
GSE プロセスは起動していない（`tasklist` で未検出、自動起動登録なし）。

★★★ **結論: C の前提（「GSE を起動したまま OS 再起動する」）がそもそも成立していない。**
判定表のどの分岐にも当てはまらない — session_end は再起動前の通常クローズで
付いたものであり、「WM_ENDSESSION が CloseRequested に翻訳されたか」を
判定する材料にならない。原因は不明（前回セッションで意図せずメインウィンドウを
閉じてしまった可能性が高いが、ログの文言だけでは通常の × 押下と区別できない）。
→ **C は仕切り直しが必要**（`decisions.md` に記録）。

## C: OS 再起動（試行2 — 確定）

対象: `gse_o1_20260909_053529.ndjson`（2026-09-09 14:35 起動・PID 31540。
`RESUME-AFTER-REBOOT.md` に事前に記録した手順どおり実施）。

実行: `shutdown /r /t 15 /c "GSE C検証 試行2"`（キャンセルなし・即時実行）。

★ **ギャップ確認**（試行1 の反省を反映）: `net stats workstation` 実測=
システム起動 2026-09-09 14:41:47、判定コマンド実行 14:47:32。**差 5 分 45 秒**
（試行1 の 9 時間ギャップと違い、実際の再起動直後と確認できた）。

再起動直後の判定:

```
tail -3 gse_o1_20260909_053529.ndjson  # 最終行は type=feat（session_end 無し）
grep -o '"session_end"' ...            # (session_end なし)
grep -F "O1 orphan sweep" gse-app.log | tail -10  # 05:21台の古い記録のみ、新規なし
tasklist | grep -i gse                 # (GSE プロセスなし)
```

→ **GSE は自動起動していない**（判定表の分岐3）。手順どおり
`target/release/gse-next.exe` を手動起動し、直後の `gse-app.log` を確認:

```
2026-09-09T05:47:57.104880Z  WARN gse_next_lib::o1: O1 orphan sweep: closed
  Some("gse_o1_20260909_053529.ndjson") with session_end=1788932877100
  (the app did not shut down cleanly last time; the 48h deletion window starts now)
2026-09-09T05:47:57.104921Z  WARN gse_next_lib: O1 orphan sweep finished closed=1 failed=0
```

★★★ **結論**: `session_end` は OS 再起動の瞬間には付かなかった
（`WM_ENDSESSION` は `CloseRequested` に翻訳されなかった）。**手動起動後の
orphan sweep だけが回収した** —— これは §1-B（`taskkill /F` による強制終了 →
再起動で回収）と**同じ経路**である。`RESUME-AFTER-REBOOT.md` の判定表の
2 番目の分岐（「`session_end` が無い状態で残っている → GSE を起動した後に付く」）
が実測で確定した。★ **どちらでも「正常」**（`decisions.md` 判断2 が
「翻訳されなくても直る実装にした」と明記した設計どおり）。

## ⚠️★★★ 副次発見: 検証用ビルドの手順ミス（本番動作には影響しない）

試行2 の結果確認の過程で、上記で起動した `gse-next.exe`（`cargo build --release`
で再ビルドしたもの）の**メインウィンドウが「localhost 接続が拒否されました」を
表示する**欠陥に気づいた（研究者が実機画面で目視）。

調査の結果:

- 原因は **`custom-protocol` Cargo feature が有効になっていないこと**。Tauri v2 は
  この feature の有無でメインウィンドウの URL 解決先を切り替える
  （devUrl `http://localhost:1420` か、埋め込み済みフロントエンドか）。
  この分岐は **Rust の release/debug プロファイルとは無関係**——
  `cargo build --release` を素で叩くだけでは `custom-protocol` は付かない。
  `Cargo.toml` の `tauri` 依存に `custom-protocol` は列挙されておらず、
  `tauri-cli`（`npm run tauri build` / `npm run tauri dev`）が呼び出し時に
  暗黙で付与する設計になっている。
- 再現: `cargo build --release --features package` で再ビルド → 同じ欠陥が再現
  （プロファイルは無関係という仮説を確認）。
- 修正確認: `npm run build && npm run tauri build -- --no-bundle` で作り直した
  バイナリは dev server なしで正常にダッシュボードを表示した（研究者が実機で確認）。
- **本番への影響なし**: `.github/workflows/ci.yml` の実配布ビルド
  （`npx tauri build --no-bundle` / `npx tauri build --bundles dmg --features package`）
  は元から `tauri-cli` 経由であり、この欠陥の対象外。O1/G1 で配布済みの
  v0.1.29〜v0.1.33 はこの経路を通っていないため影響を受けない。
- **§1 A/B/壊れ/べき等/C試行2 の判定への影響なし**: 孤児回収ロジック
  (`o1::close_orphaned_sessions` 等) は純 Rust バックエンドで、メインウィンドウの
  URL 解決とは独立に動作する（ログの `O1 orphan sweep` 系メッセージは全経路で
  正常に出ている）。
- **教訓**: `design.md` §ビルド の「`target/release/gse-next.exe` を現 HEAD で
  再ビルドする」という記述は具体的なコマンドを指定しておらず、素の
  `cargo build --release` を誘発した。★ **Tauri アプリの手動検証ビルドは
  必ず `npm run tauri build -- --no-bundle` を使う**（`cargo build` 直叩き禁止）。

★ 補足（未確定の仮説・断定しない）: `design.md` の GUI 操作の自動化判断は
「`shutdown /r /t 60 /c "..."` で 60 秒遅延・キャンセル可能な形で実行する」としていた。
もし前回セッションがこのコマンドを実行し、その後 `shutdown /a` で**一旦キャンセルして**
（＝ 05:24:33 のクローズは `shutdown /r` のカウントダウン中に送られた WM_QUERYENDSESSION が
`CloseRequested` に翻訳された結果）、9 時間後に改めて別の再起動を手動実行した、という
経路であれば分岐 1（翻訳される）を裏付ける材料になる。★ ただし `gse-app.log` の文言
（`main window close requested -> shutting down`）は通常の × 押下と区別がつかず、
`shutdown /a` の実行有無もログに残っていないため、**この仮説は検証できない**。
→ C は次回、ログを分岐できる形（`shutdown /r` 実行直後の秒単位のログ監視、キャンセルしない）
でやり直す。
