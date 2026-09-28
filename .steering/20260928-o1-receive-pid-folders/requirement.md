# o1-receive-pid-folders — O1 の受け取りフォルダを P-ID ごとに分ける

## 背景

研究者判断（2026-09-28）「フォルダに分けた方がいい」。現状の O1 受け口 `Form_O1/GSE_O1_Submit.gs` は
スクリプト プロパティ `FOLDER_ID` の **1 つのフォルダ直下**にすべての `.age` を保存する。
被験者が増えると P-ID 単位の確認・削除要求への対応（`docs/o1-deletion-ledger.md` A-1）が名前頼みになる。
⚠️ **O1 を配る前に入れる**（配った後だと既存の受領分と置き場が混ざる）。
出典: `.steering/_handoff/next-session-o1-autostart-stage-b.md` §2-3。

## ゴール

- 受け口が `<受け取りフォルダ>/<P-ID>/` に保存する（無ければ作る・作成は直列化・同名複数なら最古）。
- 受領台帳 `GSE_O1_Ledger.gs` が **直下 ＋ P-ID サブフォルダ**を走査し、受け口だけ変えたときの
  「全員が未受領・途絶」誤報を起こさない。
- 削除台帳 A-1 を新しい置き場に合わせる。

## スコープ

### 含むもの
- `GSE_O1_Submit.gs`（`doPost` の保存先決定・新ヘルパ）/ `GSE_O1_Ledger.gs`（`o1LedgerSync_` / `o1LedgerCheck` の走査）
- `o1_submit_guard_test.cjs` / `o1_ledger_test.cjs` / 変異検査（ledger・submit に変異を足す）
- `docs/o1-deletion-ledger.md` A-1

### 含まないもの
- 実配備（受け口・台帳の再デプロイ）と合成ファイルでの実地確認 → **研究者の手順**として渡す
- 直下に既にある旧形式ファイルの移動（台帳は両方を読むので移さない）
- handoff §2-1（段階 B・Mac の本当のログイン）/ §2-2（Windows 実機）/ §2-4（G-3）→ 研究者の手作業
- G1 の配布物・G1 の受け口。同意文書の「未了」の採否

## 受け入れ条件

- [ ] `node Form_O1/o1_submit_guard_test.cjs` 緑。新ケース: P-ID フォルダへ保存／無ければ作る／同名複数なら最古／重複判定は P-ID フォルダ内／ロック取得失敗は `ok:false` で保存しない
- [ ] `node Form_O1/o1_ledger_test.cjs` 緑。新ケース: サブフォルダ内のファイルを数える／直下の旧形式も数える／ごみ箱のサブフォルダは数えない
- [ ] 変異検査（ledger・submit）で新ガードを壊すと赤
- [ ] A-1 の記述が `<P-ID>/` フォルダ（＋直下の旧形式）になっている

## 関連ドキュメント

- `.steering/_handoff/next-session-o1-autostart-stage-b.md` §2-3
- `docs/o1-deletion-ledger.md` A-1
- `.steering/20260927-o1-receipt-ledger/decisions.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計は handoff §2-3 で研究者判断として指定済み（保存先・作成の直列化・台帳の走査範囲）。複数案を比べる余地が小さい。
