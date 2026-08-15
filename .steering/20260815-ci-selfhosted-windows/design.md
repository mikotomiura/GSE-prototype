# 設計 — Windows self-hosted ＋ 30 秒フォールバック

## 実装アプローチ

★ **前段に `decide-win-runner` を置き、`check` の `runs-on` を動的に解決する。**

```
decide-win-runner (ubuntu-latest / timeout 5m)
   └─ gh api repos/{owner}/{repo}/actions/runners を 5s × 6 = 最大 30s ポーリング
        ├─ gse-win が status=online → outputs.runs_on = ["self-hosted","gse-win"]
        └─ それ以外（未登録 / offline / API エラー / PAT 未設定）→ ["windows-latest"]
                                    ↓ needs
check (matrix 2 本)
   ├─ gse-mac-selfhosted → ["self-hosted","gse-mac"]   （★ 従来どおり固定）
   └─ gse-win-selfhosted → fromJSON(needs.decide-win-runner.outputs.runs_on)
```

### ★ 設計上の核（★ ここを外すと意味が無い）

1. ★★★ **失敗側は必ず hosted。** PAT 未設定・API エラー・タイムアウトのいずれでも
   `["windows-latest"]` を返す。⚠️ **絶対にキューへ滞留させない。**
2. ★ **ポーリングにする理由**: ★ 単発チェックだと「今まさに起き上がっている最中」を拾えない。
   ⚠️ **ただし 30 秒で起き切らなければ諦める**（★ 研究者の指示どおり）。
3. ★ **出力は常に JSON 配列**（`["windows-latest"]` も配列）。★ `fromJSON` の戻り型を揃え、
   `runs-on` の解釈ぶれを無くす。

### ⚠️ 却下した案

| 案 | 却下理由 |
|---|---|
| ★ 短い `timeout-minutes` を付けたプローブジョブ | ⚠️★★★ **`timeout-minutes` はキュー待ちに効かない**（実測）。★ プローブ自体が滞留する |
| `continue-on-error: true` の self-hosted ジョブ ＋ 後段 hosted | ⚠️ **offline 時は「失敗」ではなく「滞留」**なので発火しない |
| `if: failure()` で hosted に再実行 | ⚠️ **本物のテスト失敗でも再実行され、Windows は 2 倍課金** → ★ **目的（課金削減）と衝突** |
| repository variable による手動切替 | ⚠️ **落とす前にフラグを戻す運用が要り、忘れると 24 時間滞留**（★ 研究者が自動側を選択） |
| `build-windows` も self-hosted へ | ⚠️ タグ時のみ＝恒常支出でない。★ **途中で落ちるとリリース成果物が壊れる** |

## 変更対象

### 修正するファイル
- `.github/workflows/ci.yml`
  - ★ `decide-win-runner` ジョブを**新規追加**
  - ★ `check` に `needs: decide-win-runner` を追加、matrix の Windows 側を
    `windows-latest` → `gse-win-selfhosted` に変更、`runs-on` を動的解決へ
  - ★ 判断の根拠・**救えない範囲**・PAT の要否をコメントとして本体に記述
  - ★ `build-windows` に「hosted のまま残す理由」を明記

### 新規作成するファイル
- ★ なし（★ ランナー本体は repo 外に置く）

## 影響範囲

| 影響先 | 内容 |
|---|---|
| ★ `check` の mac 側 | ⚠️ **`needs` により decide の完了（最大 30 秒）を待つ**。★ 両 OS を 1 matrix に保つための代償 |
| ★ `frontend-check` / `build-*` / `release` | ★ **影響なし**（`needs` を張っていない） |
| ★ 手動発火（`workflow_dispatch`） | ★ **影響なし**（`decide` / `check` とも `if` で除外済み） |
| ⚠️ secret | ★ **`RUNNER_STATUS_TOKEN` が増える**（★ fine-grained・当 repo のみ・`Administration: Read`・期限付き） |

## 既存パターンとの整合性

- ★ mac 側の `runs-on: ${{ ... && fromJSON('["self-hosted","gse-mac"]') || ... }}` という
  **三項式の書き方をそのまま踏襲**した。
- ⚠️ **matrix が 2 本である前提の三項式**になっている。★ 3 本目を足すときは書き換えが要る旨をコメントに明記。

## テスト戦略

★ **本セッションで 3 経路をローカル実測済み**（★ workflow の `run:` を YAML から取り出して直接実行）:

| 経路 | 期待 | 実測 |
|---|---|---|
| ランナー online | self-hosted | ✅ **attempt 1 で即決**（★ `gse-win` は未登録なので、実在する `gse-mac` にラベルを差し替えて検算） |
| 未登録 / offline | 30 秒後に hosted | ✅ `["windows-latest"]` |
| PAT 未設定 | **即** hosted | ✅ ポーリングせず即決 |

★ 静的検査: **YAML parse OK** ／ **`bash -n` rc=0** ／ `decide` と `check` の `if` が一致。

⚠️ **未実施（★ 研究者の手が要る）**:
- [ ] 実 PR での self-hosted 側の実走
- [ ] ★ **ランナーを落とした状態での PR**（★ **これが本命の検査**）

## ロールバック計画

- ★ `git revert` 1 回で `ci.yml` は戻る（★ 1 コミットに閉じた）。
- ★ **ランナーを止めるだけでも安全側に倒れる**（★ 30 秒後に hosted へ落ちるため CI は止まらない）。
- ⚠️ **secret は revert では消えない** → 不要になったら GitHub 側で削除する。
- ★ ランナーの登録解除は `.\config.cmd remove --token <REMOVE_TOKEN>`。
