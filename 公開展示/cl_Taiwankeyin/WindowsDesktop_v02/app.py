"""CELL TaiwanKeyin Windows Desktop: standalone preview, not a system TSF IME."""
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from engine import Engine, MAP, TONES

THEMES=[('#182334','#304259','#4A9EE6','#FFFFFF'),('#F1F3F8','#D9E0E9','#537BB8','#182333'),('#20182B','#473354','#A467D9','#FFFFFF'),('#182A22','#365849','#4BA880','#FFFFFF')]

class App:
    def __init__(self, root):
        self.root=root
        root.title('CELL 臺灣注音・Windows 桌面預覽 v0.2.1')
        root.geometry('910x565')
        root.minsize(650,420)
        self.theme=0
        self.main=ttk.Frame(root,padding=7);self.main.pack(fill='both',expand=True)
        data=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'full_zhuyin_mobile.sqlite3'
        try:self.engine=Engine(data)
        except Exception as ex:
            messagebox.showerror('詞庫載入失敗',str(ex));root.destroy();return
        self.status=tk.StringVar(value='完整臺灣正體詞庫 · 注音輸入，免選聲調 · 空白上字')
        self.preedit=tk.StringVar()
        ttk.Label(self.main,textvariable=self.status).pack(anchor='w')
        ttk.Label(self.main,textvariable=self.preedit,font=('Microsoft JhengHei',15,'bold')).pack(anchor='w')
        self.candidates=ttk.Frame(self.main);self.candidates.pack(fill='x')
        self.edit=tk.Text(self.main,height=9,font=('Microsoft JhengHei',16),wrap='word',undo=True)
        self.edit.pack(fill='both',expand=True,pady=6)
        self.edit.bind('<Key>',self.keydown)
        self.key_area=ttk.Frame(self.main);self.key_area.pack(fill='x')
        tools=ttk.Frame(self.main);tools.pack(fill='x',pady=6)
        ttk.Button(tools,text='清除組字',command=self.cancel).pack(side='left')
        ttk.Button(tools,text='複製全文',command=self.copy).pack(side='left')
        ttk.Button(tools,text='主題變換',command=self.toggle_theme).pack(side='left')
        ttk.Label(tools,text='Windows 文字工作台預覽；非系統層 TSF 輸入法').pack(side='right')
        self.draw_keys();self.refresh()
        self.edit.focus_set()
        root.protocol('WM_DELETE_WINDOW',self.close)
    def toggle_theme(self):
        self.theme=(self.theme+1)%len(THEMES)
        self.draw_keys()
    def keydown(self,event):
        if event.keysym in ('BackSpace','Delete') and self.engine.backspace():self.refresh();return 'break'
        if event.keysym=='Escape':self.cancel();return 'break'
        if event.char and event.char in '3467' and (self.engine.raw or self.engine.parts):
            tones={'3':'ˇ','4':'ˋ','6':'ˊ','7':'˙'}
            if self.engine.tone(tones[event.char]):self.refresh();return 'break'
        if event.keysym=='space' and self.engine.choices:
            self.select(0);return 'break'
        if event.keysym in ('Return','KP_Enter') and self.engine.choices:
            self.select(0);return 'break'
        if event.char and event.char.lower() in MAP and event.char.isascii():
            if self.engine.push(event.char):self.refresh();return 'break'
        if self.engine.raw or self.engine.parts:self.engine.clear();self.refresh()
        if event.char and event.char.isprintable():
            self.engine.committed(event.char);self.root.after_idle(self.refresh)
        return None
    def press_phonetic(self,code):
        if self.engine.push(code):self.refresh()
        self.edit.focus_set()
    def select(self,index):
        value=self.engine.choose(index)
        if value:self.edit.insert('insert',value)
        self.refresh();self.edit.focus_set()
    def follow(self,text):
        self.edit.insert('insert',text)
        self.engine.committed(text);self.refresh();self.edit.focus_set()
    def refresh(self):
        self.preedit.set('注音：'+self.engine.current_bare() if self.engine.current_bare() else '輸入文字後顯示智慧接續建議')
        for child in self.candidates.winfo_children():child.destroy()
        if self.engine.choices:
            choices=[c.text for c in self.engine.choices[:8]]
            callback=lambda i:self.select(i)
        else:
            choices=self.engine.followups(8)
            callback=lambda i:self.follow(choices[i])
        for i,t in enumerate(choices):
            ttk.Button(self.candidates,text=t,command=lambda j=i:callback(j)).pack(side='left',padx=2,pady=3)
    def draw_keys(self):
        for child in self.key_area.winfo_children():child.destroy()
        bg,panel,accent,fg=THEMES[self.theme]
        self.root.configure(bg=bg)
        rows=['125890-','qwertyuiop','asdfghjkl;','zxcvbnm,./']
        for n,codes in enumerate(rows):
            strip=tk.Frame(self.key_area,bg=bg);strip.pack(fill='x')
            for code in codes:
                tk.Button(strip,text=MAP[code],font=('Microsoft JhengHei',13),bg=panel,fg=fg,
                      activebackground=accent,relief='flat',command=lambda c=code:self.press_phonetic(c))\
                      .pack(side='left',fill='x',expand=True,padx=2,pady=2)
        tones=tk.Frame(self.key_area,bg=bg);tones.pack(fill='x')
        for label in ['ˉ','ˊ','ˇ','ˋ','˙']:
            tk.Label(tones,text=label,bg=accent,fg=fg,width=8).pack(side='left',expand=True,padx=2)
    def press_tone(self,mark):
        self.engine.tone(mark);self.refresh();self.edit.focus_set()
    def cancel(self):self.engine.clear();self.refresh()
    def copy(self):
        self.root.clipboard_clear();self.root.clipboard_append(self.edit.get('1.0','end-1c'))
        self.status.set('全文已複製，可以貼到 Word 或其他 Windows 軟體。')
    def close(self):self.engine.close();self.root.destroy()

if __name__=='__main__':
    root=tk.Tk()
    App(root)
    root.mainloop()
