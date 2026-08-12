# タスクリスト — Step 3（層 0 を鳴らす ＋ リアルタイム化）

## 準備
- [x] 引き継ぎ §1 の 4 文書を読む（S0-D1〜D14 / spec §1§2§5 / verification-log §6.9 / D21）
- [x] 必須 Skill を読む（`reproducibility-discipline` / `verify-before-claiming` / `data-privacy` / `browser-verification` / `grilling`）
- [x] grill で判断分岐を閉じる（試聴媒体 / 候補の軸 / 試聴時間）→ `decisions.md` S3-D1〜D10

## experiments/ を起こす（★ Step 3 から義務）
- [x] `experiments/20260812-expression-layer0-drone/` を作る
- [x] `SEED`（★ 乱数を使っていないこと自体を記録）/ `data.md`（sha256 で固定）/ `env.md`
- [x] `HMM_VERSION` (0.3.0) / `EXPR_VERSION` (0.2.0-step3) を刻む
- [x] `run.sh check | data | serve | all` で 1 コマンド再現

## 実装
- [x] `layer0.config.json`（★ 凍結物・合成パラメータ ＋ `expr_version`）
- [x] `expr_smooth.py` の `EXPR_VERSION` を `0.2.0-step3` へ（★ 定数 1 行のみ）
- [x] ~~`scripts/csv_to_js.py`~~ → ★ **作らない**（S3-D9。`FileReader` で渡す）
- [x] `player/layer0.html` — 層 0 の実時間合成
  - [x] 持続音 ＋ 整数次倍音のみ（★ 常に最大構成で組み、作り直さない）
  - [x] ★ **停止ボタン**（ランプで 0 へ落としてから suspend）
  - [x] ★ **音量スライダ**（`setTargetAtTime` で連続変更）
  - [x] 候補の軸切替（基音 / 減衰則 / 超低速ゆらぎ）★ **全軸が連続ランプだけで移る**
  - [x] Step 3b: 平滑化 CSV を ±0.5 dB でマスターゲインに乗せる（★ 既定 OFF）
  - [x] S3-D6: 離席復帰の 2 案（carry / restart）を切り替え可能に
  - [x] 自己検査モード（`OfflineAudioContext` + Hann 窓 DFT + 逆検査）

## テスト（★ 検査を書いたら「壊した状態で赤くなる」ことを必ず実測する）
- [x] `scripts/layer0_selftest.py` — **30 ok / 0 fail**
- [x] ★ **逆検査（meta）— 25 ok / 0 fail**。★ **本物の silent pass を 1 件検出**（音量スライダの検査が緩かった）
- [x] `expr_smooth.py --selftest` — **51 ok / 0 fail**（版 bump 後も回帰なし）
- [x] 実データ 3 本（P010 / P011 / P013）を通す — **exit 0**、P010 は §6.9.2 の実測値と一致
- [x] ★ `git check-ignore` で実データ・派生物が載らないことを実測（`run.sh check` 手順 3）
- [x] ブラウザ自己検算: **24 通りすべて PASS・最悪 −192.6 dB**（判定 −60 dB）
- [x] ★ 逆検査が赤くなること（包絡 −13.0 dB / 側帯波 −19.0 dB）
- [x] ★ 陽性対照（ゆらぎ 0.005 / 0.0031 Hz を −24 dB 台で検出）＝ 計器が生きている証拠
- [ ] ⚠️ **停止ボタン / 音量スライダが実際に効くこと** — ★ **未検証**（Chrome ウィンドウが最小化）
- [ ] ⚠️ **10 分連続再生**（メモリ・位相）— ★ **未実施**
- [ ] ⚠️ `file://` 直開き — ★ **未確認**（`http://127.0.0.1:8766` で検証した）

## 研究者に渡す（★ DONE-B — エージェントは判定しない）
- [x] 聴き方の手順を `notes.md` §4 に書く
- [x] ★★ **B1** 10 分聴いて「気になるか」 → **通過**（2026-08-12・「作業というていでは気にならなかった」）
- [x] 耳の結果を `notes.md` §0 / `decisions.md` S3-D11〜S3-D16 に記録（★ 所見を要約で潰さず保存）
- [x] ★★★ **耳が仕様を動かしたので `media-expression-spec.md` §2 / §7 / §9 を改訂**
      （S3-D10 の約束「実装だけ先に進めて仕様を放置しない」を実行）
- [ ] **B2** 採る候補を選ぶ → ★ **意図的に開いたまま**（S3-D15。層 0 の形がまだ動く）
- [ ] **B3** ★ 離席復帰は carry / restart どちらか → Step 4 へ持ち越し（2 Step 目）
- [ ] **B4** ★★★ 停止・音量が**実際に効く**か（交渉不可）→ Step 4 へ持ち越し
- [ ] **B5** どの減衰則で「ブラウンノイズに聴こえた」か → Step 4 へ持ち越し

## 次への引き継ぎ
- [x] `.steering/_handoff/next-session-prompt-step4-layer2-grain.md` を作成
      （★ 主題は「音を増やすこと」ではなく **S3-D13 の混同問題**）

## レビュー
- [ ] ⚠️ `code-reviewer` + `security-checker` の並列起動 — ★ **未実施**
      （本セッションのシステム指示が「ユーザーの要求なしに Agent を呼ばない」と定めているため。
      ★ **skip を隠さない**。CLAUDE.md の要求とぶつかるので、実施要否は研究者の判断）
- [ ] ⚠️ `/cross-review` — ★ **未実施**（同上。⚠️ 実施する場合も **実データを diff に含めない**）
- [x] 自前レビューで発見・修正した欠陥 5 件（`design.md` の差分表 2–7）

## ドキュメント
- [x] `docs/glossary.md` に表現層の用語 15 件を追加（層 0–3 / 分節 / ISE / 禁止帯 / オフスイッチ要件 ほか）
- [x] `notes.md` に仮説・PreReg との関係を書く（★ **接続が無いことを明示**）と出典 `[Pn]`
- [x] 引き継ぎ §7 の「やり残し」4 件の現況を `notes.md` §7 に記録（★ 4 件とも未着手）

## 完了処理
- [x] `design.md` の最終化（★ 実装中に変わった 7 点を差分表に）
- [x] `decisions.md`（S3-D1〜S3-D10）
- [ ] `/finish-task` → git commit
