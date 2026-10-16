# 引き継ぎ: 手跡の案 A —— Mac で小面が取り込みに写る。会議の画面共有で写るかを確かめ、案 A の扱いを選び直す（Mac）

作成 2026-10-16（Mac）。返答・記録は日本語で。記号（★・⚠️）を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-capture-exclusion-mac.md を読んで、§3 の進め方を研究者に確かめるところから始めて。
```

## 1. 背景（決まったこと・分かったこと）

- 小面の試作は閉じた（`.steering/20261016-handmark-a-surface-spike/`・枝 `spike/handmark-a-surface`・worktree `/Users/johnd/GSE-prototype-handmark-a`・push 済み・PR なし）。
  - 満たした: 打鍵から描画までの遅れ（アプリの中の区間・合成の打鍵 310 回で中央値 52 ms・最大 67 ms）・フォーカスを奪わない・クリックを奥へ通す・前面に出続ける・トレイからすぐ閉じられる・設定の失敗で出さない（模擬）。
  - 満たさなかった: 取り込みからの除外。macOS 27.0.1 で `NSWindow.sharingType` を `None` に設定し読み返しも通ったが、標準のスクリーンショット（全画面・窓の指定）に写った（研究者の目視）。画面収録は判定できず、画面共有は未。
  - 画面に光が出るまでの抜き取り撮影と試視は行っていない（試作の判断 10）。
- 親タスク `.steering/20261015-tangibility-design/decisions.md` 判断 29: 判断 16 の「取り込みから外す」は変えずに、外す方法を探す（研究者の選択）。取り込みを検知して隠す手は `scripts/check_invitation_surface.py` が禁じるので候補にしない。
- 2026-10-16 の Web の下調べ（Claude・一次は未読の箇所あり）:
  - macOS 15 以降、`sharingType = .none` は ScreenCaptureKit の取り込みに効かないという報告が複数ある。Tauri #14200（open・「既知の回避策なし」・`status: upstream`）、Electron #48258（未読・Tauri の issue から参照）。Apple の公式の説明は見つかっていない。
  - 窓の層を上げる・別の窓を重ねるなど、窓の側の古い手は効かないとされる（Tauri #14200）。
  - 写すかどうかは取り込む側のアプリが決める形になっている。Electron（Chromium）は ScreenCaptureKit で取り込むときに保護された窓を自分で除く修正を入れた（取り込みの開始の前に保護された窓に限る）。Zoom は「窓を選んで除く高度な取り込み」を有効にすると隠れ、QuickTime の画面収録には写った、という報告がある（Adam Svoboda の記事）。
  - 出典: https://github.com/tauri-apps/tauri/issues/14200 ・ https://adamsvoboda.net/how-interview-cheating-tools-hide-from-zoom/ ・ https://ayakael.net/mirrors/electron/commit/fd88908457a986f06e310e80499e4b2775d8ba70 ・ https://developer.apple.com/forums/thread/808016

## 2. 問い

アプリの側から外す手はほぼ無い。残る問いは「実際に人に見られる経路（会議の画面共有）で小面が写るか」。写らないなら、写るのは本人が撮るスクリーンショットと収録だけ、と言え、案 A の扱いを選び直す材料が変わる。

## 3. 進め方（研究者に確かめる・Claude の推奨は 2）

1. 調べるのはここまでにして、判断 29 で退けた 3 案から選び直す。
   - 除外できる OS だけで出す（Mac では A を出さない・Windows で小面の除外を実機で確かめる）
   - 写ることを許す（判断 16 を緩め、代償を書く）
   - 案 A を保留し、D・C に重心を移す
2. 会議の画面共有で写るかを実測してから、上の 3 案から選び直す（推奨）。
   - 対象: Zoom（「高度な取り込み（窓のフィルタ）」の設定あり・なし）と、Chrome で開く Meet。研究者の手間は 10 分ほどで、相手側の画面（別の端末）が要る。
   - 手順は試作の `manual-check.md` §0（起動と後片づけ）と §1-4 を使う。`GSE_DATASET` を一時フォルダに向け、終わったら消す。
   - 試作の worktree のバイナリ（`GSE_HANDMARK_SPIKE=1 GSE_DEBUG=1 VITE_GSE_DEBUG=1 npx tauri dev`）をそのまま使える。
3. 一次をもう少し読む（Electron #48258・Apple の文書と forums）。Claude だけでできるが、結論が変わる見込みは小さい。

## 4. 守ること

- 結果は試作の `results.md` §2 と、親タスクの decisions（判断 30 以降）に書く。
- 研究者の打鍵は記録しない（試作の判断 4）。共有の確認の間、本体は一時フォルダに NDJSON を書くので、終わったら消す。
- この Mac では Claude は画面を撮れない（TCC）。目視は研究者。
- PR は出さず、push で止める。
- worktree `/Users/johnd/GSE-prototype-handmark-a` を残すか消すかは、研究者がまだ決めていない。消すなら、この確認が終わってから。
