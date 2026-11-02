#!/bin/bash
# 毎日の cargo 掃除 (launchd local.gse.cargo-sweep) を導入・再導入する。
#
# ⚠️★★★ なぜ repo に置くか (code-reviewer 指摘 #3, 2026-08-31):
#   初版は実体が `~/.local/bin/gse-cargo-sweep.sh` と `~/Library/LaunchAgents/*.plist` にしか
#   無く、**repo の外・未追跡**だった。→ レビューもできず、再現もできず、
#   壊れても誰も気づかない。★ 正本を repo に置き、インストーラを通してのみ配置する。
#
# ★ 冪等。何度実行してもよい。
#
# 使い方:
#   bash scripts/maintenance/install-cargo-sweep-launchd.sh          # 導入 + 検証
#   bash scripts/maintenance/install-cargo-sweep-launchd.sh --verify # 現状の検査のみ (書き込まない)
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/scripts/maintenance/gse-cargo-sweep.sh"
DEST="$HOME/.local/bin/gse-cargo-sweep.sh"
LABEL="local.gse.cargo-sweep"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG="$HOME/Library/Logs/gse-cargo-sweep.log"

VERIFY_ONLY=0
[ "${1:-}" = "--verify" ] && VERIFY_ONLY=1

fail=0
ok()   { printf '  ✅ %s\n' "$1"; }
ng()   { printf '  ❌ %s\n' "$1"; fail=$((fail + 1)); }
warn() { printf '  ⚠️  %s\n' "$1"; }

# ── 検査 (--verify でも導入後でも同じものを通す) ────────────────────────
verify() {
  echo "── 検査 ──"

  if command -v cargo-sweep >/dev/null 2>&1; then
    ok "cargo-sweep がある: $(command -v cargo-sweep)"
  else
    ng "cargo-sweep が無い (これが無いと定期ジョブは毎回 exit 1 する)"
  fi

  if [ -x "$DEST" ]; then
    ok "掃除スクリプトが実行可能: $DEST"
  else
    ng "掃除スクリプトが無い / 実行できない: $DEST"
  fi

  # ★ 正本と複製がずれていないか。⚠️ ずれたまま気づかないのが初版の欠陥だった。
  if [ -f "$DEST" ] && cmp -s "$SRC" "$DEST"; then
    ok "複製が正本と一致している (scripts/maintenance/gse-cargo-sweep.sh)"
  elif [ -f "$DEST" ]; then
    ng "複製が正本とずれている。★ 本スクリプトを再実行して上書きすること"
  fi

  if [ -f "$PLIST" ]; then
    ok "plist がある: $PLIST"
  else
    ng "plist が無い: $PLIST"
  fi

  # ⚠️ plist が「ある」ことと launchd に「積まれている」ことは別。両方見る。
  if launchctl list "$LABEL" >/dev/null 2>&1; then
    ok "launchd に登録されている ($LABEL)"
  else
    ng "launchd に登録されていない ($LABEL)"
  fi

  # ⚠️ plist の ProgramArguments が実在するパスを指しているか (壊れたリンクを黙って積まない)
  if [ -f "$PLIST" ]; then
    prog="$(/usr/libexec/PlistBuddy -c 'Print :ProgramArguments:0' "$PLIST" 2>/dev/null || true)"
    if [ -n "$prog" ] && [ -x "$prog" ]; then
      ok "plist の指すプログラムが実在する: $prog"
    else
      ng "plist の指すプログラムが無い / 実行できない: ${prog:-(読めない)}"
    fi
  fi

  if [ -f "$LOG" ]; then
    ok "ログがある: $LOG (最終行: $(tail -1 "$LOG" 2>/dev/null | cut -c1-60))"
  else
    warn "ログがまだ無い (1 度も走っていない)"
  fi

  echo
  if [ "$fail" -eq 0 ]; then
    echo "✅ 定期掃除 (毎日) は導入済みです (通過 / 未達 0)"
  else
    echo "❌ 未達 ${fail} 件。上の ❌ を消してください"
  fi
  return "$fail"
}

if [ "$VERIFY_ONLY" -eq 1 ]; then
  verify
  exit $?
fi

# ── 導入 ───────────────────────────────────────────────────────────────
echo "── 導入 ──"

# 1) cargo-sweep
if command -v cargo-sweep >/dev/null 2>&1; then
  echo "  cargo-sweep: すでにある ($(command -v cargo-sweep))"
elif command -v cargo >/dev/null 2>&1; then
  echo "  cargo-sweep: cargo install cargo-sweep を実行します (数分かかります)"
  cargo install cargo-sweep || echo "  ⚠️ cargo install に失敗しました (下の検査で ❌ になります)"
else
  # ⚠️★★★ 2026-08-31 に実際に踏んだ状態: `~/.cargo/bin/*` は 13 個すべて `rustup` への
  #   symlink だが、**rustup 本体だけが消えていた** (`file` で broken symbolic link)。
  #   ★ toolchain 実体 (`~/.rustup/toolchains/*/bin/cargo`) は無事だったので、
  #   cargo が「無い」のではなく「shim が壊れている」状態である。混同しないこと。
  echo "  ⚠️ cargo が見つかりません。cargo-sweep を入れられません。"
  echo "     ★ ~/.cargo/bin/cargo が rustup への壊れた symlink になっていないか確認:"
  echo "         file ~/.cargo/bin/cargo"
  echo "     ★ 壊れていたら rustup を入れ直す:"
  echo "         curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --no-modify-path -y"
fi

# 2) 掃除スクリプトを正本からコピー
mkdir -p "$HOME/.local/bin"
cp "$SRC" "$DEST"
chmod +x "$DEST"
echo "  配置: $DEST"

# 3) plist を $HOME から生成する (★ パスを直書きした plist を追跡しないため)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${DEST}</string>
    </array>
    <!-- 毎日 03:00。スリープ中なら次回起床時に実行される。 -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>3</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <!-- CI ランナーと競合しないよう低優先度で走らせる -->
    <key>LowPriorityIO</key>
    <true/>
    <key>Nice</key>
    <integer>10</integer>
</dict>
</plist>
PLIST_EOF
echo "  生成: $PLIST"

# 4) launchd へ積み直す (★ 冪等にするため一度降ろしてから積む)
uid="$(id -u)"
launchctl bootout "gui/${uid}/${LABEL}" 2>/dev/null || true

# ⚠️ `bootout` の直後に `bootstrap` すると、前インスタンスが未解放で
#   `Bootstrap failed: 5: Input/output error` になることがある (既知の競合)。
#   ★ 少し待って数回試してから旧 API へ落とす。
booted=0
for _ in 1 2 3; do
  if launchctl bootstrap "gui/${uid}" "$PLIST" 2>/dev/null; then
    echo "  launchd: bootstrap 済み"
    booted=1
    break
  fi
  sleep 1
done
if [ "$booted" -eq 0 ]; then
  # ★ 古い macOS / 一部の環境では bootstrap が使えないので load へ落とす。
  launchctl load "$PLIST" 2>/dev/null && echo "  launchd: load 済み (旧 API)" \
    || echo "  ⚠️ launchd への登録に失敗しました (下の検査で ❌ になります)"
fi

echo
verify
