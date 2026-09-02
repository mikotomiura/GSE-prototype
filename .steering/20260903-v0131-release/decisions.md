# decisions — v0.1.31 のリリースと配布物の検算

## D-1 ⚠️★★★ 引き継ぎメモ §1b 手順 4 の検査は**壊れている**（★ 実測で判明）

### 何が書かれていたか

`.steering/_handoff/next-session-prompt-g1-o1-gas-deployment.md` §1b 手順 4:

```bash
for p in o1.mode label_row_allowed GSE_O1_MODE; do
  printf '%-22s %s\n' "$p" "$(LC_ALL=C grep -ac -- "$p" "$BIN")"; done
```
> ⚠️ **`label_row_allowed` が 0 なら、また古いものを配ろうとしている。**

### ⚠️ 実測（2026-09-03・新旧の dmg を両方ダウンロードして対照）

| 検査 | v0.1.30（旧） | v0.1.31（新） | 判定 |
|---|---|---|---|
| `gse_next_lib`（陽性対照） | 11 | 12 | ★ grep は機能している |
| `o1.mode` | 4 | **5** | ★ 判別できる |
| `GSE_O1_MODE` | 1 | 1 | ⚠️ 判別できない（両方に在る） |
| ⚠️ **`label_row_allowed`** | **0** | **0** | ⚠️★★★ **両方 0 ＝ 判定に使えない** |
| `記録のみ`（新の文言） | 0 | 0 | ⚠️ 後述 |
| `較正モード`（**陰性対照**） | 0 | 0 | ⚠️★ **対照も 0 ＝ 検査が成立していない** |
| バイナリの同一性 | — | ★ `cmp` で**異なる** | ★ 更新はされている |

### ★ なぜ壊れているか（★ 2 つの独立した理由）

1. ⚠️ **`label_row_allowed` は Rust の関数名**（`src-tauri/src/o1.rs:211` の `pub fn`）である。
   ★ release ビルドでインライン化・シンボル除去されるので、**機能が入っていても 0 件**になる。
   ⚠️ メモの「HEAD は 6 件」は**ソースの grep 結果**であって、バイナリの値ではなかった。
   → ★ **修正が確実に入っている v0.1.31 でも 0 件**である。つまりこの規則は
   **正しいバイナリを必ず「古い」と誤断する**。

2. ⚠️★★ **`2d83304`（O1 で出てはいけない UI を塞ぐ修正）の本体は `Dashboard.tsx`＝フロントエンド**である。
   ★ Tauri はフロントを `gse-next` バイナリに**埋め込む**が、**圧縮されている**。
   ⚠️ 実測: `index-` = 2 件 / `stylesheet` = 9 件（HTML シェルは残る）に対し、
   `calibration-notice-badge` = **0 件**、`\uXXXX` エスケープ形でも **0 件**。
   → ★ **JS/CSS アセットは grep では原理的に検証できない。**
   ⚠️ したがって「バイナリを grep して UI 修正の有無を判定する」ことは**できない**。

### ★ 代わりに何で確かめたか（★ 3 段）

1. **来歴** — リリース run `33630803294` の `head_sha` = `db08211`。
   ⚠️ v0.1.29 の失敗形態（★ ファイルが 0 バイト）を潰すため、**その commit の中身を実測**した:
   - `src-tauri/src/o1.rs` = **38,903 bytes** / `label_row_allowed` **6 件**
   - `src/components/Dashboard.tsx` = **33,342 bytes** / `記録のみ` **1 件** / `ふだんどおり…` **1 件**
   - `git merge-base --is-ancestor` で `2d83304` / `cddbe3a` / `e69f7ff` の**3 つとも祖先**と確認
2. **成果物の差** — v0.1.30 と v0.1.31 のバイナリは `cmp` で**異なり**、
   サイズ 12,454,640 → **12,475,328**（+20,688）、`o1.mode` 4 → **5**。
3. **zip の同一性** — 配布 zip 内の `gse-next` が**リリース dmg のものと sha256 まで一致**し、
   ★ **v0.1.30 のものとは異なる**ことを確認した。

### ⚠️ それでも残る限界（★ 正直に書く）

⚠️ **フロントエンドの UI 修正が実際に効いているかは、バイナリからは確認できていない。**
★ 確かめる唯一の手段は**アプリを起動して画面を見ること**である
（→ 引き継ぎメモ §6 の「まだ済んでいないもの」2 番と同じ経路）。
→ ★ **研究者の初回起動時に「記録のみ」バッジと O1 用の説明文が出ることを目視すること。**
⚠️ 「バイナリ検算が通ったから UI も正しい」とは**書かない**。

### ★ 使える検査へ差し替える（★ 次のセッションのために）

⚠️ `label_row_allowed` を**使わない**。★ 代わりに:

```bash
# ① 来歴（★ ファイルが空でないことまで見る）
SHA=$(gh api repos/<owner>/<repo>/actions/runs/<run_id> -q .head_sha)
git cat-file -s "${SHA}:src-tauri/src/o1.rs"          # ★ 0 バイトでないこと
git show "${SHA}:src/components/Dashboard.tsx" | grep -c 記録のみ   # ★ 1 以上

# ② 成果物（★ 陽性対照つき・旧版との対照つき）
for p in o1.mode GSE_O1_MODE; do LC_ALL=C grep -ac -- "$p" "$BIN"; done
LC_ALL=C grep -ac gse_next_lib "$BIN"      # ★ 陽性対照（0 なら測定器が壊れている）
cmp -s "$OLD_BIN" "$NEW_BIN"               # ★ 旧版と同一なら赤

# ③ ⚠️ UI は目視でしか確かめられない
```

★ なお `make-common-app-zip.sh` **自身の検査は健全**である —— 実測すると
`gse-next の実体に O1 あり ✅ (o1.mode / gse_o1_)` と、
⚠️ **シンボルではなく文字列リテラルを見ている**。→ ★ 壊れているのは**引き継ぎメモだけ**。

## D-2 ★ v0.1.31 のリリースは成功した

| | 値 |
|---|---|
| タグ | `v0.1.31` → `db08211` |
| run | `33630803294` → **success** |
| 成果物 | `gse-next_0.1.31_aarch64.dmg` 9MB / `gse-next.exe` 10MB / `gse-submit.exe` 5MB / `gse-unpack(.exe)` |

### ⚠️★★ PR #145（キャッシュ無効化）の効果が**ここで初めて実証された**

★ `build-macos` は**タグ限定ジョブ**なので PR #145 の CI では一度も発火していなかった。
→ ★ 本 run が**本命の検証点**であり、実測はこうなった:

| ステップ | v0.1.30 | v0.1.31 |
|---|---|---|
| `Run Swatinem/rust-cache@v2` | 1s | ★ **skipped** |
| `Post Run Swatinem/rust-cache@v2` | 0s | ★ **step ごと消滅** |
| `Run actions/setup-node@v4` | 2s | 0s |
| ⚠️ **`Post Run actions/setup-node@v4`** | ⚠️ **10m39s** | ★ **0s** |
| `Build Tauri app` | 6m15s | 6m10s |
| **ジョブ全体** | **17m54s** | ★ **6m37s** |

★ ⚠️ **リリースビルドの所要時間の 6 割を占めていた npm キャッシュ転送が消えた。**

## D-3 ★ 配布 zip を作り直した（⚠️ Drive は触っていない）

```bash
./make-common-app-zip.sh --mode o1 --tag v0.1.31 --config ../../Form_O1/o1_submit.json
```

★ selftest **19 通過 / 0 失敗**、本体も全項目 ✅ で完走した。

⚠️ **G1 が巻き添えで作り直されていないこと**を sha256 で対照した:

| ファイル | 作成前 sha | 作成後 sha | 判定 |
|---|---|---|---|
| `G1_実施用_Windows.zip` | `e043c12f8f12704c` | `e043c12f8f12704c` | ★ **不変**（正しい） |
| `G1_実施用_macOS.zip` | `89c0fe4ec742a291` | `89c0fe4ec742a291` | ★ **不変**（正しい） |
| `O1_実施用_Windows.zip` | `b3ebccd8cbe551b9` | `60185f3ab244201e` | ★ 更新 |
| `O1_実施用_macOS.zip` | `669e8b9ec28774d2` | `6ebd00c1fc1bcdc9` | ★ 更新 |

⚠️ ★ **Drive の差し替えは行っていない**（★ 研究者の指示で「zip 作成まで」）。
→ ★ 古い zip の削除を伴い**元に戻せない**ので、別途承認を得ること。

## D-4 ★ 配布ゲートの状態

`bash scripts/check-o1-release-readiness.sh` → **通過 18 件 / 未達 1 件**（⚠️ 実施前は 17 / 2）。

- ★ 消えた赤: 「リリースタグ v0.1.30 は古い」→ **`✅ O1 実装を含むリリースタグがある（v0.1.31）`**
- ⚠️ 残る赤: **送信 timeout が未実測**（★ 引き継ぎメモ §7・`/reimagine` 規模の設計変更が要る）
