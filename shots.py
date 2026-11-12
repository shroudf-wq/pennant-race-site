# 紹介ページの写真(assets/ の webp 4枚)を撮り直す道具
# 使い方: PYTHONPATH=<開発用リポジトリ>/tools python3 shots.py <本編の index.html> <出力先のフォルダ>
#   watch.webp  : スマホ幅(390・2倍)のハイライト観戦。打席の画面で3球目まで(乱数 3・2アウト二・三塁の場面)
#   news.webp   : 優勝の号外(乱数 4 の1年目。幅 450・2倍。上から 540 まで)
#   lineup.webp : 編成の野手(PC 幅 1100。40試合のあと)
#   standings.webp: 順位表(PC 幅 1100。40試合のあと。予想の列つき)
import sys, os
from h import *
from PIL import Image
URL = "file://" + os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
FIND = """()=>{ for(let g=0; g<200 && gameIdx<schedule.length; g++){ if(typeof cupBusy==="function" && cupBusy()){ cupAuto(); continue; }
    const x=simScheduledGame(); if(!x||!x.isMy) continue;
    const q=pickHighlights((x.r.log&&x.r.log.events)||[], league[myTeam].name);
    const k=q.findIndex(ev=>{ if(!Array.isArray(ev.pn) || !bcEachOn(ev)) return false; const bc=bcOfEv(ev); return !!bc && bc.seq.length>=3; });
    if(k<0) continue;
    const t=q[k]; startHighlightReel(x.r); const j=highlightQueue.findIndex(e=>e.inn===t.inn && e.half===t.half && e.batter===t.batter && e.pitcher===t.pitcher && e.po===t.po && e.kind===t.kind); if(j<0){ closeHighlights(); continue; }
    highlightIdx=j; renderHighlightScene(); return {inn:t.inn, half:t.half, batter:t.batter}; }
  return null; }"""
def webp(png, out, w=None, h=None, crop=None):
    im = Image.open(png).convert("RGB")
    if crop: im = im.crop(crop)
    im.save(out, "WEBP", quality=86, method=6); return Image.open(out).size
def page(br, w, h, dpr, seed):
    ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=dpr); pg = ctx.new_page(); pg.errs = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e)))
    pg.add_init_script(SEED_JS % (seed, "")); pg.goto(URL, wait_until="domcontentloaded"); pg.wait_for_timeout(500); return pg
with sync_playwright() as pw:
    br = pw.chromium.launch()
    # 1 観戦
    pg = page(br, 390, 844, 2, 3); create(pg, {"tacSel": "off"})
    pg.evaluate("()=>{ HLO.speed='normal'; HLO.bc='each'; HLO.bcv='bat'; }")
    f = pg.evaluate(FIND); got = False
    for _ in range(300):
        st = pg.evaluate("()=>{ const m=document.getElementById('bcvMarks'), b=document.getElementById('bcfBat'), p=document.getElementById('bcfPit'); return [m? m.children.length : 0, b? b.className.baseVal||b.getAttribute('class')||'' : 'x', p? p.getAttribute('data-f') : 'x']; }")
        if st[0] >= 2 and "sw" not in st[1] and "fo" not in st[1] and st[2] == "0":
            pg.wait_for_timeout(250); pg.locator("#highlightOverlay .hlBox").screenshot(path="/tmp/s_watch.png"); got = True; break
        pg.wait_for_timeout(40)
    print("watch", f, got, webp("/tmp/s_watch.png", os.path.join(OUT, "watch.webp")) if got else None, pg.errs[:2])
    pg.context.close()
    # 2 号外(優勝)
    pg = page(br, 560, 1100, 2, 4); create(pg); pg.evaluate(SEASON)
    nid = pg.evaluate("()=>{ const n=newsArchive.find(n=>n.kind==='pennant'); return n && n.id; }")
    pg.evaluate("(id)=>openNews(id)", nid); pg.wait_for_timeout(800)
    sel = pg.evaluate("""()=>{ const c=[...document.querySelectorAll('#playerModal *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>380 && r.height>500 && /np|paper|nl/i.test(e.className||''); });
        c.sort((a,b)=>a.getBoundingClientRect().width-b.getBoundingClientRect().width); return c.map(e=>e.tagName+'.'+String(e.className).split(' ').join('.')+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height)).slice(0,4); }""")
    print("news cands", sel)
    pg.screenshot(path="/tmp/s_news_full.png", full_page=False)
    pg.locator("#playerModal article.paper").screenshot(path="/tmp/s_news.png")
    im = Image.open("/tmp/s_news.png"); print("news", im.size, webp("/tmp/s_news.png", os.path.join(OUT, "news.webp"), crop=(0, 0, im.size[0], min(im.size[1], round(im.size[0]*1.05)))))
    pg.context.close()
    # 3・4 編成・順位表(40試合のあと)
    pg = page(br, 1100, 900, 1.25, 4); create(pg)
    pg.evaluate("()=>{ for(let g=0; g<400 && league[myTeam].w+league[myTeam].l<40; g++){ if(typeof cupBusy==='function' && cupBusy()){ cupAuto(); continue; } simScheduledGame(); } }")
    pg.evaluate("()=>{ try{ closeModal(); }catch(e){} }")
    pg.add_style_tag(content="#toast,#tipHost{display:none!important}")
    pg.click("#mainNav [data-p=lineup]"); pg.wait_for_timeout(600)
    pg.evaluate("()=>{ const n=document.getElementById('openingNotice'); if(n) n.classList.add('hidden'); }")
    b = pg.locator("#p-lineup .card").first.bounding_box()
    pg.screenshot(path="/tmp/s_lineup.png", clip={"x": b["x"], "y": b["y"], "width": b["width"], "height": round(b["width"] * 0.6)})
    pg.click("#mainNav [data-p=standings]"); pg.wait_for_timeout(600)
    pg.locator("#p-standings .card").first.screenshot(path="/tmp/s_stand.png")
    for src, name in (("/tmp/s_lineup.png", "lineup.webp"), ("/tmp/s_stand.png", "standings.webp")):
        im = Image.open(src).convert("RGB"); im = im.resize((1100, round(im.size[1] * 1100 / im.size[0])), Image.LANCZOS); im.save(src)
        print(name, webp(src, os.path.join(OUT, name)))
    print("pc", pg.evaluate("()=>[league[myTeam].w,league[myTeam].l]"), pg.errs[:2])
    br.close()
