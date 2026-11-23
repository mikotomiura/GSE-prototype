# paper-write と attack-me に「想定読者に届く書き方」を足す

## 背景
論文 A（JoWR 2396）は範囲内なのに「要旨と序論から方法が何を目指すかがぼんやりとしか分からない」として査読に回されず、プログラミングの素養のない書く研究者に伝わる書き直しを招かれた（~/Affective-Tactility-Keystroke/.steering/20261118-paper-a-jowr-rewrite/ 記録 39）。書き直しの attack-me 2 round で、効いた書き方と、言い換えで生じる漂流が分かった。研究者が両 Skill に足すと決めた（2026-11-18・AskUserQuestion: 読み手は投稿先で決める・main に入れてよい）。

## ゴール
- paper-write: 想定読者の素養を Step 0 で決め、Step 3b で書き方の型と言い換えの点検を行う。
- attack-me: E が想定読者の素養で読み、読みやすさ（見ること 7）を見る。監査役が言い換えの漂流を見る。

## 受け入れ条件
- [ ] 「初学者」に一律に合わせず、投稿先のいちばん広い読者の素養で決める形になっている
- [ ] 言い換えの点検（分析の地位・著者の量と文献の指標・定義に限った性質・判定の規則）が両 Skill にある
- [ ] empirical-prompt-tuning（Lite）で不明瞭点を直した
- [ ] /cross-review（Claude と Codex）を通した
