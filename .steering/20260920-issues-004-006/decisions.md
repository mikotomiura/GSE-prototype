# 設計判断 —— issue 004（`T1c`）/ 006（`T1d`）

> ★ 本ファイルは **実装フェーズの設計裁定**の記録である。
> ⚠️ 上位の裁定（算出式・名前・E1/E2 の存在自体）は
> `.steering/20260918-theory-critical-review/decisions.md` 判断 1 / 2 / 3 と
> `.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25 / 26 が持つ。
> ★ ここで決めるのは、判断 26 が「実装フェーズで決める」と明示して残した **U1〜U4 / V1〜V5** と、
> ⚠️ **実装中に一次で見つかった追加の 1 点（V6）**である。

---

## 判断 1: issue 004（`T1c` = 削除と挿入の遷移の形）U1〜U4 —— ★ **4 件とも推奨を承認**

- **判断日時**: 2026-09-20（Opus・裁定セッション）
- **一次資料**: `issues/004.md` Background（推奨表）／
  `definitions-restop-t1d-t1c.md` §6.2 / §6.2b ／
  `src-tauri/src/analysis/feat_offline/mod.rs`（`key_net_delta` / `extract_pause_resumptions`）／
  `src-tauri/src/analysis/anonymize.rs`（`KeyCategory`）／
  `src-tauri/src/analysis/features.rs:26`（`PAUSE_THRESHOLD_MS = 2_000`）

| # | 論点 | ★ 裁定 | 理由（★ 一次で確かめたこと） |
|---|---|---|---|
| **U1** | 削除の走りを切る press | ★ **推奨を承認** —— **削除系以外の press はすべて切る**（全 press 列での連続） | ★ 「連続する削除系 press の走り」という §6.2 の逐語に最も素直である。⚠️ 対案（挿入系だけが切る）を採ると `navigation` を挟んだ 2 本が 1 本に潰れ、§6.2 が**位置の代理**として挙げた `navigation` の情報が消える（★ GSE はカーソル位置を持たないので、これは取り返せない）。★ 新しい分類も定数も要らない |
| **U2** | `category_bigram_repeat_rate` の式 | ★ **推奨を承認** —— **`1 − 種類数 ÷ 総数`**（bigram 0 個の burst は `null`） | ★ 「重複率」の語に対応するのは「**既出の型を繰り返した出現の割合**」であり、これは `1 − 種類数/総数` そのものである。⚠️ 対案（2 回以上現れる型に属する出現の割合）は「1 回目の出現」まで重複に数えるので、`AA, AB` のような列で **1 回しか出ていない型を重複と呼ぶ**。★ どちらでも `[0, 1)` に収まり `Alphabetic` 優位で burst 長と相関する点は同じ（issue 004 Background の注記のまま）なので、**式の素直さで選ぶ** |
| **U3** | 走り・burst 単位の値を載せる tick | ★ **推奨を承認** —— **閉じが確定した時点の tick**（走り = 次の削除系以外の press または burst の閉じ ／ burst = 最後の press ＋ `PAUSE_THRESHOLD_MS`） | ★ **causal であること**が決め手。ADR-030 D10 の block ablation は `T1c` を **onset の予測**に使うので、対案（最後の press の tick）だと **その tick を閉じた時点では未来の press を見ないと値が決まらない**（＝ 未来が漏れる）。★ もう 1 つの対案（次の burst の最初の press の tick）は**末尾の burst を構造的に落とす** |
| **U4** | 走りの最小の長さ | ★ **推奨を承認** —— **1 から** | ★ 「最大連続長」の自然な読みであり、⚠️ 2 以上にすると **新しい定数 `2` を導入する**ことになる（★ `004-acceptance.sh` が数値定数の宣言を検査して落とす）。★ AC5 の fixture（`instrument_rich`・backspace 3 連）はどちらでも通る |

### ★ U1 ＋ U3 から機械的に従う細目（★ 推測ではなく導出。実装 doc にも書く）

1. **走りは burst をまたがない。** U3 の逐語が閉じる契機に「**burst の閉じ**」を挙げているので、
   pause を挟んだ削除系 press は別の走りになる。
   → ★ これで `delete_runs_after_first_in_burst`（走りが属する burst が一意に決まること）が成立する。
2. **件数は「数える単位が閉じた tick」に載せる。**
   `delete_runs` / `delete_runs_after_first_in_burst` は**走りが閉じた tick**、
   `del_to_ins_transitions` は**遷移を確定させた挿入系 press の tick**（★ その瞬間に確定する）。
3. **burst 単位の値は burst が閉じた tick に載せる。**
   `di_alternations_max` / `category_bigram_repeat_rate`。
   ★ burst の閉じは互いに `PAUSE_THRESHOLD_MS`（2000ms）以上離れるので、
   **1 tick（1000ms）に閉じる burst は高々 1 つ**である（`max` は安全弁）。
4. **閉じがグリッドの外に落ちた単位は黙って捨てる。**
   ★ `stall_onset` の `column_from_onsets`（グリッド外の `t0` を捨てる）と**同じ規約**。
   ⚠️ 実測（`instrument_rich`）: 最後の burst（最終 press `+114350`）の閉じは `+116350` で、
   グリッドの右端（15 tick = `+114350` まで）を越えるため**末尾 burst の burst 単位の値は出ない**。
   → ★ これは欠陥ではない。**閉じを観測していない**から出さないのであり、U3 の causal 規約そのものである。
5. **`null` と `0` の使い分け**（既存原則の適用・issue 004 Background）:
   件数（`delete_runs` / `del_to_ins_transitions` / `delete_runs_after_first_in_burst`）は**常に数**（0 を含む）、
   最大値・率（`delete_run_max` / `di_alternations_max` / `category_bigram_repeat_rate`）は
   **閉じる単位がその tick に無ければ `null`**（⚠️ 0 で埋めない）。
   ★ `di_alternations_max` は burst が閉じていれば **D/I の press が 1 つも無い burst でも `0`**（交替が無かった、という観測である）。

### ⚠️ 却下した細部（★ 記録として残す）

- **`KeyCategory` から挿入系 / 削除系を独自に定義する**: ⚠️ **却下**。
  ★ ADR-030 D3 の写像 SSOT は `mod.rs::key_net_delta`（`metrics::is_text_producing` / `is_backspace`）である。
  → ★ 代わりに `revision.rs` は `KeyCategory` → `{Insert, Delete, Neither}` の写像を持つが、
  **全 VK（`0x00..=0xFF`）で `key_net_delta` と一致することを単体テストで固定する**（`category_class_matches_key_net_delta`）。
  ⚠️ これは「新しい分類」ではなく「**SSOT の同値な言い換えを鍵で固定したもの**」である。
  ★ こうする理由は AC3（引数が `KeyCategory` と時刻だけ＝本文非参照）を**構造として**満たすためである。

---

## 判断 2: issue 006（`T1d` = 再開）V1〜V5 —— ★ **V1 / V2 / V3 / V5 は推奨を承認・V4 は「いま足さない」**

- **判断日時**: 2026-09-20（Opus・裁定セッション）
- **一次資料**: `issues/006.md` Background ／ `definitions-restop-t1d-t1c.md` §2 / §3 / §5 ／
  `ADR-030` D2（buffer `B`）/ D3（条件 A）/ D8 (b-2)（観測区間）／
  `ADR-029` D5（censoring の分離）／ `ADR-031:52`（主 criterion に「再停止までの時間」）／
  `src-tauri/src/analysis/feat_offline/stall_onset.rs`（`detect_stall_onsets_for_interval` / `net_at_fast` / `observed_intervals`）

| # | 論点 | ★ 裁定 | 理由 |
|---|---|---|---|
| **V1** | E1 の集計窓と実装順 | ★ **推奨を承認** —— **検出列（`stall_onset`）は変えない。E1 は `recovery` と同時に別層で入れる。本 issue は E2 の窓 `[o, 次の onset の s)`（観測区間の右端 `b` で打ち切り）で数える** | ★ **一次で確認した前提が生きている**: `progress_proxy` を使う `recovery` は `feat_offline` に**未実装**（`grep -rn progress_proxy src-tauri/src/` の実測ヒットは `features.rs` のコメントと `replay.rs` の警告文のみ）。⚠️ この状態で E1（「エピソードは転帰か打ち切りでだけ閉じる」）を検出列に入れると、**同じ観測区間では最初の onset しか立たなくなる** —— ★ それは `stall_onset`（issue 008・merge 済み・ゴールデンあり）の**破壊的変更**であり、本 issue の Allowed Files と Stop Conditions を明らかに越える。★ [V146]「**検出と束ねを分ける**」にも E1 を別層に置く方が沿う |
| **V2** | 条件 A の辺の取り出し方 | ★ **推奨を承認** —— `stall_onset.rs` から **`pub(super)` で条件 A の辺の列を出す**（★ Allowed Files に `stall_onset.rs` を追加）。右端ちょうど（`s'_1 = b`）は `t0 <= b` と**対称に確定扱い** | ⚠️ 条件 A の評価は `stall_onset.rs` の**非公開関数**（`detect_stall_onsets_for_interval` / `net_at_fast`）にある。★ 出さずに実装すると **`restart.rs` が条件 A を再実装する＝定義が二重になる**（Codex TASK-PRE 指摘 5 と同型で、⚠️ 005 と食い違ったまま気づけない）。★ Allowed Files を 1 本増やす代償のほうが小さい |
| **V3** | fixture | ★ **推奨を承認** —— `006-acceptance.sh` AC6 の fixture を **`stall_onset_observed.ndjson`** へ差し替える | ⚠️ `deep_silence.ndjson` は **feat 行を持たない**ため観測区間が無く、issue 008 以後 **onset が 1 つも立たない**（起票 17）。★ `stall_onset_observed.ndjson` は実測で **onset が 2 つ**立つ（`t0 = +40160` / `+187600`。★ `--features` を直接実行して確認した） |
| **V4** | 打ち切りの指標（`censored` フラグ） | ⚠️ **推奨に倒さない —— 本 issue では足さない**（★ 新しい blocker として起票する） | ★ 理由 1（**情報が増えない**）: 本設計では、onset のある行で `restop_ms` が `null` になる経路は **観測区間の右端 `b` に達した右側打ち切りだけ**である（`r_1` が無い／`s'_1` が無い／窓が無い、のいずれも `b` までの観測で事象が起きなかったという同じ事実）。→ ★ `censored` は **`stall_onset.t0_ms != null && restop_ms == null`** で完全に復元でき、**boolean 1 個では新しい情報を 1 ビットも足さない**。★ 理由 2（**本当に足りないのは別のもの**）: 生存解析（`ADR-031:52` 逐語「主 criterion: …**再停止までの時間**…」）に要るのは打ち切りの**追跡時間**（`b − o`）であって真偽値ではない。★ 理由 3（**契約**）: `definitions-restop-t1d-t1c.md` §5 が「足すなら AC の改訂 ＝ **研究者判断**」と明記している。⚠️ **裁定セッションがフィールドを増やす側に倒すのは契約違反**である。→ ★ **復元規則を `mod.rs` の doc に明記**して情報を落とさないようにしたうえで、追跡時間のフィールドは `blockers.md` 起票 20 として研究者へ上げる |
| **V5** | 集計窓そのものが無いときの `post_t0_*` / `resumption_count` | ★ **推奨を承認** —— **`null`** | ★ 「観測できなかったものを 0 で埋めない」（AC3 の精神・`mod.rs` の「欠測の表現」節）。⚠️ `0` にすると「窓はあったが press が 0 件だった」と**区別できなくなる**。★ 窓が無いのは (a) `o = t0 + B` が観測区間の右端 `b` を越える、(b) E2 で次の onset の `s` が `o` 以前にある、の 2 通り |

### ★ V1 の帰結（実装の形）

```text
原点 o        : t0 + B          （B = StallOnsetConfig::b_ms。⚠️ 本 issue で値を決めない）
集計窓（E2）  : [o, min(同じ観測区間の次の onset の s, b+1) )   ★ 右端 b は確定扱い（V2 と対称）
              ⚠️ 窓が空（次の onset の s <= o）または o > b なら「窓が無い」→ V5
r / s'        : ⚠️ **窓ではなく観測区間 [a, b] の中の条件 A の辺だけで決まる**
                （★ issue 006 Background 逐語「束ね方に依存しない量」。E1 導入後も値が変わらない）
```

⚠️★★★ **E2 の既知の代償（★ 隠さずに書く）**: 次の onset が `o` より前にある場合、
窓が消えて `post_t0_*` / `resumption_count` が `null` になる一方、
`restop_ms` / `stable_generation_ms` は **次のエピソードに属する時間帯**を測ることがある。
★ これは [V146] が警告した**過剰分割**そのもので、**E1 で消える**（V1）。
→ ★ `restart.rs` の doc に明記し、`blockers.md` 起票 20 に併記する。

---

## 判断 3: ⚠️★★★ **追加の論点 V6（実装中に一次で発見）** —— 原点 `o` の時点で条件 A が既に `false` のとき

- **判断日時**: 2026-09-20（Opus・裁定セッション）
- ⚠️ **これは判断 26 が列挙していない論点である**（★ V1〜V5 の外。実装に降ろして初めて見えた）。

### 何が起きるか（★ 実測）

`stall_onset_observed.ndjson` の 1 つ目の onset は `t0 = +40160`、`B`（既定 = `merge_gap_ms` = 30000）を足して
**原点 `o = +70160`**。⚠️ ところが打鍵は **`+51000` に再開している**（★ 実測の press 列。`+7560` → `+51000` の 43440ms ギャップの後）。
→ ★ **`o` の時点で条件 A は既に `false`（＝ もう生成している）**。

⚠️ 定義を「`o` **以後**で条件 A が true → false に**落ちる**時刻」と**辺だけで**読むと、
**`r_1` が存在しない → `restop_ms` / `stable_generation_ms` / `stable_generation_net_presses` が全部 `null`** になる。

⚠️★★★ **実測で確かめた帰結**: この読みでは `stall_onset_observed.ndjson` の
**2 つの onset のどちらも `restop_ms` が `null`** になり、**AC6（退化していないこと）が V3 の差し替え後でも通らない**。
★ しかも意味が逆である —— **速やかに再開した人ほど「再開が観測されなかった」と記録される**。

### ★ 裁定

> ★ **生成区間を「条件 A が `false` である極大区間を `[o, b]` で切ったもの」と定義する。**
> `r_k` = **k 番目の生成区間の開始時刻（`o` より前に始まっていれば `o` にクリップする）**、
> `s'_k` = その生成区間が閉じる時刻（条件 A が `true` へ立ち上がる時刻）。

- ★ **辺の定義と矛盾しない**: `o` の時点で条件 A が `true` なら、この定義は「最初の true → false の辺」と**完全に一致する**。
  変わるのは `o` で既に `false` の場合だけである。
- ★ **`B` の役割と整合する**: ADR-030 D2 の buffer は「検出窓と転帰窓を重ねない」ためのものである。
  `[t0, o)` の産出を転帰から外すのが目的なので、**`o` で左側を切る（左側打ち切り）のが正しい扱い**であり、
  「`o` 以前に始まったから観測しなかったことにする」は目的を越えている。
- ★ **導出式が両方の場合で成り立つ**: `definitions-restop-t1d-t1c.md` §3.2 の
  「`r_1 − o = restop_ms − stable_generation_ms`（原点から最初の再開までの遅れ）」は、
  この場合に **`0`（遅れなし）** を返す。★ 意味が通る。
- ⚠️ **代償**: この場合 `restop_ms` と `stable_generation_ms` が**同じ値**になる
  （§3.2 が候補 A の欠点として挙げた「ほぼ同じ量になる」が、この場合だけ顕在化する）。
  → ★ ただし **`r_1 − o = 0` という読み取り可能な事実**であって、退化ではない。
- ⚠️ **`B` の値への感度**: `B` は `W` と同じ 30 秒系列から選ぶ（ADR-030 D4 の表）。
  ★ `B` が大きいほど「`o` で既に `false`」の場合が増える。
  → ⚠️ **この感度は事前宣言（判断 25 #13）で `B` を決めるときの材料**であり、`blockers.md` 起票 20 に併記する。

### ⚠️ 採らなかった読み

| 案 | 中身 | 却下理由 |
|---|---|---|
| **辺だけ**（厳密） | `o` 以後の true → false の辺が無ければ `r_1 = null` | ⚠️ **速やかに再開した人ほど `null` になる**（★ 上の実測）。`T1d`（＝ 再開を記述する Tier）として意味が反転する |
| **辺を `o` より前へ遡る** | `o` の時点で開いている生成区間の**実際の開始時刻**（例では `+51000`）を `r_1` にする | ⚠️ buffer `B` の内側（`[t0, o)`）の時刻を転帰の値として出すことになり、**ADR-030 D2 が分けた 2 つの窓を再び重ねる** |

---

## 判断 4: `restart` を列にする配線 —— ★ `stall_onset` の**列**（`Vec<StallOnset>`）を入力にする

- **判断日時**: 2026-09-20
- **論点**: `restart` の値をどの tick 行に載せるか。
- ⚠️ **見つけた罠**: `stall_onset` の `column_from_onsets` は
  (a) グリッド外に落ちる `t0` を捨て、(b) **同じ tick に 2 つ目の onset が落ちたら捨てる**（先着優先）。
  → ★ `restart` を**生の onset 列**から独立に作ると、**行が対応しなくなる**
  （⚠️ AC3「`t0` が立っていない行では全フィールドが `null`」が壊れる）。
- ★ **裁定**: `restart_column` は **`stall_onset_column` の出力（`&[StallOnset]`）をそのまま入力に取る**。
  各行の `t0_ms` / `s_ms` を使って値を計算するので、**捨てられた onset は `restart` にも現れない**（構造的に一致する）。
  ★ 「次の onset の `s`」（E2 の窓の右端）は、**捨てられた分も含む onset 列**（`condition_a_timeline` が返す）から取る
  —— ⚠️ 窓の右端は「次に onset が立った事実」で決まるのであって、tick 割りの都合で決まるのではない。
- ⚠️ **AC7 との関係**: この向き（`stall_onset` → `restart`）は **転帰側が検出側に渡らない**ことを配線として保証する。
  ★ 逆向きの依存は作らない。

---

## 判断 5: ⚠️★★★ 受け入れスクリプトの**実行不能な検査**を 2 件直した（★ 実測で発見）

- **判断日時**: 2026-09-20（実装フェーズ・実測）
- ⚠️ 判断 26 の逐語「**受け入れスクリプトは未検証**（`bash -n` と jq 式の検算だけ）」が
  **そのまま顕在化した**。★ 実 fixture ＋ 実装で通しで回して初めて出た（memory「Acceptance self-test」）。

### (a) `006-acceptance.sh` AC7 の grep が**構文エラーで必ず落ちていた**

```text
実測: grep: Invalid regular expression   （★ 2 回）
      [acceptance 006] NG: … mod.rs に restart が retrospective である旨の明記が無い
```

- **原因**: パターンの中に**リテラル改行**があった（`'restart[^<改行>]*retrospective|…'`）。
  ★ grep は PATTERN 引数を**改行で分割して複数パターンとして扱う**ので、
  `restart[^` / `]*retrospective|retrospective[^` という**未閉じブラケット**になっていた。
- ⚠️★★★ **実装が正しくても絶対に緑にならない検査**だった（★ 偽陰性ではなく恒久的な偽陽性）。
- **直し方**: grep は行単位で走るので `.`（改行に一致しない）で足りる
  → `'restart.*retrospective|retrospective.*restart'`。
- ★ **他のスクリプトも走査した**: 引用符が同じ行で閉じない grep 行は**この 1 件だけ**だった
  （8 本 ＋ envelope を機械的に確認）。

### (b) `007-acceptance.sh` の `stall_onset.rs` 行差分ガードが、V2 の裁定と構造的に両立しない

```text
実測: [acceptance 007] NG: stall_onset.rs を observed_intervals の可視性以外で変更している（★ 1 語だけ）
```

- ⚠️ 007 の門は「base ref との**行差分**が `fn observed_intervals(` の 1 語だけ」を要求していた。
  ★ 判断 2 の **V2** で `stall_onset.rs` が **issue 006 の Allowed Files に入った**ので、
  **この形は今後どうやっても成り立たない**（★ 006 は条件 A の辺を `pub(super)` で出す）。
- ★ **直し方（意図を保ったまま作り直した）**: 行差分をやめ、
  1. `quality.rs` が検出本体の記号（`detect_stall_onsets` / `net_at_fast` / `ThetaAccumulator` /
     `condition_a_timeline` / `stall_onset_column`）を**参照していない**こと、
  2. **条件 A の判定式**（`net_at_fast(sorted_keys, prefix, t, w) < net_diff_min`）が
     base ref と**同じ本数だけ在る**こと、
  の 2 点で見る。⚠️ 検出の**振る舞い**の回帰は `008-acceptance.sh` とゴールデン replay が別に張る。
- ⚠️★★★ **これは他 issue の門を書き換える行為である**（★ 判断 18 / 001 AC2b の先例と同型: Tier を
  足す側が最上位の門を直す）。★ 研究者が「弱めすぎ」と判断するなら差し戻せるよう、
  旧版の中身と置き換えの理由をスクリプトのコメントに逐語で残した。

### ★ 壊して赤くなることを実測した（⚠️ 「緑だから効いている」と書かない）

| 壊し方 | 結果 |
|---|---|
| V6 を外す（「辺だけ」の読みに戻す） | ★ `006` AC6 が **NG**（`restop_ms` が全行 null）／ 単体 `generation_already_open_at_origin_clips_r1_to_origin` が **FAILED** |
| `mod.rs` から `retrospective` の語を消す | ★ `006` AC7 が **NG** |
| `revision` のフィールドを 1 つ改名する | ★ `004` AC1 が **NG** |
| `quality.rs` に `net_at_fast` の語を足す | ★ `007` が **NG** |
| 条件 A の判定式を `<` → `<=` に変える | ★ `007` が **NG**（`base=1 / now=0`） |
| 最上位の行に `vk` を足す / `restart` を消す（jq で注入） | ★ `001` AC2b の式が**両方とも落ちる**ことを確認 |

- ★ いずれも**戻した後にバイト一致を確認**した（`diff` / `git status`）。

---

## 判断 6: ★ `code-reviewer` ＋ `security-checker`（並列・opus）の指摘を是正した

- **判断日時**: 2026-09-21
- ★ 範囲・禁止事項・締切を明記して 2 本を並列起動した（`subagent-delegation` ルール 2 の 5 点）。
  ★ 実測: **5.4 分 / 6.8 分**で完走し、両者とも「読んでいない範囲」を自己申告した（⚠️ ハングしていない）。

### ⚠️★★★ **両者が独立に同じ HIGH / MEDIUM を挙げた** —— ★ これが最大の収穫

| | `code-reviewer` | `security-checker` |
|---|---|---|
| 指摘 | **H1**: `restart` が onset 行ごとに変化点を線形に走り `O(R・C)` | **M1**: 同じ経路を「可用性への DoS」として指摘 |

★ **両者が同じ場所を指しているので、これは偽陽性ではない**（⚠️ 片方だけの指摘とは格が違う）。
⚠️ さらに `code-reviewer` は **AC18 / AC18b がどちらも `R = 1` なので門が効かない**ことまで降ろした
（★ AC18b は 70ms 周期の churn で θ_person を満たさず、onset は末尾沈黙の 1 本だけ）。
→ ★ **実装を `O(R log C)` に直し**（`ChangeIndex` = `true` の累積和 ＋ 二分探索）、
**多 onset の入力で素朴な走査と一致する単体テスト**を足した。門の穴は `blockers.md` **起票 21** で研究者へ。

### 是正した指摘

| # | 指摘 | 対応 |
|---|---|---|
| H1 / M1 | `restart` の `O(R・C)`（＋ `next_onset` の線形 find で `O(R²)`） | ★ **直した**。`ChangeIndex` で `O(log C)`、`next_onset` は `partition_point`。索引は**観測区間ごとに 1 回**だけ作る |
| M2 | `burst_ranges` の値一致突き合わせを守るテストが無い | ★ **直した**（`burst_ranges_survive_same_timestamp_presses_at_a_pause_boundary`: pause 境界の同時刻打鍵・両側・閾値ちょうど） |
| M3 | bigram の distinct を `as_str()` の文字列比較 ＋ clone で数えている | ★ **直した**。判別子 `as u8` で in-place ソート（⚠️ clone を落とした）。★ 率も `(total − distinct)/total` にして `1/3` の丸めを直した |
| M4 | `resumption_count` の doc と実装の食い違い（V6 のクリップ分を 1 に数える） | ★ **doc に明記した**（⚠️ 数え方は変えない ＝ V6 と整合）。★ 「`o` 前に再開済み」と「窓内で 1 回再開」は `stable_generation_ms == restop_ms` で区別できることも書いた |
| L1 | `category_bigram_repeat_rate` から `distinct` が逆算できる | ★ **doc に明記した**（⚠️「率だから安全」という前提を置かせない）。★ どの型が出たか・順序は出ないので本文復元は不可 |
| L2 | `revision_column` だけ `pub` で `tick_ms = 0` を渡せた | ★ **`pub(super)` に揃え、`debug_assert!` を足した** |
| L3 / L6 | `restart_for_onset` が使わない `s_ms` を受け取り捨てている | ★ **引数から落とした**（意図は呼び出し側のコメントへ） |
| L5 | `changes` の交替前提が型で守られておらず、破れると最初の区間が閉じない | ★ **前提を使わない実装に変えた**（累積和 ＋ 二分探索は交替に依存しない） |
| L8 | `mod.rs` の「欠測の表現」節が 2 Tier の `null` 規約に触れていない | ★ **2 Tier ぶんを足した** |
| L7 | `007` の置き換えガードはテキスト一致で `net_at_fast` の中身の変更は素通り | ⚠️ **対応しない**（★ 振る舞いの回帰は 008 ＋ ゴールデンが張ると**スクリプトに既に書いた**。★ 二重に見ない） |

### ★ 是正後の客観検証（実測）

- `cargo test --workspace` **773 passed**（724 ＋ 48 ＋ 1。★ 是正で +2）／ `clippy -D warnings`・`fmt --check` **exit 0**
- acceptance **001〜008 ＋ envelope すべて OK**（★ **008 も OK** —— 計算量の門を通した）
- ⚠️ **出力が変わっていないこと**を実測: `stall_onset_observed` の onset 2 行の `restart` は
  是正前と**完全に同じ値**（`restop_ms` 114840 / null、`resumption_count` 1 / 0）。
  ★ `instrument_rich` の `revision` も手計算と一致（tick 3: 交替 0・率 2/3 ／ tick 4: 走り 3 連・del→ins 1 ／ tick 7: 交替 1・率 2/7）。

### ⚠️ レビューが読んでいない範囲（★ 「指摘なし」ではない）

- 両者とも `.steering/20260920-issues-004-006/` の `design.md` / `requirement.md` / `tasklist.md` と
  `issues/004.md` / `006.md` の本文改訂を**読んでいない**（★ AC 本文と実装の逐語照合はレビューを経ていない）。
- `code-reviewer` は `stall_onset.rs` の `#[cfg(test)]` ブロック（約 640 行）と `quality.rs` / `activity.rs` の本体を未読。
- `security-checker` は 2026-09-18 の「削除／一時停止／欠損で stdout の sha 一致」実験を**再実行していない**
  （★ 入力依存の静的追跡で「壊れていない」と結論した）。
