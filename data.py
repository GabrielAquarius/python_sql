# Tabela:
# empregado(nome:string, cpf:string, matricula:string, sexo:char, salario:numeric, idade: integer)
import numpy as np

class Data:
    def __init__(self):
        self.data_type = np.dtype([
            ('nome', 'U50'),
            ('cpf', 'U14'),
            ('matricula', 'U8'),
            ('sexo', 'U1'),
            ('salario', 'f8'),
            ('idade', 'i4')
        ])
        
        self.table_name = 'empregados'
        self.data = None

    def load_data(self):
        self.data = np.genfromtxt(f"{self.table_name}.txt", dtype=self.data_type, delimiter=';', encoding='latin-1')
        return self.data
    
    
    
