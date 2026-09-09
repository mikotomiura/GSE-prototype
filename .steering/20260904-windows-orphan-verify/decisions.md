# 重要な設計判断

## 判断 1: §1-C（OS 再起動）試行1 は不採用・仕切り直し

- **判断日時**: 2026-09-09 14:30 頃（OS 再起動後の新セッション、実測に基づく）
- **背景**: 前回セッションは `gse_o1_20260909_052143.ndjson` を対象に GSE を起動したまま
  OS 再起動する§1-C を試みたが（`design.md` の GUI 操作の自動化判断参照）、再起動後に
  判定コマンドを実行したところ前提不成立が判明した。詳細は `evidence-s1-A-B.md` の
  「C: OS 再起動（試行1 — 前提不成立で不採用）」節。
- **観測事実**:
  - `net stats workstation` 実測: システム起動 2026-09-09 14:26:18
  - 対象 ndjson の `session_end`=1788931473562 ms = `2026-09-09T05:24:33.562`（再起動の**約9時間前**）
  - `gse-app.log` は 05:24:33 の "main window close requested -> shutting down"
    （= A と同じ `WindowEvent::CloseRequested -> shutdown_and_exit` 経路）を最後に、
    再起動時点まで一切追記がない（＝ その間 GSE は起動していなかった）
  - 再起動後、GSE は自動起動しない（`tasklist` で未検出、スタートアップ登録なし）
- **選択肢**:
  - A: 05:24:33 のクローズを「WM_ENDSESSION が CloseRequested に翻訳された」証拠として採用する
  - B: 前提不成立として棄却し、C を仕切り直す
  - C: C の検証自体を諦め、判断2（翻訳されなくても直る設計にした）だけを最終結論とする
- **採用**: B
- **理由**: 05:24:33 のクローズと実際の再起動（14:26:18）の間に 9 時間の間隔があり、
  その間 GSE プロセスは動いていなかった（ログに記録なし）ことが実測で確認できた。
  A の間隔が「シャットダウン運用のキャンセル → 後で手動再起動」だった可能性は
  `design.md` の `shutdown /r /t 60` 案と整合するが、ログの文言だけでは通常の
  × 押下と区別できず断定できない（`verify-before-claiming` 準拠）。事実として
  確定できるのは「C の前提（起動したまま再起動）が満たされないまま再起動が起きた」
  ことのみ。
- **トレードオフ**: C の再実施に実機再起動がもう一往復必要（時間コスト）。
- **影響範囲**: `.steering/20260904-windows-orphan-verify/tasklist.md` §1 の C 行、
  `RESUME-AFTER-REBOOT.md` の判定表（今回は「未知」を解消できなかった）。
- **見直しタイミング**: C を再実施し、`shutdown /r` 実行からログ末尾までの経路を
  キャンセルせず・秒単位で確認できた時点で本判断を更新する。

## 判断 2: §1-C 試行2 の確定結果 — session_end は再起動時に付かず、orphan sweep が回収

- **判断日時**: 2026-09-09 14:47〜14:48（`RESUME-AFTER-REBOOT.md` の手順どおり実施・実測）
- **背景**: 判断1 で試行1 を不採用としたため、`RESUME-AFTER-REBOOT.md` に手順を書いてから
  `shutdown /r /t 15 /c "GSE C検証 試行2"` を実行し（対象: `gse_o1_20260909_053529.ndjson`）、
  新セッションで結果を確認した。
- **観測事実**（詳細は `evidence-s1-A-B.md` 「C: OS 再起動（試行2 — 確定）」節）:
  - `net stats workstation` 実測: システム起動 14:41:47、判定実行 14:47:32（差 5 分 45 秒 = ギャップなし）
  - 再起動直後: 対象ファイルに `session_end` なし・`gse-app.log` に新規 orphan sweep 記録なし・
    GSE プロセスなし（自動起動していない）
  - 手動起動後: `O1 orphan sweep: closed ... session_end=1788932877100` が記録され、回収された
- **結論**: `WM_ENDSESSION` は `CloseRequested` に翻訳されなかった。回収は
  **§1-B（強制終了→再起動）と同じ経路**（次回起動時の orphan sweep のみ）で成立した。
  `RESUME-AFTER-REBOOT.md` の判定表の 2 番目の分岐が実測で確定。
- **評価**: ⚠️ **どちらの結果でも「正常」**（設計は「翻訳されなくても直る」ことを
  意図しており、実測はその設計どおりに動いたことを確認しただけ）。追加のコード変更は不要。
- **影響範囲**: `tasklist.md` §1 の C 行を `[x]` にする。`gse_o1_20260909_053529.ndjson` は
  証跡転記後に削除する。

## 判断 3: 検証ビルドは `cargo build` 直叩き禁止、`npm run tauri build` を使う

- **判断日時**: 2026-09-09 15:00〜15:13（試行2 の結果確認中に副次的に発覚・実測で原因特定）
- **背景**: 試行2 で起動した `gse-next.exe`（design.md の指示に従い `cargo build --release`
  相当で再ビルドしたもの）のメインウィンドウが「localhost 接続が拒否されました」を表示し、
  研究者が実機画面で気づいた。
- **調査**: `cargo build --release --features package` で再現 → 原因は Tauri v2 の
  `custom-protocol` Cargo feature 不足（devUrl `http://localhost:1420` にフォールバックする）。
  この feature は `Cargo.toml` に列挙されておらず `tauri-cli` が暗黙付与する設計であり、
  **Rust の release/debug プロファイルとは無関係**（release ビルドでも feature が無ければ
  devUrl に落ちる）。`npm run build && npm run tauri build -- --no-bundle` で作り直したところ
  dev server なしで正常表示を確認した。
- **選択肢**:
  - A: `design.md` の記述を「`cargo build --release`」と読める曖昧なまま残す
  - B: `npm run tauri build -- --no-bundle` を正式な検証ビルド手順として明記する
- **採用**: B
- **理由**: 実配布ビルド（`.github/workflows/ci.yml` の `npx tauri build`）は元から
  この経路を通っており無傷だが、**手元の実機検証だけがこの穴を踏む**。次回以降の
  手動検証で同じ時間を無駄にしないため、手順として固定する。
- **影響範囲**: 本タスクの §1 A/B/壊れ/べき等/C試行2 の判定結果そのものへの影響は
  **なし**（孤児回収は純 Rust バックエンドで frontend URL 解決と独立）。§2（8時間稼働コスト）
  以降は本判断で作り直した `gse-next.exe`（`npm run tauri build` 経由・commit `22538cc`）を使う。
- **トレードオフ**: なし（手順の明文化のみ、コード変更なし）。
- **見直しタイミング**: 今後 GSE 実機検証タスクの `design.md` テンプレートに
  「ビルドは `npm run tauri build -- --no-bundle` を使う」を既定文言として足すと再発防止になる
  （本タスクの完了処理・引き継ぎで次セッションに送る）。
