# tasklist — mac default features clippy を緑にする

## 手順 1: まず測る
- [x] `rustup show active-toolchain` = `1.98.1-aarch64-apple-darwin (overridden by rust-toolchain.toml)` ★ 期待通り
- [x] `cargo clippy --all-targets -- -D warnings` → ✅ **EXIT=0**（⚠️ 件数は受け入れ条件にしない）

## 手順 2: 出た指摘を直す
- [x] ⚠️ **該当なし** — 指摘 0 件のため**コード変更 0 行**
  - ★ したがって「lint の help を鵜呑みにしない」「浮動小数の加算順序を変えない」
    「`new_without_default` に安易に `impl Default` を足さない」の各注意は**発動しなかった**

## 手順 2.5: ⚠️ 緑が本物であることの立証（★ メモに無いが追加した）
- [x] 強制再解析（全ソース touch）→ `Checking gse-next` を確認・EXIT=0
- [x] ⚠️ 陽性対照を `-D warnings` 付きで実施 → **build.rs で止まり射程不足**（★ 失敗を記録）
- [x] ★ 陽性対照を `-D warnings` **無し**で再実施 → **7/7 ターゲットで検出**・警告総数 7（期待 7）
- [x] 対照の完全復元を `git status --porcelain` 空で確認
- [x] ⚠️ zsh 語分割で対照が空振りし**偽の緑**が出た事象を decisions 決定 4 に記録

## 手順 3: 両スコープで確かめる
- [x] `cargo clippy --all-targets -- -D warnings`（default）→ ✅ EXIT=0
- [x] `cargo clippy --all-targets --features package -- -D warnings`（CI と同じ）→ ✅ EXIT=0・退行なし
- [x] `cargo test --features package --workspace` → ✅ EXIT=0・**11 スイート / 705 件** passed, 0 failed
- [x] `gse-replay --snapshot` → ✅ `OK: 15 snapshots match`
- [x] `emit_schema` vs `schema/current.json` → ✅ **byte-equal**
- [x] ⚠️ `HMM_VERSION` を bump していない（★ ゴールデン byte-equal なので不要）

## 手順 4: CI には足さない
- [x] ⚠️ **CI 未変更**（`.github/workflows/` に触れていない）— ★ F-4 は Windows 側の仕事
- [x] ★ 完了報告に「**mac の default features clippy は exit 0**」を明記する → 本記録で明記

## §3（任意）: F-3 の判断材料
- [x] mac 実測: default **4–5 秒** / `--features package` **6 秒**（⚠️ 増分 **+1〜2 秒**）
- [x] ⚠️ 判断はしない（★ 研究者判断）

## 追加で判明したこと
- [x] ★ `cfg(not(feature = "package"))` が **repo 全体で 0 件** → default は package の**真部分集合**
      ＝ **緑は構造的に保証されていた**（decisions 決定 2）
- [x] ★ `stop-check.sh` が clippy 出力を `>/dev/null 2>&1` で捨てている件をコードで検算（決定 6）

## 記録
- [x] `.steering/20260912-mac-default-clippy-green/`（requirement / design / decisions / tasklist）
- [ ] コミット
- [ ] ⚠️ `/cross-review`（★ **コード変更 0 行なので diff は記録のみ** — 実施要否は研究者判断）
