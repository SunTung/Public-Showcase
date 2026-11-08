"""CELL TaiwanKeyin Win preview: offline Chewing dictionary and committed context."""
import sqlite3
from dataclasses import dataclass
from pathlib import Path

SYMBOL_KEYS = '1qaz2wsxedcrfv5tgbyhnujm8ik,9ol.0p;/-'
SYMBOL_VALUES = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'
MAP = dict(zip(SYMBOL_KEYS, SYMBOL_VALUES))
TONES = 'ˉˊˇˋ˙'
TONE_CODE = {'3': 'ˇ', '4': 'ˋ', '6': 'ˊ', '7': '˙'}

@dataclass(frozen=True)
class Candidate:
    text: str
    reading: str
    frequency: int

class Engine:
    def __init__(self, database: str | Path):
        path=Path(database).resolve()
        self.db=sqlite3.connect('file:'+str(path).replace('\\','/')+'?mode=ro', uri=True)
        self.db.execute('select 1 from lexicon_mobile limit 1').fetchone()
        self.raw=''
        self.parts=[]
        self.context=''
        self.choices=[]
        self.chosen={}
        self.mode='注繁'

    def close(self): self.db.close()
    @staticmethod
    def slot(code):
        pos=SYMBOL_KEYS.find(code)
        return -1 if pos<0 else 0 if pos<21 else 1 if pos<24 else 2
    @classmethod
    def valid(cls, raw):
        if not raw or len(raw)>3:return False
        slots=[cls.slot(x) for x in raw]
        return min(slots)>=0 and all(b>a for a,b in zip(slots,slots[1:]))
    @classmethod
    def complete(cls, raw):
        if not cls.valid(raw):return False
        return len(raw)>1 or raw[0] in '5tgbyhn' or cls.slot(raw[0])!=0
    @staticmethod
    def translate(raw):return ''.join(MAP.get(x,'') for x in raw)
    def current_bare(self):
        items=self.parts+([self.translate(self.raw)] if self.raw else [])
        return ' '.join(items)
    def push(self, code):
        code=code.lower()
        if code not in MAP:return False
        if not self.valid(self.raw+code):
            if not self.complete(self.raw) or len(self.parts)>=9:return False
            self.parts.append(self.translate(self.raw));self.raw=''
        self.raw+=code
        self.refresh()
        return True
    def backspace(self):
        if self.raw:self.raw=self.raw[:-1]
        elif self.parts:self.raw=self._key_for(self.parts.pop())
        else:return False
        self.refresh();return True
    @staticmethod
    def _key_for(reading):
        reversed_map={v:k for k,v in MAP.items()}
        return ''.join(reversed_map.get(c,'') for c in reading if c not in TONES)
    def clear(self):self.raw='';self.parts=[];self.choices=[]
    def refresh(self):
        bare=self.current_bare()
        self.choices=[]
        if self.raw and not self.complete(self.raw):return
        if not bare:return
        rows=self.db.execute('''SELECT word,reading,frequency FROM lexicon_mobile
           WHERE bare=? ORDER BY frequency DESC LIMIT 80''',(bare,)).fetchall()
        self.choices=[Candidate(*row) for row in rows if self._tone_match(row[1])][:18]
        self.choices.sort(key=lambda c:(-(c.frequency+self.chosen.get(c.text,0)*600),c.text))
    def _tone_match(self,actual):
        # Windows preview accepts tone-optional phonetic readings.
        return actual.translate(str.maketrans('','',TONES))==self.current_bare()
    def choose(self,index=0):
        if index<0 or index>=len(self.choices):return None
        result=self.choices[index]
        self.committed(result.text)
        self.chosen[result.text]=self.chosen.get(result.text,0)+1
        self.clear()
        return result.text
    def committed(self,text):
        if any(c in '，。！？、；,.!?;\n' for c in text):self.context=''
        else:self.context=(self.context+text)[-10:]
    def followups(self,limit=8):
        if not self.context:return []
        matches={}
        for take in range(min(4,len(self.context)),0,-1):
            prefix=self.context[-take:]
            rows=self.db.execute('''SELECT word,MAX(frequency) FROM lexicon_mobile
               WHERE word>=? AND word<? AND length(word)>length(?)
               GROUP BY word ORDER BY 2 DESC LIMIT 60''',(prefix,prefix+'\uffff',prefix)).fetchall()
            for word,freq in rows:
                suffix=word[len(prefix):]
                if suffix and len(suffix)<=3 and all(c.isalnum() for c in suffix):
                    matches[suffix]=max(matches.get(suffix,-1),freq+take*1000000)
        return [k for k,_ in sorted(matches.items(),key=lambda x:(-x[1],x[0]))[:limit]]
