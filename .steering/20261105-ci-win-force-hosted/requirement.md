# 要件: CI の Windows のジョブを変数で hosted に固定できるようにする

## 背景

- G-GEAR（Windows の self-hosted ランナー `g-gear-win-x64`・ラベル `gse-win`）は 2026-11 中、別の計算で忙しい（研究者の言・2026-11-05）。機械は online で、ランナーのサービスは 2026-11-05 時点で GitHub の API 上 offline。
- `ci.yml` の `decide-win-runner` の probe は「`gse-win` のランナーが online なら self-hosted」で、busy を見ない。ランナーが起き上がると、R1（`feature/nudge-default-off`）や M5 の Windows のジョブ（cargo のビルドとテスト）が G-GEAR の計算と重なる。
- 研究者の決定（2026-11-05）: 11 月の CI は Windows を GitHub の hosted で回す。守り方は「変数で hosted に固定する」を採った（G-GEAR のランナーを止める案・何もしない案より）。

## ゴール

リポジトリの変数 `GSE_WIN_FORCE_HOSTED` が `"1"` のとき、`gse-win` の状態を問わず Windows のジョブを `windows-latest` で走らせる。未設定・`"1"` 以外は従来どおり。

## 受け入れ条件

- [x] probe の script が `GSE_WIN_FORCE_HOSTED=1` で `["windows-latest"]` を出す（`gse-win` が online でも）
- [x] 未設定・`0`・空文字では従来どおり probe する（online なら self-hosted）
- [x] actionlint の指摘が増えない
- [ ] 変数を設定した後の実際の run で、`check (gse-win-selfhosted, …)` が hosted で走ったことをログの notice で確かめる
