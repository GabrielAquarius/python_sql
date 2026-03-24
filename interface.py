from tkinter import *
from tkinter import ttk

from sql_search import SQLSearch

class Interface:
    def __init__(self, toplevel):
        
        self.main_frame = Frame(toplevel)
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # --- CABEÇALHO ---
        self.main_masthead = Label(self.main_frame, text='SGBD G&L')
        self.main_masthead['font'] = ('Courier New', 30, 'bold')
        self.main_masthead.pack()

        # --- QUERY ---
        self.query_frame = Frame(self.main_frame)
        self.query_frame.pack(pady=10)

        self.query_title = Label(self.query_frame, text='QUERY')
        self.query_title['font'] = ('Courier New', 20)
        self.query_title.pack()

        self.error_message = Label(self.query_frame, text='', fg='red', font=('Courier New', 12, 'bold'))
        self.error_message.pack()

        self.query_entry = Text(self.query_frame, font=('Courier New', 14), width=60, height=4)
        self.query_entry.pack(pady=5)

        self.query_button = Button(self.query_frame, text='RUN', command=self.consulta_query, width=15)
        self.query_button.pack()

        # --- ÁREA DO OUTPUT ---
        self.output_frame = Frame(self.main_frame)
        self.output_frame.pack(pady=10, fill=BOTH, expand=True)

        self.output_title = Label(self.output_frame, text='OUTPUT')
        self.output_title['font'] = ('Courier New', 20)
        self.output_title.pack()

        self.text_container = Frame(self.output_frame)
        self.text_container.pack(fill=BOTH, expand=True)

        # Barras de rolagem (Horizontal e Vertical)
        self.x_scroll = Scrollbar(self.text_container, orient=HORIZONTAL)
        self.x_scroll.pack(side=BOTTOM, fill=X)
        
        self.y_scroll = Scrollbar(self.text_container, orient=VERTICAL)
        self.y_scroll.pack(side=RIGHT, fill=Y)

        # criação da tabela em Tree
        self.tree = ttk.Treeview(self.text_container, height=12,show='headings',
                                 xscrollcommand=self.x_scroll.set, yscrollcommand=self.y_scroll.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.x_scroll.config(command=self.tree.xview)
        self.y_scroll.config(command=self.tree.yview)

        self.clear_button = Button(self.output_frame, text='CLEAR', width=15, height=2)
        self.clear_button['command'] = self.clear_text
        self.clear_button.pack()

    def consulta_query(self):
        query = self.query_entry.get("1.0", "end-1c") 
        sql_search = SQLSearch()
        
        self.error_message.config(text='', fg='red')
        try:
            r = sql_search.consult(query)
            print(type(r))

            if type(r) == str:
                self.error_message.config(text=r)
            elif r and len(r) >= 2:
                tuples = r[0]
                print(tuples)
                columns = r[1]
                print(columns)
                self.atualizar_tabela(columns, tuples)
                
                self.error_message.config(text='Consulta executada com sucesso!', fg='green')
            else:
                self.clear_text()
                self.error_message.config(text='Comando executado. Nenhuma linha retornada.', fg='blue')

        except Exception as e:
            self.error_message.config(text=f'Erro SQL: {str(e)}')
            self.clear_text()

    def atualizar_tabela(self, columns, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree['columns'] = columns

        print(rows)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=W, stretch=True)

        for row in rows:
            self.tree.insert("", END, values=row)
            # print(row)

    def clear_text(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree['columns'] = []

root = Tk()
root.title('G&LDB')
root.geometry('800x650')
Interface(root)
root.mainloop()