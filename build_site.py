# 紹介サイトの index.html を作る
# 使い方: python3 build_site.py index.template.html 出力.html [affiliate_items.json]
#   版と日付は下の VERSION・DATE。リンクの設定.json を渡すと「おすすめ(広告)」欄が入る(渡さなければ入らない)。
#   リンクの設定.json: {"head":"野球の本・雑誌のおすすめ","disc":"Amazonのアソシエイトとして、当サイトは適格販売により収入を得ています。",
#                      "items":[{"t":"本の名前","u":"https://www.amazon.co.jp/dp/ASIN?tag=ストアID-22","n":"ひとこと(省略可)"}]}
import sys, json, html
VERSION, DATE = "v1.8.g", "2026.11.03"
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
ad = ""
if len(sys.argv) > 3:
    cfg = {"head": "野球の本・雑誌のおすすめ", "disc": "Amazonのアソシエイトとして、当サイトは適格販売により収入を得ています。", "items": []}
    cfg.update(json.load(open(sys.argv[3], encoding="utf-8")))
    items = cfg["items"]
    assert 1 <= len(items) <= 4, "リンクは1〜4つ"
    for it in items:
        assert it["u"].startswith("https://"), it["u"]
        assert 0 < len(it["t"]) <= 60 and len(it.get("n", "")) <= 80
    e = lambda x: html.escape(x, quote=True)
    li = "".join('<li><a href="%s" target="_blank" rel="noopener noreferrer sponsored nofollow">%s%s</a></li>' % (e(x["u"]), e(x["t"]), ("<small>%s</small>" % e(x["n"])) if x.get("n") else "") for x in items)
    ad = ('<div class="ad">\n        <div class="adHead"><span class="adTag">広告</span><span>%s</span></div>\n        <ul class="adList">%s</ul>\n'
          '        <p class="adNote">%s</p>\n        <p class="adNote">リンクを押すと、外のサイトが新しいタブで開きます。</p>\n      </div>') % (e(cfg["head"]), li, e(cfg["disc"]))
for k, v in (("{{VERSION}}", VERSION), ("{{DATE}}", DATE), ("{{AD}}", ad)):
    assert k in s, k
    s = s.replace(k, v)
assert "{{" not in s
open(dst, "w", encoding="utf-8").write(s)
print("ok", len(s.encode()), "広告:", "あり" if ad else "なし")
