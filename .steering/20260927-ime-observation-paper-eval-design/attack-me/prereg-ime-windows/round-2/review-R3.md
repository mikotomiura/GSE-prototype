# round 2 — R3（推奨 minor）

接地: Lakens 2022（l.9–12 の 6 つの n の正当化・693–697 "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval …"）・Wicherts 2016（461–465 "… (it should be exhaustive)."・210 "C4 D7 Determining the data collection stopping rule on the basis of desired results or intermediate significance testing"・215 "A4 Deciding on how to deal with outliers in an ad hoc manner"）・Koo & Li 2016（989 "researchers should explicitly specify the ICC form they used in their calculation."）。

引き継ぎ: R3-1 部分的に解消（経路の切り替えと弁の行）・R3-2 部分的に解消（証拠が `9fb61af2`・Python 1 つ）・R3-3〜R3-5 解消・R3-6 部分的に解消（設計効果と表の命令が無い）・R3-7 部分的に解消（README とぶつかる）・R3-8〜R3-10 解消。

評価: a4 b3 c4 d3 e4 f3 g3。

新しい指摘（すべて minor か nit）:
- N1 macOS の証拠を凍結しない commit で取っている → 凍結の commit で取り直すか、その後に macOS が使うファイルが変わっていないことを書く。自信 中
- N2 経路は時点ごと・弁は行を書く → §10.3 に 3 点、§10.7 の診断に「25 秒を超える行」。自信 中
- N3 `cpu_all_zero` の食い違い（idle の真の 0 で 3 回やり直して not measured になる道）→ 優先する側を 1 文で。N1 と N3 は凍結の前に必ず直す。自信 高
- N4 層の表を作る命令と Windows の計画の Σm²/Σm が無い → 命令を示し、範囲を書くか「§3.3 の D の上限は Windows に適用されない」と明記。自信 高
- N5 D4 は観測器の誤りを停止の理由にする選別の脅威 → §10.11 に限界、D4 で中止した run の数字を観測器の結果として報告すると §10.8 に。自信 中
- N6 問 5 の `working` に D2 と D4 が適用されるか・どこに記録するか → §10.8 と `data.windows.md` に。自信 中
- N7 凍結の門が Windows の凍結の前の解析を許す → 限界として明記、または §10 の印を要求。追補の OSF 登録に含めるもの（commit・export の一覧の SHA・notes.md）を §10.1 に。自信 中
- [nit] N8 節番号の参照・§10.6 に「凍結の前に変われば直す」・README の LF の取り出し方。

総合: minor（計画の立て直しは不要）。

読めなかった範囲: 応答に列挙。一覧の外は開いていない。注入の疑い: なし。
