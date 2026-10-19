# 次のセッション: 手跡の表現に、打鍵以外の入力（カーソル・クリック・ホイール）を取り入れる

> 書いた日: 2026-10-20（Mac・研究者の依頼）
> 機械: Mac だけで完結する（G-GEAR の結果は待たない）
> 枝: `docs/tangibility-design`（worktree `/Users/johnd/GSE-prototype-tangibility`）
> 返答・記録・AskUserQuestion は日本語で。記号（★・⚠️）を多用しない。決めることは推奨と理由を添えて AskUserQuestion で聞く。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-handmark-multi-input.md を読んで、§2 から始めて。
```

## 1. 先に読むもの

- `.steering/20261018-handmark-nature-v3-grading/decisions.md` の判断 8（打鍵以外の入力を、記録せずに表現の入力として使う・条件 4 つ）と判断 9（静止画の案・記録のみ）。
- `.steering/20261017-handmark-why-interesting/decisions.md` の判断 6（自然世界の制約 3 つ）・判断 9（議論の 3 点）。
- `docs/adr/ADR-014-continuous-natural-work-collection.md` の D4（ポインタの取り方と禁止の表・187〜200 行あたり）と `docs/adr/ADR-025-no-self-quantification-return.md`。
- いまの取り方: `src-tauri/src/input/observe_macos.rs`（クリックを取っていない・14 行）、`observe_windows.rs`（Raw Input）、`src-tauri/src/analysis/pointer_bin.rs`（1 秒ごとの 4 つの値だけ）。
- 見本: `.steering/20261017-handmark-why-interesting/handmark-nature.html`（公開した見本 https://claude.ai/artifact/YSNLasJ1RVhBm2UxvfQGaS ・Version 4）。

## 2. やること（研究者の言葉では「具体化、設計の決定から施策」）

1. **タスクを作る**（`/start-task`）。記録先を新しいタスクにするかは研究者に確かめる。
2. **設計を決める**（研究者に AskUserQuestion で確かめる）。
   - どの入力を、どの要素へ写すか。Claude の案は、入力ごとに別の要素へ写すこと（自分の手が動かした感じを残すため）。たとえば次のとおり。
     - 打鍵: 風（いまのまま）
     - カーソルの位置: 近くの草だけがなびく
     - クリック: その場に一回きりの波紋が立って消える
     - ホイール: 霧の流れ
   - アプリの切り替えは表現に使わない案を推奨する。回数が「注意が散っている」という評価に読まれやすいため。
   - 判断 8 の条件 4 つ（記録へ流れない構造・画面でも溜めない・数で返さない・OS の差）を、見本と実物（壁紙の層）それぞれでどう満たすか。
   - 伏せた見比べ（打鍵だけ・強さ 4 段）を先に終えるか、後回しにするか。封は `.steering/20261018-handmark-nature-v3-grading/grading.md` に記録済み。
3. **見本で試す**。ブラウザの見本はページの中のマウスしか拾えないので、確かめられるのは写し方の感じまで。画面を見るまで完了にしない。
4. **実物へ持ち込む前に確かめること**を記録する。
   - macOS の `NSEvent.mouseLocation` が権限なしで読めるか（未確認）。
   - クリックを使うなら、macOS は ADR-014 D4 の取り方を広げる判断が要る。
   - 表現用の値がロガーへ渡らないことを型とテストで固定する方法。
   - 「表現には使うが記録しない」を ADR で明示するか。
5. 完了時に `/cross-review` を行う。push まで行い、PR は研究者に確かめてから。

## 3. 守ること

- 制約 3 つ（育たない・溜まらない／天気や季節で状態を表さない／推定を使わない）。カーソルの跡も数秒で消すこと。
- 「自然だから注意を奪わない」「自然を見ると回復する」とは書かない。
- 研究者の判断は decisions.md に置き、Claude の作業（design.md）と分ける。
- 記録・送信はしない。キーの内容は読まない。

## 4. 別の系統として残すもの

- 個人のログからたまに静止画を作る案（判断 9）は、肖像の系統（`docs/theory/measurement-terminating-practice-portraiture.md`・EH3 の壁紙）の側で扱う。この引き継ぎの範囲には入れない。
