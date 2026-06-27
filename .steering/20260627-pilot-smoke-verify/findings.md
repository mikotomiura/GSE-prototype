# 発見不具合 / 確認事項 (パイロット投入前スモーク)

検証フェーズのためコードは修正しない。各 finding は follow-up を切るか研究者運用で対応する。

## F-1 ✅ 解決済 (2026-06-27) — APP_DOWNLOAD_INFO を実配布先 (Google Drive) で確定
- 配布方針確定 (ユーザー決定 2026-06-27):
  - repo は **PRIVATE** のため GitHub Releases 直リンクは被験者がDL不可・collaborator 招待は盲検崩壊。
    → アプリ一式を **Google Drive 閲覧専用フォルダ** (x.gd/6crxj → drive/folders/1n8bQ8Oy9aRL...) で配布。
  - 配布物 = gse-next.exe (Win portable, SAC回避) / gse-next_0.1.21_aarch64.dmg (macOS Apple Silicon)
    / gse-package(.exe) (暗号化CLI・cargo build --features package でローカル生成) / pubkey.txt (age公開鍵・全員共通)。
  - ⚠ 秘密鍵 ~/.gse/age-identity.txt は zip に入れない。gse-unpack(復号)は被験者に渡さない (研究者専用)。
  - 初回セッションは研究者同席 (C) で起動・権限付与・初回警告確認。
- 実装: APP_DOWNLOAD_INFO を Drive 短縮URL+OS別ファイル名+同梱明記に / PUBKEY_SOURCE_INFO を「配布フォルダ同梱・
  全員共通」に / メール本文の重複「3点」補足行を削除。→ .steering/20260627-form-demographics-shortlinks/ に集約。
- 残: Drive フォルダの共有設定が「リンクを知る全員が閲覧可」か・zip アップ済みかは研究者運用で担保。

## (旧記録) F-1 ⚠ 要対応 (pilot 投入前) — APP_DOWNLOAD_INFO がプレースホルダのまま
- 場所: `Form_Phase1/GSE_Phase1_Form_Builder.gs` L44-46
- 現状: `APP_DOWNLOAD_INFO` が
  `"（アプリ本体 gse + gse-package + pubkey.txt の入手先をここに記入。例: 配布 zip の DL リンク、または研究者から直接受領）"`
  というプレースホルダ文字列のまま。
- 影響: `AUTO_SEND=true`（L35）のため、適格な F1 提出があった瞬間に本人宛メール（f1EmailBody_）が
  自動送信される。その本文にこのプレースホルダがそのまま入るため、被験者はアプリ入手先が分からない。
- prompt §2 B.7 の「`APP_DOWNLOAD_INFO` を実配布先に書き換え済みか」が **未** の状態。
- 対応（研究者）: 実配布先（gse / gse-package / pubkey.txt の DL リンク or 受領方法）に書き換えてから
  Apps Script に貼り直す。あるいは pilot ドライランまでは AUTO_SEND=false（下書き）で運用し、
  内容確認後に手動送信→確定後に true へ戻す、も安全側の選択肢。
- **採用方針 (ユーザー決定 2026-06-27)**: 「実配布先を埋めてから AUTO_SEND=true のまま実行」。
  → 研究者から実配布先 (DL リンク or 受領方法) を受領し `APP_DOWNLOAD_INFO` を実値へ書き換え、
    Apps Script へ貼り直してから B.3 を完全な end-to-end ドライランで実施する。
  → 値は repo の .gs を単一真実源として更新（プレースホルダ→実値）。これは prompt B.7 が
    明示的に研究者の書き換えを想定した運用 config であり、HMM/挙動コードの変更ではない。
- 関連定数（参考・こちらは実値が入っている）:
  - `DROPBOX_FILE_REQUEST_URL` = https://www.dropbox.com/request/5oak4xpqjt19zx8zvh03 （実値）
  - `PUBLIC_LINKS_URL` = .../18vs0qbEa... 閲覧専用・PII なし前提（B.7 で最終確認対象）
  - `PUBKEY_SOURCE_INFO` = 配布パッケージ同梱 pubkey.txt の説明（汎用文・実害なし）

## (記入欄) 実機検証で発見した不具合
- A 系（アプリ）:
- B 系（Form）:
