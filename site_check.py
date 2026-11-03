# 紹介サイト(index.html)の確かめ。使い方: python3 site_check.py 広告なしの index.html 広告ありの index_ad.html
import sys, os
from playwright.sync_api import sync_playwright
plain, ad = [os.path.abspath(x) for x in sys.argv[1:3]]
res=[]
def ck(n,ok,info=""): res.append(bool(ok)); print(("OK  " if ok else "NG  ")+n+("" if ok else " :: "+str(info)))
U=lambda p:"file://"+p
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(path,w=1280,h=900,rm="no-preference"):
        c=br.new_context(viewport={"width":w,"height":h},reduced_motion=rm); pg=c.new_page(); pg.errs=[]
        pg.on("pageerror",lambda e:pg.errs.append(str(e))); pg.on("console",lambda m: pg.errs.append(m.text) if m.type=="error" and "fonts.g" not in m.text and "net::" not in m.text else None)
        pg.goto(U(path)); pg.wait_for_timeout(1800); return pg
    pg=page(plain)
    ck("1 エラーなし",not pg.errs,pg.errs)
    ck("2 広告なしの版には広告の欄がない",pg.evaluate("()=>!document.querySelector('.ad')"))
    ck("3 体験版・本編のリンク",pg.evaluate("()=>[...document.querySelectorAll('.cta a')].map(a=>a.getAttribute('href'))")==["play/","game/"])
    pg.evaluate("()=>window.scrollTo(0,document.documentElement.scrollHeight/2)"); pg.wait_for_timeout(1200); pg.evaluate("()=>window.scrollTo(0,0)")
    ck("4 画像は4枚とも読めて代替の文がある",pg.evaluate("()=>{const i=[...document.images]; return i.length===4 && i.every(x=>x.alt.length>10)}") and all(pg.evaluate("()=>[...document.images].map(x=>x.complete&&x.naturalWidth>0)")),pg.evaluate("()=>[...document.images].map(x=>[x.complete,x.naturalWidth])"))
    ck("5 横にはみ出さない(PC)",pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"))
    pg.evaluate("()=>document.querySelector('#railList a[data-k=\"3\"]').click()"); pg.wait_for_timeout(1200)
    ck("6 左の帯:「お知らせ」を押すと三塁が点く",pg.evaluate("()=>[document.getElementById('b3').classList.contains('on'), document.querySelector('#railList a[aria-current]').dataset.k]")==[True,"3"])
    pg.evaluate("()=>window.scrollTo(0,document.documentElement.scrollHeight)"); pg.wait_for_timeout(900)
    ck("7 いちばん下で本塁に戻る",pg.evaluate("()=>[document.getElementById('b0').classList.contains('on'), document.querySelector('#railList a[aria-current]').dataset.k]")==[True,"4"])
    pk=page(plain); pk.keyboard.press("Tab"); ck("8 キーボード:読み込んだ直後の最初の Tab で「本文へ」が出る",pk.evaluate("()=>document.activeElement.className")=="skip")
    pg2=page(plain,rm="reduce"); ck("9 動きを減らす設定では板が掛からない",pg2.evaluate("()=>getComputedStyle(document.querySelector('.plate')).animationName")=="none")
    pg3=page(plain); ck("10 通常は板が掛かる動きがある",pg3.evaluate("()=>getComputedStyle(document.querySelector('.plate')).animationName")=="hang")
    pa=page(ad); L=pa.evaluate("()=>[...document.querySelectorAll('.adList a')].map(a=>[a.getAttribute('href'),a.target,a.rel])")
    ck("11 広告:2つ・https・別タブ・sponsored",len(L)==2 and all(h.startswith("https://") and t=="_blank" and "sponsored" in r and "noopener" in r for h,t,r in L),L)
    ck("12 広告:札と決まりの文",pa.evaluate("()=>document.querySelector('.adTag').textContent==='広告' && /適格販売/.test(document.querySelector('.ad').textContent)"))
    ck("13 広告:文字は変換される",pa.evaluate("()=>!document.querySelector('.adList b') && document.querySelector('.adList').innerHTML.includes('&lt;b&gt;')"))
    ck("14 広告:エラーなし",not pa.errs,pa.errs)
    ps=page(ad,w=390,h=844)
    ck("15 横にはみ出さない(390px)",ps.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"),ps.evaluate("()=>[document.documentElement.scrollWidth,innerWidth]"))
    ck("16 スマホ:上の帯に今の場所が出る",ps.evaluate("()=>getComputedStyle(document.getElementById('now')).display!=='none' && document.getElementById('now').textContent==='遊ぶ'"))
    big=ps.evaluate("()=>[...document.querySelectorAll('a.btn,.adList a')].every(a=>a.getBoundingClientRect().height>=44)")
    ck("17 スマホ:リンク・ボタンの高さは44px以上",big)
    # ---- 共有のボタンと SNS のカード(v1.8.f の続き) ----
    import re as _re, os as _os
    base=_os.path.dirname(plain)
    html=open(plain,encoding="utf-8").read()
    m=_re.search(r'property="og:image" content="([^"]+)"',html)
    from PIL import Image as _I
    im=_I.open(_os.path.join(base,"assets","og.png"))
    ck("18 SNS のカード:og:image(絶対のURL)・twitter:card・画像は 1200×630",bool(m) and m.group(1).startswith("https://") and m.group(1).endswith("assets/og.png") and 'name="twitter:card" content="summary_large_image"' in html and im.size==(1200,630),(m and m.group(1),im.size))
    c2=br.new_context(viewport={"width":1280,"height":900}); c2.add_init_script("navigator.share=undefined;"); ps=c2.new_page(); ps.errs=[]
    ps.on("pageerror",lambda e:ps.errs.append(str(e))); ps.goto(U(plain)); ps.wait_for_timeout(1200)
    t0=ps.evaluate("()=>document.getElementById('shareText').value")
    x0=ps.evaluate("()=>document.getElementById('shX').getAttribute('href')")
    ck("19 紹介文が最初から入っていて、X のリンクに文と URL が付く",("ペナントレース" in t0) and x0.startswith("https://twitter.com/intent/tweet?text=") and "&url=" in x0 and "%E3%83%9A%E3%83%8A" in x0,x0[:120])
    ps.fill("#shareText","テスト文 #野球ゲーム"); x1=ps.evaluate("()=>document.getElementById('shX').getAttribute('href')"); b1=ps.evaluate("()=>document.getElementById('shBs').getAttribute('href')")
    ck("20 文を書き換えると、X・Bluesky のリンクも変わる",("text=%E3%83%86%E3%82%B9%E3%83%88" in x1) and ("%E3%83%86%E3%82%B9%E3%83%88" in b1),(x1[:100],b1[:100]))
    ps.fill("#shareText",t0); ps.click("#shNext"); t2=ps.evaluate("()=>document.getElementById('shareText').value")
    ck("21 「別の文にする」で文が変わり、3つを回る",t2!=t0 and ps.evaluate("()=>{ const a=[document.getElementById('shareText').value]; for(let i=0;i<2;i++){ document.getElementById('shNext').click(); a.push(document.getElementById('shareText').value);} document.getElementById('shNext').click(); return new Set(a).size===3 && document.getElementById('shareText').value===a[0]; }"))
    ps.click("#shCopy"); ps.wait_for_timeout(400)
    ck("22 「文をコピー」で知らせが出る",ps.evaluate("()=>/コピー/.test(document.getElementById('shareMsg').textContent)"),ps.evaluate("()=>document.getElementById('shareMsg').textContent"))
    ck("23 共有メニューのボタンは、使えない端末では出ない",ps.evaluate("()=>getComputedStyle(document.getElementById('shNative')).display==='none'"))
    c3=br.new_context(viewport={"width":390,"height":844}); c3.add_init_script("navigator.share=function(){return Promise.resolve()};"); p3=c3.new_page(); p3.goto(U(plain)); p3.wait_for_timeout(1200)
    ck("24 共有メニューのボタンは、使える端末(スマホ)では出る",p3.evaluate("()=>getComputedStyle(document.getElementById('shNative')).display!=='none'"))
    ck("25 スマホ幅:横にはみ出さず、ボタンの高さは44px以上",p3.evaluate("()=>document.documentElement.scrollWidth<=innerWidth && [...document.querySelectorAll('.sbtn')].filter(b=>getComputedStyle(b).display!=='none').every(b=>b.getBoundingClientRect().height>=44)"))
    ck("26 エラーなし",not ps.errs,ps.errs)
    br.close()
print("%d/%d"%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
