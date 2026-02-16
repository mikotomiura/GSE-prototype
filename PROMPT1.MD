現在のGSEプロトタイプ（MVP）を、技術設計書の仕様に近づけるため、以下の2つの重要な「推論ロジックの改善」を実装したいです。

現在のコード（src/input/keyboard.rs, src/inference/hmm.rs）をベースに、以下の変更を行ってください。

## 0.環境問題の改善
現在のGSEプロトタイプ開発において、**「ディスク容量不足」**が深刻なブロッカーになっています。
そのため、以下の「機能実装」と「容量削減」を同時に行う変更を適用してください。

## 優先度MAX: ディスク容量削減設定の適用
Rustのビルド生成物が肥大化しないよう、`Cargo.toml` を編集してリリースビルドの最適化設定を強制してください。
以下の設定を `Cargo.toml` の末尾に追加（または置換）してください。これによりバイナリサイズとキャッシュサイズを劇的に縮小します。

```toml
[profile.release]
opt-level = "z"      # サイズ優先の最適化
lto = true           # Link Time Optimization (不要コード削除)
codegen-units = 1    # 並列コンパイル数を1にしてサイズ圧縮
panic = "abort"      # パニック時の巻き戻しコードを削除
strip = true         # デバッグ情報を完全に削除 (これが最も効果大)


## 1. 新規特徴量「F6: Pause-after-Delete」の実装
技術設計書にある「Stuck（行き詰まり）」を最も強く示唆する指標である F6 を実装してください。
- **ロジック**: Backspaceキーが押された直後の「次のキー入力までの時間（Latency）」を計測する。
- **判定**: Backspace後の停止時間が `2000ms` (2秒) を超えた場合を「迷い（Hesitation）」としてカウントする。
- **実装場所**: `src/input/keyboard.rs` 内で、`VK_BACK` のタイムスタンプを追跡し、次のキーイベントとの差分を計算するロジックを追加。

## 2. HMM（隠れマルコフモデル）の多次元化
現在 `flight_time` (1次元) だけで判定しているHMMを、`backspace` の情報も加味した2次元（または多次元）観測モデルに拡張してください。
- **変更点**: `HMM::update(observation: f64)` を `HMM::update(flight_time: f64, backspace_count: u32)` (あるいはF6のスコア) を受け取れるように変更。
- **確率計算**: `src/inference/hmm.rs` の `calculate_observation_probs` において、Flight Timeの確率だけでなく、Backspace頻度の確率も掛け合わせる（Naive Bayes的なアプローチで可）ように修正。
    - **Stuck状態の定義**: 「Flight Timeが長い」かつ「Backspaceが多い」場合に、Stuckの確率が極大化するようにパラメータを設定。

## 制約事項
- 新たな重い依存クレート（torchなど）は追加せず、現在の `statrs` や標準ライブラリの範囲で実装すること（ディスク容量節約のため）。
- `src/inference/rules.rs` のルールベース判定にも、可能であれば F6 (Pause-after-Delete) の条件を追加すること。

この変更により、「単に手が止まっている（Incubation）」と「消しては悩み、止まっている（Stuck）」をより高精度に区別できるようにしてください。