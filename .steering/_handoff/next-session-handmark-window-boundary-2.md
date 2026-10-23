# 次のセッション: 手跡の背景が窓に覆われる問題 —— 論点 1 から議論する

> 書いた日: 2026-10-23（Mac）。前のセッションの記録: `.steering/20261023-handmark-window-boundary/`（枝 `docs/tangibility-design`・worktree `/Users/johnd/GSE-prototype-tangibility`）。
> 機械: Mac だけ。返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
> PR は出さない（A4 の処理が続いている間は選択肢にも入れない）。push までにする。コミットの前に `git branch --show-current`。
> O1 の収集アプリは止めない・起動しない。研究者の画面を撮らない。試作を動かして画面が切り替わるなら、その都度先に聞く。

## 最初に打ち込む文

```
/Users/johnd/GSE-prototype-tangibility/.steering/_handoff/next-session-handmark-window-boundary-2.md を読んで、前のタスク .steering/20261023-handmark-window-boundary/ の続きとして、論点 1 から議論を始めて。
```

## 前のセッションで分かったこと（`placement-map.md`）

- GSE は regular（activation policy を設定していない）。このままだと、他アプリを全画面にしたとき背景の窓は全画面の Space に入らない。層・FullScreenAuxiliary・CanJoinAllApplications では変わらなかった。accessory にすると入り、浮く層以上なら全画面の上に見えた（実測は各 1 回・素の実行ファイル・全画面役は自前の窓）。
- 全画面にしなくても、研究者のいつもの配置（窓を並べて画面をほぼ埋める）で背景はほとんど見えていない。
- `occlusionState` で「自分の窓が全部覆われたか」を、他の窓の位置を読まずに知れる（論点 4・5 の道具）。
- 他の窓の位置を読む（論点 2）には窓の一覧が要る。許可なしで読めるかは未確認。

## 議論の順番（判断 2・研究者が決めた）

1 覆われるのを性質と見るか → 6 打鍵との接続度 → 3 前に出る → 4 背景と小面の分担 → 5 見えないときに描くか → 2 境界に出す → 7 Windows
（論点の中身は前の引き継ぎ `next-session-handmark-window-boundary.md` §4。論点 1 の答えが「前に出る」に近ければ 3 を先に回す。）

## 先に読むもの

- `.steering/20261023-handmark-window-boundary/placement-map.md`・`decisions.md`
- 前の引き継ぎ §4・§5（ADR-040 補訂 1、表現の設計の判断 2〜6・10〜15、試作の判断 10・13・14）

## まだ確かめていないもの（必要になったら最小の試作で）

- 普段使うアプリ（ブラウザ・エディタ）の全画面で同じか。accessory にした GSE 本体（トレイ・設定の窓・O1）で困らないか、背景だけを別プロセスにするか。
- Mission Control・デスクトップを表示・ステージマネージャの間の振る舞い。
- 許可なしで窓の一覧から他の窓の位置が読めるか。ステータス項目・Dock のアイコンの描き換えの頻度と負荷。
