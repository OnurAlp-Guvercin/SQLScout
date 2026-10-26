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
     ('policy','POLICY AGENT','Qwen3.5-0.8B · target Qwen3.5-4B',
      '<b>Now:</b> untrained. <b>Later:</b> inside the harness, with the experience log: SFT → on-policy distillation → RL',
      '<b>Role:</b> decides which tool to call: searches values, tries SQL, looks at the result, fixes it'),
     ('harness','HARNESS (no LLM)','plain Python',
      'Context preparation, search_values, pre-check, turning the result into text, final check, the handoff decision',
      '<b>Guardrails:</b> no repeated calls · long results trimmed · context compressed · submit reminder when the budget is low'),
     ('db','REAL DATABASE','SQLite, read-only',
      'Exposed as the <i>execute_sql</i> tool',
      '<b>Rule:</b> every submitted answer has really been executed'),
     ('teacher','TEACHER LLM','Qwen3.5-9B (API) · target Qwen3.6-27B',
      'Checks the agent\'s answer. On a handoff, continues <b>where the agent left off</b>, with half the budget (5 tool calls) and the same tools',
      '<b>Role:</b> approves or rejects the agent\'s answer; solves the case the agent could not, its solution becomes training data'),
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
node(822,350,324,124,'harness','Context preparation','Question + evidence · schema, descriptions, links · column profiles',tsize=18)
arrow([(390,402),(818,402)],'k'); label(604,402,'question','k')
arrow([(984,474),(984,487),(300,487),(300,496)],'b'); label(640,487,'initial context','b')

node(70,500,320,910,'policy','','')
divs.append('''<div class="ag" style="left:86px;top:690px;width:290px">
<div class="agt">Agent loop</div>
<ul><li>Think about the current state</li><li>Pick ONE tool call</li>
<li>Chooses the order itself: search a value, explore the data or try a query</li>
<li>Look at the real result, fix it if needed</li>
<li><i>submit</i> the SQL that answers the question</li></ul>
<p>Budget: at most 10 tool calls; handoff if none of the first 4 returns rows</p></div>''')

# handoff from agent (top)
arrow([(390,524),(1736,524),(1736,1036)],'t',w=3)
label(640,524,'<b>Handoff:</b> no progress in 4 steps · 3 repeats · out of budget','t')

node(822,546,324,118,'harness','search_values','The spelling and column of a value step 1 does not show · similar column names if no value',tsize=19)
arrow([(390,584),(818,584)],'k'); label(606,584,'search_values','k')
arrow([(822,630),(394,630)],'b'); label(606,630,'spelling of a value','b')

node(822,700,324,140,'harness','Pre-check (in order)','1. Read-only?<br>2. Syntax, tables, columns (EXPLAIN); the error note shows the real columns of the tables<br>3. Already run before (cache)?',tsize=18)
arrow([(390,724),(818,724)],'k'); label(606,724,'execute_sql request','k')
arrow([(822,812),(394,812)],'b'); label(606,812,'check error or cached result','b')

node(1226,700,296,92,'db','execute_sql','Runs the query, read-only',tsize=19)
arrow([(1146,746),(1222,746)],'k'); label(1186,746,'run','k')



node(822,900,324,104,'harness','Result','At most 20 rows · if empty: check the value\'s spelling with <i>search_values</i>',tsize=18)
arrow([(1440,792),(1440,950),(1150,950)],'k')
arrow([(822,976),(394,976)],'b'); label(606,976,'real result','b')

node(822,1036,324,128,'decision','Final check','Runs without error · the agent has seen its result (else it is shown) · the teacher approves',shape='hex',tsize=18)
arrow([(390,1076),(818,1076)],'k'); label(606,1076,'submit','k')
arrow([(822,1130),(394,1130)],'p'); label(606,1130,'failed → note · keep working','p')

node(1574,1040,324,110,'teacher','Teacher','Takes the agent\'s context and continues where it left off, with half the budget (5 tool calls) and the same tools',tsize=19)
arrow([(1146,1076),(1570,1076)],'t',w=3); label(1360,1076,'failed twice or teacher says no','t')
arrow([(1574,1126),(1150,1126)],'t',w=3); label(1360,1126,'the teacher\'s submit goes here too','t')

node(1222,1230,300,100,'io','Answer','<i>ok</i> · <i>fallback</i> if it failed<br><i>no_answer</i> if no SQL returned rows',shape='pill',tsize=20)
arrow([(984,1164),(984,1280),(1218,1280)],'p'); label(1100,1280,'passed','p')


# experience log: evaluate.py writes the whole conversation after each question is scored; the agent is trained on it later
node(1600,1500,270,100,'offline','Experience log','each question: whole conversation, answer, correct?',shape='cyl',tsize=18)
arrow([(1522,1280),(1560,1280),(1560,1550),(1596,1550)],'g',dashed=True)
node(70,1500,320,100,'policy','Agent training (later)','SFT → on-policy distillation → RL · train records only',dashed=True,tsize=18)
arrow([(1735,1600),(1735,1690),(230,1690),(230,1604)],'g',dashed=True); label(980,1690,'training data','g',dashed=True)

# step badges
for (bx,by,n) in [(84,362,1),(822,350,1),(70,500,2),(822,546,3),(462,724,4),(822,700,5),(1226,700,6),(822,900,6),(848,1036,7),(1574,1040,8)]:
    divs.append(f'<div class="bd" style="left:{bx-17}px;top:{by-17}px">{n}</div>')
# legend
ly=1750
items=[('k','Tool call',False),('b','Observation to the agent',False),('p','Decision outcome',False),('t','Handoff',False),('g','After the question',True)]
x=66
for c,t,d in items:
    arrow([(x,ly),(x+56,ly)],c,dashed=d)
    divs.append(f'<div class="lg" style="left:{x+70}px;top:{ly-13}px">{t}</div>')
    x+=360
divs.append('''<div class="idea" style="left:66px;top:1790px;width:1830px"><b>Key idea:</b> the agent decides for itself which tool to use: it searches for values, tries SQL, looks at the real result and fixes it. It submits the SQL it chooses as the answer; the answer passes a final check, the teacher approves it, and everything that is submitted has really been executed. If it makes no progress or gets stuck, the agent hands the task over to the teacher (handoff), which continues where it left off. Each question\'s whole conversation is written to the experience log; the agent is trained on it later.</div>''')

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
<div class="title">Predict – Gate – Settle (PGS): agentic Text-to-SQL with an agent loop, a final check and handoff</div>
<div class="sub">What happens for a single user question. Each column is a component; numbers are the steps in AGENTIC_FLOW.md.</div>
{''.join(divs)}
</div></body></html>'''
open(HTML_PATH,'w',encoding='utf-8').write(page)
print('written:', HTML_PATH)
