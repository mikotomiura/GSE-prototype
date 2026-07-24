# 設計: clearForm 安全ガード

## アプローチ

fail-closed のガードヘルパ `assertClearableForm_(form, key)` を追加し、各 `build*` の
`if (CLEAR_EXISTING) { clearForm(form); }` の**直前**で呼ぶ。回答があり、かつ明示オプトインが
無ければ `false` を返し、build 側は `return` して中断する。

グローバル `clearForm` 自体は変更しない(F3 の `FormApp.create` 経路など回答が存在し得ない
用途もあるため、判定は「回答を持ち得る固定ID正本を作る build 側」に置く)。

## 変更対象

`Form_Phase1/GSE_Phase1_Form_Builder.gs` のみ:

1. **定数追加**(`CLEAR_EXISTING` の直後):
   `var ALLOW_CLEAR_WITH_RESPONSES = false;` — 通常 false。意図的な設問作り直し時のみ true。

2. **ヘルパ追加**(`clearForm` 定義の直前):
   ```js
   function assertClearableForm_(form, key) {
     var n;
     try { n = form.getResponses().length; }
     catch (e) { /* 取得不能 → 安全側で中断 */ return false; }
     if (n > 0 && !ALLOW_CLEAR_WITH_RESPONSES) { /* ログ出して中断 */ return false; }
     return true;
   }
   ```

3. **配線**(4 箇所): 各 build の clearForm 直前に
   `if (!assertClearableForm_(form, "<KEY>")) return;` を挿入。
   - `buildForm` → "F1"
   - `buildF2`   → "F2"
   - `buildF4`   → "F4"
   - `buildF5`   → "F5"

## なぜこの設計か

- **fail-closed**: getResponses() 例外時も中断。判定不能を「安全」と誤認しない。
- **オプトイン残置**: restart 等で本当に作り直したい時の逃げ道を1定数で提供(既定は安全)。
- **build 側に配置**: clearForm の他用途を壊さず、破壊が起きる正本フォーム経路だけを守る。
- **最小差分**: 集計・フォーム構造・メール等には一切触れない。

## テスト戦略

GAS のため cargo/自動テストの土俵ではない。検証は:
1. `node --check` 相当で .gs の JS 構文 parse を通す。
2. ロジック机上確認: n>0 かつ ALLOW=false → false / n==0 → true / 例外 → false。
3. 実地(研究者手動・任意): 回答のある F4 に対し buildF4 を実行 → 中断ログを確認、
   フォーム設問が保持される(deleteItem に到達しない)ことを確認。

## リスク / 留意

- restart 時に forms を作り直す必要が出たら、Forms UI で全回答削除(空にする)→ ガード通過、
  または一時的に ALLOW_CLEAR_WITH_RESPONSES=true。ただし現行フォームは直近 buildAllSupportForms で
  設問が最新化済みのため、restart に build 再実行は本来不要(回答クリーンアップ + ロスター初期化で足りる)。
