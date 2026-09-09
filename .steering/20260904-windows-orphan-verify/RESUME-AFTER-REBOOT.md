# 再起動後に読むファイル（§1-C 試行2 の結果確認 → §2 へ）

> ★ このファイルは 2026-09-09 14:40 頃、C 試行2 のために `shutdown /r` を実行する
> **直前**に書いた。新セッション（`/clear` 後）はまずこれを読んでから続行すること。

## 直前の状態（試行2）

- ビルド: commit `22538cc` の `src-tauri/target/release/gse-next.exe`（`o1.mode` あり = O1モード）
- §1 の A/B/壊れ/べき等、§3（idle hit-test）は実機確認済み。詳細:
  `evidence-s1-A-B.md`（A/B/壊れ/べき等 + C 試行1 の失敗記録）/ `evidence-s3-overlay.md`
- ⚠️ **C 試行1 は前提不成立で不採用**（`decisions.md` 判断1）。前回は
  `session_end` の時刻（05:24:33）と実際の再起動時刻（14:26:18）の間に**9時間のギャップ**があり、
  GSE が再起動時点で既に終了していた（原因不明。`shutdown /r /t 60` をキャンセルした可能性はあるが
  検証できなかった）。

## ★ 試行2 の実行内容（この直後に実施する）

- 対象ファイル: `gse_o1_20260909_053529.ndjson`
  （2026-09-09 14:35 起動・PID 31540。確認時点で feat 行 211、`session_end` なし）
- 実行コマンド: `shutdown /r /t 15 /c "GSE C検証 試行2"`（**キャンセルしない**。前回のような
  長い遅延を挟まない — 遅延中に何かでキャンセルされる余地を作らないため）
- 実行時刻: このファイル保存直後、Bash ツールで即座に実行する（正確な実行時刻はこの後の
  ツール呼び出しの結果、または `net stats workstation` の新しい起動時刻から逆算できる）
- ⚠️ このコマンド実行と同時に **このセッションは強制終了する**（想定通り）

## ★ まずやること: 試行2 の結果を判定する

```bash
f="/c/Users/johnd/Documents/GSE-sessions/gse_o1_20260909_053529.ndjson"
tail -3 "$f"
grep -o '"session_end":[0-9]\+' "$f" || echo "(session_end なし)"
grep -F "O1 orphan sweep" "/c/Users/johnd/Documents/GSE-sessions/gse-app.log" | tail -10
net stats workstation   # システム起動時刻（現在時刻との差でギャップの有無をまず確認）
date
tasklist | grep -i gse || echo "(GSE プロセスなし)"
```

### ★★★ 最初に必ずやること: ギャップ確認（試行1 の反省）

`net stats workstation` の起動時刻と現在時刻の差が **数分以内**であることをまず確認する。
もし前回のように大きなギャップ（数時間以上）があれば、`session_end` の時刻が再起動の
**前**に付いた通常クローズなのか、再起動によるものなのか、また判定不能になる。
ギャップが小さければ、以降の判定表がそのまま使える。

### 判定の分岐

| 観測 | 意味 |
|---|---|
| `session_end` が**再起動直後、GSE をまだ起動していない時点で既にある** | tao が `WM_ENDSESSION` を `CloseRequested` に翻訳している |
| `session_end` が無い状態で残っている → **GSE を起動した後**に付く、ログに `O1 orphan sweep: closed ... gse_o1_20260909_053529.ndjson` が出る | 翻訳されない。orphan sweep（起動時の回収）だけが頼り、という設計上の前提が実証される（B と同じ経路） |
| ログイン後に GSE が**自動起動していない**場合 | GSE は自動起動登録されていない（手動で `target/release/gse-next.exe` を起動してから上のログを見る） |

⚠️ **どちらの結果でも「正常」である**（`decisions.md` 判断2 は「翻訳されなくても直る実装にした」
と明記している）。★ 重要なのはどちらだったかを実測として記録すること。

## その後にやること

1. `gse_o1_20260909_053529.ndjson` を削除する（証跡は `evidence-s1-A-B.md` に転記後）。
2. `evidence-s1-A-B.md` に「C: OS 再起動（試行2）」として結果を追記し、`decisions.md` に
   判断2（試行2 の確定結果）を追加する。
3. `tasklist.md` の §1 C 行を `[x]` にする。

## 続けてやること: §2（稼働コスト・8時間 1本）

`.steering/20260904-windows-orphan-verify/tasklist.md` の §2 セクションを参照。
★ **§2 は対照 (without-gse) を回さない**（`0-1b` により廃止済み）。1 本 8 時間でよい。

```bash
D=experiments/20260903-o1-runtime-cost
# 1分スモーク（8列出るか。7/8列目は空でよい、0ではないことを確認）
GSE_COST_DURATION_S=60 GSE_COST_INTERVAL_S=10 bash $D/run.sh with-gse
cat $D/results/with-gse/samples.tsv
awk -F'\t' 'NR==2{print "列数 =", NF}' $D/results/with-gse/samples.tsv
rm -rf $D/results/with-gse
```

スモークが通ったら、**サンプラを先に起動 → 1分基線 → GSE をバイナリ直叩きで起動**の順で
8 時間本番を回す（`README.md` の手順どおり）。この機はデスクトップ機（MSI MS-7E66、
`Win32_Battery` は null）なので `env.md` の Windows 行にその旨を記録する。

## §3 は完了済み

`evidence-s3-overlay.md` 参照。idle 状態の 4隅+中央 hit-test は 5/5 箇所で GSE が奪っていないことを
実測済み。⚠️ 表示状態（Nudge/プローブ中）の hit-test は GUI 操作手段が無く未検証のまま残っている
（次に GUI 自動化手段が使えるセッションがあれば引き継ぐ）。
