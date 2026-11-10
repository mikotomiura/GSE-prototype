# 設計

## アプローチ

`decide-win-runner` の probe の step に env `GSE_WIN_FORCE_HOSTED: ${{ vars.GSE_WIN_FORCE_HOSTED }}` を足し、script の `decide()` の直後（`RUNNER_STATUS_TOKEN` の検査より前）に「`"1"` なら hosted に決めて終わる」分岐を置く。

- 強制を token の検査より前に置くのは、強制のときに API を叩く必要が無いため。ログには強制で hosted にしたことを notice で残す（fallback の notice と区別できる）。
- `"1"` の完全一致だけを強制とする（`true`・`yes` などは従来どおり）。誤って未設定や別の値でも hosted になる側の誤りは費用の増加だけで安全側だが、意味を一つにしておく。
- `check` の runs-on の式と、`matrix.runner` 名（`gse-win-selfhosted`）は変えない。ジョブ名は hosted で走っても `check (gse-win-selfhosted, …)` のままになる（既存の fallback と同じ）。
- 戻し方: `gh variable delete GSE_WIN_FORCE_HOSTED`。コードを戻す必要はない。
- 変数が空でも "1" でもないときは、従来どおり probe したうえで notice を 1 行出す（設定の誤りを見分けるため）。
- 効く範囲: Actions は発火した ref の ci.yml を使う。push の CI は、その枝にこの変更が入っているときだけ変数が効く。main 向けの PR は merge ref の ci.yml なので、main に入った後は自動で効く。
- 判定役の `decide-win-runner` は強制中も `gse-mac`（この MacBook）で走る。強制で hosted だけで完結するわけではないが、G-GEAR を守る目的には影響しない。

## 変更対象

- `.github/workflows/ci.yml` の `decide-win-runner` の probe の step だけ。

## テスト戦略

- 取り出した probe の script を、online の `gse-win` を返す偽の `gh`・no-op の `sleep` で、強制=1／未設定（陽性対照）／`0`／空文字／強制=1 で token 無し、の 5 通りに走らせる（`env -i` で環境を絞る）。
- actionlint の指摘の数を変更の前後で比べる。
- 本番の確かめは、変数を設定した後の PR の run の `decide-win-runner` のログ。
