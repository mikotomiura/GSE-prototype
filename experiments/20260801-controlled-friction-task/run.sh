#!/usr/bin/env bash
# G1 統制タスク実験 — 実施前チェック / 1 コマンド再現
#
#   bash run.sh              実施前チェックだけ（既定）。資材が揃えば緑・欠ければ赤
#   bash run.sh --analyze    実施前チェックのうえ、解析まで走らせる
#
# ★ 判定基準の単一真実源は preregistration.md §3（凍結）。本スクリプトはそれを変更しない。
# ⚠️ 実施は「Phase1 完了 ＋ 研究者承認による凍結解除後」。順序の決定は研究者判断であり、
#    本スクリプトは技術的な準備が整っているかだけを見る。
set -euo pipefail
cd "$(dirname "$0")"

FAIL=0
ok()   { printf '  [ OK ] %s\n' "$1"; }
bad()  { printf '  [FAIL] %s\n' "$1"; FAIL=$((FAIL + 1)); }
note() { printf '  [note] %s\n' "$1"; }

# ⚠️★ cargo のテストフィルタを走らせる (2026-08-06・/cross-review MEDIUM で判明)。
#
# ★ **`cargo test --lib <filter>` は 1 件もマッチしなくても exit 0 を返す**
#   （実測: `test result: ok. 0 passed; 0 failed; ... 271 filtered out` / rc=0）。
#   → ⚠️ テスト名を変えたりテストを消したりすると、**検査は黙って緑のまま**になる。
#   これは `silent-failure-in-guard-scripts` の「外部コマンドの rc だけを見る」型そのものである。
# ★ そこで **rc に加えて「何本通ったか」を数える**。期待本数に満たなければ赤にする。
#
# 使い方: run_cargo_filter <期待本数> <フィルタ> <ラベル>
run_cargo_filter() {
  local expect="$1" filter="$2" label="$3"
  local tmp rc passed
  tmp=$(mktemp)
  rc=0
  (cd ../.. && "$CARGO_BIN" test --quiet --manifest-path src-tauri/Cargo.toml --lib "$filter") \
    > "$tmp" 2>&1 || rc=$?
  # ★ "N passed" の N を取る。行が無ければ空 → 0 に倒す（★ 取れなかったを緑にしない）。
  passed=$(grep -oE '[0-9]+ passed' "$tmp" | head -1 | grep -oE '[0-9]+' || true)
  [ -n "$passed" ] || passed=0
  if [ "$rc" -ne 0 ]; then
    sed 's/^/    /' "$tmp"
    bad "$label の挙動テストが赤（rc=${rc}）"
  elif [ "$passed" -lt "$expect" ]; then
    sed 's/^/    /' "$tmp"
    bad "$label の挙動テストが $passed 本しか通っていない（$expect 本を期待）。★ テストが消えた/改名された可能性"
  else
    ok "$label の挙動テストが緑（$passed / $expect 本）"
  fi
  rm -f "$tmp"
}

echo "=============================================================="
echo " G1 実施前チェック (experiments/20260801-controlled-friction-task)"
echo "=============================================================="

# --- 0. 前提コマンド（不在を素通りさせない） ---------------------------------
echo
echo "[0] 前提コマンド"
if command -v python3 >/dev/null 2>&1; then
  ok "python3 = $(python3 --version 2>&1)"
else
  bad "python3 が無い。解析スクリプトは標準ライブラリのみで動くが python3 は要る"
  echo
  echo "[RED] 前提コマンドが無いため続行できない"
  exit 1
fi

# --- 1. 凍結文書 -------------------------------------------------------------
echo
echo "[1] 凍結文書"
for f in preregistration.md config.json SEED README.md notes.md env.md data.md; do
  if [ -s "$f" ]; then ok "$f"; else bad "$f が無い/空"; fi
done
if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
  ok "config.json は妥当な JSON"
else
  bad "config.json が JSON として壊れている"
fi
if grep -q 'BLOCK_ORDER_SEED=' SEED 2>/dev/null; then
  ok "SEED に BLOCK_ORDER_SEED がある"
else
  bad "SEED に BLOCK_ORDER_SEED が無い"
fi

# --- 2. 実施資材 -------------------------------------------------------------
echo
echo "[2] 実施資材"
for f in protocol.md consent.md participant-guide.md; do
  if [ -s "$f" ]; then ok "$f"; else bad "$f が無い/空（実施できない）"; fi
done
if [ -d materials ]; then ok "materials/"; else bad "materials/ が無い"; fi
# ★ 第 5 版 §2.11: 被験者の入力先は固定する（無いと「どこに打つか」が未定になる）
if [ -s writing-pad.html ]; then
  ok "writing-pad.html（被験者の入力先・§2.11）"
else
  bad "writing-pad.html が無い。被験者の入力先が固定されていない（§2.11）"
fi

# --- 3. 課題文の機械検証（§2.2 / §2.7） --------------------------------------
echo
echo "[3] 課題文の制約検証 (validate_materials.py)"
TMP_MAT=$(mktemp)
if python3 validate_materials.py > "$TMP_MAT" 2>&1; then
  sed 's/^/    /' "$TMP_MAT"
  ok "課題文の制約を満たしている"
else
  sed 's/^/    /' "$TMP_MAT"
  bad "課題文が制約を満たしていない"
fi
rm -f "$TMP_MAT"

if python3 validate_materials.py --strict >/dev/null 2>&1; then
  ok "本番用 8 題材 × 2 版が揃っている（確証セッションを回せる）"
else
  note "本番用 8 題材 × 2 版は未完成 → 回せるのは **パイロット P-1（4 ブロック）まで**"
  note "  生成: python3 assign.py --pilot"
fi

# --- 4. スクリプトの自己検証 -------------------------------------------------
echo
echo "[4] スクリプトの自己検証"
for s in assign analyze validate_blocks forms_to_blocks build_task_pages; do
  TMP_S=$(mktemp)
  if python3 "$s.py" --selftest > "$TMP_S" 2>&1; then
    ok "$s.py --selftest 緑"
  else
    sed 's/^/    /' "$TMP_S"
    bad "$s.py --selftest 赤"
  fi
  rm -f "$TMP_S"
done

# ★ 第 7 版 §2.12: 被験者への事前連絡に**題材（分野）と課題の型を書かない**と凍結した
#   （当日その場で画面提示するので教える必要が無い・§2.13）。
#   ⚠️ 一度「分野を書く」と決めて第 6 版で実装し、第 7 版で撤回した経緯がある。
#      **書き戻されたら赤にする**。node で本文生成関数を実際に呼ぶので、
#      未定義参照（実例: G1_TOPIC_TITLES の残存）も同時に捕まる。
TMP_T=$(mktemp)
if python3 ../../scripts/check_g1_emails.py > "$TMP_T" 2>&1; then
  ok "受付メールが §2.12 の開示範囲を守っている"
else
  sed 's/^/    /' "$TMP_T"
  bad "受付メールが §2.12 の開示範囲から外れている"
fi
rm -f "$TMP_T"

# ⚠️★★ 2026-08-07 の事故を再発させないためのゲート。
#   起きたこと: Apps Script の関数セレクタの選択が反映されないまま setupG1Forms を実行し、
#   buildConsentForm() が clearForm() で G1-C の全設問を削除した。
#   → 回答レコード 3 件は残ったが **どの設問への回答か失われた**（Forms に版履歴は無い）。
# ★ 対策として assertSafeToRebuild_() を入れた。**それが効いていることを毎回測る。**
#   ⚠️ 「ガードを書いた」ではなく「ガードが止める」ことを検査する
#      (0 件は通す陽性対照つき。骨抜きにすると rc=1 になることを実測済み)。
if ! command -v node > /dev/null 2>&1; then
  bad "node が無いので Form_G1 のガード検査を実行できない（★ 飛ばさず赤にする）"
else
  # ⚠️★ 件数は **出力から読む**。ここに数字を書き込むと、ケースを足したときに
  #   表示だけが古い数字のまま残り、「20 / 20 通った」が実体と無関係になる
  #   (2026-08-07 に実際に起きた: 33 ケースあるのに 20 と表示していた)。
  #   ⚠️ 読めなかったら数字を捏造せず「件数不明」と出す (0 と書くと通過に見える)。
  guard_count() {
    local n
    n=$(sed -n 's/^全 \([0-9]*\) ケース期待どおり$/\1/p' "$1" | tail -1)
    echo "${n:-件数不明}"
  }

  TMP_G=$(mktemp)
  if node ../../Form_G1/guard_test.cjs > "$TMP_G" 2>&1; then
    ok "G1 フォームの作り直しガードが効いている（$(guard_count "$TMP_G") ケース全通過）"
  else
    sed 's/^/    /' "$TMP_G"
    bad "G1 フォームの作り直しガードが期待どおり動いていない"
  fi
  rm -f "$TMP_G"

  # ⚠️★★★ G1 の **P-ID 採番と本人確認**の検査（2026-09-01 追加・起票 E-2 / E-3 / T-27）。
  #   ★ なぜ G1 のゲートで赤にするか: 採番元の Phase1 ロスターは
  #     **Phase1 / G1 / O1 の共用**であり (`docs/o1-deletion-ledger.md:179`)、
  #     ⚠️ G1 側の穴が **O1 の数週間ぶんの常時打鍵ログを別人の P-ID に混ぜる**。
  #     → 同意文書 §4-3 の「消えます」が履行不能になるので、G1 自身の準備状態である。
  #   ⚠️ `[ -f ]` で囲まない —— ★ ファイルが消えたら**黙って飛ばさず赤にする**。
  TMP_R=$(mktemp)
  if node ../../Form_G1/g1_roster_test.cjs > "$TMP_R" 2>&1; then
    ok "G1 の採番・本人確認が効いている（$(guard_count "$TMP_R") ケース全通過）"
  else
    sed 's/^/    /' "$TMP_R"
    bad "⚠️★ G1 の採番・本人確認が期待どおり動いていない（なりすまし / 二重採番の恐れ）"
  fi
  rm -f "$TMP_R"

  # ★ G1 自動提出の**受け口**（GAS `doPost`）のガード。
  #   ⚠️ 送信の成否は送信先から追えない（実行数ページはログ本文を出さず Cloud ログも開けない）。
  #   → ★ 受け口が「何を拒否するか」はローカルで測るしかない。
  #   ⚠️ 当初は各ガードが互いに冗長で **1 行ずつ壊しても赤にならなかった**（2 度踏んだ）。
  #      冗長なガードを消して 1 本ずつに整理し、★ **名前 / シークレット / サイズ上限 /
  #      保存の非握り潰し / 設定不足 / GET 拒否 / 本文なし / 0 バイト / 壊れた JSON の
  #      9 種すべてで赤になる**ことを実測済み（9 / 9）。
  TMP_S=$(mktemp)
  if node ../../Form_G1/submit_guard_test.cjs > "$TMP_S" 2>&1; then
    ok "G1 提出受け口 (doPost) のガードが効いている（$(guard_count "$TMP_S") ケース全通過）"
  else
    sed 's/^/    /' "$TMP_S"
    bad "G1 提出受け口 (doPost) のガードが期待どおり動いていない"
  fi
  rm -f "$TMP_S"

  # ★ O1 (R3-a) の受け口のガードは **ここでは赤にしない**（⚠️ 2026-08-28 に方針を決めた）。
  #   ⚠️★★★ 本スクリプトは冒頭で宣言しているとおり **G1 の技術的準備だけ**を見る。
  #     ★ O1 だけの未達で **実施中の G1 のゲートを赤にすると、G1 の判断が濁る**
  #       (code-reviewer 指摘)。
  #   → ★ O1 の受け口の検査は `scripts/check-o1-release-readiness.sh` が回す（そちらが正）。
  #     ここでは **気づけるように報告だけ**する。
  if [ -f ../../Form_O1/o1_submit_guard_test.cjs ]; then
    TMP_O=$(mktemp)
    if node ../../Form_O1/o1_submit_guard_test.cjs > "$TMP_O" 2>&1; then
      note "（参考・G1 の合否には影響しない）O1 受け口のガードは緑（$(guard_count "$TMP_O") ケース）"
    else
      note "（参考・G1 の合否には影響しない）⚠️ O1 受け口のガードが赤。★ bash scripts/check-o1-release-readiness.sh を見ること"
    fi
    rm -f "$TMP_O"
  fi

  # ★ 同じ扱いで O1 のフォームビルダー（2026-08-28 追加）。
  #   ⚠️★★★ ここに置く理由は **G1 のフォームを壊さないことの見張り**だからである:
  #     この検査は「O1 のビルダーが G1-C / G1-M / G1-S の ID を拒否するか」を測っており、
  #     ⚠️ 赤くなるということは **G1 のフォームが破壊されうる状態**を意味する
  #     （2026-08-07 に G1-C の全設問を消した事故がある）。
  #   ⚠️ それでも G1 の合否は動かさない（上のブロックと同じ方針）。★ 報告だけする。
  if [ -f ../../Form_O1/o1_form_builder_test.cjs ]; then
    TMP_FB=$(mktemp)
    if node ../../Form_O1/o1_form_builder_test.cjs > "$TMP_FB" 2>&1; then
      note "（参考・G1 の合否には影響しない）O1 フォームビルダーのガードは緑（$(guard_count "$TMP_FB") ケース）"
    else
      note "（参考・G1 の合否には影響しない）⚠️★★ O1 フォームビルダーのガードが赤。★ G1 のフォームを壊す経路が開いている可能性がある"
    fi
    rm -f "$TMP_FB"
  fi

  # ★ 変異テスト（★ 上の 89 ケースが**空回りしていない**ことの根拠はここにしか無い）。
  #   ⚠️ code-reviewer 指摘 2026-08-28: 作った直後は**どのランナーからも呼ばれていなかった**。
  #     ★ この直下のブロックが自分で「呼ばれないテストは無いのと同じ」と書いたのと同じ形の
  #     孤児を 1 本増やしていた。→ ★ 繋ぐ。
  #   ⚠️ 20 変異ぶん node を起動するので数十秒かかる。★ G1 の合否は動かさない。
  if [ -f ../../Form_O1/o1_form_builder_mutation_test.sh ]; then
    if bash ../../Form_O1/o1_form_builder_mutation_test.sh > /dev/null 2>&1; then
      note "（参考・G1 の合否には影響しない）O1 フォームビルダーの変異テストは全部赤（＝検査が効いている）"
    else
      note "（参考・G1 の合否には影響しない）⚠️★★ O1 フォームビルダーの変異テストに**すり抜け**がある。★ ガード検査の緑は当てにならない"
    fi
  fi

  # ★ 配布まわり（受付メール 1 通運用・課題ページのフォルダ探索・共有し忘れの検出）。
  #   ⚠️★ 2026-08-07 のレビューで **このテストがどのランナーからも呼ばれていない**ことが
  #   分かった（参照は README と .steering だけ）。★ 呼ばれないテストは無いのと同じなので繋ぐ。
  #   ⚠️ ここには **bash (`prepare-subjects.sh` の `DRIVE_PREFIX`) と GAS
  #   (`G1_MATERIALS_FOLDER_PREFIX`) の一致**を確かめる検査が入っている。
  #   ★ 片方だけ直すと受付メールが黙って 2 便運用に落ちるので、run.sh から必ず走らせる。
  TMP_M=$(mktemp)
  if node ../../Form_G1/materials_autosend_test.cjs > "$TMP_M" 2>&1; then
    ok "配布まわりのガードが効いている（$(grep -c '✅' "$TMP_M") 項目全通過）"
  else
    sed 's/^/    /' "$TMP_M"
    bad "配布まわりのガードが期待どおり動いていない"
  fi
  rm -f "$TMP_M"
fi

# --- 5. アプリ側の前提 -------------------------------------------------------
# ★ 第 5 版 §5.4 で検査の意図を置き換えた。
#   旧: 「G1 はコード変更ゼロで実施できる」→ src-tauri/ src/ に変更が無いこと
#   新: 「G1 が要求する変更 (プローブ kill switch) が入っており、それ以外の未コミット変更が無い」
#
#   ⚠️ 旧検査は `git status` を見るだけなので、**変更をコミットした瞬間に黙って緑に戻った**。
#      すなわち「コード変更ゼロ」を検査しているつもりで、実際には何も検査していなかった
#      (silent pass)。kill switch の存在を直接見ることで、失われたら赤になるようにする。
echo
echo "[5] アプリ側の前提（プローブ kill switch・§5.4）"
KILL_SWITCH_FN="src-tauri/src/analysis/probe_scheduler.rs"
KILL_SWITCH_USE="src-tauri/src/lib.rs"
if [ -f "../../$KILL_SWITCH_FN" ] && [ -f "../../$KILL_SWITCH_USE" ]; then
  if grep -q 'pub fn probes_disabled_by_env' "../../$KILL_SWITCH_FN" \
     && grep -q 'GSE_DISABLE_PROBES' "../../$KILL_SWITCH_USE"; then
    ok "プローブ kill switch がある（GSE_DISABLE_PROBES / probes_disabled_by_env）"
    # ★ grep は「文字列があること」しか見ない。挙動（★ 未設定で無効化しないこと）は
    #   Rust のユニットテストが持っているので、cargo があるなら実際に走らせる。
    #   ⚠️ cargo が無い環境（被験者端末は CI ビルド済みバイナリを使う）では**飛ばしたことを明示**する。
    #      黙って飛ばすと silent-failure-in-guard-scripts の「外部コマンド不在で素通り」になる。
    CARGO_BIN=$(command -v cargo || echo "$HOME/.cargo/bin/cargo")
    if [ -x "$CARGO_BIN" ]; then
      # ★ 2 本ある（未設定で無効化しない ／ "1" のときだけ無効化する）。
      #   ⚠️ 本数まで見るのは、0 件マッチでも rc=0 になるためである（run_cargo_filter のコメント）。
      run_cargo_filter 2 probe_scheduler::tests::probes_kill_switch "kill switch"
    else
      note "cargo が無いので kill switch の挙動テストは飛ばした（★ 飛ばしたことを明示している）"
      note "  → 実施後の客観検証は validate_blocks.py --dataset（probe 行 0）で行う"
    fi
  else
    bad "プローブ kill switch が見つからない（GSE_DISABLE_PROBES / probes_disabled_by_env）"
    note "  §2.6 は「アプリ内プローブを使わない」と凍結し、§3.6 が事後のブロック除外を"
    note "  禁じているので、**実施前に止めるしかない**（§5.4）"
  fi
else
  note "src-tauri/ が見つからない（この repo の外で走らせている）"
fi

# --- 5.1 セッションログを開く場所（空 NDJSON = 空の .age を防ぐ） --------------
# ⚠️ ★ 2026-08-05 の実測: `tauri-plugin-single-instance` に止められた 2 個目のプロセスは、
#    **止められる前に NDJSON を作ってから死ぬ**（0 行のファイルができた）。
#    `gse-submit` は最新 1 本を選ぶので、★ 被験者が「提出する」を押すと**空の .age** が出る。
# ★ 直し方は順序である（一次資料 `tauri` 2.10.2 `src/app.rs`）:
#    プラグインの exit(0) は Builder::build() の中、`.setup()` は App::run() の中。
#    → ログを開くのは `.setup()` の中（`log_channel.start(log_path, ..)`）でなければならない。
# ⚠️ grep は「文字列があること」しか見ないので、挙動は下の cargo test が持つ。
LOGGER_WIRING="src-tauri/src/lib.rs"
if [ -f "../../$LOGGER_WIRING" ]; then
  if grep -q 'log_channel\.start(log_path' "../../$LOGGER_WIRING" \
     && ! grep -q 'SessionLogger::start(' "../../$LOGGER_WIRING"; then
    ok "セッションログを開くのは setup() の中（2 個目のプロセスが空 NDJSON を残さない）"
    CARGO_BIN=$(command -v cargo || echo "$HOME/.cargo/bin/cargo")
    if [ -x "$CARGO_BIN" ]; then
      # ★ 2 本ある（start() までファイルを作らない ／ 先に送った行を落とさず meta が 1 行目）。
      run_cargo_filter 2 logger::tests::log_channel "LogChannel"
    else
      note "cargo が無いので LogChannel の挙動テストは飛ばした（★ 飛ばしたことを明示している）"
    fi
  else
    bad "セッションログを起動時点で開いている（lib.rs が SessionLogger::start を呼んでいる）"
    note "  ★ 2 個目のプロセスが空の NDJSON を残し、gse-submit が**空の .age** を作る"
  fi
else
  note "src-tauri/src/lib.rs が見つからない（この repo の外で走らせている）"
fi

if git rev-parse --git-dir >/dev/null 2>&1; then
  DIRTY=$(git status --porcelain -- ../../src-tauri ../../src 2>/dev/null | wc -l | tr -d ' ')
  if [ "$DIRTY" = "0" ]; then
    ok "src-tauri/ と src/ に未コミットの変更が無い（実施は検証済みビルドで行う）"
  else
    bad "src-tauri/ または src/ に未コミットの変更がある（$DIRTY 件）"
    note "  ★ 未検証のビルドで実験を回さないこと（kill switch 以外の変更は G1 に不要）"
  fi
else
  note "git repo の外なのでコミット状態のチェックを飛ばした"
fi

# --- 6. データの状態 ---------------------------------------------------------
echo
echo "[6] データの状態"
SPECS=0
if [ -d blocks ]; then
  SPECS=$(find blocks -maxdepth 1 -name 'P*.json' 2>/dev/null | wc -l | tr -d ' ')
fi
if [ "$SPECS" = "0" ]; then
  note "blocks/ に割付ファイルが無い = **まだ 1 件もデータを取っていない**（事前登録どおり）"
  note "  実施後の手順: python3 assign.py --subject P0xx --json > blocks/P0xx.json"
  note "                → 各 block に \"file\" と \"produced_chars\" を書き足す"
  note "                → python3 forms_to_blocks.py --csv <G1-M回答.csv> --subject P0xx --write"
  note "                → python3 validate_blocks.py --dataset ~/gse-dataset"
else
  ok "blocks/ に割付ファイルが $SPECS 件ある"
  # ★ 転記ミスの検出（除外も判定もしない・§3.6 に触れない）
  TMP_VB=$(mktemp)
  if python3 validate_blocks.py > "$TMP_VB" 2>&1; then
    sed 's/^/    /' "$TMP_VB"
    ok "割付ファイルの転記に問題なし"
  else
    sed 's/^/    /' "$TMP_VB"
    bad "割付ファイルに転記ミスの疑いがある（validate_blocks.py）"
  fi
  rm -f "$TMP_VB"
fi

# --- 判定 -------------------------------------------------------------------
echo
echo "=============================================================="
if [ "$FAIL" -ne 0 ]; then
  echo " [RED] 実施前チェック 失敗 $FAIL 件。上の [FAIL] を潰すこと。"
  echo "=============================================================="
  exit 1
fi
echo " [GREEN] 実施前チェック 全項目通過"
echo "   → 資材・プロトコル・同意・解析スクリプトは揃っている。"
echo "   ⚠️ 実施の可否（特に Phase1 の凍結解除前に回してよいか）は **研究者判断**。"
echo "=============================================================="

# --- 解析（明示的に要求されたときだけ） --------------------------------------
if [ "${1:-}" = "--analyze" ]; then
  echo
  if [ "$SPECS" = "0" ]; then
    echo "[NG] --analyze が指定されたが blocks/ に割付ファイルが無い（データ未取得）"
    exit 1
  fi
  DATASET="${GSE_DATASET:-${DATASET_ROOT:-$HOME/gse-dataset}}"
  echo "[analyze] dataset=$DATASET"
  echo "⚠️ preregistration.md §3.4 の見る順序（操作チェック → positive control → FS-A/FS-B）は"
  echo "   出力の並び順で強制される。順序を飛ばして読まないこと。"
  python3 analyze.py --dataset "$DATASET" --blocks-dir blocks --out results/metrics.json
elif [ $# -gt 0 ]; then
  echo
  echo "[NG] 不明な引数: $*  (使えるのは --analyze のみ)"
  exit 2
fi
