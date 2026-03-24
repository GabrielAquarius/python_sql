from sql_parser import SQLParser

import re

import numpy as np

class SQLSearch(SQLParser):
    def __init__(self):
        super().__init__()
        
        self.data=self.load_data()
        self.operators = {
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '=': lambda a, b: a == b,
            '!=': lambda a, b: a != b
        }
    
    def consult(self, query):
        # query = input('#').strip()
        if not query:
            return ValueError('Query Vazia')

        tokens = re.findall(r"'[^']'|[a-zA-Z0-9À-ÿ.-]+|[>=<!*]+", query.lower())
        tokens = [t.replace("'","") for t in tokens]
        
        result = self.parse_sql_query(tokens, query)
        
        if result == 'select':
            idx_from = tokens.index('from')
            columns_to_select = tokens[1:idx_from]
            if '*' in columns_to_select:
                columns_to_select = self.column_names
                print(columns_to_select)
            
            if 'where' in tokens:
                idx_where = tokens.index('where')
                col_condition = tokens[idx_where + 1]
                operator = tokens[idx_where + 2]
                value = tokens[idx_where + 3]

                column_type = self.data.dtype[col_condition]
                typed_value = np.array([value]).astype(column_type)[0]

                mask = self.operators[operator](self.data[col_condition], typed_value)
                return self.data[mask]
                
            if 'order' in tokens: # SELECT cpf, salario FROM empregados ORDER BY salario DESC LIMIT 5;
                init_idx = tokens.index('by')
                col_to_order = tokens[init_idx + 1]
                idx_order = np.argsort(self.data[col_to_order])
                if 'desc' in tokens:
                    idx_desc = idx_order[::-1]
                    if 'limit' in tokens:
                        top_idx = idx_desc[:int(tokens[init_idx + 4])]
                        return self.data[top_idx][columns_to_select]
                    else:
                        return self.data[idx_desc][columns_to_select]
                else:
                    return self.data[idx_order][columns_to_select]
            
            return [self.data[columns_to_select], columns_to_select]
        
        elif result == 'insert':
            idx_value = tokens.index('values')
            values = [v.replace("'", "") for v in tokens[idx_value+1:]]
            nome = values[0].title()
            cpf = values[1]
            matricula = values[2]
            sexo = values[3].upper()
            salario = values[4]
            idade = values[5]
            
            new_row = (nome, cpf, matricula, sexo, salario, idade)
            
            self.data = np.append(self.data, np.array([new_row], dtype=self.data_type))
            
            return self.data
        
        elif result == 'update': # UPDATE empregados SET salario = 6554.53 WHERE cpf = 500.993.034-00;
            idx_set = tokens.index('set')
            idx_where = tokens.index('where')

            col_to_update = tokens[idx_set + 1]
            new_value = tokens[idx_set + 3]

            col_condition = tokens[idx_where + 1]
            operator = tokens[idx_where + 2]
            cond_value = tokens[idx_where + 3]

            type_update = self.data.dtype[col_to_update]
            typed_new_value = np.array([new_value]).astype(type_update)[0]
            
            type_cond = self.data.dtype[col_condition]
            typed_cond_value = np.array([cond_value]).astype(type_cond)[0]
            
            mask = self.operators[operator](self.data[col_condition], typed_cond_value)
            
            self.data[col_to_update][mask] = typed_new_value
            
        
        elif result == 'delete': # DELETE FROM empregados WHERE cpf = 500.993.034-00;
            idx_where = tokens.index('where')
            col_condition = tokens[idx_where + 1]
            operator = tokens[idx_where + 2]
            where_value = tokens[idx_where + 3]

            column_type = self.data.dtype[col_condition]
            typed_where_value = np.array([where_value]).astype(column_type)[0]

            mask = self.operators[operator](self.data[col_condition], typed_where_value)

            self.data = self.data[~mask]

            return self.data
            
        else:
            print(result)



if __name__ == '__main__':
    search_for = SQLSearch()
    query = input('').strip()
    print(search_for.consult(query))