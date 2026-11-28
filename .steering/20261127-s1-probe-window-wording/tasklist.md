# タスクリスト

- [x] 文を研究者に聞く
- [x] `src/components/S1ProbeCard.tsx`・`src/components/S1ConsentPanel.tsx`
- [x] 同意文書の注 D・状態の表・配る前の条件 15
- [x] `Form_O1/GSE_O1_Form_Builder.gs` と `node Form_O1/o1_form_builder_test.cjs`
- [x] ADR-057 補訂 1
- [x] 表示確認のハーネス（`scripts/tests/s1-probe-card-view.html`）を ADR-057 の `step` に合わせ、3 つの段を目で見た
- [x] 研究者が同意文書を承認し、承認の印を入れ直した（2026-11-27・ADR-055・ADR-057 を Accepted）
- [x] 作業の説明と作業のときの問いの順（判断 4・ADR-055 補訂 1・ADR-057 補訂 2）
- [x] G-GEAR の引き継ぎ `.steering/_handoff/next-session-ggear-s1-n3-windows-before-start.md`
- [ ] 正本のフォームを作り直す（配る前の条件 2・13。この枝が main に入り、3 名の配布物のフォルダ〔`S1_APP_DOWNLOAD_URL`〕が決まってから）
- [ ] Windows での表示と答え方の確かめ（G-GEAR・配る前の条件 4・10・12〜15）
  - [x] 15: ポインタの行（fix/windows-pointer-raw-input・PR #442）。開発版で実際のマウスの `pointer_bin` 32 行
  - [x] 2026-11-28 の開発版（段 1・研究者デバッグ・約 12 時間・行の形と数だけを見た）: カードが 5 回出て `realtime_label` と `activity_label` が 5 行ずつ（答えた 1・閉じた 4）。手跡の日ごとの行は動いている間に書かれ（29 行）、`reveal_count` の欄がある
  - [ ] 配る版で確かめる（開発版では見ていない）: カードの表示（1 行に収まるか）・作業で Q2 だけ答えて閉じた行・Ctrl＋Alt＋数字（文字が入らない・2 分で外れる・ボタンだけ）・トレイの「やめる」「描く」（通知領域）・どけて `reveal_count` が増える・一時停止中の後半の表示
- [ ] push と PR（研究者に確かめてから）
