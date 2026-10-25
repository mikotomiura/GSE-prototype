# 次のセッション: 手跡の下の縁の帯と「他の窓をどける」の設計を詰める

> 書いた日: 2026-10-25（Mac）。前のタスクの記録: `.steering/20261023-handmark-window-boundary/`（枝 `docs/tangibility-design`・worktree `/Users/johnd/GSE-prototype-tangibility`）。
> 機械: Mac だけ。返答・記録・AskUserQuestion は日本語で。記号を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。
> 研究者は、目で見たことを聞く AskUserQuestion を拒否して言葉で答えることが多かった。目視の確認は文章で聞く。
> PR は出さない（A4 の処理が続いている間は選択肢にも入れない）。push までにする。コミットの前に `git branch --show-current`。本線にマージしない。
> O1 の収集アプリ（`~/Desktop/O1_実施用_macOS/gse-next.app`）は止めない・起動しない。研究者の画面を撮らない。試作を動かして画面が切り替わる・アプリが隠れるなら、その都度先に聞く。
> キーストロークの内容と NDJSON の生ログは外部の LLM に送らない。アプリの名前はログに書かない。

## 最初に打ち込む文

```
/Users/johnd/GSE-prototype-tangibility/.steering/_handoff/next-session-handmark-edge-strip-design.md を読んで、手跡の下の縁の帯と他の窓をどける操作の設計を詰めるタスクを始めて。
```

新しいタスクとして `/start-task` で `.steering/[日付]-handmark-edge-strip-design/` を切る（前のタスクは地図と試作までで閉じる）。

## ここまでに決まったこと（前のタスクの decisions.md）

- 判断 3・4: 壁紙の層の背景は今のまま残し、下の縁に動く帯を足す。帯の中身は「霧と粒と線」、太さ 14 点・濃さ 70% は仮。必要なときに「他の窓をどけて背景を見せる」操作を足す。
- 判断 5: どけた後は、もう一度選んで戻す（打鍵では戻さない）。押した時に見えていたアプリだけを覚えて戻し、その一覧は戻したら捨てて記録しない。どける操作は回数だけ記録する（本人には見せない。本線に入れる前に、記録の仕様・同意の文書・ADR の追記が要る。試作の段では記録しない）。
- 判断 6: 試作の結果を受けて、次は具体的な設計を詰める。
- 見本: `handmark-edge-strip.html`（公開 https://claude.ai/artifact/FFvBzRKtVTLUEL2nZcEyYL ・非公開）。

## 試作で分かったこと（`placement-map.md` §4）

- accessory・浮く層・`fullScreenAuxiliary` の帯は、テキストエディットの全画面の上でも見えた（2 回・研究者の目視あり）。GSE 本体は regular なので、本体のままでは出ない（§1）。
- 負荷は 1 コアの約 10%（60 回/秒・線だけ・合成の風）。
- 見えていたアプリだけを戻せた。前から隠していたアプリは隠れたまま。
- `hide()` / `unhide()` の戻り値は常に false。成否は `isHidden` を読み直す。
- 隠した後も 2〜3 のアプリが見えたまま残り、層 0 の窓 2 枚は動かなかった。前面のアプリが外からは隠れない見込み（推測）。
- `full_size_layer0` は全画面でも 0（ノッチのため窓が画面より低い見込み・未確認）。全画面の判定に窓の大きさは使えない。

## 最初にすること（推奨。研究者が要らないと言えば飛ばして設計へ）

どける側の設計の前提を変えうる短い試しが 2 つ残っている。どちらもアプリが隠れるので、動かす前に研究者に聞く。

1. 試し 2 のやり直し: `--activate-first` で前面のアプリも隠れるか。
   `swiftc -O probe/strip.swift -o <scratchpad>/strip` でビルドし、`<scratchpad>/strip --duration 25 --hide-at 5 --restore-at 15 --activate-first`。`hide_check not_hidden_after_1s=… active_not_hidden=…` の行を読む。研究者には「窓が残ったか」を文章で聞く。
2. 試し 3: 全画面の中でどけられるか。テキストエディットを AXFullScreen で全画面にし（run7・run8 の手順。`probe/run*-marks.txt` に印の残し方がある）、10 秒目に隠し、25 秒目に戻す。テキストエディットはもとは動いていなかったので、終わったら保存せずに閉じて終了させる。

## 詰める設計の論点（Claude の案。順番は研究者と決める）

1. プロセスの形: GSE 本体を accessory にするか、帯だけを accessory の小さな別プロセスにするか。本体を accessory にするとトレイ・設定の窓・O1 の動きに響くかは見ていない。Tauri 側の先例は `overlay_panel.rs`（NSPanel）。
2. 帯を本物の打鍵につなぐ（論点 6 の打鍵との接続度）: 試作の判断 13（「最初の線の頃の方が打鍵との接続度は強く感じる」）と `HandmarkStage.tsx` の定数（`WIND_TICK_MS` 250 など）。帯の中で線・霧・粒をどう配るか。
3. 描画の回数と負荷: 60 回/秒で約 10%。風の更新が 250ms ごとなら、描く回数を 30 か 15 に下げられるか。見えないときは止める（`occlusionState`・論点 5）。
4. 背景と帯の分担（論点 4）: 背景が見えている間も帯を出すか、背景が覆われたときだけにするか。
5. 帯の見た目の細部: 太さ・濃さ・カーソルが近づいたら薄くする・Dock と重なるときの扱い（未確認）。
6. どける操作の入口: トレイのメニューか、帯そのものか（帯はクリック透過なので、入口にするなら作りが変わる）。前面のアプリが隠れない問題への手当て（試しの結果しだい）。
7. どける回数の記録: 本線に入れる前の、記録の仕様（時刻を持つか）・同意の文書・ADR（ADR-040 の補訂か新しい ADR か）。設計の段で中身まで詰めるかは研究者に聞く。

残りの論点は前のタスクの判断 2 の順番のまま: 3 前に出る（帯で大筋は決まった）・2 境界に出す・7 Windows（収集だけの依頼で）。

## 先に読むもの

- `.steering/20261023-handmark-window-boundary/decisions.md`（判断 1〜6）・`placement-map.md`（§1 と §4）
- `.steering/20261016-handmark-expression-design/decisions.md` の判断 2〜6・10〜15
- 枝 `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`）の `.steering/20261021-handmark-stage-pointer/decisions.md` の判断 10・13・14、`src/components/HandmarkStage.tsx`
- why-interesting の判断 6 の制約 1「育たない・溜まらない」、ADR-040 D4「溜めない」・D5、ADR-025 D1

## 試作のファイル

- `probe/strip.swift`（引数 `--duration` `--hide-at` `--restore-at` `--thick` `--fps` `--activate-first`）
- ログ `probe/run3`〜`run10`（`*.log` は .gitignore にかかるので `git add -f` で入れた）
