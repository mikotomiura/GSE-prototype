# 設計案比較 — Task D

## v1 の要旨
NDJSON 1 セッションを単一パスで合成型 `SessionData` に組み立て、calibration_eval に渡す。
CLI `--calibration <file>` は **単一セッション**の within-session 指標を metrics.json 出力。
被験者内 C-index・被験者横断ゲートは純関数として実装し **unit test のみ**で検証(CLI 非経由)。
窓集約は **raw_x/raw_y の中央値**、疎ウィンドウは `MIN_WINDOW_FEATS=3` 閾値で除外。

## v2 の要旨
既存 replay.rs の `collect_*` 多パスイディオムに完全に乗り、型別コレクタを足して合成。
CLI `--calibration s1 s2 s3 ...` は **1 被験者の複数セッションを可変長で受け**、被験者内 C-index と
前向き holdout を **CLI 経路で end-to-end 決定論検証**できる。被験者横断ゲートのみ unit test。
窓集約は **ewma_x/ewma_y の平均**(デプロイ系が使うモデル出力)、疎ウィンドウは 0 件のみ除外(閾値ノブなし)。

## 主要な差異

| 観点 | v1 | v2 |
|---|---|---|
| 抽出イディオム | 単一パス合成型 `SessionData`(新型を発明) | 既存 `collect_*` 多パス踏襲(コレクタ独立テスト) |
| CLI 入力 | 単一セッション file | **1 被験者の可変長セッション群** |
| C-index/holdout 検証 | unit test のみ(CLI 非経由) | **CLI 経路で合成 fixture 検証**(受け入れ条件を直接充足) |
| 窓 X 源 | raw_x(窓ローカル) | ewma_x(モデル出力・運用妥当性) |
| 窓 統計量 | 中央値(頑健) | 平均(代表値・単純) |
| 疎ウィンドウ | MIN_WINDOW_FEATS=3 で除外 | 0 件のみ除外(ノブなし) |
| 変更規模 | replay.rs match 2 箇所 + 単一 positional | + parse_args 可変長対応(やや大) |
| テスト戦略 | C-index は in-code unit のみ | C-index も CLI fixture で(+ 横断ゲートは unit) |
| リスク | C-index/holdout が CLI で動かず E まで未実証 | parse_args 可変長で既存 1-positional 制約を緩める |

## 軸別の論点 (設計判断 A / B)

### A. 窓集約 (X 源・統計量)
- **raw vs ewma**: raw = 窓ローカルで EMA 前方漏れなし・「直前30秒」の主観と整合。
  ewma = デプロイ系が実際に行動に使う出力で「モデル検証」の対象として正当。
- **中央値 vs 平均 vs 末尾**: 中央値=過渡スパイクに頑健 / 平均=単純代表値 / 末尾(t−1s)=窓と時刻整合だが単点で脆弱。
- C-index は**順序のみ**を使うため、集約法の違いは「probe 間の X 順位」を変えた時だけ効く(影響は限定的)。

### B. C-index ペアリング
- 両案とも scope(3)「X と Q1 の順位一致割合」に従い**軸別ランク concordance**を採用(2D 象限 concordance は発明しない)。
- 両案ともゲート駆動 = X↔Q1、Y↔Q2 併報。→ **B は実質スコープで確定済み・両案一致**。

## 推奨案
**ハイブリッド(v2 ベース + A は要ユーザー判断)**。理由:
1. **抽出イディオム**は v2(`collect_*` 踏襲)が明確に優れる — コードベース一貫性・コレクタ単体テスト容易・
   `--metrics` と対称で保守者が読みやすい。合成型 `SessionData` を発明する v1 は idiom から外れる。
2. **可変長 CLI(v2)**は受け入れ条件「合成 NDJSON fixture で C-index/holdout を決定論検証」を
   unit test 依存にせず CLI 経路で満たせる点で優れる。被験者内 C-index は scope(3) の中核成果物であり、
   E まで CLI 未実証(v1)にするより D で動かせる方が「計測の血流を先に通す」D-14 趣旨に合う。
   parse_args の可変長対応は `--calibration` 限定の局所変更でリスクは小さい。
3. **窓集約 A** は方法論的妥当性に関わる選択(ewma=運用妥当性 vs raw=窓ローカル整合、平均 vs 中央値)で、
   研究者(ユーザー)の判断が要る。実装は集約関数を**差し替え可能(`AggSpec`)**にしておき、既定値だけ決める。
   → 既定の推奨は **ewma_x/ewma_y の中央値**(v2 の「モデル出力」+ v1 の「頑健性」を採る折衷)。

## 設計判断 A の既定値(ユーザー確認ポイント)
- X 源: ewma_x/ewma_y(モデル出力) / raw_x/raw_y(窓ローカル) のどちらを既定にするか。
- 統計量: 中央値(頑健) / 平均(単純) / 末尾(時刻整合) のどれを既定にするか。
- → 推奨既定: **ewma の中央値**。集約は `AggSpec{source, stat}` で切替可能にし将来比較できる形にする。
