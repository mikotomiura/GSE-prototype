# 次セッション — IME 論文: OSF の登録の記録 → M4（Mac での macOS 本計測）

> 作成: 2026-10-02（G-GEAR・M3 の凍結を終えたセッションの最後に）。
> 前の引き継ぎ `next-session-ime-paper-m3-freeze.md` の後継（その §2 の 1〜4 は済み・5 の登録は研究者・6 の出荷はこのメモを書いたセッションで行う —— 結果は `tasklist.md` の M3 の末尾）。
> ★★★ **2026-10-03 追記（G-GEAR）: §2 の 0 と 2 は済んだ。登録は `https://osf.io/9nh7r`（DOI `10.17605/OSF.IO/9NH7R`・公開・`date_registered` 2026-10-02）で、下に書いた `mbgxz` は登録の元のプロジェクト（非公開・API は 404 のまま）。添えたファイルの SHA-256 は `fa6fd586…7773` と一致し、`notes.md` に記録した（`tasklist.md` の M3 の OSF の行）。→ Mac では §2 の 3（M4）から始める。** あわせて G-GEAR で M5（Windows の較正パイロット）を先に進める（研究者の選択・M5 は M4 にも OSF にも依存しない）。
> ⚠️ **このメモを一次資料にしない。** 一次は `.steering/20260927-ime-observation-paper-eval-design/` の `decisions.md`（**判断 130・131**）・`tasklist.md`（M3 の末尾・M4）・`_issue-plan.md`（M4・M12）と、凍結した事前登録 `papers/ime-observation/experiment/preregistration.md`（§2.2・§2.4・§3.2・§3.4・§5・§9）。状態は着手時に `git fetch` で測り直す。

## §0 打ち込む用

```
git fetch → main から作業ブランチを切る（G-GEAR では main を別の worktree が checkout していることがある）。
.steering/_handoff/next-session-ime-paper-osf-m4.md を読んで §2 から始めてください。
一次は decisions.md の判断 130・131 と、凍結した事前登録の §9・§2.4・§3.2・§3.4・§5。
⚠️ 事前登録・解析のコード・凍結のハッシュの対象は凍結済み（タグ ime-observation-prereg-macos）。変えるなら §8 の逸脱。
⚠️ OSF の登録が済むまで本計測の run を始めない（登録の日 < 最初の run）。
Skill: verify-before-claiming・git-workflow・reproducibility-discipline。
応答は日本語。公開物（papers/）は学術的な英語・GSE への言及なし。コミットは git add パス指定（-A 禁止）。
```

## §1 状態（2026-10-02 の終わり）

- **凍結した**（研究者の最終の確認つき・判断 131）。凍結の commit **`ff122e3246346da7869c4e990e4978acb1f191c6`**・annotated タグ **`ime-observation-prereg-macos`**。
  - 印: `frozen_at: 2026-10-02`・`sha256: 64dfbb6e5f08222ade1fb96a8171d97c0fa1bc9ca9adb5cc987fc27bd9a8af2a`（`--check-prereg` exit 0）。
  - 凍結したファイルの SHA-256: `fa6fd586d580c47f13506cd36a87a94c08d6b9ab55b16a7b6df0b67670f87773`（タグの blob）。
  - 書き出しの一覧の SHA-256: **`29b183ba245939ad82d9fa2d7db26e1a18520e2966f4aa9ec74478a4e51e6c49`（98 ファイル）**。一覧そのものは `.steering/20260927-ime-observation-paper-eval-design/freeze-export-list-macos.txt`。
- 凍結の直前に、試しの書き出しが `pipeline.py` の selftest の 2 行で拒否されていたのを直した（`eaaeea74`・判断 130）。⚠️ 公開物のコードを変えたら 024（書き出し）も回す。
- `experiment/notes.md` に凍結の commit・タグ・一覧の SHA-256 を書いた。**登録の URL と日付はまだ無い**。
- 出荷: PR #293 → merge `2543f9fb` → main の CI（run 36988299913）success。
- ★ **OSF の登録は送信済み・承認待ち**: **`https://osf.io/mbgxz`**（研究者が 2026-10-02 に送信・状態は pending approval）。同日 23:17 JST に公開の API（`https://api.osf.io/v2/registrations/mbgxz/`）は 404（承認待ちは外から見えない）。承認は 48 時間で自動。研究者が実際に選んだ様式・分野・ライセンス・Summary の文は聞いていない（渡した手順と推奨は `tasklist.md` の M3）。

## §2 やること

0. **登録が公開になったか確かめる**: `curl -s https://api.osf.io/v2/registrations/mbgxz/` が 200 で `public: true`。まだ 404 なら研究者に状態を聞く（承認のメール）。⚠️ 公開になるまで M4 の run を始めない。
   公開になったら:
   - API の `date_registered` を読む（これを登録日にする）。
   - 登録に添えたファイルをダウンロードし（API の `files` の関係から辿る）、SHA-256 が `fa6fd586d580c47f13506cd36a87a94c08d6b9ab55b16a7b6df0b67670f87773` か確かめる。違えば研究者に戻す（ファイルは差し替えられない）。
   - 頁で様式・Summary の文（印・commit・一覧の SHA-256 が正しいか）を確かめる。
1. （済み）OSF の登録。登録に載せたもの（§9）:
   - 凍結したファイル: タグ `ime-observation-prereg-macos` の `papers/ime-observation/experiment/preregistration.md`（SHA-256 `fa6fd586…7773`）
   - 2 つの印・凍結の commit の 40 桁・書き出しの一覧の SHA-256（§1）
   - 登録は**すぐ公開**（判断 93）。⚠️ 登録は外部への操作なので研究者が行う。
   - ★ 登録の説明に添える案（判断 132・研究者が決める）: 「commit の識別子は公開していない開発履歴のもの。公開側での照合は、公開 repo の最初の commit（凍結の書き出しそのもの）から計算した一覧の SHA-256 で行う」。理由: 公開 repo は新しい履歴で作るので、読者は 40 桁の commit とタグ `ime-observation-prereg-macos` に辿り着けない。M12 でライセンスと `CITATION.cff` を足した後の公開物からは別の一覧になる。
2. **登録の URL と日付を `experiment/notes.md` に記録する**（§9。凍結の段落の後に 1 文: `https://osf.io/mbgxz` と 0 の `date_registered`）。`_style_check.py` 0 件を確かめる。
3. **M4（Mac）**: 事前登録 §3.2 の順（ON → OFF → E3 `idle` → E3 `working`）で、各 run の前に:
   - ロガーは**凍結のタグから書き出した側でビルドする**（§2.2・判断 68）。書き出しの一覧の SHA-256 が `29b183ba…6c49` になることを Mac でも確かめる（判断 68 で機械によらず一致することは確かめてある）。
   - 計画は**凍結のタグから**生成し、SHA-256 が §2.4（ON `c7a5469d…`・OFF `3759ebf7…`）と一致すること。
   - 各 run の直後・解析の前に §3.4 の点検（`delivery.py`）→ `data.md` の run の点検の表。
   - 解析は凍結のタグのクリーンな取り出しから（§5）。
4. 出荷（git-workflow ルール 6）。

## §3 気をつけること

- ⚠️ 凍結の後は、事前登録・解析のコード・`config.json`・`SEED`・`gt_rules.json` を変えない。変えるなら `experiment/deviations.md` に逸脱として先に記録する（§8）。
- ⚠️ 封印（`sealed/`）は開けない。人の打鍵データを使わない。参照のログのキーコードを表示・転記しない。
- ⚠️ タグ `v*` は ci.yml のリリースのビルドを走らせる。IME 論文のタグに `v` を使わない（Windows の追補は `ime-observation-prereg-windows` の予定・判断 131）。
- ★ M12 への申し送り（判断 131・`_issue-plan.md` の M12）: 公開 repo の最初の commit は凍結の書き出しそのもの。
- ⚠️ 作業ツリーに別トラックの未追跡 `.steering/20260921-media-expression-theory-audit/` がある。`git add` はパス指定で。
- ⚠️ git-bash で `git show origin/main:<path>` は `MSYS_NO_PATHCONV=1`。heredoc にバックスラッシュを書かない。Windows の Python に `/c/...` のパスを渡さない。
- ⚠️ `.codex/budget.json` は台帳。`git checkout --` で戻さない。
