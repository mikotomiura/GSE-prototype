#!/usr/bin/env bash
# issue 002 acceptance — analyze.py の n 未達ゲートと 登録 k / 解析 m（前提条件 8 / A-2）
# ⚠️ cwd は worktree のルート。相対パスで書く。
set -u

AN="experiments/20260801-controlled-friction-task/analyze.py"
CFG="experiments/20260801-controlled-friction-task/config.json"
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }
need () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}

echo "[002] analyze.py の収集完了ゲートと 登録 k / 解析 m"

# AC 1: selftest が緑
if python3 "$AN" --selftest >/dev/null 2>&1; then
  ok "AC1 analyze.py --selftest が exit 0"
else
  ng "AC1 analyze.py --selftest が赤"
fi

# AC 2-5: 門の分岐と矛盾検査
need "$AN" "recruitment_closed" "AC2 recruitment_closed を読んでいる"
need "$AN" "registered_k"       "AC5 registered_k を読んでいる"

# AC 6: 出力に sample_counts（登録 k / 解析 m）
need "$AN" "sample_counts" "AC6 出力に sample_counts がある"
need "$AN" "analysed_m"    "AC6 出力に analysed_m がある"

# AC 2/3/4/5 の selftest ケースが在ること（★ 4 状態を対照つきで固定しているか）
for w in "締めていなければ" "締めた後は" "完了者 0 名" "registered_k の矛盾"; do
  if grep -qF -- "$w" "$AN"; then ok "AC2-5 selftest ケース: ${w}"; else ng "AC2-5 selftest ケースが無い: ${w}"; fi
done

# AC 5 の実装: ⚠️ 既に在るものを作り直していないか（★ 重複実装の検出）
#   Fisher の n<2 非適用は :590-594 に在る。行が 2 つになっていたら重複を疑う。
n_fisher=$(grep -cF "def fisher_combine" "$AN")
if [ "$n_fisher" = "1" ]; then ok "AC5 fisher_combine が 1 つだけ（重複実装なし）"; else ng "AC5 fisher_combine が ${n_fisher} 個ある（重複実装）"; fi

# AC 7: 版を動かしていない
need "$AN" "PREREG_REVISION = 20" "AC7 PREREG_REVISION が 20 のまま"
if python3 -c "
import json,sys
c=json.load(open('${CFG}'))
r=c.get('revision',{})
sys.exit(0 if r.get('version')==20 else 1)
"; then ok "AC7 config.json の revision.version が 20 のまま"; else ng "AC7 config.json の revision.version が 20 でない"; fi

# AC 7b: config.json に 2 キーが在り、既定が緩くない（closed の既定は false）
if python3 -c "
import json,sys
c=json.load(open('${CFG}'))
r=c.get('sample_roster',{})
rc=r.get('recruitment_closed')
ok = isinstance(rc,dict) and rc.get('closed') is False and isinstance(r.get('registered_k'),int)
sys.exit(0 if ok else 1)
"; then ok "AC7b sample_roster に registered_k と recruitment_closed(closed=false) がある"
else ng "AC7b registered_k / recruitment_closed(closed=false) が無い、または既定が false でない"; fi

# AC 7c: ⚠️ n_subjects を動かしていない（凍結）
if python3 -c "
import json,sys
c=json.load(open('${CFG}'))
sys.exit(0 if c.get('design',{}).get('n_subjects')==3 else 1)
"; then ok "AC7c design.n_subjects が 3 のまま"; else ng "AC7c design.n_subjects が 3 でない"; fi

# AC 8: G1 ゲートの版 parity が緑（★ 出力の語で確かめる。ゲート全体の exit code は未達 3 件があるため見ない）
if bash scripts/check-g1-collection-readiness.sh 2>&1 | grep -qF "config.json の revision が事前登録と同じ版 (20)"; then
  ok "AC8 G1 ゲートの版 parity が緑"
else
  ng "AC8 G1 ゲートの版 parity が緑でない"
fi

# ⚠️ 欠員検査を緩めていないこと（一次の語が残っているか）
need "$AN" "確証標本に欠員がある" "AC-guard 欠員検査を消していない"

echo "  ---- 失敗 ${FAILS} 件 ----"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
