# Drive フォルダ対応表（2026-08-08 差し替え後）

親フォルダ（★ 制限付き＝ owner のみ。実測確認済み・D-7 のまま）:
https://drive.google.com/drive/folders/1qhl28IDeh-19upuZf_YxPwwdq_d9xVcI

★ 親フォルダ直下に置いた**研究者用**ファイル（⚠️ 被験者には配らない）:

| いつ | 何 | リンク | 実測 |
|---|---|---|---|
| 2026-08-09 | Windows 実機 Claude Code への調査依頼プロンプト（block01 の打鍵 / 起動①の終了） | [file/d/1mzriMKMhm5p5cFubu7v4UmsGWGAVpmMb](https://drive.google.com/file/d/1mzriMKMhm5p5cFubu7v4UmsGWGAVpmMb/view) | ★ `fileSize=10775` が手元と **byte 一致** ／ 共有は **owner のみ**（`get_file_permissions` で実測） |

⚠️ ★ **フォルダ ID は 2026-08-08 の差し替えで全部変わった。**
研究者が旧 15 フォルダを削除し、`dist/_drive` の 15 フォルダを丸ごと上げ直したため
（＝引き継ぎ `§3` の手順どおり）。★ 旧 ID を書いた資料は無効である。

| P-ID | Drive フォルダ（新 ID） | byte 照合 | 共有 |
|---|---|---|---|
| P006 | https://drive.google.com/drive/folders/1-hPz4wUTXKDxAOlUv5NjZOWMHjNpXTmq | ✅ 10 件 113290 B | anyone: reader |
| P007 | https://drive.google.com/drive/folders/1WRI09FT9wVD9ph2EmeCirKrjOFuXC_M1 | ✅ 10 件 113204 B | anyone: reader |
| P008 | https://drive.google.com/drive/folders/1eubMlhEE03_tEjpwBEOdbouR3M7sC0Kl | ✅ 10 件 113290 B | anyone: reader |
| P009 | https://drive.google.com/drive/folders/1CrCn34cKmgCEHDLHo1dwlJ8eyt_ryUbi | ✅ 10 件 113204 B | anyone: reader |
| P010 | https://drive.google.com/drive/folders/1r6mMtOkKbVIrQ-s5PUfHOH36ZL6FSFJH | ✅ 10 件 113290 B | anyone: reader |
| P011 | https://drive.google.com/drive/folders/1pfCqsXJfbzV6pYM7xWAUpic1q_nPS5MS | ✅ 10 件 113204 B | anyone: reader |
| P012 | https://drive.google.com/drive/folders/1-pTk-m0-_YKeHrCpTwoHjlYww64G54W5 | ✅ 10 件 113290 B | anyone: reader |
| P013 | https://drive.google.com/drive/folders/1ATBDWA0okcBw-66eGLCCjxUu3jw_hkh- | ✅ 10 件 113204 B | anyone: reader |
| P014 | https://drive.google.com/drive/folders/151E1l3qkMOW3ngjMBEDHgp5FzXIYYiVR | ✅ 10 件 113290 B | anyone: reader |
| P015 | https://drive.google.com/drive/folders/1VJgzzucdULCjjnoVPhpVUzTLckot0id0 | ✅ 10 件 113204 B | anyone: reader |
| P016 | https://drive.google.com/drive/folders/1aa7vTpMyvSX-CR_0SYISFQ7kKd3VUAOZ | ✅ 10 件 113290 B | anyone: reader |
| P017 | https://drive.google.com/drive/folders/1L3iJK2sULsS8pKYPh5n1_tnxph5zoDAN | ✅ 10 件 113204 B | anyone: reader |
| P018 | https://drive.google.com/drive/folders/1M1YA4ViSe_lJppdhhdktH2lymFAoNSoa | ✅ 10 件 113290 B | anyone: reader |
| P019 | https://drive.google.com/drive/folders/1cFJqrp8HRfzcOxm6U-5VfSuVo5GLWDeA | ✅ 10 件 113204 B | anyone: reader |
| P020 | https://drive.google.com/drive/folders/1E7e13V0u8axo1wYflYf_LlE9zNZy1M3b | ✅ 10 件 113290 B | anyone: reader |

★ 親フォルダ直下は **ちょうど 15 フォルダ**。同名の重複は無い
（`g1MaterialsUrlForPid_` は `hits.length > 1` で止まるので、重複があれば送信が止まる）。

## ★ 検証のやり方（この回に実際にやったこと）

1. 手元: `manifest.tsv` と `dist/_drive/G1課題文_<ID>/` を **size + sha256** で全 150 件突合（緑）
2. Drive: `search_files` で各フォルダの `fileSize` を取得
3. `verify-drive-upload.py` に通す（欠落・余分・Google 形式への変換をすべて弾く）

⚠️ ★ **byte 一致は同一の証明ではない。** ここで捕まえたのは欠落・混入・上げ忘れ・別人のファイルまで。
中身まで見るなら Drive から落として SHA-256 を突き合わせる（manifest 3 列目にある）。

## ⚠️ 実測で分かった落とし穴

- ★ **削除されたフォルダは `parentId = '<旧ID>'` で空 `{}` を返す**。「アップロード失敗」と誤読しない。
  ★ 親フォルダを引き直して **ID が変わっていないか**を先に見る。
- `search_files` は `mimeType = 'text/html' and (parentId = 'A' or parentId = 'B' …)` で
  **複数フォルダをまとめて引ける**（5 フォルダ 50 件を 1 回で取得できた）。
