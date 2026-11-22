#!/usr/bin/env python3
"""Draw a compact deterministic newspaper page using only the Python standard library."""
import os
import struct
import zlib
import math

W = H = 1024
NAVY = (10, 24, 48)
NAVY2 = (17, 39, 70)
INK = (16, 27, 42)
RED = (193, 39, 49)
RED2 = (225, 62, 61)
YELLOW = (247, 195, 55)
PAPER = (247, 244, 234)
WHITE = (255, 255, 250)
GREY = (104, 111, 119)
PALE = (224, 220, 207)

# Five by seven hand-drawn bitmap glyphs; all text is rendered from these rows.
FONT = {
'A':('01110','10001','10001','11111','10001','10001','10001'),
'B':('11110','10001','10001','11110','10001','10001','11110'),
'C':('01111','10000','10000','10000','10000','10000','01111'),
'D':('11110','10001','10001','10001','10001','10001','11110'),
'E':('11111','10000','10000','11110','10000','10000','11111'),
'F':('11111','10000','10000','11110','10000','10000','10000'),
'G':('01111','10000','10000','10111','10001','10001','01111'),
'H':('10001','10001','10001','11111','10001','10001','10001'),
'I':('11111','00100','00100','00100','00100','00100','11111'),
'J':('00111','00010','00010','00010','10010','10010','01100'),
'K':('10001','10010','10100','11000','10100','10010','10001'),
'L':('10000','10000','10000','10000','10000','10000','11111'),
'M':('10001','11011','10101','10101','10001','10001','10001'),
'N':('10001','11001','10101','10011','10001','10001','10001'),
'O':('01110','10001','10001','10001','10001','10001','01110'),
'P':('11110','10001','10001','11110','10000','10000','10000'),
'Q':('01110','10001','10001','10001','10101','10010','01101'),
'R':('11110','10001','10001','11110','10100','10010','10001'),
'S':('01111','10000','10000','01110','00001','00001','11110'),
'T':('11111','00100','00100','00100','00100','00100','00100'),
'U':('10001','10001','10001','10001','10001','10001','01110'),
'V':('10001','10001','10001','10001','10001','01010','00100'),
'W':('10001','10001','10001','10101','10101','10101','01010'),
'X':('10001','10001','01010','00100','01010','10001','10001'),
'Y':('10001','10001','01010','00100','00100','00100','00100'),
'Z':('11111','00001','00010','00100','01000','10000','11111'),
'0':('01110','10001','10011','10101','11001','10001','01110'),
'1':('00100','01100','00100','00100','00100','00100','01110'),
'2':('01110','10001','00001','00010','00100','01000','11111'),
'3':('11110','00001','00001','01110','00001','00001','11110'),
'4':('00010','00110','01010','10010','11111','00010','00010'),
'5':('11111','10000','10000','11110','00001','00001','11110'),
'6':('01110','10000','10000','11110','10001','10001','01110'),
'7':('11111','00001','00010','00100','01000','01000','01000'),
'8':('01110','10001','10001','01110','10001','10001','01110'),
'9':('01110','10001','10001','01111','00001','00001','01110'),
'.':('00000','00000','00000','00000','00000','00110','00110'),
',':('00000','00000','00000','00000','00110','00110','00100'),
':':('00000','00110','00110','00000','00110','00110','00000'),
';':('00000','00110','00110','00000','00110','00110','00100'),
'!':('00100','00100','00100','00100','00100','00000','00100'),
'?':('01110','10001','00001','00010','00100','00000','00100'),
"'":('00100','00100','00000','00000','00000','00000','00000'),
'"':('01010','01010','00000','00000','00000','00000','00000'),
'-':('00000','00000','00000','11111','00000','00000','00000'),
'+':('00000','00100','00100','11111','00100','00100','00000'),
'/':('00001','00010','00010','00100','01000','01000','10000'),
'$':('00100','01111','10100','01110','00101','11110','00100'),
'%':('11001','11010','00100','01000','10110','00110','00000'),
'&':('01100','10010','10100','01000','10101','10010','01101'),
'(':('00010','00100','01000','01000','01000','00100','00010'),
')':('01000','00100','00010','00010','00010','00100','01000'),
'=':('00000','11111','00000','11111','00000','00000','00000'),
'•':('00000','00000','01100','01100','01100','00000','00000'),
' ':('00000',)*7,
}

pixels = bytearray(W * H * 3)

def rect(x, y, w, h, c):
    x0, y0, x1, y1 = max(0, int(x)), max(0, int(y)), min(W, int(x+w)), min(H, int(y+h))
    if x1 <= x0 or y1 <= y0: return
    row = bytes(c) * (x1-x0)
    for yy in range(y0, y1):
        start = (yy*W+x0)*3
        pixels[start:start+len(row)] = row

def circle(cx, cy, r, c):
    rr = r*r
    for yy in range(max(0,cy-r), min(H,cy+r+1)):
        dy=yy-cy
        for xx in range(max(0,cx-r), min(W,cx+r+1)):
            dx=xx-cx
            if dx*dx+dy*dy <= rr:
                i=(yy*W+xx)*3; pixels[i:i+3]=bytes(c)

def line(x0,y0,x1,y1,c,width=1):
    dx,dy=abs(x1-x0),abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1; err=dx-dy
    while True:
        rect(x0-width//2,y0-width//2,width,width,c)
        if x0==x1 and y0==y1: break
        e=2*err
        if e > -dy: err-=dy; x0+=sx
        if e < dx: err+=dx; y0+=sy

def polygon(points,c):
    ymin=max(0,min(y for _,y in points)); ymax=min(H-1,max(y for _,y in points))
    for yy in range(ymin,ymax+1):
        hits=[]
        for i,(x1,y1) in enumerate(points):
            x2,y2=points[(i+1)%len(points)]
            if y1==y2: continue
            if min(y1,y2) <= yy < max(y1,y2):
                hits.append(int(x1+(yy-y1)*(x2-x1)/(y2-y1)))
        hits.sort()
        for a,b in zip(hits[0::2],hits[1::2]): rect(a,yy,b-a+1,1,c)

def text_width(s, scale=1, spacing=1):
    return max(0, len(s)*(5+spacing)*scale-spacing*scale)

def draw_text(x,y,s,c=INK,scale=1,spacing=1, max_width=None):
    s=s.upper()
    if max_width is not None and text_width(s,scale,spacing)>max_width:
        return False
    for ch in s:
        glyph=FONT.get(ch, FONT[' '])
        for gy,row in enumerate(glyph):
            for gx,p in enumerate(row):
                if p=='1': rect(x+gx*scale,y+gy*scale,scale,scale,c)
        x+=(5+spacing)*scale
    return True

def wrap(s, max_chars):
    words=s.upper().split(); out=[]; cur=''
    for word in words:
        nxt=word if not cur else cur+' '+word
        if len(nxt)>max_chars and cur: out.append(cur); cur=word
        else: cur=nxt
    if cur: out.append(cur)
    return out

def centered(s,y,scale,color,spacing=1):
    draw_text((W-text_width(s.upper(),scale,spacing))//2,y,s,color,scale,spacing)

# Warm paper and masthead.
rect(0,0,W,H,PAPER)
rect(0,0,W,132,NAVY)
rect(0,126,W,6,YELLOW)
title='THE WORLD TODAY'; title_scale=6; title_w=text_width(title,title_scale,1); tx=(W-title_w)//2
for ix,ch in enumerate(title):
    gx=tx+ix*36
    draw_text(gx,14,ch,WHITE,title_scale,1)
    if ch!=' ':
        rect(gx,14,6,2,WHITE); rect(gx,54,6,2,WHITE)
centered('SATURDAY • 21 NOVEMBER 2026 • 16 STORIES • 7 REGIONS • ONE PAGE',94,2,YELLOW,1)

# Four illustrated lead panels.
PW=256; ART_Y=132; ART_H=164; CAP_Y=296; CAP_H=88
for i in range(4): rect(i*PW,ART_Y,PW,ART_H,(217,226,224) if i in (0,2) else (207,222,231))
# Shenzhen skyline and three delegates around a conference table.
rect(0,132,256,164,(186,213,217)); circle(225,154,20,(246,205,104))
for x,w,h,col in [(0,44,62,(80,119,139)),(43,39,92,(71,107,132)),(80,31,69,(101,139,151)),(180,38,89,(68,104,129)),(216,40,66,(90,128,142))]:
    rect(x,224-h,w,h,col)
    for wy in range(230-h,218,14):
        for wx in range(x+7,x+w-3,12): rect(wx,wy,4,5,(245,210,121))
polygon([(123,222),(133,153),(139,140),(145,153),(153,222)],(50,91,120)); line(139,140,139,132,RED,2)
rect(0,244,256,52,(75,115,126))
for x,skin,suit,tie in [(47,(232,184,145),(39,55,78),RED),(112,(219,168,126),(23,39,61),RED),(177,(229,188,153),(58,58,65),YELLOW)]:
    circle(x,220,12,skin); rect(x-15,231,30,29,suit); polygon([(x,231),(x-4,238),(x,255),(x+4,238)],tie); rect(x-14,213,28,5,(42,35,31))
rect(69,258,118,9,(88,55,42)); rect(84,250,88,8,(112,75,56))
# Hormuz water, tanker, blockade buoys, and an alert flare.
rect(256,132,256,164,(87,155,179)); circle(468,164,21,(245,207,118))
for yy in (213,228,244,261,278): line(260,yy,508,yy-5,(136,194,205),2)
polygon([(298,225),(446,225),(429,247),(317,247)],(31,48,63)); rect(348,209,42,16,(232,226,205)); rect(358,198,21,11,WHITE); rect(365,192,4,6,RED); rect(380,201,5,8,RED)
rect(280,184,202,4,RED)
for x in range(290,483,28): circle(x,186,4,YELLOW)
circle(483,216,11,RED2)
for ang in range(0,360,45):
    a=math.radians(ang); line(int(483+14*math.cos(a)),int(216+14*math.sin(a)),int(483+23*math.cos(a)),int(216+23*math.sin(a)),YELLOW,2)
# Poland skyline, incoming missile, and burning freighter on the Gulf of Finland.
rect(512,132,256,164,(166,203,216)); rect(512,243,256,53,(51,91,113))
for x,w,h in [(518,34,68),(557,46,92),(608,35,57),(648,51,81),(705,56,62)]:
    rect(x,243-h,w,h,(93,113,124)); polygon([(x-3,243-h),(x+w//2,235-h),(x+w+3,243-h)],(73,92,105))
    for wy in range(243-h+15,235,17):
        for wx in range(x+7,x+w-4,13): rect(wx,wy,5,7,(244,206,112))
polygon([(664,149),(674,157),(711,202),(706,207)],(37,48,59)); polygon([(664,149),(660,164),(672,159)],RED)
line(666,161,635,139,(239,113,58),4); line(663,166,635,153,YELLOW,3)
polygon([(530,271),(669,271),(651,285),(548,285)],NAVY); rect(562,256,33,15,(211,215,207)); rect(601,250,40,21,(179,74,54)); rect(611,244,10,8,YELLOW); circle(628,241,9,RED2); circle(632,235,5,YELLOW)
# A dark smoke plume and two-tone flame make the drone-hit freighter read clearly.
circle(637,226,7,(77,77,78)); circle(642,217,6,(101,102,100)); circle(634,234,5,YELLOW); polygon([(628,244),(633,230),(638,244)],(255,132,42))
# Market chart dives in red while a bitcoin coin rebounds.
rect(768,132,256,164,(225,226,218))
for x,h in [(785,40),(812,58),(839,75),(866,66),(893,92),(920,108)]: rect(x,271-h,17,h,(133,164,168))
pts=[(778,176),(804,162),(829,180),(851,169),(873,205),(897,193),(917,231),(938,218),(952,246)]
for a,b in zip(pts,pts[1:]): line(a[0],a[1],b[0],b[1],RED,4)
polygon([(947,237),(962,250),(944,254)],RED)
circle(988,178,27,YELLOW); circle(988,178,22,(247,215,112)); draw_text(980,167,'B',NAVY,3,1); line(986,165,986,189,NAVY,2); line(991,165,991,189,NAVY,2)
line(957,220,982,205,(22,129,105),4); polygon([(977,198),(989,202),(981,211)],(22,129,105))

hero_caps=[
('SHENZHEN SUMMIT','Xi brings Trump and Putin','to one historic table.'),
('HORMUZ UNDER FIRE','Iran claims US base strikes;','flows down 15% at Hormuz.'),
('POLAND HIT','NATO: grave breach amid Kyiv barrage','Gulf ship burns after drone strike.'),
('MARKETS IN RETREAT','S&P, Dow correct; Nasdaq loses','2026 gains on AI fears; bitcoin +9%'),
]
for i,(head,l1,l2) in enumerate(hero_caps):
    x=i*PW; rect(x,CAP_Y,PW,CAP_H,NAVY); rect(x,CAP_Y,PW,4,RED if i==2 else YELLOW)
    draw_text(x+12,CAP_Y+12,head,YELLOW,2,1); draw_text(x+12,CAP_Y+40,l1,WHITE,1,1); draw_text(x+12,CAP_Y+57,l2,WHITE,1,1)

# Breaking-news ticker.
rect(0,384,W,34,RED)
ticker='APEC SUMMIT • HORMUZ BLOCKADE • POLAND STRUCK • MARKETS SLIDE • YOUTH WALKS'
draw_text(14,397,ticker,WHITE,2,1)

# Twelve concise stories in three columns and four rows.
STORIES=[
('MIDDLE EAST','Riyadh downs three Houthi missiles','Saudi air defences intercept the salvo.'),
('EUROPE','Denmark backs US-Greenland pact 109-0',"Copenhagen also moves to expel Russia's envoy."),
('AMERICAS','Mexico captures wanted cartel chief','El Chapo Isidro is seized in a Sinaloa raid.'),
('EUROPE','UK and EU agree a post-Brexit reset','Food, carbon rules and youth travel are covered.'),
('CLIMATE','COP31 talks run past their deadline','Draft text drops its fossil-fuel wording.'),
('HEALTH','New cancer pill clears tumours in some','Daraxonrasib made tumours undetectable in 1 in 12.'),
('EUROPE','Youth walkouts span 25 countries','Gen Z protesters mark a day of action.'),
('ASIA-PACIFIC','EU and Indonesia seal trade deals','Agreement follows a decade of negotiations.'),
('SPACE','BepiColombo reaches Mercury','The joint European-Japanese probe arrives.'),
('TECH','GTA 6 makes $3.79bn on day one','A record opening jolts the games business.'),
('CYBER','FBI crime database hit by suspected hack','Investigators are probing a possible breach.'),
('UKRAINE','Zelensky defends Crimea Bridge strikes','He calls the attacks a justified response.'),
]
GX=18; GY=424; GAP=12; CW=(W-2*GX-2*GAP)//3; CH=105; RG=6
for idx,(cat,headline,sub) in enumerate(STORIES):
    col=idx%3; row=idx//3; x=GX+col*(CW+GAP); y=GY+row*(CH+RG)
    rect(x,y,CW,CH,WHITE); rect(x,y,CW,23,NAVY); draw_text(x+10,y+7,cat,YELLOW,1,1); rect(x,y+23,CW,1,PALE)
    headline_lines=wrap(headline,(CW-20)//12)
    for j,ln in enumerate(headline_lines[:2]): draw_text(x+10,y+31+j*17,ln,INK,2,1)
    sublines=wrap(sub,(CW-20)//6)
    for j,ln in enumerate(sublines[:2]): draw_text(x+10,y+72+j*9,ln,GREY,1,1)

# Footer figures.
FOOT_Y=868
rect(0,FOOT_Y,W,H-FOOT_Y,NAVY); rect(0,FOOT_Y,W,4,RED)
draw_text(24,FOOT_Y+15,'THE DAY IN NUMBERS',YELLOW,3,1)
metrics=[
('15%','LESS OIL THROUGH HORMUZ'),('$60,000','BITCOIN BACK ABOVE IT  •  +9%'),('109-0','DANISH VOTE FOR THE PACT'),
('58','INJURED IN KRYVYI RIH STRIKE'),('25','COUNTRIES JOIN YOUTH WALKS'),('$3.79BN','GTA 6 OPENING-DAY SALES'),
]
MX=24; MW=309; MG=18; MY=FOOT_Y+58
for i,(number,label) in enumerate(metrics):
    col=i%3; row=i//3; x=MX+col*(MW+MG); y=MY+row*47
    if row: rect(x,y-5,MW,1,(58,76,98))
    ns=2 if len(number)>5 else 3; draw_text(x,y,number,WHITE,ns,1)
    lx=x+text_width(number,ns,1)+12
    if lx+text_width(label,1,1)>x+MW: draw_text(x,y+27,label,YELLOW,1,1)
    else: draw_text(lx,y+10,label,YELLOW,1,1)

# PNG rows use filter type 0 and fixed compression; no metadata or timestamps.
raw=bytearray(); stride=W*3
for y in range(H):
    raw.append(0); raw.extend(pixels[y*stride:(y+1)*stride])
def chunk(kind,data):
    body=kind+data
    return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
png=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',W,H,8,2,0,0,0))+
     chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))
outdir=os.environ.get('MAKEFUN_OUTPUT_DIR','out')
os.makedirs(outdir,exist_ok=True)
with open(os.path.join(outdir,'entry.png'),'wb') as f: f.write(png)
