# 環境

- Mac（Apple Silicon・10 コア）・Python 3.14.4・numpy 2.5.2。依存は numpy だけ。
- 4 プロセスで回す。BLAS の多重を切る（run.sh が OMP_NUM_THREADS=1 ほかを設定）。
