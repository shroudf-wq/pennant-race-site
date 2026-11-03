# ペナントレース シミュレーター 紹介サイト

架空のプロ野球リーグで遊ぶブラウザゲーム「ペナントレース シミュレーター」の紹介ページです(1ページだけ)。

- `index.html`: 紹介ページ(`build_site.py` で `index.template.html` から作る)
- `assets/`: ゲーム画面の写し(webp 4枚)
- `play/index.html`: サイト用の体験版(1ファイル。本編だけの機能のプログラムは抜いてあり、本編のセーブは読み込めない)
- `game/index.html`: 本編(正式版)。`pennant_source.html` をそのまま `index.html` の名前で置く。図鑑などの絵(`img/`)を使うときは、横に `img/` を置く

## 更新のしかた

1. **版と日付**:`build_site.py` の `VERSION, DATE` を直す。お知らせの行は `index.template.html` の `<ul class="news">` に足す。
2. **ページを作り直す**:`python3 build_site.py index.template.html index.html`(広告なし)。
   広告(おすすめ)欄を入れるときは、リンクの設定の JSON(形は `build_site.py` の頭に書いてある)を渡す:
   `python3 build_site.py index.template.html index.html affiliate_items.json`。
   広告欄には「広告」の札と、サービスの決まりの文がいつも付く。リンクは https:// だけ・最大4つ。
3. **確かめ**:`python3 site_check.py 広告なしの index.html 広告ありの index_ad.html`(17項目。`index_ad.html` は JSON を渡して別名で作る)。
4. **体験版**:`play/index.html` を新しいサイト用の体験版に置き換える(名前は `index.html` のまま)。サイト用の体験版は、開発用リポジトリの `tools/site/` の道具(`make_lite_site.py`)で本編のソースから作る(いつもの体験版のファイルをそのまま置かないこと)。
5. **本編**:`game/index.html` を新しい本編に置き換える。

## SNS の共有

- 紹介ページのトップのメタ情報(`og:image`・`twitter:card`)と、プレビュー用の画像 `assets/og.png`(1200×630)。貼ったときに画像つきのカードが出る。SNS 側が前の表示を覚えていると、反映まで時間がかかる(X・LINE などの確認ツールで取り直せる)。
- 「お知らせ」の下の「このゲームを紹介する」:紹介文(3種類。「別の文にする」で回る。書き換えられる)を入れて、X・Bluesky・LINE に投稿する画面を開く。「文をコピー」と、スマホの共有メニュー(使える端末だけ)もある。文は `index.template.html` の `V` に書いてある。
- 広告欄は `affiliate_items.json` で作る(ストアID `penrace-22`)。

## 使ってよい範囲

- 遊ぶことは自由です。
- このサイトのファイルの写しや、作り直したものを配ることはできません。著作権は作者にあります。
