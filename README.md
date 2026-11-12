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
3. **確かめ**:`python3 site_check.py 広告なしの index.html 広告ありの index_ad.html`(26項目。`index_ad.html` は JSON を渡して別名で作る。**このフォルダの中に作る**=`assets/` の絵がない所に作ると 15 が NG になる。11・13 はテスト用の広告の設定を前提にした項目で、いまの `affiliate_items.json` では NG になる)。本文の動きは `motion_check.py`。
4. **体験版**:`play/index.html` を新しいサイト用の体験版に置き換える(名前は `index.html` のまま)。サイト用の体験版は、開発用リポジトリの `tools/site/` の道具(`make_lite_site.py`)で本編のソースから作る(いつもの体験版のファイルをそのまま置かないこと)。
5. **本編**:`game/index.html` を新しい本編に置き換える。

## 写真の撮り直し

- `shots.py`:`assets/` の webp 4枚(観戦・号外・編成・順位表)を本編から撮り直す道具。開発用リポジトリの `tools/h.py` を使う:
  `PYTHONPATH=<開発用リポジトリ>/tools python3 shots.py game/index.html assets`
  - 観戦:スマホ幅(390・2倍)で、乱数 3 の「4回裏・同点・2アウト二・三塁」の打席。2球目以上・打者が構えているときに撮る
  - 号外:乱数 4 の1年目のリーグ優勝の号外(幅 560・2倍。写真の下の説明の行まで)
  - 編成・順位表:乱数 4 で40試合のあと(PC 幅 1100・1.25倍で枠を切り出して幅 1100 に)
  - 本編の版が変わると、同じ乱数でも場面が変わることがある。撮ったら写しを見て、`index.template.html` の `<img>` の `width`・`height`・`alt` と写真の下の文を直す

## 本文の動き

- 見出し・説明・写真・はじめかたの手順・お知らせの行は、画面に入ったときに少し下からふわっと現れる(1回だけ。手順とお知らせは1行ずつ少しずらす)。号外の写真だけ、紙が舞い落ちるように現れる(`paperDrop`)
- 隠すのは JS が「開いた時にまだ見えていない所」に `.rv` を付けたときだけ。JS が動かない・端末で動きを減らす設定にしている人には、最初から全部見える
- 確かめ:`python3 motion_check.py index.html [写しのフォルダ]`(12項目)

## SNS の共有

- 紹介ページのトップのメタ情報(`og:image`・`twitter:card`)と、プレビュー用の画像 `assets/og.png`(1200×630)。貼ったときに画像つきのカードが出る。SNS 側が前の表示を覚えていると、反映まで時間がかかる(X・LINE などの確認ツールで取り直せる)。
- 「お知らせ」の下の「このゲームを紹介する」:紹介文(3種類。「別の文にする」で回る。書き換えられる)を入れて、X・Bluesky・LINE に投稿する画面を開く。「文をコピー」と、スマホの共有メニュー(使える端末だけ)もある。文は `index.template.html` の `V` に書いてある。
- 広告欄は `affiliate_items.json` で作る(ストアID `penrace-22`)。

## 使ってよい範囲

- 遊ぶことは自由です。
- このサイトのファイルの写しや、作り直したものを配ることはできません。著作権は作者にあります。
