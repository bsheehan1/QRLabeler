import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk, ImageDraw, ImageFont

import qrcode

global program_name
program_name = 'QRLabeler'

global refresh_rate
refresh_rate = 500

class Window(Frame):
    
    def __init__(self, master=None):

        Frame.__init__(self, master)                   
        self.master = master
        self.init_window()
        
    def init_window(self):
     
        self.master.title(program_name)
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Preview", command=self.preview)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Warning",command=self.warning)
        file.add_command(label="Clear",command=self.clear)
        menu.add_cascade(label="File", menu=file)

        global qr
        qr = Image.new('RGB',(40,40),color='gray')
        global qr_list
        qr_list = []
        
        global image
        render = ImageTk.PhotoImage(qr)
        image = Label(self,image=render)
        image.image = render
        image.place(x=0,y=0)
        image.grid(column=0,row=0,sticky=(N,W))
        
        global label
        label_text = "Label"
        label = Label(self, text=label_text)
        label.text = label_text
        label.place(x=qr.size[0]+5,y=0)
        label.grid(column=1,row=0,sticky=(W))
        
        global text
        text = Text(self,height=24,width=80)
        text.grid(column=0,row=1,columnspan=6,sticky=(N,W))

        scrollbar= ttk.Scrollbar(self,orient=VERTICAL,command=text.yview)
        scrollbar.grid(column=6, row=1,sticky=(N,S))
        text['yscrollcommand'] = scrollbar.set

        global data
        data = str()

        global reset
        reset = True
        
        add_qr = ttk.Button(self, text="Add",command=self.add).grid(column=3,row=3)
        save_qr = ttk.Button(self, text="Remove",command=self.remove).grid(column=4,row=3)
        cancel = ttk.Button(self, text="Clear",command=self.clear).grid(column=5,row=3)

        self.grid_columnconfigure(1, weight=1)

        text.focus_set()

    def change_image(self):
        global image
        image.destroy() 
        render = ImageTk.PhotoImage(qr)
        image = Label(self, image=render)
        image.image = render
        image.place(x=0,y=0)
        image.grid(column=0,row=0)

    def change_label(self,data):
        global label
        label.destroy()
        if len(data) < 1:
            return
        raw_label = bytes(data,'utf-8')
        raw_label = str(raw_label)[2:-1]
        raw_label = raw_label.replace('\\t', ',')
        raw_label = raw_label.replace(' ', '_')
        raw_label = raw_label.replace('\\r', '')
        end = raw_label.find('\\n')
        raw_label = raw_label[:end]
        if raw_label.find(':') != -1:
            raw_label = raw_label[:raw_label.find(':')]
        if len(raw_label) > 80:
            raw_label = raw_label[:80]
        new_label = raw_label
        label = Label(self, text=new_label)
        label.text = new_label
        label.place(x=qr.size[0]+5,y=0)
        label.grid(column=1,row=0,sticky=(W))

    def render(self):
        global page
        page = Image.new('RGB',(850,1100),color='white')
        page_location = 0 
        for tup in qr_list:
            qr = tup[0]
            text = tup[1]
            card = Image.new('RGB',(800,qr.size[1]+1),color='white')
            card.paste(qr)
            info = ImageDraw.Draw(card)
            info.text((qr.size[0]+2,qr.size[1]/2-5),text,fill=(0,0,0))
            page.paste(card,box=(5,page_location+5))
            page_location += qr.size[1]+5

    def add(self):
        if len(data) <= 1:
            return
        else:
            qr_list.append((qr,label.text))
        text.focus_set()

    def remove(self):
        if len(qr_list) == 0:
            return
        qr_list.pop()
        text.focus_set()

    def preview(self):
        self.render()
        page.show()
        
    def save(self):
        self.render()
        page.save('./'+filename,'PNG')
        
    def clear(self):
        global qr
        global image
        global label
        image.destroy()
        label.destroy()
        text.delete('1.0', END)
        data = str()
        qr = Image.new('RGB',(29,29),color='white')
        render = ImageTk.PhotoImage(qr)
        image = Label(self,image=render)
        image.image = render
        image.place(x=0,y=0)
        image.grid(column=0,row=0,sticky=(N,W))
        label = Label(self)
        label.place(x=qr.size[0]+5,y=0)
        label.grid(column=1,row=0,sticky=(W))
        text.focus_set()
        self.after(refresh_rate,self.generate_qr)

    def warning(self):
        messagebox.showwarning('Warning','Data more than 2300 characters. Cannot convert to QR.')

    def generate_qr(self):
        global data
        global qr
        global label
        new_data = text.get("1.0",END)
        if len(new_data) > 2300:
            new_data = new_data[:2299]
            text.delete('1.0',END)
            text.insert(END,new_data)
            self.warning()
            self.after(0,self.generate_qr)
            return
        if new_data == data:
            self.after(refresh_rate,self.generate_qr)
            return
        data = new_data
        if len(new_data) == 1:
            self.clear()
            self.after(refresh_rate,self.generate_qr)
            return
        else:
            qr = qrcode.make(data,box_size=2)
            self.change_image()
            self.change_label(data)
            self.after(refresh_rate,self.generate_qr)


root = Tk()

#creation of an instance
app = Window(root)
app.generate_qr()


#mainloop 
root.mainloop()  
