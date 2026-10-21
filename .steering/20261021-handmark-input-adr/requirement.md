# 手跡の表現の入力を「表現には使うが記録しない」と決める ADR（handmark-input-adr）

## 背景

手跡の見本（自然世界）は、打鍵に加えてカーソルの位置・動き・クリック・ホイールを表現の入力に使う形で固まった（`.steering/20261020-handmark-multi-input/` 判断 12・Version 5）。ADR-014 D4 の「入れないもの」の表は絶対座標・符号付きの dx/dy・一回ごとの列を名指ししているので、表現の側のコードが座標を読むのを見た人には D4 に反するように見える。実物（背景の層の試作）へ持ち込む前に、「表現には使うが記録しない」とその境界を ADR で明示すると決めた（同 判断 7）。

## ゴール

ADR-040 を `docs/adr/` に起こし、`docs/adr/README.md` の一覧に足す。ステータスは Proposed。

## スコープ

### 含むもの
- 範囲: 手跡の表現の入力として、カーソルの位置・動き・クリック・ホイールを使ってよい。記録・送信はしない。ADR-014 D4 は O1 の収集の決まりで表現の側を縛らないことを明示する（D4 の本文は書き換えない）。
- 境界の 3 層（型・境界・振る舞い。`20261020-handmark-multi-input` 判断 9・design.md §3）。
- 溜めない（最後の 1 点と数秒で戻る値だけ）。
- 数で返さない: ADR-025 D1 を手跡の入力に当てる（本タスク 判断 3）。E-11 全体は閉じない。
- OS の差（macOS の実測・Windows は未実測・ホイールはイベントを取る仕組みが要る）。
- アプリの切り替えは使わない。

### 含まないもの
- コードの変更（実物への持ち込みは別タスク）。
- Windows の実測、macOS のホイールの権限の確かめ。
- 写し方・強さの値（ADR は値に縛られない）。
- PR を出すこと（push まで）。

## 受け入れ条件

- [x] ADR-040 が上の範囲を決定として持ち、既存 ADR の本文を書き換えていない
- [x] README の一覧に ADR-040 がある
- [x] 引用が要る記述は `citation-ssot` に従っている（外部文献に依らないならその旨を書く）
- [x] `/cross-review` を通し、指摘への対応を記録した
- [x] push した

## 関連ドキュメント

- `.steering/_handoff/next-session-handmark-input-adr.md`
- `.steering/20261020-handmark-multi-input/`（decisions.md 判断 2・7・9〜12、design.md §1〜§4）
- `.steering/20261018-handmark-nature-v3-grading/decisions.md` 判断 8
- `docs/adr/ADR-014-continuous-natural-work-collection.md` D4、`ADR-012` D4 L-b、`ADR-025`
- `src-tauri/src/wallpaper.rs` の R-P9 のテスト

## 運用メモ
- /reimagine 適用: No
- 理由: 中身は 20261020 の判断 7・9・12 でほぼ決まっていて、ADR はそれを文書にする作業（研究者・推奨どおり）
