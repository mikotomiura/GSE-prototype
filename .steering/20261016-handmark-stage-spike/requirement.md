# handmark-stage-spike —— 手跡の右下の小面を少し主張させ、背景の層（デスクトップの高さの窓）の実現性を Mac で確かめる

## 背景

- 波紋の小面（28 px・灰・白い輪・250 ms・打ち切り）を研究者が試視して「見えずらかった。やはり、少し主張したい感じで、次は壁紙の箇所などでの背景にするか。あとはついでに右下の箇所も少し残した感じで次は試作」（`.steering/20261016-handmark-ripple-spike/results.md` §6）。
- 研究者の選択（同 decisions.md 判断 7）: 背景はデスクトップの高さの窓（壁紙の上・アイコンと他の窓の下）で、壁紙の画像は書き換えない。右下の小面は残し、大きさと色の両方で主張させる。新しい枝・新しいタスクで。
- 表現の議論（枝 `docs/tangibility-design` の `.steering/20261016-handmark-expression-design/decisions.md`）の判断 2・3・5・6 は前提のまま。判断 5（28 px・灰）はこの試視で見直しの条件に当たった。背景は打鍵だけで動かし推定を受け取らない（判断 2）。30 秒の窓の要約を 1 秒ごとに更新し滑らかに移す（判断 3・`res=sec`）。参加者に出すのは EH3 の後（判断 3）。D の写し方は仮（判断 6）。
- 引き継ぎ: `.steering/_handoff/next-session-handmark-stage-and-louder-surface.md`（枝 `spike/handmark-a-surface`）。

## ゴール

Mac で次を確かめ、結果を本ディレクトリに書いて止める。本体への実装は別のタスクで決める。

1. 右下の小面を少し主張させる: 大きさ（例 40 px）と色（輪を地と差の出る濃い色に・線を太く・地の点も濃く）の候補を見本と並べ、研究者に選んでもらう。明るい壁紙と暗い壁紙の両方で見えるかを見る。窓の大きさを輪の最大に合わせ直す。
2. 背景の層の実現性: デスクトップの高さの窓に描けるか（アイコンとの上下・Spaces・全画面・複数ディスプレイ）、他の窓に覆われても 1 秒ごとの更新と移り変わりが続くか、会議の画面共有（Chrome の `getDisplayMedia`・Zoom の自動）と標準のスクリーンショットに写るか（陽性対照つき）、負荷（覆われているとき・電池のとき）。材料は打鍵の時刻だけ。写し方は仮（見本の等高線の波など）。
3. 研究者が自分の画面で、背景と右下の小面を一緒に見る。

## スコープ

### 含むもの
- 枝 `spike/handmark-stage`（worktree `/Users/johnd/GSE-prototype-handmark-stage`・`spike/handmark-a-surface` から切った）。本線にマージしない。
- `src/components/HandmarkSurface.tsx` と `src-tauri/src/handmark_spike.rs` の小面の値の変更。
- 背景の層の試作の窓と描画（新しいファイル）。
- 計測のための記録（環境変数で有効にしたときだけ・通し番号と時刻と描画の量だけ）。
- 研究者の試視（自分の画面で見るまで。何も記録しない）。

### 含まないもの
- `src-tauri/src/analysis/portrait/`・EH3 の壁紙のファイル（`wallpaper*.rs`・`eh3.rs`）・G-GEAR の `experiments/` の変更。
- `engine`・`invitation`・`p_stuck` への依存。推定を受け取る口。打鍵の内容（キーの種類）を材料にすること。
- 研究者の打鍵の記録（計測は合成の打鍵で）。Windows での確認。
- 写し方（D）の決定。C の小窓。
- PR（push で止める）。

## 受け入れ条件

- [ ] 小面の大きさと色の候補が見本で並べられ、研究者が選んだ値が decisions.md に記録されている
- [ ] 選んだ値の小面が明るい壁紙と暗い壁紙の両方で描かれ、窓の大きさが輪の最大に合っている
- [ ] 背景の窓のアイコンとの上下・Spaces・全画面・複数ディスプレイでの振る舞いが、確かめた範囲だけ書かれている
- [ ] 覆われたときの 1 秒ごとの更新と移り変わりの継続が、描画の側の記録で書かれている
- [ ] 画面共有（Chrome・Zoom）と標準のスクリーンショットへの写り方が、陽性対照つきで書かれている
- [ ] 負荷（覆われているとき・電池のとき）が測られている
- [ ] 研究者が背景と右下の小面を一緒に自分の画面で見た

## 関連ドキュメント

- `.steering/20261016-handmark-ripple-spike/`（results.md・decisions.md 判断 7・manual-check.md）
- `.steering/20261016-handmark-a-surface-spike/`（取り込みの除外・fail-closed・synthetic-keys.applescript）
- 枝 `docs/tangibility-design`: `.steering/20261016-handmark-expression-design/decisions.md` 判断 2・3・5・6
- `.steering/20261012-portrait-rhythm-motion/survey-results.md` §2（背景の層の技術・場所を確かめる）

## 運用メモ
- /reimagine 適用: No
- 理由: 段 1 は既存の小面の値を変えるだけで、背景の層は実現性を測って確かめる試作。設計の選択肢より測ることに時間を使う（研究者・2026-10-16）。
