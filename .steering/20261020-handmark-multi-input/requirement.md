# 手跡の表現に、打鍵以外の入力（カーソル・クリック・ホイール）を取り入れる

## 背景

`.steering/20261018-handmark-nature-v3-grading/decisions.md` 判断 8 で、打鍵に加えてカーソルの位置・向き・動いた量・クリック・ホイールを、記録せずに表現の入力として使ってよいことになった。条件は 4 つ（記録の経路へ流れないことを構造で保つ・画面の上でも溜めない・数や評価として返さない・OS の差を記録する）。どの入力をどの要素へ写すかと、見本で何から試すかは未決として残っていた。

引き継ぎ: `.steering/_handoff/next-session-handmark-multi-input.md`。

## ゴール

1. 写し方と条件 4 つの満たし方を決め、decisions.md に置く。
2. 打鍵だけの伏せた見比べ（v3-grading の封）を先に終え、その結果を別の入力の強さを決める基準にする。
3. 版 4 とは別のファイルで見本を作り、カーソル・クリック・ホイールの写し方を画面で確かめる。
4. 実物（壁紙の層）へ持ち込む前に確かめることを記録する。macOS の `NSEvent.mouseLocation` が権限なしで読めるかは、小さな試しのプログラムで実測する。

## スコープ

### 含むもの
- 新しい見本のページ 1 枚（版 4 の `handmark-nature.html` は触らない）
- 写し方・条件 4 つの満たし方の記録
- 実物へ持ち込む前に確かめることの記録と、権限の実測

### 含まないもの
- 実物（`HandmarkStage.tsx`・壁紙の層・`src-tauri/src/input/`）のコードの変更
- ADR の起票（要否を記録するところまで）
- アプリの切り替えを表現に使うこと（判断 3）
- 個人のログからたまに静止画を作る案（v3-grading 判断 9。肖像の系統で扱う）
- 人の段の計画

## 受け入れ条件

- [x] decisions.md に写し方・アプリの切り替え・見比べの順・範囲が研究者の判断として置かれている
- [x] v3-grading の伏せた見比べの評定が貼られ、割り当てが開示されてハッシュが一致している
- [x] 新しい見本で、カーソル・クリック・ホイールがそれぞれ別の要素を動かし、どの跡も数秒で消えることを画面で確かめた
- [x] 新しい見本で、草・粒・波紋の数が入力で増えず、数値が画面に出ない
- [x] `NSEvent.mouseLocation` を権限なしで読めるかを実測し、結果を記録した
- [x] 実物へ持ち込む前に確かめること（クリックの取り方・ロガーへ渡さない型とテスト・ADR の要否）を記録した
- [x] `/cross-review` を行った

## 関連ドキュメント

- `.steering/20261018-handmark-nature-v3-grading/decisions.md` 判断 8・9、`grading.md`
- `.steering/20261017-handmark-why-interesting/decisions.md` 判断 6・9
- `docs/adr/ADR-014-continuous-natural-work-collection.md` D4（ポインタの取り方と入れないものの表）
- `docs/adr/ADR-025-no-self-quantification-return.md`
- `src-tauri/src/input/observe_macos.rs`・`observe_windows.rs`・`src-tauri/src/analysis/pointer_bin.rs`

## 運用メモ
- /reimagine 適用: No
- 理由: 写し方は研究者がこのタスクで決め、実物の設計はこのタスクの外。見本は画面を見て直す方が早い（研究者・AskUserQuestion・推奨どおり）。
