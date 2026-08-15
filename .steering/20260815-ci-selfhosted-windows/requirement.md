# Windows の CI を self-hosted へ移す（★ 30 秒で hosted へ戻すフォールバック付き）

## 背景

★ **研究者の指示（原文・書き換えない）**:

> 「Macで実施したSelf-hostedをこっちのwindowsでもやらない？
> macとは違ってwindowsのほうではたまにシャットダウンしてるから、30秒程度ずっと応答なかったら
> 従来に戻る感じの条件分岐も追加しての実施で」
> 「てかここでのself-hostedfはこのG-GEARですよ.surfaceはもうほとんど使ってない」

- ★ **目的 = 課金・無料枠を浮かせること**（研究者判断）。★ Windows は **2 倍課金**で、
  毎 push で走る `check` が恒常的な支出になっていた。
- ★ macOS は **2026-08-01 に self-hosted へ移行済み**（`gse-mac` / `macbook-air-m-arm64`・online）。
- ⚠️ `ci.yml:41-43`（改訂前）は逐語で **「self-hosted はランナー offline 時にジョブがキューへ滞留する
  （hosted への自動フォールバックは無い）」**と書いており、★ **これが研究者の懸念そのもの**。

## ゴール

★ **Windows の `check` ジョブを self-hosted（`gse-win`）で走らせ、ランナーが落ちていたら
30 秒以内に `windows-latest`（従来）へ自動で戻す。**

## スコープ

### 含むもの
- `.github/workflows/ci.yml` — `decide-win-runner` ジョブの追加と `check` の `runs-on` 動的解決
- ★ G-GEAR への `gse-win` ランナー登録（⚠️ **要 admin・研究者の手**）
- ★ secret `RUNNER_STATUS_TOKEN` の設定（⚠️ **要 PAT 作成・研究者の手**）

### 含まないもの
- ⚠️ **`build-windows` の移行**（★ タグ時のみ＝恒常支出でない／途中で落ちるとリリースが壊れる）
- ⚠️ **実行中に落ちた場合の救済**（★ `if: failure()` の再実行は**課金削減という目的と衝突**するため不採用）
- ⚠️ **`CARGO_BUILD_JOBS` の引き上げ**（★ 現在 `2`。G-GEAR は 16 論理コアなので余地があるが、
  workflow 全体の env なので **mac 側にも効いてしまう**。★ 別タスク）

## 受け入れ条件

- [x] ★ `ci.yml` が YAML として parse でき、`bash -n` が通る
- [x] ★ **ランナー online → self-hosted を返す**（実測: attempt 1 で即決）
- [x] ★ **未登録/offline → 30 秒後に hosted へ落ちる**（実測）
- [x] ★ **PAT 未設定 → 即 hosted（fail-safe・ポーリングしない）**（実測）
- [ ] ⚠️ G-GEAR に `gse-win` ラベルでランナーを登録し、`status=online` になる
- [ ] ⚠️ secret `RUNNER_STATUS_TOKEN` を設定する
- [ ] ⚠️ **main への PR で実際に self-hosted 側が拾うことを確認する**
- [ ] ⚠️ **ランナーを落とした状態で PR を出し、30 秒後に hosted へ落ちることを確認する**

## ⚠️ 実測した制約（★ 設計の前提。測り直さない）

| 検証項目 | 実測（2026-08-15） |
|---|---|
| `timeout-minutes` はキュー待ちに効くか | ⚠️★★★ **効かない**（★ ジョブの**実行時間のみ**） |
| self-hosted が offline のときジョブは | ⚠️★★★ **24〜48 時間キューに滞留してからキャンセル** |
| `GITHUB_TOKEN` でランナー一覧を取れるか | ⚠️ **取れない**（★ 要 PAT / GitHub App の `Administration` 権限） |
| ★ 現ブランチで CI は発火するか | ⚠️★★★ **しない**。`push: [main, "feature/*"]` に `docs/*` は含まれない → ★ **検証は main への PR 経由**（`pull_request: [main]`） |
| repo の可視性 | ★ **PRIVATE** → ⚠️ fork PR から self-hosted 上で任意コードが走るリスクは構造的に小さい |
| ランナー版 | ★ **v2.336.0**（★ mac 側と同版） |
| G-GEAR | ★ **MS-7E66 / Ryzen 7 9700X (8C/16T) / 31.1 GB** |

## 関連ドキュメント

- `.github/workflows/ci.yml`（★ 判断の根拠はすべてコメントとして本体に書いた）
- `.steering/20260806-g1-followups-and-windows-verification/decisions.md`
  （★ **`workflow_dispatch` はデフォルトブランチに無いと発火できない**という既知の落とし穴）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: ★ 実現手段は**実測で 1 つに絞られた**（★ `timeout-minutes` が効かず `GITHUB_TOKEN` で
  ランナーを読めない以上、**前段ジョブ ＋ PAT** 以外に自動フォールバックの手が無い）。★ 代替案の再生成は不要。
