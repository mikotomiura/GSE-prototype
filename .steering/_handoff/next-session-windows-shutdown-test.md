# 引き継ぎ: Windows でシャットダウン → 電源オンの後に O1（v0.1.40）が自動で立ち上がるかを点検する

作成 2026-10-09 00:10（Surface Pro 8・電源を切る直前）。電源を入れ直した後、同じ機の新しい Claude Code のセッションで研究者と一緒に行う。
返答・記録では絵文字や記号（★・⚠️）を多用しない（研究者の指摘）。

## 1. 先に読むもの

- `.steering/20261008-windows-sleep-test/shutdown-test.md`（試験前の状態・基線・手順・合否・後片付け）。**基線と合否はここが正**。
- 点検スクリプト: `.steering/20261008-windows-sleep-test/win_boot_check.py`（読むだけ。NDJSON の中身は読まない）。
- 比較の相手: `.steering/20260928-o1-resilience-g1-g2-g5/g1-windows-autostart-experiment.md`（v0.1.38・サインアウト → サインイン）。

ブランチは `docs/sync-local-o1-steering-20261008`（PR #329）。始める前に `git status` と `git fetch` だけ見る（電源を切る前に push 済み）。

## 2. 手順

1. 研究者に次の 3 つを聞く:
   - サインインした後に、`gse-next` を**手で開いていないか**（開いていたら合否 2 は判定しない）。
   - シャットダウンを選んだ時刻と、電源を入れた時刻（だいたいでよい）。
   - サインイン後に 50 文字ほど打ったか。
2. `python .steering/20261008-windows-sleep-test/win_boot_check.py`（文字化けしたら `PYTHONIOENCODING=utf-8` を付ける）。
3. `shutdown-test.md` の合否の 6 項目を、出力の実測値で 1 つずつ埋めて「結果」節に書く。
   - 自動起動の判定（合否 2）では、親が `explorer.exe` であることは決め手にならない（ダブルクリックでも同じ）。起動時刻が explorer の数分後であることと、研究者が開いていないことで判断する。
   - 基線のファイルの `session_end` が、シャットダウンのときに付いたのか、次の起動の掃除（applog の `O1 orphan sweep: closed ... with session_end=...`）で付いたのかを書く。v0.1.38 のサインアウトでは掃除で付いた（終了の処理は未実装）。
4. 後片付けは `shutdown-test.md` の手順どおり。**消す前に、研究者に一覧を見せて了承を取る**。配布フォルダの `o1.autostart` を忘れない。
5. `result.md` の「まだ確かめていないこと」と、`.steering/20260926-g1-o1-mac-collection-prep/o1-resilience-findings.md` の 2026-10-08 の行に、結果を 1 行ずつ足す。
6. コミットして PR #329 に push する。この機には git の名前とメールの設定が無いので、`git -c user.name="John Do" -c user.email="johndo.mik.080@gmail.com" commit ...` とする（グローバルの設定は変えない）。

## 3. してはいけないこと

- NDJSON の生ログや打鍵の内容を外部の LLM（Codex を含む）に送らない。行の種類と件数・時刻だけを扱う。
- 研究者の了承なしに、レジストリ・`.gse`・配布フォルダ・電源設定を変えない。
- 判定できなかった項目を「問題なし」と書かない。
- 48 時間の待ちがあるので、**2026-10-11 00:00 より前に後片付けを済ませる**（P998 の記録を研究者の Drive に送らないため）。
