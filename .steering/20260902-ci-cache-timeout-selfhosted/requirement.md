# requirement — self-hosted の rust-cache が check job を timeout させる

## 背景

`.steering/_handoff/next-session-prompt-g1-o1-gas-deployment.md` §1b の手順 1 は
「PR #143 をマージ」だが、**#143 の Windows check が赤**でマージ経路が塞がっている。
研究者からの申告も「#143 は windows の self-hosted で error を起こした」。

⚠️ しかし **コード起因ではなかった**。以下は 2026-09-02 に GitHub Actions API と
run ログから実測した値である（★ 引き継ぎメモの記述ではなく一次資料）。

### 実測 — 3 job の内訳

| | #143 win | #144 mac | #144 win |
|---|---|---|---|
| run / job | 33585179172 | 33585489930 | 33585489930 |
| 実作業 (build+test+snapshot+schema) | **3m33s** | **6m00s** | **3m45s** |
| cache 復元 (`Run Swatinem/rust-cache@v2`) | 8m58s → **失敗** | 2m13s → **失敗** | 2m36s → **失敗** |
| cache 保存 (`Post Run Swatinem/rust-cache@v2`) | **16m58s → cancelled** | **21m27s → cancelled** | 16m14s (完走) |
| job 全体 | 31m20s | 31m11s | 24m44s |
| conclusion | `cancelled` | `cancelled` | `success` |

★ **実作業ステップは 3 job すべてで全 success**（build / test --features package /
snapshot regression / schema drift）。⚠️ 落ちたのは post ステップのキャッシュ保存だけ。

### 機構

1. `Swatinem/rust-cache@v2` が `Cache hit for: v0-rust-...` を出す
2. ⚠️ ダウンロードが **0.0〜0.6 MB/s** に落ち、578MB を引き切れず **`No cache found.`** で諦める
3. → 復元失敗なので rust-cache は「保存が必要」と判断する
4. ⚠️ **578〜730MB を 0.0〜0.1 MB/s でアップロード**し始め、16〜21 分かかる
5. `timeout-minutes: 30` (`ci.yml:265`) に当たり **job ごと cancel**
6. ⚠️ `gh pr checks` はこれを **`fail` と表示する**（API 上の実体は `cancelled`）

★ **#143 と #144(win) の明暗を分けたのは復元にかかった時間の差だけ**であり、コード差ではない。
⚠️ 緑赤がコイントスになっている。

### 併せて測れた事実

- ⚠️ **リポジトリの Actions キャッシュ合計 10.56 GB** — GitHub の上限 10 GB 超過。
  同一キー `v0-rust-x86_64-pc-windows-msvc-check-Windows_NT-x64-683d8049-75d23cf5` の
  ~700MB エントリが **6 本以上**重複している（ブランチごとにスコープされるため）。
- ⚠️ **self-hosted では rust-cache が構造的に不要** — mac ランナーは研究者の Mac 自身
  (`~/actions-runner`) で、`src-tauri/target` 2.1GB と `~/.cargo/registry` 392MB が
  run 間で**永続する**（09-02 付の `.rlib` を 237 個確認）。
  ★ 09-02 は復元が全 job で失敗したのに `cargo build` が 1m48s〜3m06s で終わっており、
  **速さの出所はキャッシュではなく永続 workspace** であることの裏づけになっている。
  ★ `ci.yml` 自身も L275-276 で「self-hosted は workspace が永続する」と書いている。

### ⚠️ 訂正した自分の見立て

★ 当初「self-hosted でキャッシュは一度も機能していない」と考えたが、**誤り**である。
⚠️ **08-30 / 08-31 の run では `Cache restored successfully` が出ている**（実測）。
→ ★ 壊れたのは 2026-09-02 であり、引き金は**転送速度の低下**である
（2 台のランナーが同一回線で同時に ~700MB を送っている時間帯と一致する）。
→ ★ したがって「キャッシュは常に無意味だった」ではなく
**「self-hosted では利得が永続 workspace と重複しており、失敗時のコストだけが残る」**が正しい。

## ゴール

1. check job が転送速度に左右されず、**実作業時間（4〜6 分）で完結する**こと。
2. PR #143 / #144 のマージ経路が開くこと。
3. ⚠️ hosted フォールバック経路（`decide-win-runner` が `windows-latest` を選ぶ場合）の
   キャッシュ利得を**壊さない**こと。

## 受け入れ条件

- [ ] `ci.yml` の rust-cache が self-hosted で走らず、hosted では走る
- [ ] 本 PR の check (win / mac) が **両方緑**で、job 全体が **10 分未満**
- [ ] `Post Run Swatinem/rust-cache@v2` が self-hosted の job に**存在しない**
- [ ] Actions キャッシュ合計が 10 GB を下回る
- [ ] ⚠️ 変更が **hosted 経路のキャッシュを消していない**ことを条件式から示せる

## 非ゴール

- ⚠️ ランナー機の回線速度そのものの改善（★ 本 PR の範囲外）
- ⚠️ `cargo-sweep` の実機導入（引き継ぎメモ §5-7・別件）
- ⚠️ `main` のブランチ保護（引き継ぎメモ §5-4・別件）
