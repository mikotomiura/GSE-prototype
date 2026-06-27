# 設計: F2 属性設問 ＋ 短縮URL反映

## 変更対象: Form_Phase1/GSE_Phase1_Form_Builder.gs のみ

### 変更1: 短縮URL定数の追加（リンク集定数の近く）
viewform を短縮した被験者向け回答URL。空文字なら formPublishedUrl_ にフォールバック。
```
var SHORT_URL_F1/F2/F4/F5 = "https://x.gd/...";
```

### 変更2: DROPBOX_FILE_REQUEST_URL を短縮版へ
`https://www.dropbox.com/request/5oak4xpqjt19zx8zvh03` → `https://x.gd/PHtwA`
コメントに長形式リダイレクト先を併記（機能不変・表示短縮のみ）。

### 変更3: メール本文 formUrls 注入（onF1Submit 内, 〜L1136）
```
f2: SHORT_URL_F2 || formPublishedUrl_(props, "F2"),
f4: SHORT_URL_F4 || formPublishedUrl_(props, "F4"),
f5: SHORT_URL_F5 || formPublishedUrl_(props, "F5"),
```
短縮URL優先。動的取得は短縮URL未設定時のフォールバックとして温存。

### 変更4: F2-A に年代・職業（buildF2, addSectionHeader 直後・a1 の前）
- 年代: addMultipleChoiceItem、必須。18〜19歳/20代/30代/40代/50代/60代以上。
- 職業: addMultipleChoiceItem、必須。学生/会社員・公務員/専門職（研究・士業・医療など）/
  自営業・フリーランス/その他。
配置を a1（作業種類）の前にして「属性」セクションの先頭が demographics になるようにする。

## なぜ F2-A か（D 記録）
- 匿名（P-ID 紐付け）データとして集計。実名↔属性を分離する data-privacy 思想に整合。
- F2-A は pre のみで matched(GSE-10/TSE) 制約に無関係 → byte 一致要件に影響しない。
- F1 に置くとロスター（PII対応表）に属性が同居しPII面が広がるため避ける（ユーザーも F2-A 選択）。

## テスト戦略（ユーザー実機・Apps Script）
- buildF2 を再実行 → F2-A 先頭に年代・職業が出る。既存 a1/a2/a3 と GSE-10/TSE は不変。
- onF1Submit ドライラン → 受信メールの F2/F4/F5 リンクが x.gd 短縮URL、Dropbox も x.gd。
- 短縮URL は viewform へ飛ぶ（編集権を渡さない）。

## 非対象
- 公開リンク集シート(PUBLIC_LINKS_URL=18vs0qbEa...)は手動管理シート。.gs 生成外。
- 管理シート buildLinksTab_ の回答URL列（研究者用・publishedUrl 表示）は変更しない（最小差分）。
