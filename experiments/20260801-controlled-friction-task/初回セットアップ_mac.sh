#!/bin/bash
# G1 実験 — macOS の初回セットアップ（★ 研究者が同席して 1 回だけ実行する）
#
# ⚠️★ これは「xattr を手打ちする」の置き換えである。手打ちには 4 つ問題があった:
#   1. パスがプレースホルダで、被験者ごとに違う（日本語フォルダ名を口頭で伝えていた）
#   2. パスを間違えても「効かなかった」としか分からない（切り分けができない）
#   3. quarantine が実際に消えたか、署名を壊していないかを**誰も確かめていなかった**
#   4. ⚠️ `/Applications` のアプリを消毒してしまう事故を防げない
#      （それをやると g1.mode が見えず**黙って通常モードで動く** — preregistration.md §5.4-5）
#
# ★ 使い方（★ パスは 1 文字も打たない）:
#   1. ターミナルを開く（Spotlight で "terminal"）
#   2. `bash ` と打つ（★ 末尾に半角スペース）
#   3. ★ このファイルを Finder から**ターミナルの窓へドラッグ**する（パスが入る）
#   4. Enter
#
# ★ 出力は「OK」か、理由つきの「NG」のどちらか 1 行で終わる。
# ★ 何度実行しても壊れない（idempotent）。
#
# ⚠️ `xattr -cr` は使わない（全属性を消して署名を壊すことがある）。
# ⚠️ sudo は使わない。⚠️ このフォルダの外には触れない。
#
# 自己検査: bash 初回セットアップ_mac.sh --selftest

set -u

APP_NAME="gse-next.app"
MARKER="g1.mode"
QUARANTINE="com.apple.quarantine"

ng() { printf 'NG: %s\n' "$*"; exit 1; }
ok() { printf 'OK: %s\n' "$*"; exit 0; }

# ★ 実際の処理。$1 = アプリを含むフォルダ
run_setup() {
  local dir="$1" app marker
  app="$dir/$APP_NAME"
  marker="$dir/$MARKER"

  [ -d "$dir" ] || ng "フォルダが見つかりません: $dir"

  # ⚠️★ /Applications を消毒しない。そこにあるアプリは g1.mode を見ないので
  #   黙って通常モードで動き、ランダムプローブが復活する（§5.4-5 / D-7）。
  case "$app" in
    /Applications/*)
      ng "「アプリケーション」フォルダのアプリは対象外です。★ 展開してできた「G1_実施用_macOS」フォルダの中のものを指定してください" ;;
  esac

  [ -d "$app" ] || ng "$APP_NAME がこのフォルダにありません（${dir}）。★ zip を展開してできたフォルダを指定してください"

  # ★ g1.mode が**隣にある**ことを確かめる。これが無いと実験モードにならない。
  #   ⚠️ ここで止めるのが要点である。§5.4-5 の検査は
  #      実施を全部終えた後にしか赤くならないので、取り返しがつかない。
  [ -f "$marker" ] || ng "$MARKER がこのフォルダにありません（${dir}）。★ フォルダの中身を移動していないか確認してください"

  # ★ 消毒（idempotent。付いていなくてもエラーにしない）
  xattr -dr "$QUARANTINE" "$app" 2>/dev/null

  # ★★ 消えたことを**確かめる**。⚠️ ここを確かめないと「打ったが効いていない」を見逃す。
  if xattr -pr "$QUARANTINE" "$app" 2>/dev/null | grep -q .; then
    ng "$QUARANTINE が残っています。★ 研究者に連絡してください（権限の問題かもしれません）"
  fi

  # ★★ 署名を壊していないことを確かめる。⚠️ 壊すと「壊れているため開けません」が**本当に**起きる。
  if ! codesign --verify --strict "$app" 2>/dev/null; then
    ng "署名の検証に失敗しました。★ このフォルダは使わず、zip を展開し直してください"
  fi

  ok "準備できました。$APP_NAME をダブルクリックして開き、画面に「G1 モードで動作しています」と出ることを確認してください"
}

# --------------------------------------------------------------------------
# ★ 自己検査 — ⚠️ 検査が空回りしていないことを確かめる（対照を取る）
# --------------------------------------------------------------------------
selftest() {
  local tmp fixture app rc out fails=0
  tmp=$(mktemp -d) || { echo "[NG] 作業ディレクトリを作れない"; exit 1; }
  # shellcheck disable=SC2064
  trap "rm -rf '$tmp'" EXIT

  fixture="$tmp/G1_実施用_macOS"
  app="$fixture/$APP_NAME"
  mkdir -p "$app/Contents/MacOS"
  # ★ 本物の mach-O を入れる（ad-hoc 署名できるようにするため）
  cp /bin/echo "$app/Contents/MacOS/gse-next" || { echo "[NG] fixture を作れない"; exit 1; }
  cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>gse-next</string>
<key>CFBundleIdentifier</key><string>test.gse.selftest</string>
<key>CFBundleName</key><string>gse-next</string>
<key>CFBundlePackageType</key><string>APPL</string>
</dict></plist>
PLIST
  codesign --force --sign - "$app" 2>/dev/null || { echo "[NG] fixture に ad-hoc 署名できない"; exit 1; }
  : > "$fixture/$MARKER"

  check() { # $1=期待(ok|ng) $2=説明 $3=出力
    if [ "$1" = ok ]; then
      case "$3" in OK:*) return 0 ;; esac
    else
      case "$3" in NG:*) return 0 ;; esac
    fi
    echo "  ✗ $2 — 期待=$1 実際=「$3」"; fails=$((fails + 1))
  }

  # 1) quarantine 付き → OK になり、消えていること
  xattr -w "$QUARANTINE" "0081;00000000;Safari;" "$app" 2>/dev/null
  out=$( (run_setup "$fixture") 2>&1 ); check ok "quarantine 付きで OK になる" "$out"
  if xattr -pr "$QUARANTINE" "$app" 2>/dev/null | grep -q .; then
    echo "  ✗ quarantine が消えていない"; fails=$((fails + 1))
  fi

  # 2) ★ 2 回目も OK（idempotent）
  out=$( (run_setup "$fixture") 2>&1 ); check ok "2 回目も OK（idempotent）" "$out"

  # 3) ⚠️ 対照: g1.mode が無ければ NG（★ ここが効かないと §5.4-5 を素通りさせる）
  mv "$fixture/$MARKER" "$tmp/marker.bak"
  out=$( (run_setup "$fixture") 2>&1 ); check ng "g1.mode が無ければ NG" "$out"
  mv "$tmp/marker.bak" "$fixture/$MARKER"

  # 4) ⚠️ 対照: アプリが無ければ NG
  out=$( (run_setup "$tmp") 2>&1 ); check ng "アプリが無ければ NG" "$out"

  # 5) ⚠️ 対照: /Applications は拒否する
  out=$( (run_setup "/Applications") 2>&1 ); check ng "/Applications を拒否する" "$out"

  # 6) ⚠️ 対照: 署名を壊したら NG（★ 検査が本当に署名を見ているか）
  echo broken >> "$app/Contents/MacOS/gse-next"
  out=$( (run_setup "$fixture") 2>&1 ); check ng "署名が壊れていたら NG" "$out"

  # 7) ⚠️ 対照: 存在しないフォルダは NG
  out=$( (run_setup "$tmp/no-such-dir") 2>&1 ); check ng "存在しないフォルダは NG" "$out"

  if [ "$fails" -ne 0 ]; then echo "[NG] 初回セットアップ_mac.sh --selftest: $fails 件失敗"; exit 1; fi
  echo "[OK] 初回セットアップ_mac.sh --selftest 緑（7 項目・対照つき）"
  exit 0
}

# --------------------------------------------------------------------------

if [ "${1:-}" = "--selftest" ]; then selftest; fi

# ★ 引数が無ければ「自分が置かれているフォルダ」を対象にする。
#   ＝ ドラッグして実行すれば、被験者がどこに置いていても正しく効く。
SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || ng "自分の場所を特定できません"
run_setup "${1:-$SELF_DIR}"
