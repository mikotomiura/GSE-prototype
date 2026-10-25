# タスクリスト

## 準備
- [x] ADR-040（補訂 1）・表現の設計の decisions・試作の decisions/results・`prepare()` を読む

## 地図
- [x] 置き場所の候補を洗い出す（引き継ぎ §3 の表＋足りないもの）
- [x] 一次資料で確かめる（Apple の文書・SDK のヘッダ）
- [x] 資料で決まらないものを最小の試作で確かめる（全画面の Space・層の順）
- [x] `placement-map.md` に書く

## 議論
- [x] 地図を研究者に見せ、§4 の論点の順番を AskUserQuestion で決める
- [x] decisions.md に記録する

## 完了処理
- [x] 次のセッションへの引き継ぎを書く
- [x] commit（枝を確かめてから）・push（PR は出さない）

## 続き（2026-10-23・2 回目のセッション）
- [x] 論点 1 の向きを研究者と決める（判断 3: 覆われない縁の帯を見本で探る）
- [x] 縁の帯の見本のページを作る（`handmark-edge-strip.html`・公開 https://claude.ai/artifact/FFvBzRKtVTLUEL2nZcEyYL ・候補 8 つ）
- [x] 研究者が候補を選ぶ（判断 4: 今の背景＋下の縁の帯＋他の窓をどける）
- [x] 見本に組み合わせの形を足す（Version 2）
- [x] 研究者が組み合わせの見本を見る・戻すきっかけを決める（判断 5）
- [x] 見比べの結果を decisions.md に記録する（判断 4）

## 続き（実機の最小の試作・2026-10-25 まで）
- [x] どける操作の細部を決める（判断 5）
- [x] 下の縁の帯の試作 `probe/strip.swift` を書く
- [x] (1) 全画面の上に出るか・(2) 負荷を測る（run3〜run8）
- [x] (4) 見えていたアプリだけを戻せるかを測る（run9・run10）
- [ ] 前面のアプリが隠れない問題を `--activate-first` で確かめる（ビルドのみ）
- [ ] (3) 全画面の中でどけられるかを測る（試し 3）
- [x] 結果を placement-map.md §4・decisions.md 判断 6 に書く
- [x] 次のセッションへの引き継ぎを書く（`next-session-handmark-edge-strip-design.md`）
- [x] commit・push（PR は出さない）
