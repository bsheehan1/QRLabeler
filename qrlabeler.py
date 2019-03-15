import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog

from PIL import Image, ImageTk, ImageDraw, ImageFont

import qrcode

class Window(Frame):
    
    def __init__(self, master=None):

        Frame.__init__(self, master)                   
        self.master = master

        #global variables
        self.data = str()
        self.qr_list = []
        self.qr_size = 1
        self.label_text = str()
        self.filename = str()
        self.page_list = []
        self.card_list = []
        self.save_location = os.curdir + '/tmp'
        #tkinter widgets 
        self.qr = Image.new('RGB',(40,40),color='gray')
        self.image = Label(self,image=ImageTk.PhotoImage(self.qr))
        self.image.grid(column=0,row=0,sticky=(N,W))
        self.label = Label(self, text=self.label_text)
        self.label.grid(column=1,row=0,sticky=(W))
        self.text = Text(self,height=24,width=80)
        self.text.grid(column=0,row=1,columnspan=6,sticky=(N,W,S,E))
        self.txtscrollbar = ttk.Scrollbar(self,orient=VERTICAL)
        self.txtscrollbar.grid(column=6, row=1,sticky=(N,S))
        self.text['yscrollcommand'] = self.txtscrollbar.set
        self.listbox = Listbox(self)
        self.listbox.grid(column=7, row=0, rowspan=4, sticky=(N,W,E,S))
        self.lbscrollbar = ttk.Scrollbar(self,orient=VERTICAL)
        self.lbscrollbar.grid(column=8, row=0, rowspan=4, sticky=(N,S))
        self.listbox['yscrollcommand'] = self.lbscrollbar.set

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(1, weight=1)

        self.init_window()
        
    def init_window(self):
        self.master.title('QRLabeler')
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label="Preview", command=self.preview)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save As...", command=self.save_as)
        file.add_command(label="Reset",command=self.reset)
        menu.add_cascade(label="File", menu=file)
        
        add_qr = ttk.Button(self, text="Add",command=self.add).grid(column=3,row=3)
        rem_qr = ttk.Button(self, text="Remove",command=self.remove).grid(column=4,row=3)
        cancel = ttk.Button(self, text="Clear",command=self.clear).grid(column=5,row=3)

        self.text.focus_set()

    def add(self):
        if len(self.data) <= 1:
            return
        else:
            self.qr_list.append((self.qr,self.label_text))
            self.listbox.insert(END,self.label_text[:20])
        self.text.focus_set()
        print(self.qr_list)

    def remove(self):
        if len(self.qr_list) == 0:
            return
        self.qr_list.pop()
        self.listbox.delete(END)
        self.text.focus_set()
        print(self.qr_list)

    def generate_cards(self):
        for tup in self.qr_list:
            qr = tup[0]
            text = tup[1]
            card = Image.new('RGB',(800,qr.size[1]+1),color='white')
            card.paste(qr)
            info = ImageDraw.Draw(card)
            info.text((qr.size[0]+2,qr.size[1]/2-5),text,fill=(0,0,0))
            self.card_list.append(card)
            
    def generate_pages(self):
        while True:
            page = Image.new('RGB',(850,1100),color='white')
            page_location = 0
            while len(self.card_list) > 0:
                card = self.card_list.pop(0)
                if page_location + card.size[1] + 5 > 1100:
                    self.card_list.insert(0,card)
                    self.page_list.append(page)
                    break
                else:
                    page.paste(card,box=(5,page_location+5))
                    page_location += card.size[1]+5
            if len(self.card_list) == 0:
                self.page_list.append(page)
                break

    def show_pages(self):
        tiff = self.page_list.pop(0)
        #a more elegant solution might be needed
        tiff.save(self.save_location + '/preview.tiff',"TIFF",save_all=True,append_images=self.page_list)
        image = Image.open(self.save_location + '/preview.tiff')
        image.show()
        render = ImageTk.PhotoImage(image)
        preview_window = Toplevel(self)
        label_text ='hello'
        preview_image = Label(preview_window, image=render)
        preview_image.image = render
        
        preview_image.grid(column=0,row=0)
        
    def preview(self):
        self.generate_cards()
        self.generate_pages()
        self.show_pages()
        self.page_list = []
        self.card_list = []

    def save(self):
        if self.filename == str():
            self.save_as()
            return
        self.generate_cards()
        self.generate_pages()
        pdf = self.page_list.pop(0)
        pdf.save(self.filename,"PDF",resolution=100.0,save_all=True,append_images=self.page_list)

    def save_as(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".pdf")
        self.save()

    def clear(self):
        self.text.delete('1.0',END)
        self.data = str()
        self.generate_qr()
        self.generate_image()
        self.generate_label()
        self.text.focus_set()

    def reset(self):
        self.clear()
        self.data = str()
        self.qr_list = []
        self.qr_size = 1
        self.label_text = str()
        self.filename = str()
        self.page_list = []
        self.card_list = []
        self.listbox.delete(0,END)

    def generate_qr(self):
        if len(self.data) > 2000:
            self.data = self.data[:1999]
            self.text.delete('1.0',END)
            self.text.insert(END,self.data)
            messagebox.showwarning('Warning','Data more than 2000 characters. Cannot convert to QR.')
            self.generate_qr()
        if len(self.data) == 1:
            self.qr = Image.new('RGB',(29,29),color='white')
            return
        else:
            self.qr = qrcode.make(self.data,box_size=self.qr_size)
            return
        
    def generate_image(self):
        self.image.destroy()
        render = ImageTk.PhotoImage(self.qr)
        self.image = Label(self,image=render)
        self.image.image = render
        self.image.place(x=0,y=0)
        self.image.grid(column=0,row=0,sticky=(N,W))

    def generate_label(self):
        self.label.destroy()
        raw_label = bytes(self.data,'utf-8')
        raw_label = str(raw_label)[2:-1]
        raw_label = raw_label.replace('\\t', '')
        raw_label = raw_label.replace(' ', '_')
        raw_label = raw_label.replace('\\r', '')
        end = raw_label.find('\\n')
        raw_label = raw_label[:end]
        if raw_label.find(':') != -1:
            raw_label = raw_label[:raw_label.find(':')]
        if len(raw_label) > 80:
            raw_label = raw_label[:80]
        label_text = raw_label
        self.label = Label(self, text=label_text)
        self.label.place(x=self.qr.size[0]+5,y=0)
        self.label.grid(column=1,row=0,sticky=(W))
        self.label_text = label_text
        
    def render(self):
        self.generate_qr()
        self.generate_image()
        self.generate_label()
        
    def main(self):
        data = self.text.get("1.0",END)
        if data == self.data:
            pass
        else:
            self.data = data
            self.label_text = data 
        print("...")
        self.render()
        self.after(500,self.main)

root = Tk()

#creation of an instance
app = Window(root)
app.main()


#mainloop 
root.mainloop()  
