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

> ⚠️ **これはレビュー前の姿である**（陽性 3 / 陰性 2）。
> ★ 現行は **陽性 4 / 陰性 3** —— P4（多文書）と P5（既定枝）を後から足した。下記 M-i / M-m を参照。

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

---

# 追補（2026-09-20・レビュー指摘への対応の実測）

> ★ `code-reviewer` と `security-checker` を並列（opus・範囲/禁止/締切を明記）で回した結果。
> ⚠️ **両者が独立に同じ HIGH を挙げた** —— 一致した指摘は優先度が高い（`subagent-delegation`）。

## M-i: ⚠️★★★ HIGH —— 共有の門が**多文書 JSON を素通り**していた

★ 2 レビューが独立に指摘。**一次で再現した**:

```
$ printf '{"gse_dataset":"prohibited"}\n{"gse_dataset":"prohibited"}\n' > two.json
$ jq -e 'type=="object" and (.gse_dataset? == "prohibited")' two.json
true
true            ← ⚠️ jq は **文書ごとに 1 行**出す
$ bash scripts/check_no_feature_output.sh --root <two.json のツリー>
[gate] OK: --features 出力は見つからなかった（走査 1 件）   ← ⚠️ 緑
```

★ 原因: `hit="$(jq -e ...)"` を `[ "$hit" = "true" ]` で見ていたので、
`"true\ntrue"` と一致せず **2 文書以上なら必ず緑**になっていた。
⚠️★★★ **封筒を入れた動機そのもの**（「複数セッションの出力を結合する」）に沿って
`cat feat_a.json feat_b.json > all.json` とされると素通りする ——
★ **違反が大きいほど通る**という逆向きの門だった。

★ 修正: 「**1 行でも true があるか**」で判定する（`printf '%s\n' "$hit" | grep -qx true`）。
★ **陽性対照 P4 として恒久化**した。⚠️ 突然変異（旧判定に戻した版）で **P4 だけが赤**になることを実測:

```
  ❌ P4 封筒を 2 つ連結した多文書 rc=0（期待 1）
[gate] --self-test NG: 1 件
```

⚠️★ **この検算で 1 度空振りした** —— 最初に作った「壊した版」は置換が当たっておらず
**元のままの script を回して「OK」を見ていた**。★ `grep` で置換が入ったことを確かめてから回し直した。
（⚠️ memory「Acceptance self-test」と同じ型。★ *検査を検査するときも、検査が本当に壊れたか確かめる*。）

## M-j: MEDIUM —— `capabilities` が**別セグメントから混ざっていた**

★ `code-reviewer` 指摘。**一次で再現した**（2 セグメントを連結した NDJSON）:

```
修正前: {"session_start":1700000000000,"hmm_version":"0.2.0","app_version":"0.1.0",
         "capabilities":{"unconditional":["key"]}}   ← ⚠️ 後半セグメントの宣言
修正後: {"session_start":1700000000000,"hmm_version":"0.2.0","app_version":"0.1.0",
         "capabilities":null}                        ← ★ 前半には宣言が無い、が正しい
```

★ 原因: `capabilities` を「`capabilities` を持つ最初の `meta` 行」から、
それ以外を「`session_start` を持つ最初の `meta` 行」から取っており、
⚠️ **同じ行である保証が無かった**。
→ ★ **1 行・1 パスに統合**した（`collect_meta_session_facts`）。
★ 副産物: `meta` 行の無い入力に対する**全行パースのフルパスが 1 本減った**
（⚠️ `008` の AC18 は 20 秒の予算で回っている）。
★ 回帰: `capabilities_never_come_from_a_different_meta_segment`。

## M-k: MEDIUM —— `meta` の文字列に上限が無かった

★ `security-checker` 指摘。`hmm_version` / `app_version` / `g1_mode` / `o1_mode` /
`keyboard_layout` を**長さ無制限・文字種無制限**で封筒へ複写していた。
⚠️ 同じ `meta` 行の `capabilities` には 4096 バイトの上限があるのに、こちらには何も無かった。
⚠️ 信頼境界: O1 の NDJSON は**被験者端末で生成される**ので、`meta` の中身は被験者が編集しうる。

→ ★ `MAX_META_STRING_BYTES = 256`。**切り詰めずに落とす**（「宣言が無い」へ倒す）。
★ 回帰: `oversized_meta_strings_are_dropped_not_truncated`（⚠️ **ちょうど上限は通る**ことも固定）。

## M-l: MEDIUM —— `007` は封筒を **1 本しか**走査していなかった

★ `security-checker` M2 (a)。`instrument_rich` の封筒だけを見ており、
⚠️ `minimal` / `stall_onset_observed` / 削除版 / hook 入り / legacy の封筒は**1 度も見ていなかった**。
→ ★ 取得を `capture()` に集約し、**7 本すべての封筒**に `scan_envelope`（AC3b）を掛ける。

## M-m: MEDIUM —— 共有の門が cwd 依存 / `--root ""` で fail-open

| 症状 | 修正前の実測 | 修正後 |
|---|---|---|
| `src-tauri/` から起動 | `走査 0 件`（rc=2） | **走査 121 件**（絶対パスで出す） |
| `--root ""`（変数が空） | ⚠️ **本リポを走査して `OK`**（121 件） | **rc=2「空の値が渡された」** |
| 既定枝（`git ls-files`）の対照 | ⚠️ **1 件も無かった** | **P5** を追加（別 cwd から使い捨て repo を走査） |

★ あわせて `git ls-files -z | tr '\0' '\n'` が `-z` を打ち消していたのも直した
（⚠️ 改行を含むパスが 2 つに割れて**黙って消える**）。

## M-n: 修正後の全再走（★ 通しで回した）

| 検査 | 結果 |
|---|---|
| `cargo fmt --check` | exit 0 |
| `cargo clippy --all-targets --features package -- -D warnings` | exit 0 |
| `cargo test --workspace` | **lib 701 / bin 48 / 1**（★ 回帰 2 本を追加） |
| `001` / `002` / `003` / `005` / `007` / `008` | **すべて OK** |
| `004` / `006` | ⚠️ NG（★ 理由は**自分の Tier 未実装**。「配列が来ない」ではない） |
| `envelope-acceptance.sh` | OK（⚠️ 突然変異 6 種すべてで赤を実測） |
| `check_no_feature_output.sh --self-test` | OK（陽性 4 / 陰性 3） |
| `check_no_feature_output.sh` | OK（走査 121 件） |
| `check-shell-portability.sh` | 通過 12 / 未達 0 |
| `check-tests-are-wired.sh` | 16 本すべて CI から呼ばれている |
| `check_doc_lexicon.py` | exit 0 |
