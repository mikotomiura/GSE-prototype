# design — self-hosted で rust-cache を回さない

## アプローチ

★ **`runner.environment` で「実際に割り当てられたランナー」を見て分岐する。**

```yaml
- uses: Swatinem/rust-cache@v2
  if: ${{ steps.disk_guard.outputs.wiped != 'true' && runner.environment == 'github-hosted' }}
```

### ⚠️ なぜ `matrix.runner` で分岐しないか

★ `matrix.runner` は **`gse-win-selfhosted` という文字列のまま**であり、
`decide-win-runner` が `windows-latest` へフォールバックしても**変わらない**。
⚠️ `matrix.runner` で判定すると、hosted へ落ちた run でもキャッシュが無効化され、
**フォールバック経路のビルドが毎回コールドになる**。
→ ★ `runner.environment` は**割り当て後のランナー上で評価される**ので追随する。

### ★ fail-safe の向き

⚠️ 万一 `runner.environment` が空/未定義でも `'' == 'github-hosted'` は **false**
＝ **キャッシュ無効側に倒れる**。
★ self-hosted（常用経路）ではそれが望む挙動であり、hosted フォールバック（稀）が
キャッシュ利得を失うだけで**壊れはしない**。→ 安全な向きである。

⚠️ ただし「倒れる向きが安全」は「値が正しい」の代わりにならない。
→ ★ **`runner.environment` を run ログに出す step を足し、どちらへ分岐したかを毎回証拠に残す。**

## 変更対象

| 行 | ジョブ | `runs-on` | 変更 | 理由 |
|---|---|---|---|---|
| 312-313 | `check` | self-hosted（win は hosted フォールバック有） | ★ 条件追加 | ⚠️ 今回の timeout の当事者 |
| 516 | `build-macos` | `[self-hosted, gse-mac]` | ★ 条件追加 | ⚠️ rust 側は**元から no-op**（下記の訂正）。実害は npm 側 |
| 415-418 | `build-windows` | `windows-latest` | ★ **触らない** | ★ hosted は失敗コストが小さく、変更する根拠が無い |

### ⚠️★★★ 訂正 — `build-macos` の rust-cache は元から no-op だった

★ **初版の本節は誤っていた**（code-reviewer 指摘・2026-09-02・自分で検算した）。

⚠️ 初版はここに「復元は **2m13s〜8m58s** かかって失敗する」と書いたが、
★ **それは `check` ジョブの実測値であり、`build-macos` のものではなかった。**

★ v0.1.30 のリリース run (33293939800) で `build-macos` を実測すると:

| ステップ | 所要 |
|---|---|
| `Run Swatinem/rust-cache@v2` | **1 秒** |
| `Post Run Swatinem/rust-cache@v2` | **0 秒** |

⚠️ 理由（★ 自分で検算した）:
1. rust-cache の鍵には **job id が入る**（`add-job-id-key: true` が既定）。
   ★ 実測キーは `v0-rust-x86_64-pc-windows-msvc-`**`check`**`-Windows_NT-x64-...`。
2. `build-macos` の `if:` は `startsWith(github.ref, 'refs/tags/v')` **のみ**＝**タグでしか走らない**
   （★ `ruby -ryaml` で実測）。
3. → `save-if: ${{ !startsWith(github.ref, 'refs/tags/v') }}` は**常に false**
   → ⚠️ **本ジョブの鍵は一度も保存されたことがない** → 毎回 1 秒で空振り。

→ ★ **条件を足しても `build-macos` の rust 側の挙動は変わらない。**
   3 か所で同じ規則にし、将来 hosted へ戻したとき自動復帰させるために残す。
→ ⚠️ **本ジョブの実害は rust 側ではなく npm 側にある**（次節）。

⚠️ ★ **なぜ間違えたか**: `requirement.md` の表（`check` の値）を `build-macos` の
根拠として使った。★ **自分で `build-macos` を実測しておきながら**（design.md の
「キー不一致で miss・実質無効」という記述がその痕跡）、コメントには別ジョブの数字を書いた。
→ ⚠️ memory `name-lookup-only-works-within-one-source` の同型（★ **どちら側を見ているかを問う**）。

### ⚠️★★★ 調査中に見つかった、より実害の大きい同型（★ npm キャッシュ）

★ `build-macos` は `actions/setup-node@v4` を `cache: npm` で使っている（L576 付近）。
⚠️ **これも self-hosted で走る**。v0.1.30 のリリース run (33293939800) を実測した内訳:

| ステップ | 所要 |
|---|---|
| `Build Tauri app` | 6m15s |
| ⚠️ **`Post Run actions/setup-node@v4`** | **10m39s** ← ★ 最大 |
| `Run Swatinem/rust-cache@v2` | 0m01s（★ キー不一致で miss・実質無効） |
| ジョブ全体 | 17m54s / 上限 40m |

★ **リリースビルドの所要時間の半分以上が 1097MB の npm キャッシュ転送**だった。
⚠️ 09-02 に実測した転送速度（0.0〜0.6 MB/s）では 1097MB は **30 分〜数時間**かかる。
→ ★ `timeout-minutes: 40` を確実に超え、**dmg が 1 つも作れずリリースが止まる**。

⚠️ **これは引き継ぎメモ §1b 手順 3（v0.1.31 のタグ push）を直撃する**ので同じ PR で塞ぐ。

★ 実装: `cache:` は step の `if:` では切れない（入力値なので）→ **空文字を渡す**。
```yaml
cache: ${{ runner.environment == 'github-hosted' && 'npm' || '' }}
```
⚠️ `actions/setup-node` は `cache` が falsy ならキャッシュ処理そのものを行わない。
★ `frontend-check` (ubuntu-latest) と `build-windows` (windows-latest) は**触らない**。

## ⚠️ 変更しないもの（★ 根拠を書く）

- ★ `timeout-minutes`（30 / 40）は**据え置く**。
  ⚠️ 原因は「実作業が 30 分に収まらないこと」ではなく「無意味な転送が 20 分以上食うこと」。
  ★ 上げると**症状だけ隠して原因が残る**（10GB 超過も解消しない）。
- ★ disk-guard の `wiped != 'true'` 条件は**残す**。
  ⚠️ hosted 経路では依然として意味があり、条件は AND なので self-hosted の挙動は変わらない。
- ★ `build-windows` (L415) は**無条件のまま**。⚠️ hosted なのでキャッシュが本当に効く。

## ⚠️ 退行の検討

| 懸念 | 判定 |
|---|---|
| disk-guard が `target` を全削除した直後、キャッシュが無くコールドになる | ★ **退行しない**。⚠️ 現状も wipe 時は `if:` でキャッシュ復元ごと飛ばしている（L300-311 の注記）。条件が 1 つ増えるだけ |
| self-hosted のビルドが遅くなる | ★ **ならない**。⚠️ 09-02 は復元が全 job で失敗したのに build は 1m48s〜3m06s だった＝速さの出所は永続 `target/`（2.1GB・09-02 付 `.rlib` 237 個を実測） |
| hosted フォールバック時にキャッシュを失う | ⚠️ ★ **初回は失う**（訂正）。条件式は正しく hosted 側で真になるが、`...-check-...` の鍵を**書いていたのは self-hosted の run** であり、その書き手が消える。さらに rust 系キャッシュは 09-02 に全削除済み。→ ★ **初回だけコールド**（hosted run 自身は `save-if` 既定 true で保存するので 2 回目以降は温まる）。⚠️ **その初回が 30 分に収まるかは未測定**（参考: hosted の cold `tauri build --no-bundle` 12m09s / tools 9m42s）。★ 発火は G-GEAR offline 時だけなので許容する |
| ランナーを新調したとき初回がコールド | ⚠️ **起きる**。★ ただし 1 回だけであり、許容する |

## テスト戦略

⚠️ **手元では検証できない**（★ memory `windows-only-code-needs-ci`：この Mac では
Windows レグが 1 行もコンパイルされない）。→ ★ **CI 実行そのものが検証**である。

1. ★ YAML として妥当か（`python3 -c "import yaml; yaml.safe_load(...)"`）
2. ★ PR を出し、**check (win / mac) が両方緑**になること
3. ⚠️ **job 全体が 10 分未満**であること（★ 現状 24〜31 分）
4. ⚠️ **`Post Run Swatinem/rust-cache@v2` が step 一覧に存在しない**こと
   （★ 「速くなった」ではなく「当のステップが消えた」を根拠にする）
5. ★ 追加した echo step のログに `runner.environment = self-hosted` が出ること
   （⚠️ 条件が意図した側に分岐した**直接の証拠**）

## 併せて行う外界の操作（★ 研究者承認済み・2026-09-02）

- ⚠️ **Actions キャッシュの rust 系エントリを削除**（合計 10.56GB → 上限 10GB 超過の解消）。
  ★ `node-cache-*` は残す（⚠️ `frontend-check` が実際に `Cache restored successfully` を
  出しているのを実測済み＝**hosted なので本当に効いている**）。
