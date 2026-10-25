"""Generates the English flow diagram (docs/PGS_flow_EN.png).

English mirror of akis_diyagrami.py (the Turkish original). Both must change together:
same layout, coordinates, colors and step numbers; only the text differs.

Usage (from the project root):
  python3 docs/diyagram/flow_diagram_en.py
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
    --hide-scrollbars --force-device-scale-factor=2 --window-size=1960,1930 \
    --screenshot=docs/PGS_flow_EN.png "file://$PWD/docs/diyagram/flow_en.html"

Boxes are drawn with node(), arrows with arrow(), arrow labels with label(). Coordinates are CSS pixels.
If the diagram changes, keep it consistent with docs/AGENTIC_FLOW.md (including step numbers).
"""
import os
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flow_en.html')
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
      '<b>Now:</b> untrained. <b>Later:</b> inside the harness, with the experience log: SFT → on-policy distillation → RL',
      '<b>Role:</b> decides which tool to call; predicts the result before running SQL (forecast)'),
     ('harness','HARNESS (no LLM)','plain Python',
      'Context preparation, search_values, ask_user, pre-check, compare, candidate selection, confidence gate, final check',
      '<b>Guardrails:</b> no repeated calls · long results trimmed · context compressed · submit reminder when the budget is low'),
     ('db','REAL DATABASE','SQLite, read-only',
      'Exposed as the <i>execute_sql</i> tool',
      '<b>Rule:</b> every submitted answer has really been executed'),
     ('teacher','TEACHER LLM','Qwen3.6-27B (4-bit, ~16–17 GB)',
      'Used only after a handoff. Continues <b>where the agent left off</b>, with half the budget (5 tool calls) and the same tools',
      '<b>Role:</b> solves the case the agent could not; its solution becomes training data'),
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
node(70,362,320,80,'io','User question','e.g. “Which category had the most returns in 2025?”',shape='pill',tsize=18)
node(822,350,324,124,'harness','Context preparation','Question + evidence · schema, descriptions, links · column profiles · database memory · over 16K: the policy model selects tables',tsize=18)
arrow([(390,402),(818,402)],'k'); label(604,402,'question','k')
arrow([(984,474),(984,487),(300,487),(300,496)],'b'); label(640,487,'initial context','b')

node(70,500,320,910,'policy','','')
divs.append('''<div class="ag" style="left:86px;top:690px;width:290px">
<div class="agt">Agent loop</div>
<ul><li>Think about the current state</li><li>Pick ONE tool call</li>
<li>If the question is ambiguous, ask the user (<i>ask_user</i>)</li>
<li>Before running SQL, write a <b>forecast</b>:<br><i>type</i>: error / empty / rows<br>optional: <i>columns</i>, <i>rows</i>, <i>trust</i></li>
<li>Read the observation</li><li>Repeat until <i>submit</i></li></ul>
<p>Budget: at most 10 tool calls</p></div>''')

# handoff from agent (top)
arrow([(390,524),(1736,524),(1736,1126)],'t',w=3)
label(600,524,'<b>Handoff:</b> out of budget · final check failed twice','t')

node(822,546,324,118,'harness','search_values · ask_user','The spelling of a value step 1 does not show, or the user\'s answer · copy kept for step 7',tsize=17)
node(1226,560,296,92,'io','User','Answers the ask_user question at the terminal',shape='pill',tsize=19)
arrow([(1146,584),(1222,584)],'k'); label(1186,584,'ask_user','k')
arrow([(1226,630),(1150,630)],'b'); label(1186,630,'answer','b')
arrow([(390,584),(818,584)],'k')
arrow([(822,630),(394,630)],'b'); label(606,630,'spelling of a value · user\'s answer','b')

node(822,700,324,140,'harness','Pre-check (in order)','1. Read-only?<br>2. Syntax, tables, columns (EXPLAIN)<br>3. Already run before (cache)?',tsize=18)
arrow([(390,724),(818,724)],'k'); label(606,724,'execute_sql request + agent forecast','k')
arrow([(822,812),(394,812)],'b'); label(606,812,'check error or cached result','b')

node(1226,700,296,92,'db','execute_sql','Runs the query, read-only',tsize=19)
arrow([(1146,746),(1222,746)],'k'); label(1186,746,'run','k')



node(822,900,324,104,'harness','Compare','Real result ↔ agent forecast · on a miss, a <b>surprise note</b>',tsize=18)
arrow([(1440,792),(1440,950),(1150,950)],'k')
arrow([(822,976),(394,976)],'b'); label(606,976,'real result + surprise note','b')

node(822,1032,324,150,'harness','Candidate generation & selection','Agent\'s SQL + 2 extra candidates (prompt: question + evidence + user answers + schema + search notes; no agent SQL) · 8 in total if no consensus · largest group',tsize=18)
arrow([(390,1080),(818,1080)],'k'); label(606,1080,'submit','k')
arrow([(822,1130),(394,1130)],'b'); label(606,1130,'SQL does not run → error','b')

node(1226,1050,296,112,'db','execute_sql (candidates)','Candidates not in cache are run (5 → 6)',tsize=18)
arrow([(1146,1086),(1222,1086)],'k')
arrow([(1226,1134),(1150,1134)],'k')
node(822,1194,324,96,'decision','Confidence gate','Consensus: 3/3 or ≥6/8 → high · <span style="white-space:nowrap">4–5/8 → medium</span> · ≤3/8 → low',shape='hex',tsize=18)
arrow([(984,1182),(984,1190)],'k')
arrow([(822,1242),(394,1242)],'p'); label(606,1242,'medium → summary of two groups · work a bit more','p')
arrow([(1146,1242),(1570,1242)],'t',w=3); label(1360,1242,'low or 2nd medium → handoff','t')

node(1574,1130,324,110,'teacher','Teacher','Takes the agent\'s context and continues where it left off, with half the budget (5 tool calls) and the same tools',tsize=19)

node(822,1340,324,112,'decision','Final check','Runs it if not yet run · read-only + existing tables/columns · if empty: was the forecast “empty”?',shape='hex',tsize=18)
arrow([(984,1290),(984,1336)],'p'); label(1040,1313,'high','p')
arrow([(822,1396),(394,1396)],'p'); label(606,1396,'failed → keep working','p')

node(1222,1348,300,100,'io','Answer','<i>ok</i> · <i>low_confidence</i> if it failed<br><i>no_answer</i> if no SQL ran',shape='pill',tsize=20)
arrow([(1146,1396),(1218,1396)],'p'); label(1184,1370,'passed','p')
arrow([(1736,1240),(1736,1480),(984,1480),(984,1456)],'t',w=3)
label(1530,1480,'the teacher\'s answer also goes through final check','t')

# --- database memory ---
node(822,1540,324,80,'harness','Database memory','mistake → fix records · no gold',dashed=True,tsize=18)
# database memory: written from the answer when the question ends ok; the next question reads it in step 1
arrow([(1300,1448),(1300,1580),(1150,1580)],'g',dashed=True); label(1300,1525,'ok + a mistake along the way','g',dashed=True)
arrow([(984,1620),(984,1650),(1938,1650),(1938,440),(1150,440)],'g',dashed=True); label(1440,440,'step 1 of the next question','g',dashed=True)

# experience log: evaluate.py writes the whole conversation after each question is scored; the agent is trained on it later
node(1600,1500,270,100,'offline','Experience log','each question: whole conversation, answer, correct?',shape='cyl',tsize=18)
arrow([(1522,1398),(1560,1398),(1560,1550),(1596,1550)],'g',dashed=True)
node(70,1500,320,100,'policy','Agent training (later)','SFT → on-policy distillation → RL · train records only',dashed=True,tsize=18)
arrow([(1735,1600),(1735,1690),(230,1690),(230,1604)],'g',dashed=True); label(980,1690,'training data','g',dashed=True)

# step badges
for (bx,by,n) in [(84,362,1),(822,350,1),(70,500,2),(822,546,3),(462,724,4),(822,700,5),(1226,700,6),(822,900,6),(822,1032,7),(1226,1050,7),(848,1194,8),(848,1340,9),(1574,1130,10)]:
    divs.append(f'<div class="bd" style="left:{bx-17}px;top:{by-17}px">{n}</div>')
# legend
ly=1750
items=[('k','Tool call',False),('b','Observation to the agent',False),('p','Decision outcome',False),('t','Handoff',False),('g','After the question',True)]
x=66
for c,t,d in items:
    arrow([(x,ly),(x+56,ly)],c,dashed=d)
    divs.append(f'<div class="lg" style="left:{x+70}px;top:{ly-13}px">{t}</div>')
    x+=360
divs.append('''<div class="idea" style="left:66px;top:1790px;width:1830px"><b>Key idea:</b> the agent decides for itself which tool to use, asks the user when the question is ambiguous, and writes a forecast before running any SQL; the real execution checks the forecast (predict). The answer is chosen among candidate groups by consensus (gate), and everything that is submitted has really been executed (settle). If it gets stuck, the agent hands the task over to the teacher (handoff), which continues where it left off. Each question's whole conversation is written to the experience log; the agent is trained on it later.</div>''')

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
<div class="title">Predict – Gate – Settle (PGS): agentic Text-to-SQL with a forecast-checked agent loop, candidate selection and handoff</div>
<div class="sub">What happens for a single user question. Each column is a component; numbers are the steps in AGENTIC_FLOW.md.</div>
{''.join(divs)}
</div></body></html>'''
open(HTML_PATH,'w',encoding='utf-8').write(page)
print('written:', HTML_PATH)
