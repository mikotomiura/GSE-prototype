# タスクリスト

- [x] 要件・設計（このディレクトリ）
- [x] venv（Python 3.11.9・numpy 2.2.6・scikit-learn 1.5.2）・`requirements.txt`・`env.md`
- [x] `align_vec.py` と突き合わせの検査
- [x] `seeds.py`・`corpus.py`（合成のコーパス）
- [x] `forms.py`
- [x] `attackers.py`（A0・A1・A1'・A2・A2-b・A3）
- [x] `matching.py`（全文・窓・陰性対照）
- [x] `aggregate.py`（ブートストラップ・最も強い攻撃者・形の対比・有用性の集計。設計の `bootstrap.py` をこの名にした）・`evaluate.py`（1 記録の計算）
- [x] `utility.py`
- [x] `run_main.py`・`run.sh`（合成のコーパスで通す・再実行でバイト一致）
- [x] `selftest_main.py`（陽性対照・陰性対照・変異）
- [x] レビュー 1 回目（code-reviewer・security-checker・コミット 66721d9d）
- [x] 凍結の後の直し（code-reviewer の指摘・notes.md「凍結の後・データの前の直し」）: 対比・陰性対照の攻撃者の固定・開いた世界・組み立て直しの分割・窓の偏り・有用性の集計・R3-u の A3・B だけの費用・学習の並び・表ごとの字の符号・自己検査（検査に名前・変異は狙った検査で落ちたかを照合・traceback は ERROR）
- [x] 直しのレビュー（code-reviewer 1 回・Codex 2 巡・パス限定・`raw/` は範囲の外）: 陰性対照の R3-u の A3 の版の選び直し（HIGH・両方が独立に指摘）ほかを直した（コミット e7d60504 とその次）。security-checker は今回の差分（集計と自己検査だけ・データの読み込みや外への送信なし）では回していない
- [ ] 論文用のリポジトリへ写す（凍結の後のコミット）
- [x] 実データの大きさでの時間: 1 記録 約 256 秒（単一コア・約 400 語・候補 1,200 本）。16 並列で主な表 約 3 時間・全員の補遺 約 22 時間
- [ ] ENJA15 の読み込みと節（取得と T・P・D の確認の後）・A4（KeyTAR の取得の後）
- [ ] 実データの読み込み（`load_klicke.py`・検査 2）: 例外に行の断片を出さない（書き手の通し番号と例外の型名だけを出す）・`Move From` の書式が合わない行は除外の理由に回す（security-checker LOW 2）・処理の前に `pip-audit`
