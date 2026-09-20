# 実測記録（2026-09-20・封筒 issue）

> ⚠️★★★ **本プロジェクトは「検査があるつもりで検査していない」を 3 回踏んでいる。**
> ★ ここには **「検査が突然変異で実際に赤くなったか」** だけを書く。
> ⚠️ 「実装した」ではなく「**壊したら赤くなった**」が記録の単位である。
> ★ 手本: `.steering/20260920-loop-foundation-fixes/measurements.md`。

## M-0: ⚠️★★★ 検査器自身にバグがあった（★ 突然変異が見つけた）

**初版の `scripts/check_no_feature_output.sh` は、封筒を剥がした行の配列を通していた。**

```
$ bash scripts/check_no_feature_output.sh --root <stripped.json だけのツリー>
[gate] OK: --features 出力は見つからなかった（走査 1 件）   ← ⚠️ 赤にならない
rc=0
```

★ 原因（一次で確認）: jq は `|` を `or` より**弱く**結ぶ。

```jq
[ .. | select(A) ] | length > 0 or ([ .. | select(B) ] | length > 0)
# ↑ 実際の解釈:
[ .. | select(A) ] | ( length > 0 or ([ .. | select(B) ] | length > 0) )
```

→ ⚠️ **2 本目の条件が元の文書ではなく「1 本目の結果の配列」を入力に取っていた。**
★ 修正: 2 本とも `def` に包んで呼ぶ（各呼び出しが `.` = 文書全体を受ける）。
★ **この穴を `--self-test` の陽性対照 P2 として恒久化した**（下記 M-c）。

⚠️ 教訓: **手で 1 回試すだけでは足りなかった。** 最初の手動試行では
「封筒つきが赤になった」ところで満足しかけた。★ 剥がした形を試したから見つかった。

---

## M-a: 共有の門 — 内容別の判定（`--root` 経路）

| 検体 | 期待 | 実測 rc | 判定 |
|---|---|---|---|
| `envelope.json`（本物の `--features` 出力） | 赤 | **1** | ✅ マーカーで拾う |
| `stripped.json`（`jq '.rows'` で剥がした配列） | 赤 | **1** | ✅ 行の形で拾う（★ M-0 の修正後） |
| `notes.txt`（拡張子だけ変えた同じ中身） | 赤 | **1** | ✅ **名前で判定していない** |
| `only_tms.json`（`t_ms` だけを持つ別物） | 緑 | **0** | ✅ 偽陽性なし |
| `metrics.json`（gse-dataset へ出す唯一の共有物） | 緑 | **0** | ✅ 偽陽性なし |
| `envelope.json.gz`（圧縮） | ⚠️ 見えない | **2** | ⚠️ 走査 0 件 ＝「検査できなかった」（★ 隠さず記録） |

## M-b: 共有の門 — 既定経路（`git ls-files` = 追跡ファイル）

★ 使い捨ての git repo（`$TMP/gaterepo`）に検体を `git add` して実測した。

| 追跡している検体 | 期待 | 実測 rc |
|---|---|---|
| `feat.json`（封筒つき） | 赤 | **1** |
| `rows.json`（剥がし済み） | 赤 | **1** |
| `m.json`（metrics 形のみ） | 緑 | **0** |

★ 本リポの実走査: `走査 121 件` で **rc=0**（2026-09-20）。

## M-c: 共有の門の `--self-test`（★ 対照を script に内蔵した）

```
$ bash scripts/check_no_feature_output.sh --self-test
  ✅ P1 封筒つき（マーカー）           rc=1
  ✅ P2 封筒を剥がした行の配列          rc=1
  ✅ P3 拡張子だけ変えた持ち出し         rc=1
  ✅ N1 metrics.json 形（共有物）       rc=0
  ✅ N2 t_ms だけを持つ別物             rc=0
  ✅ N3 空ツリーは「検査できなかった」    rc=2
[gate] --self-test OK   (rc=0)
```

⚠️★★★ **self-test 自身が空振りしていないことも確かめた** —— M-0 のバグを戻した版を回すと:

```
  ❌ P2 封筒を剥がした行の配列 rc=0（期待 1）
  ❌ P3 拡張子だけ変えた持ち出し rc=0（期待 1）
[gate] --self-test NG: 2 件   (rc=1)
```

## M-d: 封筒の受け入れ検査（`envelope-acceptance.sh`）の突然変異

★ `ACC_REPLAY_CMD` に、本物の出力を jq で歪める偽コマンドを与えて実測した。

| 突然変異 | 期待 | 実測 | 捕まえた AC |
|---|---|---|---|
| （無変異） | 緑 | **rc=0 OK** | — |
| `jq '.rows'`（封筒を捨てて配列に戻す） | 赤 | **NG** | AC1（トップレベルが 3 キーでない） |
| `del(.provenance.sharing)` | 赤 | **NG** | AC2（provenance のキー集合） |
| `capabilities` を行に戻す | 赤 | **NG** | AC5（`rows[].quality` に残っている） |
| `generated_at` を足す（非決定） | 赤 | **NG** | AC2（キーが増えた） |
| `source_sha256` を定数にする | 赤 | **NG** | AC6（異なる入力で同じ値） |
| `tool_version` だけを非決定にする（★ キーは増やさない） | 赤 | **NG** | **AC9**（2 回実行でバイト不一致） |

⚠️ 最後の 1 件を足した理由: `generated_at` を足す変異は **AC2（キー集合）**が先に拾ってしまい、
★ **AC9（byte-equal）が本当に働くか分からなかった**。→ キーを増やさない変異で AC9 を直接確かめた。

## M-e: 既存 acceptance 8 本 —— 封筒が無いと赤になるか（fail-closed）

```
$ bash -c 'set -uo pipefail; out="$(echo "[{\"t_ms\":1}]" | jq ".rows")" || echo NG'
jq: error (at <stdin>:1): Cannot index array with string ("rows")
NG   (rc=1)
```

★ 001〜006 はこの形（取得時に `| jq '.rows'`）なので、**封筒が無い出力では必ず赤**になる。
★ 007 を封筒なし出力で実走:

```
[acceptance 007] NG: 出力から封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）
rc=1
```

⚠️★★★ **008 の計時検査（AC18 / AC18b）だけは形を変えた。**
★ `timeout ... | jq` にすると、打ち切られた出力で jq が 5 を返した瞬間に
`pipefail` が「最も右の非 0」= 5 を採り、**`rc=124`（時間切れ）が消える**。
→ ★ 時間切れの診断が「非 0 で終了した」に化けるので、**生の rc を先に確定させてから剥がす**。

## M-f: 既存 acceptance 8 本の実走（★ 封筒導入後）

| issue | 状態 | 実測 |
|---|---|---|
| 001 | merged | **OK** |
| 002 | merged | **OK** |
| 003 | merged | **OK** |
| 004 | ⚠️ blocked | NG: **「全行に revision の必須フィールドが揃っていない」** |
| 005 | merged | **OK** |
| 006 | ⚠️ blocked | NG: **「全行に restart の必須フィールドが揃っていない」** |
| 007 | merged | **OK** |
| 008 | merged | **OK**（AC18: 14s / AC18b: 3s） |

★ **004 / 006 の赤は自分の Tier が未実装であるため**であり、
⚠️ **「配列が来ない」では赤になっていない**（★ 受け入れ条件の 1 つ）。

## M-g: 単体テスト・封筒検査

```
$ cargo test --workspace     # src-tauri/
test result: ok. 701 passed; 0 failed   (lib)
test result: ok.  46 passed; 0 failed   (bin gse-replay)
test result: ok.   1 passed; 0 failed

$ bash .steering/20260920-envelope-issues/envelope-acceptance.sh
[acceptance envelope] OK   (rc=0)
```

## M-h: ⚠️ 検査の前提が外れた 1 件（★ 記録に残す）

★ 当初 `envelope_carries_meta_facts_and_sharing_marker` に
「fixture の `meta.hmm_version` は現行バイナリと同じ値のはず」と書いて**赤になった**。

```
left:  Some("0.2.0")   ← instrument_rich.ndjson の meta
right: Some("0.5.0")   ← 現行バイナリの HMM_VERSION
```

→ ★ これは**封筒が 2 つの `hmm_version` を別フィールドで持つ理由そのもの**だった
（収集時 ≠ 解析時）。⚠️ 検査を実測に合わせ、さらに
`envelope-acceptance.sh` AC8 で「**同じ値になったら赤**」にした
（★ 揃ってしまうと「2 つ持つ意味」を誰も見なくなるため）。
