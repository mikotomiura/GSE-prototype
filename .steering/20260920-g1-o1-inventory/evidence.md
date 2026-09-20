# 一次確認の証拠（★ 2026-09-20 に実測したもの）

> ⚠️ 本ファイルは「確かめた事実と、その根拠の所在」だけを書く。判断は `decisions.md`、
> 残タスクの一覧は `inventory.md` に置く。
> ★ 引き継ぎ `.steering/_handoff/next-session-g1-o1-inventory.md` の記述は**未検証メモ**であり、
> ここで確かめた内容が食い違う場合は**こちらが正**。

## Q3 の材料 —— 「テストの中の陽性対照」の境界

| 事実 | 根拠 |
|---|---|
| 判断 4 #8 の一次は `.steering/20260919-theory-ssot-promotion/decisions.md:72`（★ `20260920-decision4-reflection` 側の「判断 4」は改名の件で**別物**。同ファイルで Q3 を起票したのは判断 8 の M4 = `:107`） | 実測 |
| CORE-CS の所在は `.steering/20260916-gse-theory-operationalization-review/core-cs-evaluation-contract.md`（ステータス: pre-SSOT review contract） | 同ファイル |
| 「陽性対照 / positive control」の全ヒットは **7 件**（`:12` / `:77` / `:95` / `:98` / `:148` / `:190` / `:238` / `:240`）。★ **境界が未決**と明記しているのは `:95` だけで、他は `CS-C0` / `W-pre` という**研究計器側**の定義 | grep 実測 |
| `EH1` = 「replay / log / test による停止閉包、非再捕捉、運用継続の監査」。`test` とは書いてあるが `#[cfg(test)]` / CLI フラグ / feature の区別は**書かれていない** | 同ファイル `:57-62` |
| `OnlineUpdater` は **repo 全体で 0 ヒット**（未実装）。ADR-008 は **Proposed** | `grep -rn "OnlineUpdater" src-tauri/src/` = 0 件 / `docs/adr/ADR-008-online-learning-boundary.md:3` |
| ADR-033 D6 用の陽性対照テストは**まだ無い**。ただし「陽性対照」を明示した `#[cfg(test)]` の**先例はある** | `src-tauri/src/redaction.rs:853-860`（`naive_rewrite_would_drop_permissions_positive_control`） |
| `gse-replay` のフラグのうち、Nudge の意思決定を**オフラインで発火・評価する**のは `--intervention`（`:599`）/ `--sweep`（`:605`）/ `--nudge-diag`（`:608`） | `src-tauri/src/bin/replay.rs:589-617` |
| `Cargo.toml` の `[features]` は **`package` の 1 項目のみ**（age 暗号化と HTTP 送信。default ビルドに載らない）。★ 介入 / Nudge を切り替える feature は**存在しない** | `src-tauri/Cargo.toml:89-94` |
| 配布物は `gse-next.exe` / `gse-submit.exe` だけ（`gse-replay` は配らない） | `make-common-app-zip.sh`（判断 8 Q3 の注記） |

## Q4 の材料 —— R-1 の「被験者」に `EH2` / 開発者利用が入るか

| 事実 | 根拠 |
|---|---|
| IDE = Intervention Decision Engine（Layer 5-7 の SSOT・Accepted） | `docs/architecture/intervention-decision-engine.md:1,3` |
| 見直し候補は **R-1 の 1 本だけ**（R-2 以降は無い） | `:152,157`・`grep "^### R-"` |
| R-1 の「いまは効いていない理由」の行が、**Q4 を「未決」と明記して研究者へ差し戻している** | `:163-167` |
| `EH2` = 「本人による計器・手順の確認。外部知覚の証拠にしない」。★ 「研究者本人のパイロット」がここに当たるかは CORE-CS 側では定義していない | core-cs-evaluation-contract.md:57-62 |
| 「Nudge を被験者に出すこと」自体を禁止 / 許可した文書は**無い**（grep で該当なし）。あるのは R-1 という上位の未決だけ | `grep -rn "Nudge" docs/*.md docs/architecture/*.md docs/adr/*.md` |
| 介入のグローバルゲートの**既定値は `true`** | `src-tauri/src/lib.rs:111` `static INTERVENTION_ENABLED: AtomicBool = AtomicBool::new(true);` |
| O1 は**コードで強制的に false**（`record_session_meta` を通らないので明示的に落とす） | `src-tauri/src/lib.rs:3321-3326` |
| G1 は**コードで止めていない**（手順と既定値だけ）。UI の初期選択が `week1_blind`（`interventionEnabled: false`）で、UI で第 2 週を選べば `true` になる | `src/App.tsx:111-130,243` / `:116` / `:125`、`lib.rs:2393-2426` |
| ⚠️ よって「研究者本人のパイロット・開発者の日常利用」は、O1 モードでない限り**UI の切り替えだけで Nudge が出る状態に到達できる** | 上記の合成（★ R-1 の記述とも一致） |

## O1 / ADR-034 の材料（★ 実測 2026-09-20）

### ADR-034 の状態
| 事実 | 根拠 |
|---|---|
| ADR-034 は **Accepted**（2026-09-20・研究者判断） | `docs/adr/ADR-034-g1-o1-parallel-conduct.md` 冒頭 |
| D1 の律速は 4 点（① ADR-031 M9 の追補 ② `check-o1-release-readiness.sh` の緑 ③ 本 ADR の Accepted = **済** ④ **D6（案内日の分離）が G1 と O1 の両方の募集に入っていること**） | 同 D1 |
| D3 は「G1 の配布物を**最初の配布のリリースタグで固定**し、収集完了まで別のタグで作り直さない」。⚠️ 「最初の配布」の定義は ADR 本文で**未決**（リブート前の P007/P014/P016 = `app_version 0.1.29` と区別が要る） | 同 D3 / 代償・残る障害 #1 |
| D5 の逆向き（O1 の解析に G1 を読み込ませない）は「**まだ機械的な歯止めが無い**」→ Migration 6 | 同 D5 |

### Migration 1〜6 の実測
| # | 状態 | 根拠 |
|---|---|---|
| 1 | ✅ 済 | `docs/adr/README.md:41, :61` を更新済み |
| 2 | ✅ 済 | `docs/o1-roster-operations.md` §5（`:81-108`）に D6 の規則あり |
| 3 | ❌ 未 | `experiments/20260801-controlled-friction-task/` に「最初の配布」「リリースタグ」の記録 **0 件** → **Q2** |
| 4 | ❌ 未 | ADR-031 M9 と `check-o1-release-readiness.sh` の緑が**両方とも未達** |
| 5 | — 未着手（トリガー未発生） | G1/O1 結合の別 ADR は存在しない（現状それを求める場面が無い） |
| 6 | ❌ 未 | ★ **O1 の事前登録文書そのものが存在しない**（`find experiments -iname "*left-observation*"` = 0 件）。`docs/glossary.md:88` が「作る日は O1 の最初の配布より前」と整合 |

### ADR-031 / ADR-032
| 事実 | 根拠 |
|---|---|
| ⚠️ **両方とも Proposed**（Accepted ではない）。★ 引き継ぎの「ADR-031 / ADR-032 の Accepted」は「**Accepted にするのが残っている**」の意味で読む | 各 ADR 冒頭のステータス行 |
| 発効しない理由はどちらも「**同意文書の改訂が研究者の承認待ち**・被験者向け文書は契約」 | 同上 |
| O1 用の同意文書は**配布済みファイルとして存在しない**（ドラフトは `.steering/20260823-o1-nonkeystroke-gap-and-prereg/consent-draft-o1.md`）。`:281` に「未了: 6 択 ESM（注 D）の追補は**案**であり研究者の承認待ち」が残存・承認マーカ `<!-- o1-esm-consent: approved -->` は未挿入 | 同ドラフト |
| G1 用同意文書は `experiments/20260801-controlled-friction-task/consent.md`（§3 = 「記録するもの / 記録しないもの」）。O1 への言及 0 件 | grep 実測 |

### `scripts/check-o1-release-readiness.sh`（★ 副作用なしを確認して実行）
| 事実 | 根拠 |
|---|---|
| **終了コード 1**。通過 18 件 / 未達 **3 件** | `bash scripts/check-o1-release-readiness.sh` |
| 赤 ①: 同意文書の状態表に「⚠️ **未了**」が残っている | 検査 [1]（`:68-138`） |
| 赤 ②: リリースタグ `v0.1.35` が古い（HEAD と 22 コミット差） | 検査（`:218-298`） |
| 赤 ③: ⚠️ **bash 3.2 互換性検査 `check-shell-portability.sh` が rc=2 =「検査できなかった」で失敗**（★ 検査対象ではなく**検査そのもの**の故障） | 検査（`:347-360`） |
| D6（案内日の分離）の検査は **0 件**（`grep -n "案内日\|D6\|募集"` がマッチなし） | grep 実測 |
| Migration 6 の「G1 のログを入力に取ったら止まる」検査は**存在しない**（`o1.rs` の `g1_mode` は宣言 UI の排他制御で別物。O1 用解析スクリプト自体が未作成） | grep 実測 |

### 募集と配布の分離に伴う被験者への約束
| 事実 | 根拠 |
|---|---|
| ADR-034「影響を受ける文書」表が **被験者向け文書は「変えない」**と明記 | ADR-034 `:190` |
| 「募集してから配布までの間」を説明する記述は被験者向け文書に **0 件** | grep 実測（consent-draft-o1 / participant-setup-guide / o1-roster-operations） |
| ★ よってこれは「見落とし」ではなく **ADR の設計判断の帰結**だが、空白であること自体は事実 | 合成 |

### ADR-035 との関係
- ADR-035 は招待（Physical Anchor の PC 面）だけが対象で、**ADR-034 を改訂していない**（`grep "ADR-034"` = 0 件）。

## マージ / schema parity / 配布経路の材料（★ 実測 2026-09-20）

### 差分と衝突
| 事実 | 根拠 |
|---|---|
| `main...HEAD` = **251 files / +32,624 / -227**（Add 201・Modify 50・**Delete と Rename は 0**） | `git diff --stat` / `--name-status` |
| 内訳: `.steering/` 180・`docs/` 約 35・`src-tauri/` 19・`scripts/` 5・`experiments/` 4・`.claude/` 4・`.github/` 1・`.codex/` 1・root 2 | 同上 |
| ★ merge-base から見た **main 側の純増分は `.steering/_handoff/README.md` の 1 ファイルだけ**（ADR-029 は分岐点より前に共有履歴へ入っていた） | `git diff --name-status HEAD...main` / `git cat-file -e a41150e:docs/adr/ADR-029-...` |
| **衝突予測 = 1 件のみ**: `.steering/_handoff/README.md`（同じ表のセルを両側が別文字列に書き換え） | `git merge-tree --write-tree main HEAD` → exit 1・`CONFLICT (content)` 1 行だけ（★ 作業ツリーは変えていない） |
| `.github/workflows/ci.yml` の差分は **+24/-0 の追記のみ**（`loop-worktree-deny-test.sh` を check / frontend-check に追加）。`build-*` / `release` ジョブは無変更・main 側も触っていない → **衝突しない** | 同 diff |

### schema parity
| 事実 | 根拠 |
|---|---|
| `python scripts/check_schema_parity.py --dataset C:/gse-dataset` → **exit 1 / DRIFT**。`Missing variants in B: activity_label` | 実行（read-only・副作用なし） |
| ⚠️★ **この drift は main には無い。作業ブランチが新規に生んだもの**（main の `schema_dto.rs` / `schema/current.json` に `activity_label` / `ActivityCategoryDto` は 0 件） | `git show main:...` の grep = 0 |
| gse-dataset クローンは `C:\gse-dataset`・clean（最新 `dc2c76c` 2026-09-11） | `git -C /c/gse-dataset status` |
| 更新手順は「`emit_schema` → `schema/current.json` → **gse-dataset 側へコピー** → 両 repo を同期 commit」 | `docs/development-guidelines.md` §10.3（`:544-559`）/ `docs/verification-runbook.md:53-54` |

### 配布の経路（★ Q2 と直結）
| 事実 | 根拠 |
|---|---|
| GitHub Release が作られるのは **`v*` タグの push 時のみ**（`workflow_dispatch` はビルドのみで Release を作らない） | `.github/workflows/ci.yml` `on:` / `build-windows:846-852` / `release:1197-1202` |
| 配布スクリプトは **ローカルビルドを使わず**、`gh release download "$TAG"` で CI の成果物（`gse-next.exe` / `gse-submit.exe` / `*.dmg`）を取る | `make-distribution.sh:21-23,134-136` / `make-common-app-zip.sh:474-476` |
| ⚠️ **既定タグがハードコードで古い**: `make-distribution.sh` は `TAG="v0.1.23"`、`make-common-app-zip.sh` は `TAG="v0.1.24"`（`--tag` で上書き可）。最新タグは **`v0.1.35`** | 各スクリプト冒頭 / `git tag --list 'v*'` |
| 配布前に**タグの git 内容**と**実バイナリの文字列**（`strings` で `reconcile` / `o1.mode` 等）を二重検査する設計 | 同スクリプト |
| 上位 5 タグ（`v0.1.35`〜`v0.1.31`）は **main の祖先**。作業ブランチにしかないコードは**どの配布物にも入っていない** | `git merge-base --is-ancestor <tag> main` |
| ★ ブランチのコードが配布に載るのは **① main へマージ → ② 新しい `v*` タグを push → ③ 配布スクリプトに `--tag` で指定** の 3 条件が揃ったときだけ | 合成 |

### ⚠️ 未確認（★ 推測で埋めない）
- `scripts/` の `check-o1-release-readiness.sh` / `loop-run.sh` / `loop-spawn.sh` が A か M かの個別確認。
- main 側 2 コミットが触った `.steering/20260911-outcome-arbitration-and-o1-preflight/` の**記述内容**とブランチ側の整合（★ パスの交差は 0 なので git 上は無衝突だが、内容の整合は別）。

## G1 の材料（★ 実測 2026-09-20）

### 収集開始の前提条件 1〜7（所在と機械検査の有無）
| # | 内容（要旨・逐語は `preregistration.md`） | 所在 | 機械検査 |
|---|---|---|---|
| 1 | ADR-013 の実装（`meta.capabilities` / `meta.app_version` / `starve_window` / `dropped_delta`） | `:355-361`（第 17 版） | ❌ 無い（`*.py` / `*.sh` に語が 0 ヒット） |
| 2 | G-1 の修正（実行中の再押下は「前を閉じてから新規」） | 同上 | ⚠️ 実装とテストは在る（`g1.rs:370` `decide_start_action`・`:681-849` の `RotateForRestart` 群）が **`run.sh` は呼んでいない**（run.sh が名指しするのは kill switch と LogChannel の 2 本のみ） |
| 3 | 同意文書・participant-guide の記録項目表に `starve_window` / `app_version` を追記し、配布済みの電子同意フォームと突合 | 同上 | ❌ 無い（人手） |
| 4 | ゴールデン 6 本 byte-equal / schema parity / 両 OS の対のテストが緑 | 同上 | ❌ 無い（`run.sh` に `golden` / `gse-replay` / `parity` が 0 ヒット） |
| 5 | 課題ページを修正後の `build_task_pages.py` で作り直し、**配布先（Drive）を差し替える**（検査は `**` 0 枚 ＋ 陰性対照 `<strong>` 全枚数） | `:226-234`（第 18 版） | ⚠️ `build_task_pages.py --selftest` はあるが**内部ロジックの検査**。配布済み HTML を見る経路は無い |
| 6 | 記録用紙に「文字数」欄があること（§3.5 の産出量報告義務） | 同上 | ❌ ファイルの存在すら検査していない。`validate_blocks.py` は `produced_chars` 欠落を **WARN 止まり**（§3.6 の除外禁止のため） |
| 7 | **やめた人の途中までの記録の数え方**を決めて記録する（(a) §3.6 の同意撤回に当たるか (b) n に数えるか (c) 補充するか）。記録先は**改訂履歴（第 20 版以降）**＋`config.json` の `revision`。⚠️ **§3 には書かない**（凍結） | `:43-67`（第 19 版） | ❌ 決定そのものが未了 → **Q1** |
| — | ★ 「やめた」は**本人の申し出で確定する**（ADR-034 D4-2c。技術的中断・連絡の途絶・研究者の推測では「やめた」としない） | `:67` | — |

★ **`run.sh` の緑は前提条件 1〜7 を 1 つも検査していない**（run.sh 自身が `:7-9` と `:391-393` で「技術的な準備だけ」「実施の可否は研究者判断」と明記）→ 引き継ぎの記述を実測で確認。

### `run.sh` の実行結果（★ 副作用が無いことを確認して実行）
| 実行 | 結果 |
|---|---|
| `bash run.sh` | **exit 1**。FAIL 2 件 —— ① `config.json が JSON として壊れている`（★ **壊れていない。encoding の問題**） ② `受付メールが §2.12 の開示範囲から外れている`（★ `check_g1_emails.py` のクラッシュ由来）。加えて `[3]` の出力が文字化け（FAIL にはならない） |
| `PYTHONUTF8=1 bash run.sh` | **exit 0**・`[GREEN] 実施前チェック 全項目通過` |

★ cp932 問題の**実体は 2 か所**（`open()` の encoding 欠落だけではない）:
1. `run.sh:71` の `python3 -c "import json; json.load(open('config.json'))"` —— `open()` に encoding 指定が無い。
2. `scripts/check_g1_emails.py` —— `subprocess.run(..., text=True)` が node の stdout を cp932 でデコードして `UnicodeDecodeError: 'cp932' codec can't decode byte 0x83` → `r.stdout` が `None` → `AttributeError` でクラッシュ（exit≠0）。
   ★ `PYTHONUTF8=1` 単体実行では `[OK] 受付メール(2 分岐)・課題ページメールは §2.12（第 11 版）を守っている`・exit 0。

### `config.json` の `status`
| 事実 | 根拠 |
|---|---|
| 現在値 `CONFIRMATORY_IN_PROGRESS_1_OF_3` | `config.json:4` |
| ★ **この値を読むコードは 1 件も無い**（`analyze.py` / `assign.py` / `validate_blocks.py` / `check_frozen_sections.py` が読むのは `sample_roster` / `design.n_subjects` / `revision`） | grep 実測 |
| 実態は **0/3 名**（`blocks/` に `P*.json` 0 件・`results/` は `.gitkeep` のみ）。★ しかも `sample_roster.confirmatory` は **`["P017","P018"]` の 2 名**で 3 人目が未登録 | ディレクトリ実測 / `preregistration.md:91` |

### Q1 の材料（計器の現在の挙動 —— ★ 3 つが別々の答えを出している）
| 計器 | 途中でやめた人（一部ブロックだけ実施）をどう扱うか | 根拠 |
|---|---|---|
| `validate_blocks.py` | ⚠️ **FAIL**（「一部だけ未記入は記入漏れとして fail のまま」）。★ 全ブロック未記入なら「まだ実施していない」で note 止まり | `:225-259`（特に `:233`・`:244`） |
| `analyze.py`（主判定） | **静かに `skipped: True`**（8 本 HI4/LO4 が揃わない / 陽性対照は 10 本無いと skip）。結果 JSON には残る | `:692-704` |
| `analyze.py`（名簿の検査） | ★ **roster に載っていれば人数に数える**（`len(conf)` と `n_subjects` を比較） | `:127-203` |
| `analyze.py`（群判定） | ★ `skipped` の人は **`n_subjects_analysed` に数えない** | `:874-896` |
★ つまり **「名簿の n」と「解析対象の n」は別の値になりうる**。

### Q1 の材料（契約の逐語）
- `preregistration.md` §3.6（`:2174-2189`）: 「❌ **被験者を事後に除外しない**（除外規則: 事前に宣言した**同意撤回のみ**）」／
  「❌ **ブロックを事後に除外しない**（除外規則: **技術的なログ欠損・切断のみ**。事前に凍結）」。
  ★ §3.5-S「中断のあったブロックの感度分析」は **ハードウェア/OS 由来の記録欠損**（P010 のセッション分割）の話で、本人が「やめる」場合とは別物。
- `consent.md` §5（`:107-116`）: 「**途中でやめられます。** 理由を説明する必要はありません。」と
  「★ **後からデータの削除を求められます。** …★ **すでに送信されたものも対象**です。」は**別項目**。
  ★ 同意欄（`:152`）は「**いつでも中断でき、後からデータ削除を求められる**ことを理解した」。
  ⚠️ 「やめる＝削除される」とはどこにも書かれていない。

### 週の選択（G1 モードでの強制）
| 事実 | 根拠 |
|---|---|
| ⚠️ **G1 モードでも週セレクタが出る**。JSX が `g1Mode` の条件分岐で囲まれていない（同ファイルの他の多くの箇所は囲まれている） | `src/App.tsx:941-966`（対比: `:544,567,605,703,736,744,795,854,877,969-983`） |
| 週を決めているのは **既定値**（`useState<PhaseWeek>("week1_blind")`・`:243`）と**手順書のチェックボックス**だけ | `protocol.md:921-923` |
| ⚠️ `protocol.md` に `週セレクタ` / `week1_blind` の語は **0 件**（実装の変数名と手順書の文言が文書上は突き合わせられない） | grep 実測 |

### ⚠️ 未確認（★ 推測で埋めない）
- 前提条件 2 のテストが `cargo test --workspace` で緑かどうか（`run.sh` 経由では検査されない）。
- `record-sheet-confirmatory.md` に実際に「文字数」欄があるか（存在のみ確認・中身は未精読）。
- 3 人目の確証標本の募集状況。
