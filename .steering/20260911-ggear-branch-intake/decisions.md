# 設計判断 — G-GEAR ブランチ取り込み

## 判断 1: 規模の数え方を `merge-base..branch` へ改める

- **決定**: 取り込み量は `git diff $(git merge-base main BR)..BR` で数える。
- **理由**: 引き継ぎメモの 246 ファイル / −4,870 行は `main..branch` の**二点差分**で、
  main 側 60 コミットが branch に無いこと (= 巻き戻し) を取り込み量に数え込んでいた。
  実測は **199 ファイル / +28,054 / −670**。★ 削除行が 7 倍違う。
- **却下案**: メモの数字をそのまま使う → ⚠️ 「branch が 4,870 行消す」と誤読し、
  存在しない退行リスクに時間を使うことになる。

## 判断 2: 5 本ではなく 2 本の PR に割る

- **決定**: PR-A (Rust ＋ 下流) / PR-B (それ以外) の 2 本。
- **理由**: main と branch が**両方触ったファイルは 23 件だが、うち 17 件は最終内容が
  バイト一致**しており、実際に衝突しうるのは **6 件**しかない。分割の主目的だった
  「衝突の局所化」が不要になり、残る目的は「検証の関門を分けること」だけ。
  関門 (`--snapshot` 6 本) が要るのは Rust だけなので、そこだけ独立させれば足りる。
- **却下案**: 丸ごと merge して 1 本 → +28,054 行を 1 PR でレビューすることになる。

## 判断 3: 衝突 6 件のうち 4 件は **main を採る**

- **決定**: `experiments/20260903-o1-runtime-cost/{notes,env}.md` と
  `.steering/_handoff/{README,next-session-prompt-post-windows}.md` は **main 側を残す**。
- **理由**: branch 側の `notes.md` は CPU% を **Windows=全16論理コア基準 / macOS=1コア基準**
  のまま記録し「macOS 換算 33.0% → FAIL 相当」と結論している。⚠️ main はこれを
  **両 OS 同一基準 `one_core_100`** に是正済み (Win 2.06% / mac 2.19%)。
  branch を採ると**決着済みの結論が退行する**。
- **却下案**: union で両方残す → ⚠️ 同じ実測に 2 つの矛盾する結論が併存する。

## 判断 4: 衝突 2 件 (`.gitignore` / `.github/workflows/ci.yml`) は union、ただし重複ステップは 1 本に畳む

- **決定**: 両者の追加行を残す。⚠️ ただし `bash scripts/secrets-filter-test.sh` を走らせる
  step は main 側と branch 側で**名前違いの同一コマンド**なので、main 側の 1 本に畳む。
- **理由**: 追加位置が同じだけの純追加で、意味は競合しない
  (`.gitignore`: main=`ndjson-size-start.tsv` / branch=`out.txt`)。
  ⚠️ 同じコマンドを 2 回走らせる CI step は無駄なだけでなく、
  「どちらが番人か」が曖昧になる。
- **却下案**: branch の step 名を採る → main 側の他ゲート群と命名が揃わない。

## 判断 5: `HMM_VERSION` は bump しない

- **決定**: bump せず、ゴールデンも再生成しない。
- **理由**: design.md「`HMM_VERSION` bump は不要 — 根拠」の実測 4 点。
  ★ 特に **陽性対照で `--snapshot` が赤になることを確かめた上で** 6 本緑。
- **却下案**: 念のため bump → ⚠️ 既存の全ゴールデンを再生成することになり、
  「改名が `FeatSnapshot` に影響しない」という事実が記録から消える。

## 判断 6: fixture `P104/sess_d.metrics.json` は旧名のまま残す

- **決定**: 書き換えない。
- **理由**: `build_analysis_db.py` の `LEGACY_FIELD_ALIASES` が旧名を吸収する。
  実測で `(1, 0.0, 0.0)` と生の値に一致して入った (NULL 化しない)。
  ★ 旧名 fixture が 1 本残ることが、**後方互換経路の回帰テストそのもの**になる。
- **却下案**: 新名に揃える → ⚠️ 後方互換経路を誰も踏まなくなり、黙って壊れても気づかない。

## 判断 7: `docs/architecture.md` の改名追随は PR-A に入れる

- **決定**: `compute_recovered_at` → `compute_pflow_exit_at` (2 行) を PR-A で直す。
- **理由**: ⚠️ branch はこのファイルを **1 度も触っていない** (実測 0 件)。
  改名を入れる PR が、その改名で嘘になる仕様記述を同時に直さないと、
  PR 単体で整合しない。
- **却下案**: PR-B へ回す → PR-A だけ merge された瞬間に docs が実装と食い違う。

## 判断 8: `docs/adr/ADR-018,019,020` と `docs/mitou_submission/` の旧名は残す

- **決定**: 書き換えない。
- **理由**: ADR は本文を書き換えない規約 (CLAUDE.md / `docs/adr/README.md`)。
  `mitou_submission/` は提出済み文書。`docs/literature/` のカードも記録であり、
  当時の記述が正しい。
