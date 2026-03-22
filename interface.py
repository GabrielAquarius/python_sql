from tkinter import *
from sql_search import SQLSearch

class Interface:
    def __init__(self, toplevel):
        
        self.main_frame = Frame(toplevel)
        self.main_frame.pack()

        self.main_masthead = Label(self.main_frame, text='SGBD G&L')
        self.main_masthead['font'] = ('Courier New', 30)
        self.main_masthead.pack()

        self.query_frame = Frame(self.main_frame)
        self.query_frame.pack()

        self.query_title = Label(self.query_frame, text='QUERY')
        self.query_title['font'] = ('Courier New', 25)
        self.query_title.pack()

        self.query_entry = Entry(self.query_frame)
        self.query_entry['font'] = ('Courier New', 20)
        self.query_entry['width'] = 60
        self.query_entry.pack()

        self.query_button = Button(self.query_frame, text='RUN')
        self.query_button['command'] = self.consulta_query
        self.query_button.pack()

        self.output_frame = Frame(self.main_frame)
        self.output_frame.pack()

        self.output_title = Label(self.output_frame, text='OUTPUT')
        self.output_title['font'] = ('Courier New', 25)
        self.output_title.pack()

        self.output_text = Label(self.output_frame, text='')
        # self.output_text['width'] = 80
        # self.output_text['height'] = 30
        self.output_text['bg'] = "#fff"
        self.output_text.pack()

        self.clear_button = Button(self.output_frame, text='CLEAR')
        self.clear_button['command'] = self.clear_text
        self.clear_button.pack()
    
    def consulta_query(self):
        sql_search = SQLSearch()

        query = self.query_entry.get() # query do usuário
        r = sql_search.consult(query)
        self.output_text['text'] = r

    def clear_text(self):
        self.output_text['text'] = ''

root = Tk()
root.title('G&LDB')
root.geometry('800x600')
# root['bg'] = ('#d9d9d9') # cor de fundo 
Interface(root)
root.mainloop()