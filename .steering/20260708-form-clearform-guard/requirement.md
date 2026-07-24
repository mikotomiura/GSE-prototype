# F4/F2/F5 正本フォーム誤クリア防止ガード

## 背景

2026-07-08、`buildAllSupportForms()`(= `buildF2`/`buildF4`/`buildF5`)を再実行した結果、
被験者が提出中の固定ID(openById)正本フォーム F2/F4/F5 に対して `clearForm()` が走り、
全設問が `deleteItem` された。Google Forms の仕様上、設問を削除すると既存回答の中身も
削除されるため、**再構築より前の全回答の中身(P-ID・セッションID・S1〜S5)が復元不能に消失**した
(F4 の場合: 回答レコード17件は残るが、うち16件が空・最新1件のみ中身あり)。

管理シートの「セッション数 / F4回答(計)」は保存値ではなく `refreshRosterStatus()` →
`countByPid_("F4")` がフォーム回答から毎回数え直す derived 値のため、回答の中身が消えると
全参加者の集計が 0 になる。

根本原因は、F1〜F5 が固定ID化された後も `build*` が `CLEAR_EXISTING=true` で
**回答の有無を確認せず無条件に clearForm** する設計にある。create 量産時代の名残で、
固定ID再利用(2026-06-27〜)により「再実行=正本の破壊」に変質していた。

## ゴール

`build*`(F1/F2/F4/F5)が、**回答が1件でも存在する正本フォームを clearForm しようとしたら
中断する**安全ガードを入れ、同種の全消失事故を構造的に再発不能にする。

## スコープ

### 含むもの
- `Form_Phase1/GSE_Phase1_Form_Builder.gs` にガード定数 + ヘルパを追加
- `buildForm` / `buildF2` / `buildF4` / `buildF5` の clearForm 直前にガードを配線

### 含まないもの
- 消失した F2/F4/F5 回答の復元(復元不能。restart 方針で対応)
- 管理シート集計ロジック(`refreshRosterStatus` / `countByPid_`)の変更
- restart 運用手順そのもの(別途 restart チェックリストで扱う)

## 受け入れ条件

- [ ] 回答のあるフォームに対し build系が clearForm に到達せず中断し、明確なログを出す
- [ ] 中断時は refreshRosterStatus() を案内し、意図的な作り直し手段(ALLOW_CLEAR_WITH_RESPONSES)も示す
- [ ] 回答が 0 件のフォーム(初回構築)は従来どおり build できる
- [ ] getResponses() が例外を投げた場合は安全側(中断)に倒れる(fail-closed)
- [ ] JS 構文が妥当(node --check 相当で parse 通過)

## 関連

- インシデント経緯: 本セッションの調査(F4復旧ダンプで中身消失を確認)
- 集計の仕組み: `refreshRosterStatus`(:1675)/ `countByPid_`(:1722)
- 破壊経路: `clearForm`(:2123)/ `buildAllSupportForms`(:894)
