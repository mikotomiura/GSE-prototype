# 引き継ぎ: 手跡の案 A —— 画面端の小面が Mac で成り立つかを確かめる最小の試作（Mac）

作成 2026-10-16（Mac）。返答・記録は日本語で。記号（★・⚠️）を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-a-surface-spike.md を読んで、/start-task で手跡の案 A の小面の試作のタスクを立て、§3 の決めることを研究者に確かめるところから始めて。
```

## 1. 背景（決まったこと）

- 研究者の判断（2026-10-16・AskUserQuestion）: 次のセッションは 2 本立てにする。
  - 1 本目は `next-session-eh3-pre-freeze-f1-and-separation.md`（F-1 の壁紙の見比べ → 肖像と招待の分け方の検査）。研究者が数日かけて壁紙を見比べる。
  - その間に、別の worktree で本メモ（手跡の試作）を進める。
- 試作は **案 A の小面が Mac で成り立つ条件** から始める（研究者の判断）。見た目の作り込みはその後にする。案 D は、G-GEAR の机上の検査（相対のタイミングの漏れ）が終わるまで作らない。
- attack-me は、試作と研究者自身の最初の試視の後に回す（研究者の判断）。原稿も事前登録もまだ無いため。
- 設計の出典:
  - `.steering/20261015-tangibility-design/decisions.md` 判断 12（A は小面だけ・1 打に 1 回の短い変化）・判断 16（小面の規則は肖像の規則を引き継ぎ、肖6 だけを外す）・判断 28（手跡）。
  - `idea-section13.md` の表と「未決」の行。小面を取り込みから外せるかは「試作の段の必須の項目」で、小面そのものでは未確認。EH3 の窓では確認済み。
  - 理論は `docs/theory/measurement-terminating-practice-portraiture.md` §1.4。

## 2. 確かめること（成り立つ条件）

1. **遅れ**: 打鍵から小面の変化が見えるまでが 250 ms 以内か（承認した文面）。評定の主体感は 200 ms を超えると下がる [P486]（S-TG 台帳 #2・N = 27）。測り方は着手のときに決める。
   - 打鍵の時刻は CGEventTap の側で取れる。描画の時刻をどう取るかは未決。
   - 合成キー入力は CGEventTap に届く（memory `macos-app-visual-check-workflow`）ので、打鍵は自動で流せる。
2. **取り込みから外せるか**: 画面の撮影・画面共有に小面が写らないか。
   - EH3 の窓で使った方法が小面の窓にも効くかを、実物で確かめる。
   - この Mac では私（Claude）が画面を撮れない（TCC）。撮影と目視は研究者の手順として渡す。
3. **クリックを奥へ通すか・常に前面に出るか・フォーカスを奪わないか**: 過去の overlay で、透明な余白がクリックを奪った（memory `macos-overlay-clickthrough-bug`）。小面の窓は内容の実寸ちょうどにする。
4. **規則を壊さないか**（判断 16）: 推定（`p_stuck`・`level`）を使わない。本人の操作を記録しない。持ち越さない。すぐ閉じられる。数値や良し悪しを載せない。

## 3. 決めること（研究者・AskUserQuestion で）

- 試作の置き場: 本線にマージしない枝（例: `spike/handmark-a-surface`。`origin/docs/tangibility-design` から切る）に、Tauri の別窓として作るか。`src-tauri/src/analysis/portrait/`・`eh3.rs`・`wallpaper*.rs` は、1 本目のセッション（F-1・分け方の検査）が触るので触らない。
- 小面の大きさ・位置、変化の中身（仮のものでよいか）。
- 遅れの測り方と、合格の線（250 ms を何回中何回か）。
- 研究者の打鍵を試作で使うか（EH2 と同じく本人の PC の中だけで、記録を外部の LLM に送らない）。使わないなら合成の列だけで回す。

## 4. 守ること

- 試作は本線に入れない。成り立つ条件が分かったら、結果を `.steering/` に書いて止める。本体への実装は別のタスクで決める。
- 1 本目のセッションとは worktree を分ける（memory `parallel-sessions-share-checkout`）。コミットの前に `git branch --show-current` を確かめる。
- 画面を変えたら、目で見るまで完了にしない（memory `ui-changes-need-eyes`）。
- 打鍵の内容は記録しない。時刻と、キーの種類の分類だけを使う（`data-privacy`）。
- PR は出さず、push で止める（memory `feedback-push-only-no-pr-during-runs`）。
