# 次セッション開始プロンプト — 表現チャネル SSOT 昇格の **積み残し 4 件**

> ★ **本ファイルは `_handoff/next-session-prompt-expression-channel-ssot.md`（2026-08-30）の後続**である。
> ⚠️ **旧引き継ぎは役目を終えた**（★ 論点 1〜6 は 2026-08-30 に裁定済み。記録は
> `.steering/20260830-expression-channel-ssot/decisions.md`）。
> ⚠️★★★ **本ファイルを読む前に `/clear` すること。**

このファイルの「===」以下をコピペして開始する。

---

===

## §0 ⚠️ 前提（★ ここは既に決まっている・蒸し返さない）

★ **2026-08-30 に SSOT へ昇格した**:

| SSOT | 何が決まったか |
|---|---|
| `docs/adr/ADR-017-expression-channel-boundary.md` | **D1** 表現チャネルと媒体の分離／**D2** 境界は**イベント**（常時ストリームではない）／**D3** **PC → スマホの一方向**・inbound の「歩いた」二値を作らない／**D4** PC 側に常設 LAN リスナを置かない／**D5** **音声の自動開始は Phase1 の範囲外**／**D6** 曝露予算で表現を 2 層に割る／**D7** 表現層は Physical Anchor を出口に持つ／**D8** 復帰後の差分は「入力 1 = 時計の事実 / 入力 2 = `p_stuck`」に割る／**D9** inbound を開くなら `data-privacy` に位置情報の節が先に要る |
| `docs/architecture/expression-channel.md` | 設計の SSOT（§0–§8） |
| `docs/research-positioning.md` §1 / §4 / **§5** / §7 / §8 / §9 | 主張の温度を一次に合わせた（★ 研究者承認済み）。★ **§5 は H-Y の測り方 ＋ H-Y-b（自律性・Gate H の計器）新設 ＋ H-PA 改訂 ＋ H-EXPR 新設**。⚠️ **確証の核 H-X1 / H-X1b と PreReg-1〜8 は不変** |
| `docs/architecture/gse-v2-overview.md` | 製品定義を「**本人が自ら是認できる (self-endorsed) 範囲**で」へ訂正（[P178]） |

⚠️★★★ **次も 1 バイトも変えない**: `src-tauri/` の記録仕様／凍結済み `docs/preregistration-v0.3.md`・
G1 事前登録／ADR-009 の X 軸。

---

## §1 ★ 積み残し（★ **F-4 / F-5 は 2026-08-30 中に完了**。残りは 4 件）

| # | 件 | ★ 何をするか | ⚠️ 難度・依存 |
|---|---|---|---|
| **F-1 ★★★** | **`data-privacy` SKILL に位置情報の節が無い** | ★ **位置情報（GPS / 位置履歴）の規定を新設**する。⚠️ **ADR-017 D9 が「inbound のセンサ経路を開く前に要る」とブロッカーとして明示**している。★ PM-D11 条件 3（`geolocator` は `pedometer` と別扱い）が出発点 | ★ 単独で着手可。⚠️ **ADR-017 D3 により第 1 版のブロッカーではない**ので急がないが、**参照先が空のまま**なのは事故のもと |
| **F-2 ★★★** | **[P6] の書誌が未検証**（`provisional`） | ★ **"Proc. Design Society, 2019" に該当が見つからない。**Kawakami の SICE 論文群 / Springer 2023 / [P176] の共著者 Naito, K. の系列を当たる | ★ サーヴェイ 1 ラウンド。⚠️ **`citation-ssot` の append-only / renumber 禁止 / tombstone 規約を守る** |
| **F-3 ★★** | **[P170] 図 1 の Objective / Subjective 分類**（判定不能 U-1） | ★ **8 枚の不便益カードのどれが Objective でどれが Subjective か**を一次で確定する。⚠️ **GSE の headline と益カテゴリがずれている可能性がある** | ★ F-2 と同じラウンドで回せる |
| ~~**F-4**~~ | ~~`research-positioning.md` §5 の改訂~~ | ★★★ **2026-08-30 に追加承認され適用済み**（H-Y の測り方 / **H-Y-b 新設** / H-PA 改訂 / **H-EXPR 新設** / 依存関係）。記録は `.../decisions.md` EC-D9 | ★ **完了** |
| ~~**F-5**~~ | ~~`gse-v2-overview.md:44`~~ | ★★★ **2026-08-30 に適用済み** —— 「本人が **自ら是認できる (self-endorsed)** 範囲で」＋ [P178] の逐語 ＋ ⚠️ **計器未確定**の注記 | ★ **完了** |
| **F-6 ★** | **`intervention-design` SKILL のルール 5（Monk Mode）** | ⚠️ **ADR-015 D2 で Monk Mode は削除されたのに、ルール 5 が残っている可能性がある**（★ 2026-08-30 は未確認）。★ まず grep で実測する | ★ 小さい。⚠️ **実測してから直す**（`verify-before-claiming`） |

---

## §2 ⚠️ 依然として未決の設計判断（★ 文献では埋まらないものが多い）

| # | 未決 | ★ 実際に動かすもの |
|---|---|---|
| **W-1** | **wire protocol の具体** | ★ **実装着手時の別 ADR**。⚠️ ADR-017 D4 の 4 制約（常設 LAN リスナ禁止 / on-demand ＋ ティアダウン / 不在でも層 0 へ縮退 / フレームを捏造しない）を満たすこと |
| **PS-Q1** | 表現層の第 1 版を 1 要素に絞るか | ★★★ **GSE 自身の検出力計算**（⚠️ **文献では埋まらない** — PS-D9） |
| **PS-Q3** | 層 0（音）を第 1 版から外すか | ★★★ **B1（層 0 = 1.0 で 10 分・「気になるか」）の実施** —— `spec` §9-4 が「**α の可否はここでしか決まらない**」と明記 |
| **PS-Q5** | 本人 / 他者を THAT・WHAT・HOW のどの段で止めるか | ★★★ **試作の試視**（`experiments/20260812-expression-step4-grain/player/step4.html` は既にある） |
| **PM-Q7** | 既決 D9（報酬版を採らない）を維持するか改訂するか | ⚠️ **`expression-channel.md` §5.3 の非対称な応答がこの主題に触れる。★ 2026-08-30 は確定させなかった** |
| **PM-Q8** | 主アウトカムを「増加」でなく「維持」に置くか | ⚠️ 未決のまま |
| **E-1** | 本人が「離席 ↔ 表現」の対応を理解する必要があるか | ⚠️ [P164]: **5 秒でも contingency knowledge は落ちる**（t(236)=3.03, p=.002） |
| **E-2** | 個人ベースラインの継続学習をどう入れるか | ⚠️ **PreReg-5 の凍結**（β 較正 → 凍結）と **ADR-008（Proposed）**との整合 |
| **E-4** | 「翌日反映」を採るか | ⚠️ **日オーダーの遅延はメタ解析の外**（[P159] 著者逐語 *"relatively few studies involving delays of one day or longer"*）→ ★ **自分で測るほかない** |
| **G-1** | [P77] 実験 4 の 1 項目（1 = Definitely work 〜 7 = Definitely fun）をどこで撃つか | ⚠️★★★ **Phase1 には入れない**（PreReg-2 の凍結に荷重する）。★ 送り先は **Phase 1.5 / Gate H の運用指標** |

---

## §3 ⚠️ 規約（★ 守らないと後で戻る）

- ★ **`/start-task` で `.steering/[YYYYMMDD]-[task-name]/` を作る**
- ⚠️★★★ **`citation-ssot`**: `docs/` へ主張を上げる瞬間に `docs/references.md` への **append-only 登録**が要る。
  ★ **renumber 禁止・tombstone・番号の再利用禁止。**★ 次の空き番号は **[P192] / [V89]**。
  ★ 検算は `PYTHONUTF8=1 python scripts/check_citations.py`
- ⚠️ **`verify-before-claiming`**: 「〜は不要」「〜は壊れる」と断定する前に一次まで降りる
- ⚠️ **`docs/glossary.md`**: 新しい用語を確定したら追記する（★ **禁止用語の確認も含む** —— ★ 2026-08-30 に
  「歩数達成 / 距離達成」「あなたは歩いた等の断定」「不便益 HCI である」「不便益を測定可能にした」を追加した）
- ★ **`/finish-task` で完了処理**。⚠️ **`/cross-review` は各タスク完了時に必須**
  （★ memory: 無関係な未コミット変更でブロックされるので `scripts/run-codex-review.sh -- <paths>` で
  パス限定。★ Codex は `--sandbox read-only` では repo を読めないので**資料はプロンプトに貼る**）

## §4 ⚠️ 落とし穴（★ 2026-08-30 に実測）

1. ⚠️★★ **ヒアドキュメントは CJK ＋ 記号の混在でシェル引用が壊れる。**
   → ★ **Write ツールで Python スクリプトを作り、アンカー文字列の出現回数を検算してから置換する**形が安定した
   （★ `scratchpad/patch_*.py` の形。★ **1 件でも当たらなければ全体を中止**させること）。
2. ⚠️★★ **Windows コンソールは cp932** → Python は **`PYTHONUTF8=1`**。
3. ⚠️ **WebFetch は PDF 本文を読めない** → ★ **保存して pypdf**。
4. ★ **ACM DL の PDF は `curl -sL -A "<Chrome UA>" https://dl.acm.org/doi/pdf/<doi>` で取れる場合がある**
   （★ DOI ごとに成否が違う）。⚠️ **MDPI は 403 が固い。**
