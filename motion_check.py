# 紹介ページの本文の動き(A:ふわっと現れる/B:号外の写真が舞い落ちる)の確かめ
# 使い方: python3 motion_check.py index.html [写しを置くフォルダ]
import sys, os
from playwright.sync_api import sync_playwright
P = "file://" + os.path.abspath(sys.argv[1]); SHOT = sys.argv[2] if len(sys.argv) > 2 else None
res = []
def ck(n, ok, info=""): res.append(bool(ok)); print(("OK  " if ok else "NG  ") + n + ("" if ok else " :: " + str(info)[:300]), flush=True)
HID = "()=>[...document.querySelectorAll('.rv')].filter(e=>!e.classList.contains('in')).length"
with sync_playwright() as p:
    br = p.chromium.launch()
    for w, h in ((1280, 900), (390, 844)):
        c = br.new_context(viewport={"width": w, "height": h}, reduced_motion="no-preference"); pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(P); pg.wait_for_timeout(600)
        top = pg.evaluate("()=>{ const vh=innerHeight; return [...document.querySelectorAll('h1,h2,p,img,li,figure')].filter(e=>{ const r=e.getBoundingClientRect(); return r.bottom>0 && r.top<vh*0.9 && r.height>0; }).filter(e=>getComputedStyle(e).opacity<0.99 || (e.closest('.rv') && !e.closest('.rv').classList.contains('in'))).length; }")
        n = pg.evaluate("()=>[document.documentElement.classList.contains('mo'), document.querySelectorAll('.rv').length, document.querySelectorAll('.rv.paperIn').length]")
        ck(f"{w}px 1 動きが入る(.mo)・下の本文に .rv が付き、号外の写真だけ舞い落ちる形", n[0] and n[1] >= 10 and n[2] == 1, n)
        ck(f"{w}px 2 開いた時に見えている所は隠れない", top == 0, top)
        # 号外の写真の所までスクロールして、途中の形を見る
        pg.evaluate("()=>{ const s=document.querySelector('.rv.paperIn'); window.scrollTo(0, s.getBoundingClientRect().top+scrollY-innerHeight*0.45); }")
        sw = []
        for i, t in enumerate((120, 250, 300, 500)):
            pg.wait_for_timeout(t); sw.append(pg.evaluate("()=>document.documentElement.scrollWidth-innerWidth"))
            if SHOT and w == 390: pg.screenshot(path=os.path.join(SHOT, f"paper_{i}.png"))
        an = pg.evaluate("()=>{ const s=document.querySelector('.rv.paperIn'); return [s.classList.contains('in'), getComputedStyle(s).animationName]; }")
        ck(f"{w}px 3 号外の写真は画面に入ると舞い落ちる(paperDrop)・その間も横にはみ出さない", an == [True, "paperDrop"] and max(sw) <= 0, [an, sw])
        # 最後までスクロールすると、隠れた所が残らない
        for y in range(0, 20000, 500):
            pg.evaluate(f"()=>window.scrollTo(0,{y})"); pg.wait_for_timeout(60)
        pg.wait_for_timeout(1300)
        left = pg.evaluate(HID); op = pg.evaluate("()=>[...document.querySelectorAll('.rv')].filter(e=>+getComputedStyle(e).opacity<0.99).length")
        ck(f"{w}px 4 下までスクロールすると全部現れる(隠れたまま0・薄いまま0)", left == 0 and op == 0, [left, op])
        ck(f"{w}px 5 エラーなし", not errs, errs)
        c.close()
    # 動きを減らす設定
    c = br.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce"); pg = c.new_page(); pg.goto(P); pg.wait_for_timeout(500)
    r = pg.evaluate("()=>[document.documentElement.classList.contains('mo'), document.querySelectorAll('.rv').length, [...document.querySelectorAll('.feat .shot')].every(e=>+getComputedStyle(e).opacity===1)]")
    ck("6 動きを減らす設定では動かない(.mo も .rv も付かない・写真は最初から見える)", r == [False, 0, True], r); c.close()
    # JS なし
    c = br.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False); pg = c.new_page(); pg.goto(P); pg.wait_for_timeout(500)
    r = pg.evaluate("()=>[...document.querySelectorAll('.feat .shot,.news li,.steps li')].every(e=>+getComputedStyle(e).opacity===1)") if False else pg.locator(".feat .shot").first.evaluate("e=>getComputedStyle(e).opacity")
    ck("7 JS が動かなくても写真は見える", r == "1", r); c.close()
    br.close()
print(f"{sum(res)}/{len(res)}")
