# 次のセッション: 匿名化で activity_label の recall_window_* が相対化されていない

## 見つけた経緯

2026-11-21、`.steering/20261121-auto-context-segmentation/` の実データの解析中に見つけた（同 decisions.md 判断 18・19）。

## 事実（一次で確かめたこと）

- `src-tauri/src/analysis/anonymize.rs:116` の `ABSOLUTE_TIME_FIELDS` は `t` / `ts` / `session_start` / `session_end` / `scheduled_ts` / `analysis_window_start_ms` / `analysis_window_end_ms` / `recovered_at` の 8 つだけで、`activity_label` の `recall_window_start_ms` / `recall_window_end_ms` が無い。
- O1 の提出物（`~/gse-o1-derived/20261116-o1-conduct-record/plain/P009/`・P009 は研究者本人）の `activity_label` 33 行で、`t` は相対（例 66226）なのに、`recall_window_*` は絶対の epoch ms（例 1794147156704）のまま残っていた。P006・P011・P013 の提出物には `activity_label` の行が無い（0 行）。
- 本人の段 1 の記録（`~/Documents/GSE-sessions/`）にも `activity_label` が 205 行ある。段 1 の提出物を作れば同じことが起きる。
- `anonymize.rs` のテスト `adr013_lines_are_anonymised_too` は、決まった行種の欄しか見ていない。新しい `*_ms` の欄が一覧から漏れても赤にならない。

## やること（案）

1. `ABSOLUTE_TIME_FIELDS` に 2 欄を足す。あわせて、「`_ms` で終わる欄のうち、継続時間の一覧（`idle_ms` など）に無いもの」を拾って赤にするテストを足し、漏れを構造で塞ぐ。陽性対照として、欄を 1 つ外すと赤になることを確かめる。
2. 段 1 の配布物（配った版）に入っているかを確かめ、配布と提出の手順に影響があるかを研究者に聞く。
3. すでに提出された O1 の P009 の 33 行の扱い（P009 は研究者本人）を研究者に聞く。
4. data-privacy Skill に従い、security-checker を回す。

## 触らないこと

- 提出物の受け取り（復号）の手順と、O1 の台帳。
