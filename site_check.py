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
    pg.keyboard.press("Tab"); ck("8 キーボード:最初の Tab で「本文へ」が出る",pg.evaluate("()=>document.activeElement.className")=="skip")
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
    br.close()
print("%d/%d"%(sum(res),len(res))); sys.exit(0 if all(res) else 1)
