"""Akış diyagramını (docs/PGS_akis_TR.png) üretir.

Kullanım (proje kökünden):
  python3 docs/diyagram/akis_diyagrami.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
    --hide-scrollbars --force-device-scale-factor=2 --window-size=1960,1930 \
    --screenshot=docs/PGS_akis_TR.png "file://$PWD/docs/diyagram/flow.html"

Kutular node(), oklar arrow(), ok etiketleri label() ile çizilir. Koordinatlar CSS pikseli.
Diyagram değişirse docs/AGENTIC_FLOW.md ile tutarlı tutulmalı (adım numaraları dahil).
"""
import os
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow.html')
import html as H

W, HGT = 1960, 1930
LX = [50, 426, 802, 1178, 1554]; LW = 364
C = {
 'policy':  ('#2f6db5', '#e8f0fb', '#f3f7fd'),
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
      '<b>Şimdi:</b> eğitilmemiş. <b>İleride:</b> harness içinde, experience log\'la SFT → on-policy distillation → RL',
      '<b>Rolü:</b> hangi tool\'u çağıracağına karar verir: değer arar, SQL dener, sonuca bakar, gerekirse sorar'),
     ('harness','HARNESS (LLM yok)','düz Python',
      'Context preparation, search_values, ask_user, pre-check, sonucu metne çevirme, candidate selection, confidence gate, final check',
      '<b>Guardrail\'ler:</b> aynı çağrı tekrarı yok · uzun sonuç kırpılır · bağlam sıkıştırılır · budget azalınca submit hatırlatması'),
     ('db','GERÇEK VERİTABANI','SQLite, salt okunur',
      '<i>execute_sql</i> tool\'u olarak sunulur',
      '<b>Kural:</b> gönderilen her cevap gerçekten çalıştırılmış olur'),
     ('teacher','TEACHER LLM','Qwen3.6-27B (4-bit, ~16–17 GB)',
      'Yalnızca handoff\'tan sonra kullanılır. Agent\'ın <b>kaldığı yerden</b>, yarım budget\'la (5 tool call) ve aynı tool\'larla devam eder',
      '<b>Rolü:</b> agent\'ın çözemediği vakayı çözer; çözümü eğitim verisi olur'),
    ]
    for x,(k,t,s,a,b) in zip([LX[0],LX[2],LX[3],LX[4]],heads):
        stroke,fill,bg=C[k]
        svg.append(f'<rect x="{x}" y="130" width="{LW}" height="1530" rx="14" fill="{bg}" stroke="{stroke}" stroke-opacity="0.35" stroke-width="1.5"/>')
        svg.append(f'<rect x="{x}" y="130" width="{LW}" height="215" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        divs.append(f'<div class="hd" style="left:{x+14}px;top:142px;width:{LW-28}px">'
                    f'<div class="ht" style="color:{stroke}">{t}</div><div class="hs" style="color:{stroke}">{s}</div>'
                    f'<p>{a}</p><p>{b}</p></div>')

def node(x,y,w,h,kind,title,body='',shape='rect',dashed=False,tsize=19):
    stroke,fill,_=C[kind]
    if kind in ('io',): fill='#ffffff'
    da=' stroke-dasharray="8 6"' if dashed else ''
    f = '#ffffff' if dashed and kind in ('policy','harness','db') else fill
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
node(822,350,324,124,'harness','Context preparation','Soru + evidence · şema, açıklamalar, bağlantılar · column profile\'ları · database memory · 16K aşılırsa policy modeli tablo seçer',tsize=18)
arrow([(390,402),(818,402)],'k'); label(604,402,'soru','k')
arrow([(984,474),(984,487),(300,487),(300,496)],'b'); label(640,487,'başlangıç bağlamı','b')

node(70,500,320,910,'policy','','')
divs.append('''<div class="ag" style="left:86px;top:690px;width:290px">
<div class="agt">Agent loop</div>
<ul><li>Mevcut durumu düşün</li><li>TEK bir tool call seç</li>
<li>Soru belirsizse kullanıcıya sor (<i>ask_user</i>)</li>
<li>SQL dene, gerçek sonuca bak, düzelt</li>
<li>Observation\'ı oku</li><li><i>submit</i>\'e kadar tekrarla</li></ul>
<p>Budget: en fazla 10 tool call</p></div>''')

# handoff from agent (top)
arrow([(390,524),(1736,524),(1736,1126)],'t',w=3)
label(600,524,'<b>Handoff:</b> budget bitti · 3 tekrar · 2 kez final check','t')

node(822,546,324,118,'harness','search_values · ask_user','Adım 1\'in göstermediği bir değerin yazılışı ya da kullanıcının cevabı · kopyası adım 7 için saklanır',tsize=17)
node(1226,560,296,92,'io','Kullanıcı','ask_user sorusunu terminalde cevaplar',shape='pill',tsize=19)
arrow([(1146,584),(1222,584)],'k'); label(1186,584,'ask_user','k')
arrow([(1226,630),(1150,630)],'b'); label(1186,630,'cevap','b')
arrow([(390,584),(818,584)],'k')
arrow([(822,630),(394,630)],'b'); label(606,630,'değerin yazılışı · kullanıcının cevabı','b')

node(822,700,324,140,'harness','Pre-check (sırayla)','1. Salt okuma mı?<br>2. Sözdizimi, tablo, sütun (EXPLAIN)<br>3. Daha önce çalıştı mı (cache)?',tsize=18)
arrow([(390,724),(818,724)],'k'); label(606,724,'execute_sql isteği','k')
arrow([(822,812),(394,812)],'b'); label(606,812,'kontrol hatası ya da cache\'ten sonuç','b')

node(1226,700,296,92,'db','execute_sql','Sorguyu çalıştırır, salt okunur',tsize=19)
arrow([(1146,746),(1222,746)],'k'); label(1186,746,'çalıştır','k')



node(822,900,324,104,'harness','Sonuç','En fazla 20 satır · boşsa: değerin yazılışını <i>search_values</i> ile kontrol et',tsize=18)
arrow([(1440,792),(1440,950),(1150,950)],'k')
arrow([(822,976),(394,976)],'b'); label(606,976,'gerçek sonuç','b')

node(822,1032,324,150,'harness','Candidate generation & selection','Agent\'ın SQL\'i + 2 ek candidate (prompt: soru + evidence + kullanıcı cevapları + şema + search notes; agent\'ın SQL\'i yok) · consensus yoksa toplam 8 · en kalabalık grup',tsize=18)
arrow([(390,1080),(818,1080)],'k'); label(606,1080,'submit','k')
arrow([(822,1130),(394,1130)],'b'); label(606,1130,'SQL çalışmıyor → hata','b')

node(1226,1050,296,112,'db','execute_sql (candidate\'ler)','Cache\'te olmayan candidate\'ler çalıştırılır (5 → 6)',tsize=18)
arrow([(1146,1086),(1222,1086)],'k')
arrow([(1226,1134),(1150,1134)],'k')
node(822,1194,324,96,'decision','Confidence gate','Consensus: 3/3 ya da ≥6/8 → high · 4–5/8 → medium · ≤3/8 → low',shape='hex',tsize=18)
arrow([(984,1182),(984,1190)],'k')
arrow([(822,1242),(394,1242)],'p'); label(606,1242,'medium → iki grubun özeti · biraz daha çalış','p')
arrow([(1146,1242),(1570,1242)],'t',w=3); label(1360,1242,'low ya da 2. kez medium → handoff','t')

node(1574,1130,324,110,'teacher','Teacher','Agent\'ın bağlamını alır, kaldığı yerden yarım budget\'la (5 tool call) ve aynı tool\'larla devam eder',tsize=19)

node(822,1340,324,112,'decision','Final check','Çalıştırılmadıysa çalıştırır · salt okuma + var olan tablo/sütun · boşsa: agent bunu görmüş müydü?',shape='hex',tsize=18)
arrow([(984,1290),(984,1336)],'p'); label(1040,1313,'high','p')
arrow([(822,1396),(394,1396)],'p'); label(606,1396,'geçmedi → çalışmaya devam','p')

node(1222,1348,300,100,'io','Cevap','<i>ok</i> · geçmediyse <i>low_confidence</i><br>çalışan SQL yoksa <i>no_answer</i>',shape='pill',tsize=20)
arrow([(1146,1396),(1218,1396)],'p'); label(1184,1370,'geçti','p')
arrow([(1736,1240),(1736,1480),(984,1480),(984,1456)],'t',w=3)
label(1530,1480,'teacher\'ın cevabı da final check\'ten geçer','t')

# --- database memory ---
node(822,1540,324,80,'harness','Database memory','hata → düzeltme kaydı · gold yok',dashed=True,tsize=18)
# database memory: soru ok bitince cevaptan yazılır, sonraki soru adım 1'de okur
arrow([(1300,1448),(1300,1580),(1150,1580)],'g',dashed=True); label(1300,1525,'ok + yolda hata','g',dashed=True)
arrow([(984,1620),(984,1650),(1938,1650),(1938,440),(1150,440)],'g',dashed=True); label(1440,440,'sonraki sorunun adım 1\'i','g',dashed=True)

# experience log: evaluate.py her soru puanlandıktan sonra bütün konuşmayı yazar; agent ileride bununla eğitilir
node(1600,1500,270,100,'offline','Experience log','her soru: bütün konuşma, cevap, doğru mu',shape='cyl',tsize=18)
arrow([(1522,1398),(1560,1398),(1560,1550),(1596,1550)],'g',dashed=True)
node(70,1500,320,100,'policy','Agent eğitimi (ileride)','SFT → on-policy distillation → RL · yalnızca train kayıtları',dashed=True,tsize=18)
arrow([(1735,1600),(1735,1690),(230,1690),(230,1604)],'g',dashed=True); label(980,1690,'eğitim verisi','g',dashed=True)

# step badges
for (bx,by,n) in [(84,362,1),(822,350,1),(70,500,2),(822,546,3),(462,724,4),(822,700,5),(1226,700,6),(822,900,6),(822,1032,7),(1226,1050,7),(848,1194,8),(848,1340,9),(1574,1130,10)]:
    divs.append(f'<div class="bd" style="left:{bx-17}px;top:{by-17}px">{n}</div>')
# legend
ly=1750
items=[('k','Tool call',False),('b','Agent\'a dönen observation',False),('p','Karar sonucu',False),('t','Handoff',False),('g','Soru bittikten sonra',True)]
x=66
for c,t,d in items:
    arrow([(x,ly),(x+56,ly)],c,dashed=d)
    divs.append(f'<div class="lg" style="left:{x+70}px;top:{ly-13}px">{t}</div>')
    x+=360
divs.append('''<div class="idea" style="left:66px;top:1790px;width:1830px"><b>Ana fikir:</b> agent hangi tool\'u kullanacağına kendisi karar verir: değer arar, SQL dener, gerçek sonuca bakar, soru belirsizse kullanıcıya sorar. Cevap candidate grupları arasından consensus ile seçilir ve gönderilen her şey gerçekten çalıştırılmış olur. Takılırsa agent işi teacher\'a devreder (handoff); teacher kaldığı yerden devam eder. Her sorunun bütün konuşması experience log\'a yazılır; agent ileride bununla eğitilir.</div>''')

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
<div class="title">Predict – Gate – Settle (PGS): agent loop, candidate selection ve handoff ile agentic Text-to-SQL</div>
<div class="sub">Tek bir kullanıcı sorusu için olanlar. Her sütun bir bileşendir; numaralar AGENTIC_FLOW.md'deki adımlardır.</div>
{''.join(divs)}
</div></body></html>'''
open(HTML_PATH,'w',encoding='utf-8').write(page)
print('yazıldı:', HTML_PATH)
