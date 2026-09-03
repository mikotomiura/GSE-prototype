# design — O1 の bare-row-claim 移植

## アプローチ

★ G1 の `bare-row-claim` を**そのまま移植**する。⚠️ ただし前セッションの教訓
「**移植は『元を読み比べる』までが移植**」に従い、**列構成を実測で突き合わせてから**移す。

```js
if (!rowEmail) {
  var rowName = String(rows[i][1] == null ? "" : rows[i][1]).trim();
  if (!rowName) return { conflict: true, pid: rowPid, row: i + 1, reason: "bare-row-claim" };
  return { pid: rowPid, row: i + 1 };   // ★ 氏名がある = 研究者が用意した行
}
return { conflict: true, pid: rowPid, row: i + 1, reason: "email-mismatch" };
```

## ★ 安全側の向き

⚠️ 誤って `conflict` にしても、研究者が確認して再提出してもらえばよい。
★ 逆（誤って通す）は**他人の P-ID を渡す**ので取り返しがつかない。→ **止める側に倒す。**

## テスト戦略

⚠️ **`o1FindInPhase1Roster_` を呼ぶテストは 1 件も無かった**（★ 129 ケース全部が緑なのに、
当の関数は一度も実行されていなかった）。→ ★ **直接呼ぶ**形で 5 ケース書く。

| ケース | 種類 |
|---|---|
| 裸の行は取れない | ★ 本命 |
| 氏名がある行は通る | ⚠️ **陽性対照**（これが無いと「全部 conflict」でも緑になる） |
| メール不一致は conflict | 本命 |
| メール一致が最優先 | ⚠️ **陽性対照**（既存経路を壊していない） |
| 該当なしは null | 境界 |

★ ⚠️ **変異を注入して赤になることを毎回確かめる**（前セッションで検査が 7 件壊れていた）。

## ⚠️ 変更しないもの

- ⚠️ **T-27**（プロジェクト跨ぎの二重採番）—— ★ `LockService` では防げない。別件・`/reimagine` 規模
- ⚠️ **`O1_MGMT_SHEET_ID`** の実装 —— 別件（HIGH）
- ⚠️ **G1 へのロスター形検査の移植** —— 別件（中）
