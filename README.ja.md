<div align="center">

# 🧠 GSE — Generative Struggle Engine

**打鍵のしかたから、作業状態と「介入すべきタイミング」を推定する — プライバシー保護型 HCI。**

GSE はあなたの脳内を読みません。読むのは*キーストローク動態*だけ。そこから、
そっと促す Nudge が「今、本当に役立つか」と、「今は黙っているべきか」を判断します。

> **現況:** 稼働している介入は **Nudge のみ**です。全画面の Wall と Monk Mode は
> **2026-08 に削除しました**（[ADR-015](docs/adr/ADR-015-wall-removal.md)）。
> Physical Anchor は**設計済み・未実装**です
> （[ADR-017](docs/adr/ADR-017-expression-channel-boundary.md)）。

[![CI / Release](https://github.com/mikotomiura/GSE-prototype/actions/workflows/ci.yml/badge.svg)](https://github.com/mikotomiura/GSE-prototype/actions/workflows/ci.yml)
![Platform](https://img.shields.io/badge/platform-Windows%2011%20·%20macOS-2563EB)
![Tauri](https://img.shields.io/badge/Tauri-2.0-24C8DB?logo=tauri&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-1.77+-CE412B?logo=rust&logoColor=white)
![License](https://img.shields.io/badge/license-Research%20Prototype-8B8B8B)

[🇺🇸 English README](README.md) · [📐 設計の変遷](docs/design-history.ja.md) · [📥 ダウンロード](https://github.com/mikotomiura/GSE-prototype/releases)

</div>

---

## なぜ GSE か

ライター・プログラマー・知識労働者は、**滑らかな出力**・**有用な停止**・**非生産的なループ**を
絶えず行き来します。GSE はこれらを — 直接観測できる脳内状態ではなく — 作業レベルの*行動パターン*
として扱い、**生産的苦闘**を中断せずに守ります。

鍵は、2 つの問いを切り分けることです。

| 問い | 名称 | シグナル |
|---|---|---|
| *今、介入は役立ちそうか?* | **Need（必要性）** | キーストローク特徴量から得る HMM `p_stuck` |
| *今は中断コストの低い瞬間か?* | **Opportunity（好機）** | idle・post-burst pause・cooldown・daily cap・recent dismiss |

**Need × Opportunity** の両方が揃ったときだけ GSE は動きます — `none` / `nudge` / `defer`。
`defer`（「いま苦闘の最中だから割り込まない」）は沈黙ではなく、**ログに残る第一級の判断**です。

ウェアラブル不要・カメラ不要・生テキスト不要。OS が既に出している打鍵タイミングだけを使います。

---

## しくみ

```
任意のアプリ ──▶ キーボードフック (Rust)      Win: WH_KEYBOARD_LL · Mac: CGEventTap
                  │  crossbeam channel · ノンブロッキング・本文を持たない
                  ▼
              分析スレッド · 1 Hz ゲート
                  │  30 秒ウィンドウで F1/F3–F6
                  │   → X（認知摩擦） / Y（生産的な前進）
                  │   → EWMA 平滑化 → HMM 前向き 1 ステップ → ヒステリシス層
                  ▼
              介入ポリシー            Need (p_stuck) × Opportunity
                  │  → none / nudge / defer
                  ├──▶ React UI        Dashboard + Overlay（Nudge カード）
                  └──▶ Session logger  NDJSON — 行動特徴量のみ・本文は記録しない
```

`analysis/` は **OS 非依存**。OS 固有のコードはすべて `input/` に隔離されています。
スレッドモデルとバージョン別の詳細な根拠は **[設計の変遷](docs/design-history.ja.md)** を参照。

---

## 特徴量抽出

5 つの特徴量を **30 秒スライディングウィンドウ**で計算し、押下ごとに更新します。
沈黙中は 1 秒ごとに合成観測値を生成して HMM を回し続けます。

| 特徴量 | 記号 | 定義 | 意味 |
|---|:---:|---|---|
| フライトタイム中央値 | **F1** | キー離し→次押下間隔(ms)の中央値 | 速度 — 低い=Flow |
| 修正率 | **F3** | (Backspace + Delete) / 全押下 | エラー — 高い=Stuck |
| バースト長 | **F4** | 間隔 < 200 ms の連続キー平均長 | 流暢性 — 高い=Flow |
| ポーズ回数 | **F5** | ウィンドウ内の ≥ 2 s 間隔の回数 | 熟考 |
| 削除後停止率 | **F6** | 削除直後に ≥ 2 s 間隔が生じた割合 | 修正後フリーズ — 高い=Stuck |

各値はベースライン相対の `φ(x,β) = clamp((x−β)/(2β), 0, 1)` で `[0,1]` に正規化し、
2 つの解釈可能な軸へ射影します。

```text
X（認知摩擦）   = 0.30·φ(F3) + 0.25·φ(F6) + 0.25·φ(F1) + 0.20·φ(F5)
Y（生産的沈黙） = 0.40·φ(F4) + 0.35·(1−φ(F1)) + 0.25·(1−φ(F5))
```

`(X, Y)` を 5×5 グリッド（+ Backspace ペナルティビン）に離散化し、3 状態 HMM
（**Flow / Incubation / Stuck**）へ前向きアルゴリズム 1 ステップで投入、上層にヒステリシス EMA を重ねます。
遷移/放出行列・β ベースライン・量子化・チューニング履歴は **[設計の変遷](docs/design-history.ja.md)** に収録。

---

## 介入

| レベル | トリガー | 効果 | 解除 |
|---|---|---|---|
| **Nudge** | `action == nudge` | クリック透過の小カード。不透明度は Need に比例 | 一定時間で自動消去 |
| **Physical Anchor** | *未実装* | 画面から離れることへの**方向づけ** | — |
| ~~**Wall**~~ | ~~全画面遮断~~ | **2026-08 に削除** — 下記参照 | — |

**抑制（すべて稼働中）**: 能動的にタイプ中（打鍵間隔 < 2 秒）は `defer` / cooldown 10 分 /
1 日 6 回まで / 直近 dismiss から 20 分は抑制 / 無入力 180 秒以上で介入を全停止。

**なぜ Wall を消したか**（[ADR-015](docs/adr/ADR-015-wall-removal.md)）: 全画面遮断は
**AI への近道も、助けを求める行為も、作業そのものも一律に止めてしまう**。抑えたい振る舞いは
もっと狭く（「答えをそのまま受け取ること」）、画面を塞ぐ手段ではそこを狙えない。
`wall_server.rs`・QR / スマホ解除の経路・Monk Mode・Zen Timer・早期解除はすべて削除した。
**HIR（有害介入率）は残してある** — 変わったのは対象集合だけである。

**Physical Anchor**（[ADR-017](docs/adr/ADR-017-expression-channel-boundary.md)）が実際に労力を
担う層であり、**まだ実装されていない**。
★★★ **系はその開始も完了も判定しない**（[ADR-018](docs/adr/ADR-018-physical-anchor-without-completion.md)）——
どれだけ離れるか・いつ戻るかに**系の側の閾値を置かず**、**タイマー・カウントダウン・残り時間表示も実装しない**。
GSE は**身体活動を一切センシングしない**（GPS・歩数計・加速度センサを使わない）。

> ⚠️★★★ **2026-09-01 訂正。** 旧文はここで完了条件を「**一定時間の離席と作業への復帰**」と書いていたが、
> **ADR-018 D1 がその条件を取り下げた**。★ 歩数の目標を時間の目標に替えても
> 「**届かなかった**」というセルが残る点は同型であり、そこが内発的動機を最も損なう
> （[P99] performance-contingent で目標に届かなかった群 `d = −0.88`）。
> ★ **段階呼称 Lv1〜Lv4 を落としたのも同じ理由** —— Wall が消え完了条件も無くなった結果、
> **番号を振るべき「強度が単調に上がる段」が現存しない。**

---

## 🔒 プライバシー

- **本文は一切保存しません。** ログに残るのはタイミング・カウント・判断であり、文字内容ではありません。
- キーストローク内容・生 NDJSON は外部サービス／LLM に**決して送信しません**。
- セッションはローカルの `Documents/GSE-sessions/*.ndjson` に保存。共有するのは ~1 KB/session の
  集計 `--metrics --json` のみ（[`gse-dataset`](https://github.com/mikotomiura/gse-dataset) 参照）。
- NDJSON スキーマは Rust 型から機械生成し、CI が drift を構造的にブロックします。

---

## 📥 インストール

ビルド済み成果物はバージョンタグごとに自動公開されます →
**[Releases](https://github.com/mikotomiura/GSE-prototype/releases)**。

| プラットフォーム | ファイル | こんな時に |
|---|---|---|
| **Windows（ポータブル）** | `gse-next.exe` | **推奨** — インストール不要、そのまま実行 |
| Windows（インストーラー） | `gse-next_X.Y.Z_x64-setup.exe` | スタートメニュー登録が欲しい時 |
| macOS（Apple Silicon） | `gse-next_X.Y.Z_aarch64.dmg` | — |

### Windows

これは研究用ビルドで**コード署名されていない**ため、Windows は警告を出します（想定どおりです）。

1. まず**ポータブル版 `gse-next.exe`** を使ってください（インストーラー不要・UAC 昇格なし）。
2. **SmartScreen**（「WindowsによってPCが保護されました」）が出たら → **詳細情報** → **実行**。
3. **Smart App Control (SAC)** にブロックされた場合（「実行」ボタンが出ない）:
   **設定 → プライバシーとセキュリティ → Windows セキュリティ → アプリとブラウザーの制御 →
   スマートアプリコントロールの設定 → オフ**、その後再実行。
   > ⚠️ SAC は一度オフにすると再有効化できません（Windows の仕様）。オフにしたくない場合は
   > 署名済みビルドをメンテナーに依頼してください。

### macOS

ad-hoc 署名（Apple Developer ID なし）のため、隔離属性を消すまで Gatekeeper がブロックします。

```bash
# 初回起動の「前」に実行:
xattr -dr com.apple.quarantine /Applications/gse-next.app
codesign --force --deep --sign - /Applications/gse-next.app
```

> `xattr -cr` は使わないでください — 全属性を消し、署名を無効化する恐れがあります。

その後 **システム設定 → プライバシーとセキュリティ → Input Monitoring → gse-next** を許可し、
アプリを再起動してください（許可がないとキーボードフックが動きません）。

<details>
<summary>権限付与後も Input Monitoring が効かない場合</summary>

1. **再付与**: Input Monitoring で gse-next のチェックを外し、再度オンにして再起動。
2. **TCC リセット**: `tccutil reset ListenEvent` 後、再付与して再起動。
3. **隔離属性の再削除**: 以前 `xattr -cr` を使ったなら、DMG から再コピーし
   `xattr -dr com.apple.quarantine /Applications/gse-next.app` を使用。
4. **Mac を再起動**: 一部の TCC 変更は完全な再起動が必要です。
</details>

---

## 🛠️ ビルド

| ツール | バージョン |
|---|---|
| Rust | 1.77+（`rustup update stable`） |
| Node.js | 22+ |
| Tauri CLI v2 | `cargo install tauri-cli --version "^2"` |

```bash
npm install
npm run tauri dev      # 開発実行
npm run tauri build    # リリース → src-tauri/target/release/bundle/
```

**リリース前・マージ前の検証** — `docs/verification-runbook.md` を上から実行:
自動回帰（`cargo test` · `gse-replay --snapshot` · `emit_schema` · `tsc`）、macOS 機能検証、
Windows 差分、Google Form ビルダー。

<details>
<summary><b>研究者 / デバッグモード（二重ゲート）</b></summary>

デバッグ機能は 2 つのフラグで保護され、被験者は**フラグなし**（完全ブラインド）で起動します。

| フラグ | 種別 | 効果 |
|---|---|---|
| `VITE_GSE_DEBUG=1` | ビルド時（Vite） | デバッグボタン表示・week-2 モデル出力表示 |
| `GSE_DEBUG=1` | 実行時（Rust） | `force_nudge` / `debug_force_probe` / `get_ime_shadow_debug` 有効化 |

```bash
VITE_GSE_DEBUG=1 GSE_DEBUG=1 npm run tauri dev
```
詳細は `docs/calibration-smoke-runbook.md` §1.1–1.2。
</details>

<details>
<summary><b>リリース手順（メンテナー向け）</b></summary>

```bash
# package.json · src-tauri/tauri.conf.json · src-tauri/Cargo.toml のバージョンを揃える
git commit -am "chore: bump version to vX.Y.Z"
git tag vX.Y.Z && git push && git push --tags
# GitHub Actions が Windows(exe) + macOS(dmg) をビルドし Release を公開します。
```
</details>

---

## ログとリプレイ

セッションごとにタイムスタンプ付き NDJSON を生成し、`gse-replay` がそれをオフライン再実行します —
単体・回帰・GT 評価・チューニングの背骨（リプレイ 1 本で 4 役を兼ねる）。

```bash
cargo run --bin gse-replay -- session.ndjson --snapshot tests/snapshots/s.json  # 回帰（byte-equal）
cargo run --bin gse-replay -- session.ndjson --metrics --json                    # GT メトリクス
```

リアルタイム Ground Truth ラベリングは実装済み（`Ctrl/⌘ + Shift + Alt + F/I/S`）。主観ラベルを
production HMM path に一切触れずに同じログへ追記します。

---

## 📁 構成

```
src/                 React / TypeScript フロントエンド（UI + IPC のみ）
src-tauri/src/
  analysis/          engine.rs · features.rs · intervention.rs · loop_step.rs   （OS 非依存）
  input/             hook_* · ime_*                                              （OS 固有）
  lib.rs · logger.rs · schema_dto.rs · redaction.rs · recording.rs
src-tauri/bin/       gse-replay（評価 CLI） · emit_schema
docs/                architecture · functional-design · design-history · runbooks
```

## 📚 ドキュメント

| ファイル | いつ読むか |
|---|---|
| [`docs/design-history.ja.md`](docs/design-history.ja.md) | v2.1–v2.22 の詳細（ヒステリシス・IME・介入・パリティ） |
| `docs/architecture.md` | スレッドモデルとデータフロー |
| `docs/functional-design.md` | 意図・要件・ユースケース |
| `docs/development-guidelines.md` | 規約・テスト・レビュー・データ repo 運用 |

<details>
<summary><b>学術的参考文献</b></summary>

1. **Csikszentmihalyi, M.** (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row.
2. **Csikszentmihalyi, M.** (1996). *Creativity*. HarperCollins.
3. **Sio, U. N., & Ormerod, T. C.** (2009). Does incubation enhance problem solving? *Psychological Bulletin, 135*(1). — Incubation 自己遷移(0.80) と Pause→Burst シグネチャ。
4. **Ohlsson, S.** (1992). Information-processing explanations of insight. In *Advances in the Psychology of Thinking*. — 行き詰まり・固執 → Stuck。
5. **Rabiner, L. R.** (1989). A tutorial on hidden Markov models. *Proceedings of the IEEE, 77*(2). — 前向きアルゴリズム。
6. **Dhakal, V., et al.** (2018). Observations on typing from 136 million keystrokes. *CHI 2018*. — β ベースライン。
7. **Salthouse, T. A.** (1986). Transcription typing. *Psychological Bulletin, 99*(3). — F1/F4 設計。
8. **Microsoft** (2023). *WinEvent Hooks*, MSDN. — クロスプロセス IME 検出。
</details>

---

<div align="center">
<sub>研究プロトタイプ · All rights reserved · 生産的苦闘を守るために</sub>
</div>
