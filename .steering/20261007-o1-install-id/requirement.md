# O1: 導入ごとの識別子（install_id）を meta 行に刻む

## 背景
- 研究者判断 2026-10-07: O1 で 1 人が複数端末で計測してよい。解析で端末を分けるため識別子を足す。
- v0.1.39 の meta 行には端末を区別する値が無い（ADR-013 D6 はマシン GUID 等を「フィンガープリントになる」として禁止）。
- 同じ P-ID の 2 台ぶんが区別できず、端末 A を離れて B で作業した時間が「離脱」と混ざる（G2 の入力が汚れる）。

## ゴール
- O1 モードのときだけ、`meta`(session_start) 行に `o1_install_id`（導入ごとにランダム生成・ハードウェア由来でない 16 桁 hex）を刻む。
- 非 O1（通常・G1）の NDJSON は 1 バイトも変わらない。
- 新タグ v0.1.40 で配布できる状態にする。

## 受け入れ条件
- [ ] 識別子は `~/.gse/o1_install_id` に保存され、再起動しても同じ値（冪等）。壊れていたら作り直す。
- [ ] 値は 16 桁の小文字 hex のみ（JSON を壊す経路が無い）。ハードウェア・OS・ユーザー名由来の値を使わない。
- [ ] 非 O1 の meta 行は従来と byte 一致。O1 では `o1_mode` の直後に `o1_install_id`。
- [ ] schema/current.json を再生成し drift 検査が通る（optional フィールドの additive 追加）。
- [ ] anonymize が meta の `o1_install_id` を保つ。
- [ ] cargo test / clippy / fmt 緑。

## スコープ外
- 同意フォームの本文改訂の実施（文面案は用意するが、Apps Script への反映は研究者）。
- gse-dataset 側の schema 更新、Drive 差し替え、O1 事前登録の凍結。
## 運用メモ
- /reimagine 適用: No
- 理由: 既存の o1_mode と同形の additive 追加で、設計の分岐が小さい。
