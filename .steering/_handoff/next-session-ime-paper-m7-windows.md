# 次セッション — IME 論文: Windows の追補の OSF 登録と M7（Windows の本計測）

> ★ **2026-10-03 追記: 追補は OSF に登録済み — https://osf.io/4jwzn（DOI 10.17605/OSF.IO/4JWZN・2026-10-03T13:56 UTC・添えたファイルの SHA が一致・`notes.md` に記録）。§1 の未了 1 は済み。**
> 作成: 2026-10-03（Surface Pro 8・M5 と M6 を終えたセッションの最後）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 137〜142**）・`tasklist.md`・`pilot-windows-1-notes.md`・`attack-me/prereg-ime-windows/round-1・2/verdict.md` と、凍結した `papers/ime-observation/experiment/preregistration.md` の **§10**・`deviations.md`・`data.windows.md`・`kit/run/README.windows.md`。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → 状態を確かめる（PR の merge・タグ ime-observation-prereg-windows が origin にあるか）。
.steering/_handoff/next-session-ime-paper-m7-windows.md を読んで §2 から始めてください。
一次は decisions.md の判断 137〜142、事前登録 §10（とくに §10.6〜§10.9）、deviations.md、data.windows.md、kit/run/README.windows.md。
⚠️ 凍結のタグ ime-observation-prereg-windows のコードは変えない（変えるなら deviations.md に逸脱として先に記録し、研究者に戻す）。
⚠️ Windows の計測は、追補の OSF 登録の日付より後でなければならない（§10.1）。登録が済むまで計測しない。
⚠️ 合成キーを送る run は研究者の答えで「離席中に自動」（研究者は常に離席している扱い）。
Skill: verify-before-claiming・reproducibility-discipline・git-workflow・data-privacy。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-03 の終わり）

- **M5（Windows の較正パイロット）と M6（Windows の追補）は済んだ**。Surface Pro 8 = 計測する機械で行った（判断 136）。
  - 凍結の commit `a57c4fd79134d68364c29b440637bfb717a881cb`・タグ `ime-observation-prereg-windows`（annotated）。`frozen_at: 2026-10-03`・`sha256` は macOS と同じ値（`64dfbb6e…`）。
  - 書き出しの一覧: 108 ファイル・SHA-256 `f61af353301e1370ac27c4a7425e8c2eb32991df9f7a2a765a26948da87787b7`（`.steering/…/freeze-export-list-windows.txt`）。凍結したファイルの SHA-256 `f86209631e495d2c7e80dab266a91814728aa55a18485da106df836c3cec2b1d`。`experiment/notes.md` に記録済み（OSF の URL はまだ）。
  - 逸脱 D1（Windows の S4 は Esc 3 回）・D2（Windows の計画と参照 `win_tsf` の照合）・D3（長い試行は oracle の送出の幅・正解の長さは感度）・D4（観測の key 行が送った押下で説明されなければ中止）。macOS の計画と結果が変わらないことは `3cc151c7` で確かめた（`deviations.md` 末尾）。
  - attack-me: round 1 major → round 2 minor → 直して凍結。完了時レビュー（code-reviewer ∥ security-checker）の指摘も直した。⚠️ `/cross-review` は省略（この Surface に Codex CLI が無い・`python3` が Store のスタブで Codex 系の hook が fail-closed になる）。
- **未了**:
  1. ★ **研究者の作業: OSF Registries に追補を登録する**（macOS の登録 `https://osf.io/9nh7r` の前例。添えるもの: 凍結したファイル〔`git show ime-observation-prereg-windows:papers/ime-observation/experiment/preregistration.md` を LF のまま〕・commit の 40 桁・一覧の SHA）。→ URL・DOI・登録の日付・添えたファイルの SHA-256 を `experiment/notes.md` に追記（macOS の段落と同じ形）。
  2. PR（枝 `feature/ime-m6-windows-addendum`）の merge。
- この機械の注意: 作業コピーは `core.autocrlf=true`（CRLF）→ 計画は**書き出し（LF）から**作る。`kit/check.sh` は LF の worktree（`git -c core.autocrlf=false worktree add …`）で回す。`python3` は `~/ime-pilot/bin` を PATH の先頭に置くと 3.11.9 になる。パイロットの生ログ・封印は `~/ime-pilot/runs/`（git に入れない）。

## §2 やること（M7: Windows の本計測・登録の後）

1. 登録の日付を `notes.md` で確かめる（今日より前・計測より前）。
2. タグ `ime-observation-prereg-windows` から書き出す（`export.internal.py --allow-missing-license`）→ 一覧の SHA が `f61af353…` と一致することを確かめる → 書き出した側でロガーと `refinput-windows` をビルド（`--locked`）。
3. `kit/run/README.windows.md` の手順: 計画を作り SHA が `b7bdf8fc…36b0` と一致すること・セルのファイル（`cell.windows.json` を写して `ime` に版、`clock_sync_disabled` / `auto_update_disabled` を true に）・Windows 11 Home の更新の一時停止（12〜13 時間を覆う）と「時刻を自動的に設定」を切る・電源。
4. ★ §10.8: **IME の版（`IMJPTIP.DLL`）がパイロット（10.0.26100.8875）と違えば**、先に 39 試行の点検（`plan-verify` と同じ形）を回し、39 / 39 でなければ測らずに研究者に戻す。
5. 本計測（Windows のセル）→ 直後に `delivery.py` の点検（§3.4 と §10.8: k = 0・`excluding_mode_keys`・`src` が `win_tsf`・D4 の観測の区間）→ `data.windows.md` の Run checks に 1 行 → **すぐ commit して push**（§10.8）。中止なら同じ計画で最大 3 回。
6. 問 5 の Windows（`idle` → `working`・別の夜・`kit/e3`）。`working` も §10.8 の規則と点検の行。`cpu_all_zero` は `working` だけ不十分（§10.9）。
7. 解析は §10.7 の命令（`pipeline.py --runs-from experiment/data.windows.md … --out experiment/results/windows`）で、Windows のタグから。macOS のセルは Windows のタグから解析しない。

## §3 気をつけること

- ⚠️ 凍結のコードを変えない。欠陥が見つかれば直さずに止めて研究者に戻す（逸脱の記録は研究者が決める）。
- ⚠️ 観測の ImeShadow（セッションの行）は、計測の解析まで読まない（パイロットの封印は寄託のためにだけ開ける・§10.10）。
- ⚠️ 生ログを git に入れない・外部の LLM に渡さない。参照のログのキーコードを転記しない。
- ⚠️ 合成キーは前面の窓に入る。run の間は誰も PC に触れない（タブレットなのでタッチ・ペンも）。
- ⚠️ G-GEAR は Windows の CI の self-hosted runner。この Surface はそうではない（確かめてから）。
