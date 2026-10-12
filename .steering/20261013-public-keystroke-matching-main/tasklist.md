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
- [ ] レビュー（code-reviewer・security-checker・`/cross-review`）
- [ ] 論文用のリポジトリへ写す（凍結の後のコミット）
- [x] 実データの大きさでの時間: 1 記録 約 256 秒（単一コア・約 400 語・候補 1,200 本）。16 並列で主な表 約 3 時間・全員の補遺 約 22 時間
- [ ] ENJA15 の読み込みと節（取得と T・P・D の確認の後）・A4（KeyTAR の取得の後）
