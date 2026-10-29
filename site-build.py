#!/usr/bin/env python3
"""Offline bilingual preview builder. No credentials, Git writes, or publishing."""
import argparse,base64,html,json,re,shutil
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--publish',action='store_true');opt=ap.parse_args()
OUT=Path(opt.output).resolve();OUT.mkdir(parents=True,exist_ok=True)
C=json.loads((ROOT/'site-data.json').read_text());CONTACT=json.loads((ROOT/'site-contact.json').read_text())['email_b64']; EMAIL=base64.b64decode(CONTACT).decode('utf-8')
banned=ROOT/'content'/'banned_words.txt'
if banned.exists():
 content_blob=json.dumps(C,ensure_ascii=False).lower()
 for term in banned.read_text().splitlines():
  term=term.strip()
  if term and not term.startswith('#') and term.lower() in content_blob:raise SystemExit('Content failed public-word check')
def esc(s):return html.escape(str(s),quote=True)
def txt(item,lang):return item[lang]
def name(id,lang):return ('zh-' if lang=='zh' else '')+id+'.html'
def pair_nodes(obj):
 if isinstance(obj,dict):
  if set(obj)=={'en','zh'}:yield obj
  else:
   for v in obj.values():yield from pair_nodes(v)
 elif isinstance(obj,list):
  for v in obj:yield from pair_nodes(v)
for item in pair_nodes(C):
 assert item['en'] and item['zh']
 for sentence in re.split(r'(?<=[.!?])\s+',item['en']):
  words=re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*(?:-[A-Za-z0-9]+)*",sentence)
  assert len(words)<=20,(len(words),sentence)
P={p['id']:p for p in C['pages']}
for lang in ['en','zh']:
 U={k:txt(v,lang) for k,v in C['ui'].items()}
 if opt.publish:U.pop('preview',None)
 def link(id):return name(id,lang)
 def case_rows(ids):
  return '<div class="case-grid">'+''.join(f'<a class="case-card" href="{link(id)}"><img src="{esc(P[id]["image"])}" alt="{esc(txt(P[id]["image_alt"],lang))}" loading="lazy" width="1280" height="720"><div class="card-meta">CASE {P[id]["case_number"]:02d} <span aria-hidden="true">↗</span></div><h3>{esc(txt(P[id]["title"],lang))}</h3><p>{esc(txt(P[id]["lede"],lang))}</p></a>' for i,id in enumerate(ids))+'</div>'
 def thought_rows(ids):
  return '<div class="thought-list">'+''.join(f'<a class="case-row" href="{link(id)}"><span class="number">0{i+1}</span><h3>{esc(txt(P[id]["title"],lang))}</h3><p>{esc(txt(P[id]["lede"],lang))}</p><span class="arrow" aria-hidden="true">↗</span></a>' for i,id in enumerate(ids))+'</div>'
 def label(title,dest,more):return f'<div class="section-label"><span>{esc(title)}</span><a href="{link(dest)}">{esc(more)}{(' <span lang="en">/ More</span>' if lang=='zh' else '')} ↗</a></div>'
 for id,p in P.items():
  title=txt(p['title'],lang);lede=txt(p['lede'],lang)
  nav=''.join(f'<a href="{link(n)}"'+(' aria-current="page"' if id==n or (n=='practice' and id.startswith('case-')) or (n=='writing' and id.startswith('thought-')) else '')+f'>{esc(U[n])}</a>' for n in ['practice','writing','updates','about'])
  sections=''.join(f'<section id="section-{i}"><h2>{esc(txt(s["title"],lang))}</h2>'+''.join(f'<p>{esc(txt(v,lang))}</p>' for v in s['paragraphs'])+'</section>' for i,s in enumerate(p['sections']))
  toc=''.join(f'<a href="#section-{i}">{esc(txt(s["title"],lang))}</a>' for i,s in enumerate(p['sections']))
  if p.get('source'):toc+=f'<a href="#sources">{esc(U["sources"])}</a>'
  header=(('' if opt.publish else f'<div class="preview">{esc(U["preview"])}</div>')+f'<header class="header"><div class="wrap header-inner"><a class="brand" href="{link("index")}" aria-label="Fate · {esc(U["home"])}"><img src="avatar.jpg" alt="" width="36" height="36">Fate<span style="color:var(--accent)">.</span></a><nav class="links" aria-label="{esc(U["home"])}">{nav}</nav><div class="tools"><button data-search-open class="search-open" aria-label="{esc(U["search"])}">/</button><a href="{name(id,"zh" if lang=="en" else "en")}" lang="{"zh-Hant" if lang=="en" else "en"}">{"繁中" if lang=="en" else "EN"}</a><button data-theme-button>{esc(U["theme"])}</button></div></div></header>')
  kicker=esc(txt(p['kicker'],lang))
  title_html='<span class="title-line">讓 AI 融入</span><span class="title-line">工作的方式。</span>' if id=='index' and lang=='zh' else esc(title)
  if id=='index':
   f=p['profile'];art='<aside class="profile-note" aria-label="'+('Personal profile' if lang=='en' else '個人標籤')+'"><p class="editorial-head">A FEW THINGS ABOUT ME</p><blockquote>'+esc(txt(f['statement'],lang))+'</blockquote><p class="profile-role">'+esc(txt(f['role'],lang))+'</p><p class="profile-previous">'+esc(txt(f['previous'],lang))+'</p><div class="profile-tags">'+''.join('<span>'+esc(t)+'</span>' for t in f['tags'])+'</div></aside>'
   body=f'<main id="main" class="wrap"><section class="hero"><div><p class="kicker">{kicker}</p><h1>{title_html}</h1><p class="lede">{esc(lede)}</p><p class="hero-principle">{esc(txt(p["principle"],lang))}</p><a class="hero-cta" href="{link("practice")}">{esc(U["explore"])}<b aria-hidden="true">↗</b></a><div class="edition">{esc(U["edition"])}</div></div>{art}</section>'
   body+=label(U['selected'],'practice',U['more_practice'])+case_rows(p['case_ids'])
   body+='<section class="journey"><div class="section-label"><span>THE JOURNEY / '+('AI TRANSFORMATION' if lang=='en' else 'AI 轉型歷程')+'</span></div><h2>'+esc(txt(p['journey_title'],lang))+'</h2><ol>'+''.join('<li><span class="stage">'+x['stage']+'</span><h3>'+esc(txt(x['title'],lang))+'</h3><p>'+esc(txt(x['text'],lang))+'</p></li>' for x in p['journey'])+'</ol></section>'
   body+=label(U['selected_thoughts'],'writing',U['more_thoughts'])+thought_rows(p['thought_ids'])
   recent=P['updates']['timeline'][-3:][::-1]
   body+='<section class="feature-note"><div><p class="kicker">'+esc(U['updates'])+'</p><h2>'+esc(txt(p['updates_heading'],lang))+'</h2></div><div><p>'+esc(txt(p['updates_description'],lang))+'</p><a class="text-link" href="'+link('updates')+'">'+esc(U['all'])+' ↗</a><ul class="recent-notes">'+''.join('<li><time datetime="'+x['date']+'">'+x['date']+'</time> <span>'+esc(txt(x['title'],lang))+'</span></li>' for x in recent)+'</ul></div></section>'
  else:
   back=f'<a class="backlink" href="{link("practice")}">← {esc(U["back"])}</a>' if id.startswith('case-') else (f'<a class="backlink" href="{link("writing")}">← {esc(U["back_thoughts"])}</a>' if id.startswith('thought-') else '')
   body=f'<main id="main" class="wrap">{back}<section class="page-hero"><p class="kicker">{kicker}</p><h1>{title_html}</h1><p class="lede">{esc(lede)}</p></section>'
   if id in ('case-continuity','case-support'):
    first=p['sections'][0]
    body+='<section class="case-intro" id="section-0"><h2>'+esc(txt(first['title'],lang))+'</h2>'+''.join('<p>'+esc(txt(v,lang))+'</p>' for v in first['paragraphs'])+'</section>'
    sections=''.join(f'<section id="section-{i}"><h2>{esc(txt(item["title"],lang))}</h2>'+''.join(f'<p>{esc(txt(v,lang))}</p>' for v in item['paragraphs'])+'</section>' for i,item in enumerate(p['sections']) if i>0)
   if p.get('image'):body+=f'<figure class="artifact"><a href="{esc(p["image"])}" aria-label="{esc(txt(p["image_alt"],lang))}"><img src="{esc(p["image"])}" alt="{esc(txt(p["image_alt"],lang))}" width="1280" height="720"></a></figure>'
   if p.get('quote'):
    quote_tag='blockquote' if p['quote_type']=='excerpt' else 'div class="viewpoint-text"'
    quote_close='blockquote' if p['quote_type']=='excerpt' else 'div'
    body+='<figure class="pullquote"><p class="quote-kind">'+esc(txt(p.get('quote_kind',{'en':'','zh':''}),lang))+'</p><'+quote_tag+'>'+esc(txt(p['quote'],lang))+'</'+quote_close+'><figcaption id="sources">'+esc(txt(p['source'],lang))+'</figcaption></figure>'
   if sections:
    body+=f'<div class="article-layout"><nav class="toc" aria-label="{"On this page" if lang=="en" else "本頁目錄"}">{toc}</nav><article class="prose">{sections}'
    if p.get('social'):body+='<div class="social-links"><a href="mailto:'+esc(EMAIL)+'">'+esc(EMAIL)+'</a>'+''.join('<a href="'+esc(s['url'])+'" rel="noopener noreferrer">'+esc(s['label'])+' ↗</a>' for s in p['social'])+'</div>'
    if p.get('related'):
     r=p['related'];body+=f'<div class="related"><p class="kicker">{esc(U["practice"] if r.startswith("case-") else U["writing"])}</p><a href="{link(r)}">{esc(txt(P[r]["title"],lang))} ↗</a></div>'
    body+='</article></div>'
   if p.get('case_ids'):body+=case_rows(p['case_ids'])
   if p.get('thought_ids'):body+=thought_rows(p['thought_ids'])
   if p.get('knowledge'):body+='<section class="knowledge" id="knowledge"><div class="section-label"><span>KNOWLEDGE / '+esc(U['knowledge_title'])+'</span></div><h2>'+esc(U['knowledge_title'])+'</h2><p>'+esc(U['knowledge_note'])+'</p><ul>'+''.join('<li><span>'+f'{i+1:02}'+'</span>'+esc(txt(x,lang))+'</li>' for i,x in enumerate(p['knowledge']))+'</ul></section>'
   if p.get('timeline'):
    months=sorted(set(x['date'][:7] for x in p['timeline']));body+='<div class="timeline-layout"><nav class="toc" aria-label="'+('Months' if lang=='en' else '月份')+'">'+''.join('<a href="#month-'+m+'">'+m+'</a>' for m in months)+'</nav><div class="timeline">'
    for m in months:
     body+='<section class="timeline-month" id="month-'+m+'"><h2>'+m+'</h2><ol>'
     for x in [t for t in p['timeline'] if t['date'].startswith(m)]:body+='<li><time datetime="'+x['date']+'">'+x['date'][5:].replace('-','.')+'</time><div><h3>'+esc(txt(x['title'],lang))+'</h3><p>'+esc(txt(x['text'],lang))+'</p></div></li>'
     body+='</ol></section>'
    body+='</div></div>'
  body+=f'<section class="contact-banner"><p>{esc(U["contact_note"])}</p><a href="{link("about")}" data-contact="{esc(CONTACT)}">{esc(U["email"])} ↗</a></section></main>'
  footer=f'<footer class="footer"><div class="wrap"><div class="footer-top"><span class="wordmark">Fate.</span><span>{esc(U["footer"])}</span><a href="feed.xml">RSS</a></div></div></footer>'
  search=[dict(title=txt(v['title'],lang),lede=txt(v['lede'],lang),href=link(key),text=' '.join(txt(x,lang) for x in pair_nodes(v))) for key,v in P.items()]
  dialog=f'<dialog id="search-dialog" aria-label="{esc(U["search"])}"><div class="search-head"><input id="query" type="search" aria-label="{esc(U["search"])}" placeholder="{esc(U["search_hint"])}" autocomplete="off"><button class="close" data-search-close aria-label="{esc(U["close"])}">×</button></div><div class="results" id="results" aria-live="polite"></div></dialog>'
  dump=lambda x:json.dumps(x,ensure_ascii=False).replace('<','\\u003c')
  canonical='https://0xfate.me/'+name(id,lang)
  robots='<meta name="robots" content="index,follow">' if opt.publish else '<meta name="robots" content="noindex,nofollow">'
  metadata=(f'<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="en" href="https://0xfate.me/{name(id,"en")}"><link rel="alternate" hreflang="zh-Hant" href="https://0xfate.me/{name(id,"zh")}"><meta property="og:title" content="Fate — {esc(title)}"><meta property="og:description" content="{esc(lede)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website"><meta property="og:image" content="https://0xfate.me/og.png">' if opt.publish else '')
  beacon=('<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "681672e48627417ba21e8e42f246ca91"}\'></script>' if opt.publish else '')
  page=f'<!doctype html><html lang="{"en" if lang=="en" else "zh-Hant"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}{metadata}<meta name="description" content="{esc(lede)}"><title>Fate — {esc(title)}</title><link rel="icon" href="favicon.png"><link rel="stylesheet" href="styles.css"><link rel="alternate" type="application/rss+xml" title="Field notes" href="feed.xml"></head><body data-page="{id}"><a class="skip" href="#main">{esc(U["skip"])}</a>{header}{body}{footer}{dialog}<script id="ui-data" type="application/json">{dump(U)}</script><script id="search-data" type="application/json">{dump(search)}</script><script src="site.js" defer></script>{beacon}</body></html>'
  (OUT/name(id,lang)).write_text(page)
for a in ['site.js','avatar.jpg','favicon.png']+[p['image'] for p in P.values() if p.get('image')]:
 if (ROOT/a).resolve()!=(OUT/a).resolve():shutil.copy2(ROOT/a,OUT/a)
shutil.copy2(ROOT/'site-source.css',OUT/'styles.css')
feed='<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Fate — Field notes</title><link>https://0xfate.me/</link><description>A personal field journal.</description>'
for x in reversed(P['updates']['timeline']):
 feed+=f'<item><title>{escape(x["title"]["en"])}</title><link>https://0xfate.me/updates.html#month-{x["date"][:7]}</link><guid isPermaLink="false">fate-{x["date"]}-{P["updates"]["timeline"].index(x)}</guid><description>{escape(x["text"]["en"])}</description></item>'
(OUT/'feed.xml').write_text(feed+'</channel></rss>')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://0xfate.me/sitemap.xml\n' if opt.publish else 'User-agent: *\nDisallow: /\n')
if opt.publish:
 sitemap='<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
 for page_id in P:
  for language in ['en','zh']:sitemap+='<url><loc>https://0xfate.me/'+name(page_id,language)+'</loc></url>'
 (OUT/'sitemap.xml').write_text(sitemap+'</urlset>')
print(f'Built {len(P)*2} bilingual pages at {OUT}')
