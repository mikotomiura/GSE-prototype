# 引き継ぎ — 合流: 招待の契機・循環・書き場所・主要アウトカムを研究者が決める

> 作成: 2026-11-02（研究者の決定: 次のセッションは合流）。入口は `next-session-gse-three-parallel-tracks.md` §4。
> このメモを一次資料にしない。事実は一次で確かめ直す。

## 0 入口の文（新しいセッションに貼る）

「`.steering/_handoff/next-session-gse-merge.md` の合流を実施。問いは three-parallel-tracks §4 の 1〜4」

## 1 読む材料（この順）

| | 結果 | 研究者の判断 |
|---|---|---|
| 位置づけ・信号の一覧 | `.steering/20261102-gse-public-data-landscape/positioning.md` | 同じ steering の `decisions.md` |
| 俯瞰（KLiCKe・CoAuthor・記述だけ） | `experiments/20261102-public-data-landscape/notes.md`（末尾の「合流への材料」） | 同上 |
| T2（KLiCKe・止まりの初期の発火と案 A の追試） | `experiments/20261101-klicke-early-stall-trigger/notes.md` | `.steering/20261101-gse-public-data-fit-item2/decisions.md` |
| 案 A（CoAuthor・停滞の手前の上がり） | `experiments/20261101-coauthor-pre-stall-signal/notes.md` | `.steering/20261101-gse-pre-stall-signal/decisions.md` |
| T3（O1・止まりの最中のフォーカスの離脱と受領） | `experiments/20261101-focus-leave-before-receipt/notes.md` | `.steering/20261101-gse-focus-leave-before-receipt/decisions.md` |
| T1（差し替えの口・未 push） | `/Users/johnd/GSE-prototype-nudge-off`（ブランチ `feature/nudge-default-off`）の `.steering/20261031-nudge-default-off/`・`.steering/20261101-invitation-wiring/`・`.steering/_handoff/next-session-gse-invitation-wiring.md` | 同じ枝の decisions |

- 項目 1（CoAuthor で AI の提案を求める手前）は古い形の問いで、根拠にも反証にも数えない（three-parallel-tracks §4 の「結果の読み方」）。
- 一次の SSOT: `docs/research-positioning.md` §1 の 2026-10-31 改訂・ADR-040・ADR-021 D4・ADR-024・ADR-030。

## 2 材料の要点（一次は上の notes）

- 推定の 30 秒の上がりで「停滞の手前」を先回りする前提は、AI なしの作文（T2・AUC 0.51〜0.52）でも共同執筆（案 A・0.49〜0.50）でも弱い。
- 休止を本人の θ の数分の一で切る契機は 1 時間に 100 回を超え、停滞に至るのは 1 割未満（T2）。停滞の時計で切ると t0 とほぼ同じ時刻で先回りにならない（T2）。
- 今の契機（`p_stuck ≥ 0.60` が 30 秒）は短い作文ではほとんど出ない（T2・俯瞰 L2）。
- 停滞は t0 の後に短く終わる（再開した停滞の中央値 6〜15 秒・俯瞰 L1）。KLiCKe では停滞の約半分に削除以外の手の操作がある（俯瞰 L3）。
- 停滞と推定は作業の後ろに偏る（俯瞰 L6）。契機を比べるときは時期を揃える。
- O1 で、止まりの最中のフォーカスの離脱は受領に先立つとは言えない（RR 1.29・0.99〜1.67・誤発火 75%・遷移の 79% は停滞の検出の前・T3）。遷移を契機にすると副のアウトカム「ウィンドウを離れずに再開」の対象が構造的に外れる（循環・T3）。
- ADR-024 の出来事（180 秒以上の途切れ明け）は 30 分の作文で 1 人 0〜1 件。受領はデータの仕組みで 3% にも 81% にもなる（俯瞰 L4）。ふつうのデスクワークでの受領の経路は O1 でしか見られない。
- 約 11 分の単位では、人の中の揺れは数え上げの揺れと同じ大きさ（俯瞰 L5）。単位を長く取る必要がある。

## 3 進め方

1. 材料を読み、4 問それぞれに推奨と理由（材料の出典つき）を用意する。
2. AskUserQuestion で日本語で聞く（1 問ずつ・推奨を先頭に・memory `feedback-decisions-via-askuserquestion`）。
3. 決まったことを新しい steering（`.steering/<日付>-gse-merge/decisions.md`）に書く。ADR の本文は書き換えない（補訂か新しい ADR）。凍結した事前登録は触らない。
4. 決まった中身を T1 の口に入れる実装・O1 での数え直し・positioning の本文の改訂は、それぞれ別タスク（引き継ぎを書いて分ける）。

## 4 未決で残っているもの（合流で扱う候補）

- T1 の残り（実機の確かめ・push・schema parity）は合流とは別。合流の結果が `InvitationSettings.tsx` の説明文・通常のモードの同意文書・契機の中身に響く（T1 の引き継ぎ）。
- CS1 は著者の返事待ち（`next-session-cs1-reply.md`）。合流を待たせない。

## 5 合流で方向として聞く候補: 停滞の分解（研究者の決定・2026-11-02）

- 研究者の問い（2026-11-02）: 「停滞は思ったより溢れており、今の検出の形だと検知が難しそう。より敏感に検出し、要素や特徴を分解できるものを作るか」。
- Claude の見立て: 停滞が多いのは、停滞の始まりの定義がふつうの休止まで拾っているため（ADR-030 の 9b・詰まりの判定ではない）。難しさは感度の不足ではなく、どの停滞が詰まりかを見分ける手がかりの不足。感度を上げると誤発火が増える（T2: 1 時間に 100 回超）。
- 研究者の決定: 合流で方向として決め、分解はその後の別タスク（推奨どおり）。
- 方向の案（合流の問い 1 の候補として推奨つきで出す）: 停滞を型に分ける。
  - 手の様子: 沈黙だけ・削除が続く・移動やクリックで操作・フォーカスが外へ出た
  - 長さ: すぐ戻る・長く続く
  - 作業の中の位置: 序盤・終盤
  - 段 1 はアプリのコードを変えずに記録から分解する（打鍵の層は公開データ、フォーカス・ポインタ・受領は O1）。段 2 で型ごとに O1 の 6 択の自己申告・プローブ・その後の受領と結び付け、詰まりらしい型があるかを見る。見えれば、その型を T1 の差し替えの口に入れる契機の中身にする。
- 合流で先に決めること: 結び付ける先（主要アウトカム＝受領か、自己申告か）。問い 4 の答えで決まるので、問い 4 を先に聞くか、問い 1 と 4 を続けて聞く。
