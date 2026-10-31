# 設計

## 変更（`src/App.tsx` の統合ポーリング）
- `windowLabel === "overlay"` なら、`get_intervention_decision` だけを取る。
- 主窓は、`document.visibilityState === "hidden"` の間は `get_cognitive_state`・`get_keyboard_idle_ms` を取らない。
- 主窓の `get_intervention_decision` は、O1（`o1Mode` が真）で見えない間だけ取らない。通常運用と G1 では見えなくても取る（判定の時計）。
- `visibilitychange` で見えるようになったら、すぐに 1 回取る。
- O1 の判定がまだ（`o1Mode === undefined`）の間は、O1 ではないものとして判定の時計を回す（取りこぼしの側に倒さない）。

## 確かめ方
- 一時的な計装 IPC-DIAG（`lib.rs`）: 30 秒ごとに `get_cognitive_state` の回数（主窓と overlay の和）と、`get_intervention_decision` の回数を主窓・overlay に分けて 1 行出す。コミットの前に外す。
- O1 の形の開発版（`probe/run-dev-o1.sh`・識別子 `com.johnd.gse-next-trim-polling`・HOME と GSE_DATASET は一時フォルダ）で、主窓が見える・最小化（`probe/axclick.swift` の minimize。題名 gse-next の窓だけ）を 60 秒 × 2 ずつ、`probe/cpu-window.sh` と `probe/procs.py` で測る。
- 通常運用の確かめ: 非 O1 で起動し、「開始する」の後に最小化して、`decision_main` の回数が続くかを見る。
