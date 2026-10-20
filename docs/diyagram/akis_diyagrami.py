"""Akış diyagramını (docs/PGS_akis_TR.png) üretir.

Kullanım (proje kökünden):
  python3 docs/diyagram/akis_diyagrami.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
    --hide-scrollbars --force-device-scale-factor=2 --window-size=1960,2230 \
    --screenshot=docs/PGS_akis_TR.png "file://$PWD/docs/diyagram/flow.html"

Kutular node(), oklar arrow(), ok etiketleri label() ile çizilir. Koordinatlar CSS pikseli.
Diyagram değişirse docs/AGENTIC_FLOW.md ile tutarlı tutulmalı (adım numaraları dahil).
"""
import os
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow.html')
import html as H

W, HGT = 1960, 2230
LX = [50, 426, 802, 1178, 1554]; LW = 364
C = {
 'policy':  ('#2f6db5', '#e8f0fb', '#f3f7fd'),
 'world':   ('#b5730f', '#fdf0db', '#fdf8ef'),
 'harness': ('#2e7d55', '#e6f3ec', '#f2f8f4'),
 'db':      ('#b8323a', '#fbe5e6', '#fcf3f3'),
 'teacher': ('#0e7490', '#e0f2f7', '#f1f8fb'),
 'decision':('#6a45b8', '#f0eafa', None),
 'io':      ('#333333', '#ffffff', None),
 'offline': ('#777777', '#f2f2f2', None),
}
ARROW = {'k':'#333333','b':'#2f6db5','p':'#6a45b8','t':'#0e7490','g':'#888888'}
svg, divs = [], []

def lane_headers():
    heads = [
     ('policy','POLICY AGENT','Qwen3.5-4B',
      '<b>İlk sürüm:</b> eğitilmemiş hâliyle. <b>Eğitim (isteğe bağlı, en sonda):</b> teacher izleriyle SFT → on-policy distillation → RL',
      '<b>Rolü:</b> hangi tool\'u çağıracağına karar verir; SQL çalıştırmadan önce sonucu tahmin eder (forecast)'),
     ('world','WORLD MODEL','İlk sürüm: placeholder LLM',
      '<b>İlk sürüm:</b> eğitilmemiş bir LLM, prompt\'la world model gibi davranır. <b>Eğitim (isteğe bağlı):</b> Qwen3.5-0.8B + LoRA, kayıtlı çalıştırmalardan',
      '<b>Rolü:</b> çalıştırma pahalıyken pre-check; cevabın yerine geçmez'),
     ('harness','HARNESS (LLM yok)','düz Python',
      'Context preparation, search, ask_user, pre-check, compare & log, candidate selection, gate\'ler, final check',
      '<b>Guardrail\'ler:</b> aynı çağrı tekrarı yok · uzun sonuç kırpılır · bağlam sıkıştırılır'),
     ('db','GERÇEK VERİTABANI','SQLite, salt okunur',
      '<i>execute_sql</i> tool\'u olarak sunulur',
      '<b>Kural:</b> gönderilen her cevap gerçekten çalıştırılmış olur; prediction tek başına cevap olamaz'),
     ('teacher','TEACHER LLM','Qwen3.6-27B (4-bit, ~16–17 GB)',
      'Yalnızca handoff\'tan sonra kullanılır. Agent\'ın <b>kaldığı yerden</b>, yeni bir budget\'la ve aynı tool\'larla devam eder',
      '<b>Rolü:</b> zor vakayı çözer; çözümü yeni distillation verisi olur'),
    ]
    for i,(k,t,s,a,b) in enumerate(heads):
        x=LX[i]; stroke,fill,bg=C[k]
        svg.append(f'<rect x="{x}" y="130" width="{LW}" height="1890" rx="14" fill="{bg}" stroke="{stroke}" stroke-opacity="0.35" stroke-width="1.5"/>')
        svg.append(f'<rect x="{x}" y="130" width="{LW}" height="215" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        divs.append(f'<div class="hd" style="left:{x+14}px;top:142px;width:{LW-28}px">'
                    f'<div class="ht" style="color:{stroke}">{t}</div><div class="hs" style="color:{stroke}">{s}</div>'
                    f'<p>{a}</p><p>{b}</p></div>')

def node(x,y,w,h,kind,title,body='',shape='rect',dashed=False,tsize=19):
    stroke,fill,_=C[kind]
    if kind in ('io',): fill='#ffffff'
    da=' stroke-dasharray="8 6"' if dashed else ''
    f = '#ffffff' if dashed and kind in ('policy','world','harness','db') else fill
    if shape=='rect':
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{f}" stroke="{stroke}" stroke-width="2.5"{da}/>')
    elif shape=='pill':
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="#fff" stroke="{stroke}" stroke-width="2.5"/>')
    elif shape=='hex':
        d=26
        pts=f'{x+d},{y} {x+w-d},{y} {x+w},{y+h/2} {x+w-d},{y+h} {x+d},{y+h} {x},{y+h/2}'
        svg.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
    elif shape=='cyl':
        e=14
        svg.append(f'<path d="M{x},{y+e} A{w/2},{e} 0 0 1 {x+w},{y+e} L{x+w},{y+h-e} A{w/2},{e} 0 0 1 {x},{y+h-e} Z" fill="{fill}" stroke="{stroke}" stroke-width="2.5" stroke-dasharray="8 6"/>')
        svg.append(f'<path d="M{x},{y+e} A{w/2},{e} 0 0 0 {x+w},{y+e}" fill="none" stroke="{stroke}" stroke-width="2.5" stroke-dasharray="8 6"/>')
    tc = stroke if kind!='io' else '#222'
    pad = 34 if shape=='hex' else 12
    top = 22 if shape=='cyl' else 0
    divs.append(f'<div class="nd" style="left:{x+pad}px;top:{y+top}px;width:{w-2*pad}px;height:{h-top}px">'
                f'<div class="nt" style="color:{tc};font-size:{tsize}px">{title}</div>'
                + (f'<div class="nb">{body}</div>' if body else '') + '</div>')

def arrow(pts,c='k',dashed=False,w=2.5):
    p=' '.join(f'{a},{b}' for a,b in pts)
    da=' stroke-dasharray="7 6"' if dashed else ''
    svg.append(f'<polyline points="{p}" fill="none" stroke="{ARROW[c]}" stroke-width="{w}"{da} marker-end="url(#m{c})"/>')

def label(x,y,text,c='k',dashed=False,bold=False):
    col=ARROW[c]; bs='dashed' if dashed else 'solid'
    fw='600' if bold else '500'
    divs.append(f'<div class="lb" style="left:{x}px;top:{y}px;color:{col};border:1.5px {bs} {col}aa;font-weight:{fw}">{text}</div>')

lane_headers()
# --- online flow ---
node(70,362,320,80,'io','Kullanıcı sorusu','ör. “2025’te en çok iade edilen kategori hangisi?”',shape='pill',tsize=18)
node(822,350,324,112,'harness','Context preparation','Soru + evidence · şema, açıklamalar, bağlantılar · column profile\'ları · sorudaki kelimelerin değer eşleşmeleri · database memory',tsize=18)
arrow([(390,402),(818,402)],'k'); label(604,402,'soru','k')
arrow([(984,462),(984,478),(300,478),(300,496)],'b'); label(640,478,'başlangıç bağlamı','b')

node(70,500,320,1160,'policy','','')
divs.append('''<div class="ag" style="left:86px;top:690px;width:290px">
<div class="agt">Agent loop</div>
<ul><li>Mevcut durumu düşün</li><li>TEK bir tool call seç</li>
<li>Soru belirsizse kullanıcıya sor (<i>ask_user</i>)</li>
<li>SQL çalıştırmadan önce <b>forecast</b> yaz:<br><i>result type:</i> hata / boş / dolu<br><i>result shape:</i> sütunlar + kaç satır<br>+ <i>trust</i> ya da <i>unsure</i></li>
<li>Observation\'ı oku</li><li><i>submit</i> ya da <i>handoff</i>\'a kadar tekrarla</li></ul>
<p>Budget: en fazla 10 tool call</p></div>''')

# handoff from agent (top)
arrow([(390,524),(1736,524),(1736,1376)],'t',w=3)
label(600,524,'<b>Handoff:</b> budget bitti · agent takıldı · final check 2 kez geçmedi','t')

node(822,546,324,118,'harness','search_schema · search_values · ask_user','Adım 1\'in vermediği tablo, sütun, değer ya da kullanıcının cevabı · kopyası adım 8 için saklanır',tsize=17)
node(1226,560,296,92,'io','Kullanıcı','ask_user sorusunu cevaplar (değerlendirmede user simulator)',shape='pill',tsize=19)
arrow([(1146,584),(1222,584)],'k'); label(1186,584,'ask_user','k')
arrow([(1226,630),(1150,630)],'b'); label(1186,630,'cevap','b')
arrow([(390,584),(818,584)],'k')
arrow([(822,630),(394,630)],'b'); label(606,630,'tablolar, sütunlar, değerler · kullanıcının cevabı','b')

node(822,700,324,140,'harness','Pre-check (sırayla)','1. Salt okuma mı?<br>2. Sözdizimi, tablo, sütun (EXPLAIN)<br>3. Daha önce çalıştı mı (cache)?<br>4. World model\'e gidilsin mi?',tsize=18)
arrow([(390,724),(818,724)],'k'); label(606,724,'execute_sql isteği + agent forecast','k')
arrow([(822,812),(394,812)],'b'); label(606,812,'kontrol hatası ya da cache\'ten sonuç','b')

node(1226,700,296,92,'db','execute_sql','Sorguyu çalıştırır, salt okunur',tsize=19)
arrow([(1146,746),(1222,746)],'k'); label(1186,746,'çalıştır','k')

node(446,868,324,108,'world','predict_sql','<i>Result type:</i> hata / boş / dolu<br><i>Result shape:</i> sütunlar + kaç satır<br><i>Values</i> · + her biri için confidence',tsize=19)
arrow([(900,840),(900,920),(774,920)],'k'); label(900,876,'pahalı sorgu · budget az','k')

node(446,1012,324,84,'decision','Prediction gate','Type ve shape confidence ≥ 0.9 mu?<br>(values yalnızca bilgi)',shape='hex',tsize=18)
arrow([(608,976),(608,1008)],'k')
arrow([(560,1096),(560,1124),(394,1124)],'b'); label(560,1124,'trusted → prediction, yalnızca ara adım için','b')
arrow([(770,1054),(1300,1054),(1300,796)],'p'); label(1040,1054,'untrusted ya da %5 audit → çalıştır','p')

node(822,1150,324,104,'harness','Compare & log','Gerçek sonuç ↔ agent forecast ↔ world model prediction · tutmadıysa <b>surprise note</b>',tsize=18)
arrow([(1440,792),(1440,1200),(1150,1200)],'k')
arrow([(822,1226),(394,1226)],'b'); label(606,1226,'gerçek sonuç + surprise note','b')

node(822,1282,324,150,'harness','Candidate generation & selection','Agent\'ın SQL\'i + 2 ek candidate (prompt: soru + evidence + kullanıcı cevapları + şema + search notes; agent\'ın SQL\'i yok) · consensus yoksa toplam 8 · en kalabalık grup',tsize=18)
arrow([(390,1330),(818,1330)],'k'); label(606,1330,'submit','k')

node(1226,1300,296,112,'db','execute_sql (candidate\'ler)','Cache\'te olmayan candidate\'ler çalıştırılır · pahalı sorguda önce world model eler (5 → 6)',tsize=18)
arrow([(1146,1336),(1222,1336)],'k')
arrow([(1226,1384),(1150,1384)],'k')
node(822,1444,324,96,'decision','Confidence gate','Consensus: 3/3 ya da ≥6/8 → high · 4–5/8 → medium · ≤3/8 → low',shape='hex',tsize=18)
arrow([(984,1432),(984,1440)],'k')
arrow([(822,1492),(394,1492)],'p'); label(606,1492,'medium → iki grubun özeti · biraz daha çalış','p')
arrow([(1146,1492),(1570,1492)],'t',w=3); label(1360,1492,'low ya da 2. kez medium → handoff','t')

node(1574,1380,324,110,'teacher','Teacher','Agent\'ın bağlamını alır, kaldığı yerden yeni budget\'la ve aynı tool\'larla devam eder',tsize=19)

node(822,1590,324,112,'decision','Final check','Çalıştırılmadıysa çalıştırır · salt okuma + var olan tablo/sütun · boşsa: forecast “boş” muydu?',shape='hex',tsize=18)
arrow([(984,1540),(984,1586)],'p'); label(1040,1563,'high','p')
arrow([(822,1646),(394,1646)],'p'); label(606,1646,'geçmedi → çalışmaya devam','p')

node(1222,1604,300,88,'io','Cevap','<i>ok</i> · teacher\'ın cevabı geçmezse ya da fallback answer ise <i>low_confidence</i>',shape='pill',tsize=20)
arrow([(1146,1646),(1218,1646)],'p'); label(1184,1620,'geçti','p')
arrow([(1736,1490),(1736,1730),(984,1730),(984,1706)],'t',w=3)
label(1460,1730,'teacher\'ın cevabı da final check\'ten geçer','t')

# --- offline loop ---
node(1240,1766,240,104,'offline','Experience log','forecast + prediction + gerçek sonuç + maliyet',shape='cyl',tsize=18)
arrow([(1146,1240),(1528,1240),(1528,1800),(1484,1800)],'g',dashed=True)
arrow([(1810,1490),(1810,1840),(1484,1840)],'g',dashed=True); label(1650,1840,'teacher çözümleri','g',dashed=True)
svg.append('<polyline points="1360,1870 1360,1890" fill="none" stroke="#888" stroke-width="2.5" stroke-dasharray="7 6"/>')
svg.append(f'<polyline points="1360,1890 232,1890" fill="none" stroke="#888" stroke-width="2.5" stroke-dasharray="7 6"/>')
for cx in (232,608,984):
    arrow([(cx,1890),(cx,1930)],'g',dashed=True)
node(92,1934,280,80,'policy','Policy re-distillation','isteğe bağlı · train\'deki handoff vakaları · promotion gate',dashed=True,tsize=18)
node(468,1934,280,80,'world','World model training','isteğe bağlı · train çalıştırmaları, dengeli',dashed=True,tsize=18)
node(830,1934,308,80,'harness','Memory & calibration','database memory (gold yok) + gate eşikleri (train ile)',dashed=True,tsize=18)

# step badges
for (bx,by,n) in [(84,362,1),(822,350,1),(70,500,2),(822,546,3),(462,724,4),(822,700,5),(446,868,6),(472,1012,6),(1226,700,7),(822,1150,7),(822,1282,8),(1226,1300,8),(848,1444,9),(848,1590,10),(1574,1380,11)]:
    divs.append(f'<div class="bd" style="left:{bx-17}px;top:{by-17}px">{n}</div>')
# legend
ly=2062
items=[('k','Tool call',False),('b','Agent\'a dönen observation',False),('p','Karar sonucu',False),('t','Handoff',False),('g','Offline learning',True)]
x=66
for c,t,d in items:
    arrow([(x,ly),(x+56,ly)],c,dashed=d)
    divs.append(f'<div class="lg" style="left:{x+70}px;top:{ly-13}px">{t}</div>')
    x+=360
divs.append('''<div class="idea" style="left:66px;top:2100px;width:1830px"><b>Ana fikir:</b> agent hangi tool'u kullanacağına kendisi karar verir, soru belirsizse kullanıcıya sorar ve her SQL'i çalıştırmadan önce forecast yazar; yönlendirmeyi harness yapar; gerçek çalıştırma forecast'i denetler ve her adım için ayrı bir öğrenme sinyali üretir. World model yalnızca çalıştırma pahalıyken pre-check yapar. Cevap candidate grupları arasından consensus ile seçilir ve gönderilen her şey gerçekten çalıştırılmış olur. Takılırsa agent işi teacher'a devreder (handoff); teacher kaldığı yerden devam eder ve bu vakalar yeni distillation verisi olur.</div>''')

markers=''.join(f'<marker id="m{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>' for k,v in ARROW.items())
page=f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;background:#fff;font-family:"Inter",-apple-system,"Helvetica Neue",Arial,sans-serif;color:#222}}
#c{{position:relative;width:{W}px;height:{HGT}px}}
svg{{position:absolute;left:0;top:0}}
.title{{position:absolute;left:50px;top:26px;font-size:33px;font-weight:800;color:#1b1b1b}}
.sub{{position:absolute;left:50px;top:76px;font-size:19px;color:#555}}
.hd{{position:absolute}} .ht{{font-weight:800;font-size:19px;letter-spacing:.2px}} .hs{{font-weight:600;font-size:17px;margin-top:3px}}
.hd p{{margin:9px 0 0;font-size:14.5px;line-height:1.4;color:#333}}
.nd{{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
.nt{{font-weight:700}} .nb{{font-size:15px;line-height:1.38;color:#333;margin-top:4px}}
.ag{{position:absolute}} .agt{{font-size:24px;font-weight:700;color:#2f6db5;text-align:center;margin-bottom:12px}}
.ag ul{{margin:0;padding-left:22px;font-size:17px;line-height:1.55;color:#222}} .ag li{{margin-bottom:6px}}
.ag p{{font-size:17px;margin:14px 0 0 0;color:#222}}
.lb{{position:absolute;transform:translate(-50%,-50%);background:#fff;border-radius:7px;padding:3px 9px;font-size:14.5px;white-space:nowrap}}
.bd{{position:absolute;width:34px;height:34px;border-radius:17px;background:#1f1f1f;color:#fff;font-weight:800;font-size:17px;display:flex;align-items:center;justify-content:center;border:2.5px solid #fff;box-shadow:0 0 0 1px #1f1f1f}}
.lg{{position:absolute;font-size:18px;color:#333}}
.idea{{position:absolute;background:#f5f5f5;border-left:5px solid #6a45b8;padding:14px 18px;font-size:17px;line-height:1.5;color:#222}}
</style></head><body><div id="c">
<svg width="{W}" height="{HGT}"><defs>{markers}</defs>{''.join(svg)}</svg>
<div class="title">Predict – Gate – Settle (PGS): forecast ile denetlenen agent loop, candidate selection ve handoff ile agentic Text-to-SQL</div>
<div class="sub">Tek bir kullanıcı sorusu için olanlar. Her sütun bir bileşendir; numaralar AGENTIC_FLOW.md'deki adımlardır.</div>
{''.join(divs)}
</div></body></html>'''
open(HTML_PATH,'w',encoding='utf-8').write(page)
print('yazıldı:', HTML_PATH)
