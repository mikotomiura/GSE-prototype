# O1 送信 timeout の実測記録票（★ ゲートが読む）

> ⚠️★★★ **このファイルはゲート `scripts/check-o1-release-readiness.sh` が機械で読む。**
> ★ 下の「実測結果」の欄は**書式ごと**検査される。★ 見出しや太字を崩さないこと。

## なぜこの票があるか

⚠️ 旧版のゲートは `grep from_secs(180)` **ただ 1 本**だった。
→ ★ **数字を書き換えるだけで緑になった**。⚠️ 実測しないまま緑にできる検査は、
本リポジトリがいちばん嫌っている「**見えないまま緑**」を**ゲート自身**に作る。

→ ★ いまのゲートは **(a) この票が埋まっている** かつ **(b) `reconcile.rs` の
`from_secs(180)` が消えている** の**両方**でだけ緑になる。
⚠️ 片方だけでは緑にならないことを `--selftest` が陽性対照つきで確かめている。

## 何を測るのか（★ `Form_G1/GSE_O1_Submit.gs` 配備手順 8）

⚠️★★ **デプロイ済みの受け口が要る**（→ B-1）。★ 手順:

1. 受け口（`doPost`）をデプロイし、`checkSubmitConfig()` が緑であることを確かめる。
2. **1 日ぶんの実サイズ**の `.age` を用意する（★ 実測の目安 18MB → base64 で約 24MB）。
   ⚠️ 小さいファイルで測らない。★ 測りたいのは**上限に近い側**の挙動である。
3. 端末から実際に送り、**送信開始から `doPost` の応答が返るまで**を測る。
   ⚠️★★★ **Drive への保存時間を含めること。**
   ★ 既存の実測（`.steering/20260806-g1-auto-submit-on-block-end/gas-measurements.md`・
   300KB / 1.45s ≒ 207 KB/s）は **Drive 保存を含んでいない**ので、そのまま外挿しない。
4. ⚠️ 受け口の上限は `MAX_BYTES = 48 MB`。★ **上限いっぱいでも通るか**を別に確かめる
   （★ base64 64MB 相当。⚠️ 現行の 180 秒では確実に足りない見積もりである）。

## 実測結果（★ ゲートが読む欄。⚠️ 書式を変えない）

<!-- gate:o1-upload-timeout -->
- 状態: **未実施**
- 実測日: **（未記入）**
- 送信バイト数 (base64 後): **（未記入）**
- 所要時間 (Drive 保存を含む): **（未記入）**
- 実効スループット: **（未記入）**
- 採用した timeout: **（未記入）**

### 記入例（★ そのまま貼らない。実測した値を入れる）

⚠️ ★ 以下は **2 文字下げてある**。★ ゲートが読むのは上の `<!-- gate:o1-upload-timeout -->`
直後のブロックだけだが、⚠️ 例が誤って拾われないよう**書式でも二重に外して**ある。

```
  - 状態: **実測済み**
  - 実測日: **2026-09-01**
  - 送信バイト数 (base64 後): **24 MB**
  - 所要時間 (Drive 保存を含む): **210 秒**
  - 実効スループット: **117 KB/s**
  - 採用した timeout: **固定 900 秒（★ 48MB 上限でも 2 倍の余裕を持たせる）**
```

## 測ったあとにやること

1. ★ 上の欄を埋める（⚠️ 「状態」を **実測済み** にする）。
2. ★ `src-tauri/src/reconcile.rs` の `HttpUploader` の timeout を、**採用した timeout** に直す。
   ⚠️ 固定値にするかサイズ比例にするかも、ここに書いた根拠で決める。
3. `bash scripts/check-o1-release-readiness.sh` が緑になることを確かめる。
4. ⚠️ 変更したら `cd src-tauri && cargo test --features package --workspace`
   （★ `--features package` を落とすと **34 件**が走らない —— 実測 2026-08-28:
   `reconcile.rs` の 25 件 ＋ `packaging.rs` の 9 件。★ 全体は 528 → 563 件になる）。

## 関連

- `Form_G1/GSE_O1_Submit.gs`（★ 受け口・`MAX_BYTES = 48 MB`）
- `src-tauri/src/reconcile.rs`（★ 送信側・現在は `from_secs(180)` 固定）
- `.steering/20260806-g1-auto-submit-on-block-end/gas-measurements.md`（★ 旧実測・Drive 保存を含まない）
- `.steering/20260828-o1-gate-closeout-and-deployment/design.md`
