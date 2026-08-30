#!/bin/bash
# G1 / O1 共通 — macOS の初回セットアップ（★ 研究者が同席して 1 回だけ実行する）
#
# ⚠️★ これは「xattr を手打ちする」の置き換えである。手打ちには 4 つ問題があった:
#   1. パスがプレースホルダで、被験者ごとに違う（日本語フォルダ名を口頭で伝えていた）
#   2. パスを間違えても「効かなかった」としか分からない（切り分けができない）
#   3. quarantine が実際に消えたか、署名を壊していないかを**誰も確かめていなかった**
#   4. ⚠️ `/Applications` のアプリを消毒してしまう事故を防げない
#      （それをやるとマーカーが見えず**黙って通常モードで動く** — preregistration.md §5.4-5）
#
# ⚠️★★★ **マーカーは決め打ちにしない**（2026-08-30 に本番欠陥として実測）:
#   旧版は `MARKER="g1.mode"` の決め打ちだったので、O1 の配布物
#   （`o1.mode` を持ち `g1.mode` を持たない）では **必ず NG になり**、
#   ★ O1 の macOS 被験者は README 【1】を 1 人も完了できない状態だった。
#   ⚠️ 2 か所のゲートが緑だったのは、どちらも `--selftest`（自前 fixture に
#     `g1.mode` を作る）しか回しておらず、**配られる実体を 1 度も見ていなかった**ため。
#   → ★ 本 script は「隣にあるマーカーを読んでモードを決める」。
#     ⚠️ ゲート側は `--selftest` だけでなく **実体に対して引数なしで**回すこと
#       （`make-common-app-zip.sh` の「配布物そのもので初回セットアップ」検査）。
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
# ⚠️★ マーカーは 2 種類ある。★ どちらが隣にあるかで実験モードが決まる。
MARKER_G1="g1.mode"
MARKER_O1="o1.mode"
QUARANTINE="com.apple.quarantine"

ng() { printf 'NG: %s\n' "$*"; exit 1; }
ok() { printf 'OK: %s\n' "$*"; exit 0; }

# ★ 実際の処理。$1 = アプリを含むフォルダ
run_setup() {
  local dir="$1" app has_g1=0 has_o1=0 label expect

  app="$dir/$APP_NAME"

  [ -d "$dir" ] || ng "フォルダが見つかりません: $dir"

  # ⚠️★ /Applications を消毒しない。そこにあるアプリはマーカーを見ないので
  #   黙って通常モードで動き、ランダムプローブが復活する（§5.4-5 / D-7）。
  case "$app" in
    /Applications/*)
      ng "「アプリケーション」フォルダのアプリは対象外です。★ 展開してできた「実施用_macOS」フォルダの中のものを指定してください" ;;
  esac

  [ -d "$app" ] || ng "$APP_NAME がこのフォルダにありません（${dir}）。★ zip を展開してできたフォルダを指定してください"

  # ★ マーカーが**隣にある**ことを確かめる。これが無いと実験モードにならない。
  #   ⚠️ ここで止めるのが要点である。§5.4-5 の検査は
  #      実施を全部終えた後にしか赤くならないので、取り返しがつかない。
  [ -f "$dir/$MARKER_G1" ] && has_g1=1
  [ -f "$dir/$MARKER_O1" ] && has_o1=1

  # ⚠️★★ 両方あると `lib.rs` が起動を拒否する
  #   （"BOTH g1.mode and o1.mode are present"）。★ ここで先に止める。
  if [ "$has_g1" = 1 ] && [ "$has_o1" = 1 ]; then
    ng "${MARKER_G1} と ${MARKER_O1} が両方あります（${dir}）。★ アプリが起動できません。研究者に連絡してください"
  fi

  if [ "$has_g1" = 1 ]; then
    label="G1"
    expect="画面に「G1 モードで動作しています」と出ることを確認してください"
  elif [ "$has_o1" = 1 ]; then
    label="O1"
    # ★ O1 はスタート画面を飛ばす（App.tsx）ので G1 の帯は出ない。
    #   ⚠️ 被験者に確認させるのは同意文書 §2 逐語の「記録中」の印である
    #     （RecordingControls.tsx「記録中 · 作業の種類: ○○」）。
    expect="画面のすみに「記録中 · 作業の種類: …」と出ることを確認してください"
  else
    ng "${MARKER_G1} も ${MARKER_O1} もこのフォルダにありません（${dir}）。★ フォルダの中身を移動していないか確認してください"
  fi

  # ⚠️★★★ **`xattr` が無いと「消毒できた」と嘘をつく**（code-reviewer MEDIUM・2026-08-30）。
  #   ★ `xattr -dr … 2>/dev/null` は失敗しても止まらず、続く `xattr -pr … | grep -q .` は
  #     **入力が空になるので rc=1** ＝ 「残っていない」と読まれ、★ `OK:` が出てしまう。
  #   ⚠️ 被験者は「準備できました」を見たまま、quarantine の残った `.app` を開いて
  #     「壊れているため開けません」に当たる。→ ★ 冒頭で不在を弾く
  #     （memory: `silent-failure-in-guard-scripts` の「外部コマンド不在」型）。
  command -v xattr > /dev/null 2>&1 \
    || ng "xattr が見つかりません。★ 研究者に連絡してください（消毒できたか確かめられません）"
  command -v codesign > /dev/null 2>&1 \
    || ng "codesign が見つかりません。★ 研究者に連絡してください（署名を確かめられません）"

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

  # ★ モードを取り違えたときに読み手が気づけるよう、表示に label を出す。
  ok "準備できました（${label} モード）。$APP_NAME をダブルクリックして開き、${expect}"
}

# --------------------------------------------------------------------------
# ★ 自己検査 — ⚠️ 検査が空回りしていないことを確かめる（対照を取る）
# --------------------------------------------------------------------------
selftest() {
  local tmp fixture app appsdir out fails=0
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
  : > "$fixture/$MARKER_G1"

  # ⚠️★★ NG は**理由まで**照合する。2026-08-08 に実測で踏んだ:
  #   `/Applications` ガードを丸ごと外しても、`/Applications/gse-next.app` が
  #   存在しないので **別の理由で NG になり、テストは緑のままだった**。
  #   ★ 「NG になったこと」ではなく「**狙った理由で** NG になったこと」を見る。
  #   $1=期待(ok|ng) $2=説明 $3=出力 $4=出力に含まれるべき語
  #     ⚠️★ NG では必須。★ OK でも渡せる（2026-08-30 追加）——
  #       モードごとに **違う文面が出ること**まで見ないと、`g1.mode` 決め打ちの
  #       欠陥が「OK: で始まっているから緑」で素通りするため。
  check() {
    if [ "$1" = ok ]; then
      case "$3" in
        OK:*)
          [ -z "${4:-}" ] && return 0
          case "$3" in
            *"$4"*) return 0 ;;
            *) echo "  ✗ $2 — OK だが文面が違う（「$4」を含むはず）: 「$3」"
               fails=$((fails + 1)); return 1 ;;
          esac ;;
      esac
      echo "  ✗ $2 — 期待=OK 実際=「$3」"; fails=$((fails + 1)); return 1
    fi
    case "$3" in
      NG:*)
        case "$3" in
          *"$4"*) return 0 ;;
          *) echo "  ✗ $2 — NG だが理由が違う（「$4」を含むはず）: 「$3」"
             fails=$((fails + 1)); return 1 ;;
        esac ;;
    esac
    echo "  ✗ $2 — 期待=NG 実際=「$3」"; fails=$((fails + 1))
  }

  # 1) quarantine 付き → OK になり、消えていること
  xattr -w "$QUARANTINE" "0081;00000000;Safari;" "$app" 2>/dev/null
  out=$( (run_setup "$fixture") 2>&1 ); check ok "quarantine 付きで OK になる（G1）" "$out" "G1 モードで動作しています"
  if xattr -pr "$QUARANTINE" "$app" 2>/dev/null | grep -q .; then
    echo "  ✗ quarantine が消えていない"; fails=$((fails + 1))
  fi

  # 2) ★ 2 回目も OK（idempotent）
  out=$( (run_setup "$fixture") 2>&1 ); check ok "2 回目も OK（idempotent）" "$out"

  # 3) ⚠️ 対照: マーカーが 1 つも無ければ NG（★ ここが効かないと §5.4-5 を素通りさせる）
  mv "$fixture/$MARKER_G1" "$tmp/marker.bak"
  out=$( (run_setup "$fixture") 2>&1 ); check ng "マーカーが 1 つも無ければ NG" "$out" "も ${MARKER_O1} もこのフォルダにありません"

  # ⚠️★★★ 3b) **O1 の配布物で OK になる**（2026-08-30 追加 — ここが抜けていた）
  #   ★ 旧版は `MARKER="g1.mode"` の決め打ちで、O1 では必ず NG だった。
  #   ⚠️ この 1 件が無かったせいで、**配布物が壊れたままゲートが全部緑**だった。
  : > "$fixture/$MARKER_O1"
  out=$( (run_setup "$fixture") 2>&1 ); check ok "★ o1.mode だけでも OK になり、O1 の文面が出る" "$out" "記録中 · 作業の種類"
  # ★ 対照: G1 の文面が**出ていない**こと（★ 取り違えたら赤くする）
  case "$out" in
    *"G1 モードで動作しています"*)
      echo "  ✗ O1 なのに G1 の文面が出ている: 「${out}」"; fails=$((fails + 1)) ;;
  esac

  # ⚠️★★ 3c) 両方あると NG（★ `lib.rs` が起動を拒否するので、ここで先に止める）
  mv "$tmp/marker.bak" "$fixture/$MARKER_G1"
  out=$( (run_setup "$fixture") 2>&1 ); check ng "両方あれば NG" "$out" "が両方あります"
  rm -f "$fixture/$MARKER_O1"

  # 4) ⚠️ 対照: アプリが無ければ NG
  out=$( (run_setup "$tmp") 2>&1 ); check ng "アプリが無ければ NG" "$out" "$APP_NAME がこのフォルダにありません"

  # 5) ⚠️★★ 対照: /Applications は**ガードで**拒否する。
  #   ⚠️ ここは「NG になること」だけを見てはならない。ガードを外しても
  #     `/Applications/gse-next.app` が無ければ別の理由で NG になり、**空回りする**
  #     （2026-08-08 に実測で踏んだ）。★ 理由の文言まで照合する。
  out=$( (run_setup "/Applications") 2>&1 ); check ng "/Applications をガードで拒否する" "$out" "「アプリケーション」フォルダのアプリは対象外です"
  # ★ さらに: /Applications に**アプリが実在しても**ガードが先に効くこと（fixture で模擬）
  appsdir="$tmp/Applications-like"; mkdir -p "$appsdir"
  cp -R "$app" "$appsdir/" 2>/dev/null; : > "$appsdir/$MARKER_G1"
  out=$( (run_setup "/Applications") 2>&1 ); check ng "アプリが実在しても /Applications は拒否" "$out" "「アプリケーション」フォルダのアプリは対象外です"

  # 6) ⚠️ 対照: 署名を壊したら NG（★ 検査が本当に署名を見ているか）
  echo broken >> "$app/Contents/MacOS/gse-next"
  out=$( (run_setup "$fixture") 2>&1 ); check ng "署名が壊れていたら NG" "$out" "署名の検証に失敗しました"

  # 7) ⚠️ 対照: 存在しないフォルダは NG
  out=$( (run_setup "$tmp/no-such-dir") 2>&1 ); check ng "存在しないフォルダは NG" "$out" "フォルダが見つかりません"

  if [ "$fails" -ne 0 ]; then echo "[NG] 初回セットアップ_mac.sh --selftest: $fails 件失敗"; exit 1; fi
  # ⚠️★★★ **この自己検査が緑でも「配られる実体が動く」ことは意味しない。**
  #   ★ ここは自前の fixture を作って回しているだけである（2026-08-30 の欠陥はこの穴を通った）。
  #   → 実体に対する検査は `make-common-app-zip.sh` の「配布物そのもので初回セットアップ」側にある。
  # ⚠️★ 件数は `check` の呼び出し回数 ＋ `check` を経由しない 2 件（quarantine 消去 /
  #   O1 で G1 の文面が出ていないこと）を**数えて書く**（code-reviewer LOW・2026-08-30:
  #   ★ 旧版は「11 項目」と書いていたが `check` は 10 回で、読み手が網羅性を誤る）。
  echo "[OK] 初回セットアップ_mac.sh --selftest 緑（12 項目・NG は理由まで照合）"
  echo "     ⚠️ これは fixture の中の緑である。★ 配布物そのものは make-common-app-zip.sh が実体で回す。"
  exit 0
}

# --------------------------------------------------------------------------

if [ "${1:-}" = "--selftest" ]; then selftest; fi

# ★ 引数が無ければ「自分が置かれているフォルダ」を対象にする。
#   ＝ ドラッグして実行すれば、被験者がどこに置いていても正しく効く。
SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || ng "自分の場所を特定できません"
run_setup "${1:-$SELF_DIR}"
