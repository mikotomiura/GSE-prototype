# 次のセッション —— 人ごとのリズムの型の world: 試作の時間を測る → 固定のコミット → 研究者の許可 → 4 段の計測

> 書いた日: 2026-11-23（G-GEAR）。タスク: `.steering/20261123-rhythm-stage-person-world/`。ブランチ `docs/rhythm-stage-person-world`・worktree `C:/wt/rhythm-stage-person-world`（最後のコミットはこのメモを足したもの。その 1 つ前が `fa2ac154`）。元の引き継ぎは `next-session-rhythm-stage-person-world.md`（§4 の「守ること」はそのまま効く）。

## 0. 始める条件（研究者の指示）

研究者が別のセッションで WSL を使う重い処理を回している。**それが終わってから**始める。2026-11-23 の時点で `vmmemWSL` が約 17 GB を使っており、試作が 2 回「メモリ不足」で Claude Code に止められた。

始める前に一次で確かめて記録する。

1. `tasklist //FO CSV //NH | grep -i -E "python|vmmem"` で、`vmmemWSL` が無いか小さいこと、python が 1 つも動いていないことを見る。WSL が大きいまま残っていたら、研究者に別のセッションの処理が終わったかを聞く（自分で `wsl --shutdown` しない）。
2. `gh run list --limit 5` で CI が走っていないことを見る。
3. `git -C C:/wt/rhythm-stage-person-world status --short` がきれいで、`experiments/zz-proto-person-world/` が無いこと。

## 1. ここまでの状態

- design・計器・自己検査（325 件 ok・失敗 0）・変異（19 本・生き残り 0）・code-reviewer と security-checker・`/cross-review` 2 巡（判断 10・11）まで終わっている。
- 残りは tasklist の「試作で時間を測る」から後。

## 2. 試作で時間を測る（並列 12）

研究者の指示で、並列は 12 に戻す（前のセッションで 6 への引き下げを提案したが、WSL の処理が終わってから 12 で回すことになった）。

```
bash C:/wt/rhythm-stage-person-world/.steering/20261123-rhythm-stage-person-world/proto/proto_run.sh <scratchpad の絶対パス> 12
```

- `run_in_background` で、ほかの重い処理と重ねずに 1 本だけ回す。
- 写し `experiments/zz-proto-person-world/`（seed 4000・git の外）で m049 を ceiling → pilot → apply-pilot → smoke → main と回し、段ごとの秒を `<scratchpad>/proto_times.log` に書く。
- 試作の値は時間の見積もりだけに使い、design の判断には使わない。本番の seed（20261125 とその +1・+2）の列は固定の前に開かない。
- 終わったら `proto_times.log` と各段のログを一次で読む（完了の通知を信じない）。そのあと写しを `rm -rf` で消す。コミットしない。

前のセッションで分かっていること:
- ceiling は 333 秒（その前の回は 376 秒）。
- pilot は並列 12 で本体が約 1.1 GB、子のワーカーが 12 個 × 約 150 MB、合わせて約 3 GB。
- Claude Code がバックグラウンドの shell をメモリ不足で止めると、外側の bash だけが止まり、python の木は孤立して残る。孤立したら `tasklist` で PID を確かめ、研究者に `! taskkill //PID <起動元> //T //F` を頼む（自動モードは Claude の taskkill を拒む）。自分から回し直さない。

測った時間を design §4（所要）の見込み（段あたり 2.5〜3.5 時間、4 段で 8〜11 時間）と並べて、design §4 に実測として書き足す（判定の規則は変えない）。

## 3. 固定のコミット → 研究者の許可

1. design・計器・試作の時間を、どの結果よりも前にコミットして push する（PR は出さない。計測の run の間は push だけ）。コミット本文に、固定の前に計算した値は試作（seed 4000）の時間と ceiling の通り抜けだけで、本番の seed の列は開いていないことを書く。
2. AskUserQuestion で研究者に 4 段の計測を始めてよいかを聞く（推奨と理由・所要の実測の見込みを添える・日本語）。

## 4. 4 段の計測（許可の後）

段の順は m049 → m068 → r049 → r068。各段で 下見 0（`--ceiling`）→（r の段は `--pilot-k` → `--apply-pilot`）→ 下見 1（`--pilot`）→ `--apply-pilot` → `--smoke` → `--main`、いずれも `--jobs 12`。

- 各段の前に §0 の 1・2 を見て記録する。重い処理は 1 本ずつ。
- 段の本番の結果（`results/<step>/main/`）はコミットしてから次の段へ（run.sh が前の段の summary を求める）。
- スモークは同じ seed で 2 回回して、時間の欄と `provenance.json` を除いて一致すること、違う段どうしで違いが出ることを確かめる（design §6）。

## 5. その後

notes.md と `check_notes.py` → 次の段への引き継ぎ → `/finish-task`（commit → push → PR → CI 緑なら merge）。

## 6. 守ること（追加分）

元の引き継ぎ §4 に加えて:
- 応答・記録・AskUserQuestion の引数は日本語。文脈の要約から再開した直後の 1 通目も日本語で書く。
- python の置換は Edit か Write の .py で（heredoc に `cat > /dev/null` を残すと止まる）。
- 実行中に計器のファイルを編集しない（自己検査の J2・J3 が `inspect.getsource` の行のずれで落ちた）。
