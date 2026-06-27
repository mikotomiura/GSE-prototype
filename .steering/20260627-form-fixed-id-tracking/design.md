# 修正: F2/F4 の固定ID化（記録漏れ解消）＋ Dropbox 提出状況の集計

## 不具合（ユーザー報告 2026-06-27）
F2 を提出しても管理シートに記録されない。

## 根本原因
`buildF2`/`buildF4` が `FormApp.create()` で**実行のたび新フォームを量産**していた（F1/F5 は
`openById` 固定）。`refreshRosterStatus()` → `countByPid_("F2")` は `FORMURL_F2`（最後に作った
フォーム）の `getResponses()` を読むため、被験者に配った短縮URL(x.gd)が指すフォームと集計が読む
フォームがズレ、回答0件＝記録されない。PR #47 で追加した属性設問も短縮URL先の旧フォームには未反映。

## 修正
### 1. F2/F4 を固定ID再利用に（F1/F5 と同方式）
- `F2_FORM_ID` / `F4_FORM_ID` 定数を追加（**正本＝被験者配布の短縮URL先フォームの編集ID**。
  空のときは buildF2/F4 がガードで停止＝量産防止）。
- `buildF2`/`buildF4` を `FormApp.create` → `openById(...)` + `clearForm` に変更。
- これで「短縮URL ↔ 設問（属性含む）↔ 集計フォーム」が永続一致する。

### 2. Dropbox 提出状況の集計（自己申告ベース）
- Dropbox File Request 提出は GAS から不可視（API連携なし）＝自動同期は無い。
- F4 の S4「セッションログを Dropbox に提出しましたか？」自己申告を `countByPid_` で抽出し、
  `refreshRosterStatus()` がロスター「Dropbox提出」列(11)に「提出済み数/F4回答数（F4自己申告）」を反映。
- ⚠ 真の提出確認は研究者が Dropbox を見るのが最終手段（自己申告は取りこぼし検知用）。

## 影響範囲・非影響
- F2-B(GSE-10)/F2-C(TSE) の項目・pre/post byte一致は不変（設問定義は触らず取得方式のみ変更）。
- F2/F5 では Dropbox 設問が無いため dropboxDone=0（害なし）。
- F3 は廃止フォームのため `FormApp.create` のまま放置（量産影響は廃止により無視可）。

## 運用（ユーザー）
- `F2_FORM_ID`/`F4_FORM_ID` に正本フォームの編集ID（forms/d/<ID>/edit）を記入してから buildF2/F4 を実行。
- 既存の量産フォームは混乱の元なので破棄推奨。短縮URL先を正本に統一。

## テスト（実機）
- F2_FORM_ID 記入 → buildF2 → 短縮URL先フォームに設問が入る → 同フォームに提出 →
  refreshRosterStatus() でロスター F2事前列が埋まる。
- F4 同様＋Dropbox提出列に「n/m（F4自己申告）」。
