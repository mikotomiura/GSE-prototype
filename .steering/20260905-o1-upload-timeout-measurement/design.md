# design — 送信 timeout の実測

## 測り方

★ `reconcile.rs::HttpUploader` と**同じ本文**（`{secret, name, b64}` の JSON を POST）を
python から送り、**client 実時間**と受け口が返す **`elapsed_ms`**（★ Drive 保存を含む）を取る。

⚠️★★ **中身は合成ランダムバイト**にする:
- ★ 測りたいのは**転送時間と Drive 保存時間**で、中身は無関係
- ⚠️ ランダムバイトは**非圧縮性なので最悪値側**を測れる
- ★ 被験者データを一切含まない
- ★ 名前を `TIMEOUTTEST_o1day99_...` にして後から見分けられるようにする

## ⚠️ 先に計測器を検算する（★ 本測の前に）

| 対照 | ★ 期待 |
|---|---|
| ⚠️ 名前が規則外 | `bad name` で弾かれる（＝ `ok:true` が空虚でない証拠） |
| ★ 小さいサイズ | `ok:true` ＋ `elapsed_ms` が返る |

## ★ サイズの決め方

⚠️ 1 点だけ測って外挿しない。★ **崖を探す**ために段階的に上げる
（1 → 4 → 12 → 20 → 28 → 36 → 40 → 47 MB）。

## ⚠️ 採用値の制約（★ 測る前から分かっていること）

★ `reconcile.rs` に `LOCK_STALE_AFTER >= timeout × 10` の不変条件がテストで固定されている。
⚠️ `LOCK_STALE_AFTER = 3600 s` なので、**timeout は 360 s を超えられない**。
→ ★ 実測がそれを超えたら、⚠️ **timeout ではなく `LOCK_STALE_AFTER` の側を議論する**。

## テスト戦略

- ★ `cargo test --features package --workspace`（⚠️ `--features package` を落とすと 34 件走らない）
- ⚠️ **陽性対照**: 不変条件を 600 s にすると `the_stale_threshold_is_longer_than_a_worst_case_run`
  が赤になることを確かめる（★ 「600 秒だと壊れる」という主張の実証）
- ★ ゲート `check-o1-release-readiness.sh` が緑になること
