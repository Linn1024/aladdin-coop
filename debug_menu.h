// Shared frontend pause menu. Uses controller edges, with no emulation while open.
#pragma once
struct DebugMenu {
 unsigned paused=0,selected=0,previous=0,waitingRelease=0,stage=1,debug=0;
 const char *notice="";
 unsigned pack() const {return paused|((selected&7)<<1)|((selected&8)<<2)|(waitingRelease<<4)|(debug<<6)|(previous<<8)|(stage<<24);}
 void unpack(unsigned v){paused=v&1;debug=(v>>6)&1;selected=((v>>1)&7)|((v>>2)&8);waitingRelease=(v>>4)&1;previous=(v>>8)&65535;stage=(v>>24)&15;notice="";}
 bool update(unsigned buttons,int (*command)(unsigned),int (*loadStage)(unsigned)=nullptr) {
  unsigned edge=buttons&~previous;previous=buttons;
  if(edge&(1<<3)){paused=!paused;debug=0;selected=0;waitingRelease=!paused;notice="";return true;}
  if(!paused){
   if(waitingRelease){if(!(buttons&((1<<8)|(1<<3)|3)))waitingRelease=0;return true;}
   return false;
  }
  if(!debug) {
   if((buttons&0x103)==0x103 && (edge&0x103)){debug=1;selected=0;notice="";}
   return true;
  }
  if(edge&(1<<4)){selected=(selected+9)%10;notice="";}
  if(edge&(1<<5)){selected=(selected+1)%10;notice="";}
  if(selected==9){if(edge&(1<<6))stage=(stage+12)%13;if(edge&(1<<7))stage=(stage+1)%13;}
  if(edge&(1<<8)) {
   if(!selected){paused=0;debug=0;waitingRelease=1;}
   else if(selected==9)notice=loadStage&&loadStage(stage)?"QUEUED - RESUME TO LOAD":"STAGE LOAD UNAVAILABLE";
   else notice=command(selected)?((selected<=2||selected==8)?"TOGGLE UPDATED":"QUEUED - RESUME TO APPLY"):
      (selected==4?"P1 MUST BE GROUNDED / NOCLIP OFF":"UNAVAILABLE - RESPAWN OR NOCLIP");
  }
  return true; // Consume closing-button frame too, preventing an accidental jump.
 }
 void draw(std::vector<uint32_t>& out,unsigned w,unsigned h,unsigned flags,bool complete=false) const {
  if((!paused&&!complete)||out.size()!=w*h||w!=320||h!=224)return;
  BITMAPINFO bi={};bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);
  bi.bmiHeader.biWidth=w;bi.bmiHeader.biHeight=-(int)h;
  bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=32;
  void *bits=nullptr;HDC dc=CreateCompatibleDC(nullptr);
  HBITMAP bm=CreateDIBSection(dc,&bi,DIB_RGB_COLORS,&bits,nullptr,0);
  if(!dc||!bm){if(bm)DeleteObject(bm);if(dc)DeleteDC(dc);return;}
  auto old=SelectObject(dc,bm);memcpy(bits,out.data(),w*h*4);
  RECT box=(!debug&&!complete)?RECT{60,82,260,140}:RECT{12,8,308,217};HBRUSH brush=CreateSolidBrush(RGB(18,22,38));FillRect(dc,&box,brush);DeleteObject(brush);
  HFONT font=CreateFontA(-12,6,0,0,FW_NORMAL,FALSE,FALSE,FALSE,ANSI_CHARSET,OUT_DEFAULT_PRECIS,CLIP_DEFAULT_PRECIS,NONANTIALIASED_QUALITY,FIXED_PITCH,"Courier New");
  auto oldFont=SelectObject(dc,font);SetBkMode(dc,TRANSPARENT);
  auto line=[&](int y,const char *s,COLORREF color){SetTextColor(dc,color);TextOutA(dc,24,y,s,(int)strlen(s));};
  if(complete) {
   line(65,"FIRST LEVEL COMPLETE!",RGB(255,215,110));
   line(95,"BOTH PLAYERS REACHED THE EXIT",RGB(230,235,245));
   line(145,"RESTART LEVEL TO PLAY AGAIN",RGB(170,185,205));
  } else if(!debug) {
   auto centered=[&](int y,const char *s,COLORREF color){SIZE extent={};GetTextExtentPoint32A(dc,s,(int)strlen(s),&extent);SetTextColor(dc,color);TextOutA(dc,(320-extent.cx)/2,y,s,(int)strlen(s));};
   centered(92,"PAUSED",RGB(255,215,110));
   centered(116,"ENTER / START: RESUME",RGB(230,235,245));
  } else {
  line(15,"DEBUG CHEATS",RGB(255,215,110));
  const char *names[]={"RESUME","INVINCIBLE TO DAMAGE","UNLIMITED APPLES","REFILL BOTH HEALTH BARS","SET CHECKPOINT AT P1","DEFEAT BOTH / TEST RESPAWN","DAMAGE P1 (-1 HP)","DAMAGE P2 (-1 HP)","NOCLIP / FLY P1","STAGE"};
  for(unsigned i=0;i<10;i++) {
   char s[64];snprintf(s,sizeof(s),"%c %s%s",i==selected?'>':' ',names[i],i==1?(flags&1?" [ON]":" [OFF]"):i==2?(flags&2?" [ON]":" [OFF]"):i==8?(flags&4?" [ON]":" [OFF]"):"");
   if(i==9){const char *stages[]={"ROOFTOPS","AGRABAH","ABU MARKET","DESERT","DUNGEON","CAVE OF WONDERS","ABU CAVE","THE ESCAPE","RUG RIDE","INSIDE THE LAMP","SULTAN PALACE","JAFAR","IAGO"};snprintf(s,sizeof(s),"%c STAGE: %s",selected==9?'>':' ',stages[stage]);}
   line(32+i*13,s,i==selected?RGB(255,215,110):RGB(230,235,245));
  }
  line(178,notice,RGB(130,215,255));
  line(193,selected==9?"LEFT/RIGHT: STAGE  JUMP: LOAD":"UP/DOWN: SELECT  JUMP: APPLY",RGB(170,185,205));
  line(204,"ENTER / START: RESUME",RGB(170,185,205));
  }
  GdiFlush();memcpy(out.data(),bits,w*h*4);
  SelectObject(dc,oldFont);DeleteObject(font);SelectObject(dc,old);DeleteObject(bm);DeleteDC(dc);
 }
};
