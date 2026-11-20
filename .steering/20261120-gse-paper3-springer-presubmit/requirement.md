# requirement —— 論文 3 を Springer Nature の様式へ移し、投稿前の未決 1〜7 を閉じる

## 背景
引き継ぎ `.steering/_handoff/next-session-gse-paper3-springer-template.md`。本文 main.tex と補足 supplement.tex は article の草稿の形で、投稿前の未決が 7 つ残っていた（様式・Uto の評価の設計・Liu & Meng の雑誌版・検索の記録・記号列のハッシュ・Code availability・Data availability の理由）。

## ゴール
- 本文を sn-jnl（Springer Nature LaTeX template v3.1）へ移し、規程（UMUAI の Submission guidelines を Chrome で一次から取得）に合わせる。
- 未決 1〜7 を閉じるか、残る理由を書く。

## 受け入れ条件
- 本文・補足とも警告 0 で組める。要旨 250 語以下。語数と頁を length-log に書く。
- 研究者の選択（未決 4〜7）を decisions に記録する。
- 数値の照合（Opus・読むだけ）を本文と補足に通す。
- [skip ci] で枝にだけ push。PR は出さない。
