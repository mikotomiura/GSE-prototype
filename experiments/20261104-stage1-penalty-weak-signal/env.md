# 環境

- Mac（Apple Silicon・10 コア）・Python 3.14.4・numpy 2.5.2。scipy は使わない。
- 依存は numpy だけ（lockfile は置かない。版は provenance.json に刻む）。
- BLAS の多重を切る（run.sh が OMP_NUM_THREADS=1 ほかを設定）。
