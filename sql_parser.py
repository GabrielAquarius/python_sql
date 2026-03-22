import re

from data import Data

class SQLParser(Data):
    def __init__(self):
        super().__init__()
    
    def parse_sql_query(self, tokens, query):
        
        if tokens[0] == 'select':
            return self._validate_select(tokens, query)
        elif tokens[0] == 'insert' and tokens[1] == 'into':
            return self._validate_insert(tokens, query)
        elif tokens[0] == 'update':
            return self._validate_update(tokens, query)
        elif tokens[0] == 'delete' and tokens[1] == 'from':
            return self._validate_delete(tokens, query)
        else:
            raise UserWarning(f'O comando {tokens[0]} é inválido.')
    
    def _validate_select(self, tokens, query):
        try:
            if 'from' not in tokens:
                raise SyntaxError(f"A consulta {query} é inválida! É necessário o comando FROM.")
            
            from_index = tokens.index('from')
            if from_index < 2:
                raise SyntaxError(f"A consulta {query} é inválida! É insuficiente ou mal formatada.")

            columns = tokens[1:from_index]
            table = tokens[from_index + 1].lower()
            
            if table != self.table_name:
                raise ValueError(f"A tabela {table} não foi encontrada.")            
            
            for col in columns:
                col_lower = col.lower()
                if col_lower == '*':
                    continue
                
                if col_lower.startswith('count') or col_lower.startswith('sum') or col_lower.startswith('avg'):
                    col_name = col_lower.replace('count', '').replace('sum', '').replace('avg', '').strip('()')
                    if col_name != '*' and col_name != '' and col_name not in self.data_type.names:
                        raise ValueError(f"A coluna {col_name} na função de agregação não existe na tebela {table}.")

                    continue
                if col_lower not in self.data_type.names:
                    raise ValueError(f"A coluna {col} não existe na tabela {table}.")
            
            idx = from_index + 2
            while idx < len(tokens):
                clause = tokens[idx]
                
                if clause == 'where':
                    if idx + 3 > len(tokens):
                        raise SyntaxError('Cláusa WHERE incompleta.')
                    where_col = tokens[idx + 1].lower()
                    if where_col not in self.data_type.names:
                        raise ValueError(f"A coluna {where_col} não existe na tabela {table}.")
                    operator = tokens[idx + 2]
                    if operator not in ['=', '>', '<', '>=', '<=', '!=', 'LIKE']:
                        raise ValueError(f"Operador {operator} inválido na cláusula WHERE.")
                    idx += 4
                    
                    if idx < len(tokens) and tokens[idx] in ['AND', 'OR']:
                        if idx + 3 > len(tokens):
                            raise SyntaxError(f"Cláusa {tokens[idx]} incompleta.")
                        and_col = tokens[idx + 1].lower()
                        if and_col not in self.data_type.names:
                            raise ValueError(f"A coluna {and_col} não existe na tabela {table}.")
                        idx += 4
                
                elif clause == 'order':
                    if idx + 2 >= len(tokens) or tokens[idx + 1] != 'by':
                        raise SyntaxError('Cláusa ORDER BY mal formatada.')
                    order_col = tokens[idx + 2].lower()
                    if order_col not in self.data_type.names:
                        raise ValueError(f"A coluna {order_col} não existe na tabela {table}.")
                    idx += 3
                    if idx < len(tokens) and tokens[idx] in ['asc', 'desc']:
                        idx += 1
                elif clause == 'limit':
                    if idx + 1 >= len(tokens):
                        raise SyntaxError('Cláusula LIMIT mal formatada.')
                    if not tokens[idx + 1].isdigit():
                        raise ValueError('O valor do LIMIT precisa ser um número inteiro.')
                    idx += 2
                elif clause == 'group':
                    if idx + 2 >= len(tokens) or tokens[idx + 1] != 'BY':
                        raise SyntaxError('Cláusa GROUP BY mal formatada.')
                    group_col = tokens[idx + 2].lower()
                    if group_col not in self.data_type.names:
                        raise ValueError(f"A coluna {group_col} não existe na tabela {table}.")
                    idx += 3
                
                elif clause == 'having':
                    if idx + 3 >= len(tokens):
                        raise SyntaxError('Cláusula HAVING incompleta.')
                    
                    having_func = tokens[idx + 1].lower()
                    if not (having_func.startswith('count') or having_func.startswith('sum') or having_func.startswith('avg')):
                        raise ValueError("A cláusula HAVING exige uma função de agregação (COUNT, SUM, AVG).")
                    
                    col_name = having_func.replace('count', '').replace('sum', '').replace('avg', '').strip('()')
                    if col_name != '*' and col_name != '' and col_name not in self.data_type.names:
                        raise ValueError(f"A coluna {col_name} na função de agregação do HAVING não existe na tabela {table}.")
                    
                    operator = tokens[idx + 2]
                    if operator not in ['=', '>', '<', '>=', '<=', '!=']:
                        raise ValueError(f"Operador {operator} inválido na cláusula HAVING.")
                    
                    idx += 4 
                else:
                    raise SyntaxError(f"Cláusula {clause} não reconhecida na consulta {query}.")
                
            return 'select'
        
        except Exception as e:
            return f"Erro ao processar: {e}"
        
    def _validate_insert(self, tokens, query):
        try:
            if len(tokens) < 10:
                raise SyntaxError ('A consulta {query} é insuficiente')
            if len(tokens) > 10:
                raise SyntaxError ('A consulta {query} possui argumentos em excesso')

            table = tokens[2]
            keyword_values = tokens[3]
            nome = tokens[4]
            cpf = tokens[5]
            matricula = tokens[6]
            sexo = tokens[7]
            
            try:
                salario = float(tokens[8])
                if salario < 0:
                    raise ValueError('Salário precisa ser um número positivo')
            except:
                raise ValueError('Salário precisa ser um número')
            try:
                idade = int(tokens[9])
                if idade < 0:
                    raise ValueError('Idade precisa ser um inteiro positivo')
            except:
                raise ValueError('Idade precisa ser um inteiro')
            if table != self.table_name:
                raise ValueError(f"A tabela {table} não foi encontrada.")
            if keyword_values != 'values':
                raise SyntaxError(f"A consulta {query} é inválida! É necessário o comando VALUES após tabela.")

            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$', nome):
                raise ValueError(f"O nome {nome} contém caracteres inválidos (use apenas letras).")
            if len(cpf) != 14:
                raise ValueError(f"O cpf {cpf} é inválido")
            if len(matricula) != 6:
                raise ValueError(f"A matrícula {matricula} é inválida")
            if sexo not in ['m', 'f']:
                raise ValueError(f"Sexo {sexo} inválido, precisa ser M ou F")

            return 'insert'
            
        except Exception as e:
            return f"Erro ao processar {e}"
    
    def _validate_update(self, tokens, query):

        try:
            if len(tokens) < 7:
               raise SyntaxError ('A query {query} é insuficiente')
           
            table = tokens[1].lower()
            keyword_set = tokens[2]
            column_1 = tokens[3].lower()
            logic_operator_1 = tokens[4]
            keyword_where = tokens[6]
            column_2 = tokens[7].lower()
            logic_operator_2 = tokens[8]
            
            if table != self.table_name:
                raise ValueError(f"A tabela {table} não foi encontrada.")
            if keyword_set != 'set':
                raise ValueError(f"A consulta {query} é inválida! É necessário o comando SET após tabela.")
            if column_1 not in self.data_type.names:
                raise ValueError(f"A coluna {column_1} não existe na tabela {table}.")
            if logic_operator_1 != '=':
                raise ValueError(f"O operador lógico '=' é necessário na consulta {query}")
            if keyword_where != 'where':
                raise SyntaxError(f"A consulta {query} é inválida! É necessário o comando WHERE após coluna.")
            if column_2 not in self.data_type.names:
                raise ValueError(f"A coluna {column_2} não existe na tabela {table}.")
            if logic_operator_2 != '=':
                raise ValueError(f"O operador lógico '=' é necessário na consulta {query}")
            
            return 'update'

        except Exception as e:
            return f"Erro ao processar {e}"
    
    def _validate_delete(self, tokens, query):
        try:
            if len(tokens) < 7:
               raise SyntaxError ('A query {query} é insuficiente')
           
            table = tokens[2].lower()
            keyword_where = tokens[3]
            column = tokens[4].lower()
            logic_operator = tokens[5]
            
            if table != self.table_name:
                raise ValueError(f"A tabela {table} não foi encontrada.")
            
            if keyword_where != 'where':
                raise SyntaxError(f"A consulta {query} é inválida! É necessário o comando WHERE após tabela.")
            
            if column not in self.data_type.names:
                raise SyntaxError(f"A coluna {column} não existe na tabela {table}.")
            
            if logic_operator != '=':
                raise ValueError(f"O operador lógico '=' é necessário na consulta {query}")

            return 'delete'
        
        except Exception as e:
            return f"Erro ao processar {e}"
            
            
        
'''         
if __name__ == '__main__':
    test = SQLParser()
    
    queries = [
        # DEVEM RETORNAR TRUE
        "SELECT * FROM empregados;",
        "SELECT nome, cpf FROM empregados;",
        "SELECT * FROM empregados WHERE salario > 5000.00;",
        "SELECT * FROM empregados WHERE sexo = 'M' AND salario < 3000.00;",
        "SELECT * FROM empregados ORDER BY cpf DESC;",
        "SELECT * FROM empregados ORDER BY salario DESC LIMIT 5;",
        "SELECT COUNT(*) FROM empregados WHERE sexo = 'F';",
        "SELECT nome, SUM(salario) FROM empregados GROUP BY sexo;",
        "SELECT nome, AVG(idade) FROM empregados GROUP BY sexo HAVING AVG(salario) > 5000.00;",
        "INSERT INTO empregados VALUES ('Pedro Santos', '344.262.312-05', 413147, 'M', 13743.62, 27);",
        "UPDATE empregados SET salario = 6554.53 WHERE cpf = 500.993.034-00;",
        "DELETE FROM empregados WHERE cpf = 500.993.034-00;",
        "SELECT * FROM empregados WHERE nome LIKE 'Ana%';",
        
        # DEVEM RETORNAR ERRO
        # TODO: Fazer os erros para cada raise
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print(f"Resultado: {test.parse_sql_query(query)}\n")
'''