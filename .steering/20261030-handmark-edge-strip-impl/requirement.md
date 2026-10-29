# 手跡の下の縁の帯とどける操作を試作の枝に入れる

## 背景

手跡の背景の層（デスクトップの層）は、普段の配置ではほとんど他の窓に覆われ、全画面の間は見えない。設計のタスク（`docs/tangibility-design` の `.steering/20261029-handmark-edge-strip-design/`）で、画面の下の縁に細い帯を常に出すことと、トレイから他の窓をどけて背景を見る操作を設計した（判断 1〜7）。帯は GSE 本体の窓 1 枚（非アクティブの NSPanel）として作ると決めたが、確かめたのは Swift の素の NSPanel だけで、Tauri の webview の窓では確かめていない。どける操作の「前面に出られなければやめる」判定も、本体のトレイの操作からは確かめていない（判断 7）。

## ゴール

試作の枝 `spike/handmark-stage` で、次が動き、設計の残りの確かめ（design.md 末尾の 1〜4）の結果が記録されている。

- 帯: 本体の窓 1 枚。非アクティブの NSPanel・浮く層・`canJoinAllSpaces` / `stationary` / `ignoresCycle` / `fullScreenAuxiliary`・クリック透過。風で揺れる線 1 本を主に、薄い霧 1 本と粒を少し。風は背景と同じものを 1 か所で計算して配る。描く回数は入力がある間 30 回/秒・ない間 10 回/秒。帯が全部覆われたら止める。カーソルが近づいたら薄くする。
- どける操作: トレイのメニュー 1 項目（「背景を見る」と「戻す」を切り替える）。前面に出られなければ隠さずにやめる（判断 7 の結果しだいで事後確認に切り替える）。終了時に戻す・焦点を奪わない・やめたことを知らせる。覚えた一覧は記録しない。

## スコープ

### 含むもの
- 帯の窓（Rust: NSPanel 化・層と振る舞い。フロント: 帯の描画）
- 風の状態の 1 か所での計算と配布
- トレイの「背景を見る / 戻す」と、隠す・戻す手順
- 最初の確かめ 1〜4（全画面の上に出るか・普段のアプリの全画面・トレイから前面に出られるか（外と中）・負荷）

### 含まないもの
- どける回数の記録（design.md 論点 7。本線に入れるタスクで詰める）
- 本線（main）へのマージと PR（push までにする）
- Windows 版（帯もどける操作も macOS だけ）
- O1 の配布物・同意文書・schema への変更

## 受け入れ条件

- [ ] 帯が Tauri の webview の NSPanel として、テキストエディットの全画面の上で `onscreen=1` かつ研究者の目視で見える
- [ ] 普段使うアプリ（ブラウザ・エディタ）の全画面で同じか、結果が記録されている
- [ ] トレイから前面に出られるかが、全画面の外と中の両方で記録され、やめる判定（判断 6 のままか事後確認か）が決まっている
- [ ] 帯の負荷（30・10 回/秒）が測られ、Swift の試作（約 7〜11%）と並べて記録されている
- [ ] 帯の層と振る舞いを読むテスト、隠す・戻す手順の純粋な部分（順番の決め方など）のテストが緑
- [ ] 帯とどける操作で、キーストロークの内容・アプリの名前・覚えた一覧をログやファイルに書いていない
- [ ] cargo test・tsc・clippy が緑、code-reviewer と /cross-review を通している

## 関連ドキュメント

- 設計: `/Users/johnd/GSE-prototype-tangibility/.steering/20261029-handmark-edge-strip-design/`（design.md・decisions.md・probe-results.md・probe/strip.swift）
- 先例: `src-tauri/src/overlay_panel.rs`・`handmark_stage_spike.rs`・`tray.rs`・`src/components/HandmarkStage.tsx`
- ADR-040（手跡の入力を記録しない・カーソル位置の持ち込み）
- memory: macos-overlay-clickthrough-bug（NSPanel のクリック透過の穴）

## 運用メモ
- /reimagine 適用: No
- 理由: プロセスの形は設計のタスクで /reimagine 済み（判断 3・4）。残りは決まった設計の中の実装の細部で、迷う点は decisions.md に記録して AskUserQuestion で聞く（研究者・2026-10-30）。
