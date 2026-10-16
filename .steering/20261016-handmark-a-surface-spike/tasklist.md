# tasklist

- [x] `handmark_spike.rs`: 環境変数の解釈・窓の生成・NSPanel 化・除外の設定と読み返し（fail-closed）・通知・計測の CSV・閉じる処理
- [x] `lib.rs`: mod 宣言・setup で窓を作る・分析スレッドで通知・CloseRequested から外す・invoke の登録（すべて cfg macos）
- [x] `tray.rs`: 「小面を閉じる」
- [x] `capabilities/handmark.json`
- [x] `src/main.tsx` の分岐と `src/components/HandmarkSurface.tsx`
- [x] cargo test・clippy・tsc・check_invitation_surface.py
- [x] 合成の打鍵のスクリプト
- [x] 実機: 窓が出る・前面・クリックの透過・フォーカス（AX）
- [x] 実機: fail-closed（模擬の失敗で窓が出ない）
- [x] 実機: 遅れ 約 200 回 → 95 パーセンタイル・最大
- [x] 研究者の手順書（取り込みの目視・抜き取り撮影・試視）
- [x] code-reviewer + security-checker・指摘対応（判断 8）
- [x] 結果を results.md に書く（取り込みは研究者の目視で写った・§3 の撮影と §4 の試視は未のまま閉じる・判断 10）
- [x] /finish-task（/cross-review 済み・判断 9・PR は出さず push で止める）
