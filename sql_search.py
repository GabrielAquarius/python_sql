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
            '!=': lambda a, b: a != b,
        }

        self.no_columns = ['count', 'avg', 'sum']
        
    def consult(self, query):
        if not query:
            raise ValueError('Query Vazia')

        # TODO: Implementar LIKE
        
        tokens = re.findall(r"'[^']*'|[a-zA-Z0-9À-ÿ.-]+|[>=<!*%_]+", query)
        tokens = [t.lower() if not (t.startswith("'") and t.endswith("'")) else t.strip("'") for t in tokens]
        
        result = self.parse_sql_query(tokens, query)
        
        if result == 'select':
            idx_from = tokens.index('from')

            agg_select = {}
            if 'avg' in tokens[1:idx_from]:
                idx_avg = tokens.index('avg')
                agg_select['avg'] = tokens[idx_avg+1]
                
            if 'count' in tokens[1:idx_from]:
                idx_count = tokens.index('count')
                col_count = tokens[idx_count+1]
                agg_select['count'] = None if col_count == '*' else col_count

            if 'sum' in tokens[1:idx_from]:
                idx_sum = tokens.index('sum')
                agg_select['sum'] = tokens[idx_sum+1]
            
            columns_to_select = [col for col in tokens[1:idx_from] if col not in self.no_columns and col not in agg_select.values()]
            if '*' in columns_to_select:
                columns_to_select = self.column_names
                
            working_data = self.data
            if 'where' in tokens:
                idx = tokens.index('where') + 1 
                mask = None
                current_logic = None

                while idx < len(tokens) and tokens[idx] not in ['order', 'group', 'limit']:
                    col_condition = tokens[idx]
                    operator = tokens[idx+1]
                    value = tokens[idx+2]
                    
                    column_type = self.data.dtype[col_condition]
                    typed_value = np.array([value]).astype(column_type)[0]

                    condition_mask = self.operators[operator](working_data[col_condition], typed_value)
                    
                    if mask is None:
                        mask = condition_mask
                    else:
                        if current_logic == 'and':
                            mask = mask & condition_mask
                        elif current_logic == 'or':
                            mask = mask | condition_mask
                    
                    idx += 3
                    if idx < len(tokens) and tokens[idx] in ['and', 'or']:
                        current_logic = tokens[idx]
                        idx += 1
                    else:
                        break
                
                working_data = working_data[mask]
                
            if 'group' in tokens:
                init_idx = tokens.index('group')
                col_to_group = tokens[init_idx + 2]
                
                unique_vals = np.unique(working_data[col_to_group])
                grouped_results = []
                
                for val in unique_vals:
                    group_mask = working_data[col_to_group] == val
                    group_data = working_data[group_mask]
                    
                    include_group = True
                
                    if 'having' in tokens:
                        idx_having = tokens.index('having')
                        hav_func = tokens[idx_having+1]
                        hav_col = tokens[idx_having+2]
                        hav_op = tokens[idx_having+3]
                        hav_val = tokens[idx_having+4]
                        hav_agg_val = 0
                        
                        if hav_func == 'count':
                            hav_agg_val = len(group_data)
                        elif hav_func == 'sum':
                            hav_agg_val = np.sum(group_data[hav_col])
                        elif hav_func == 'avg':
                            hav_agg_val = np.mean(group_data[hav_col].astype(float))
                        
                        hav_val = type(hav_agg_val)(tokens[idx_having+4])
                        
                        include_group = self.operators[hav_op](hav_agg_val, hav_val)
                    
                    if include_group:
                        row_result = {col_to_group: val}
                        
                        if 'count' in agg_select:
                            row_result['count'] = len(group_data)
                        if 'sum' in agg_select:
                            row_result['sum'] = np.sum(group_data[agg_select['sum']])
                        if 'avg' in agg_select:
                            row_result['avg'] = np.mean(group_data[agg_select['avg']].astype(float))
                            
                        grouped_results.append(row_result)
                
                return grouped_results
                
            if agg_select:
                row_result = {}
                if 'count' in agg_select:
                    row_result['count'] = len(working_data)
                if 'sum' in agg_select:
                    row_result['sum'] = np.sum(working_data[agg_select['sum']])
                if 'avg' in agg_select:
                    row_result['avg'] = np.mean(working_data[agg_select['avg']].astype(float))
                    
                return row_result

            if 'order' in tokens: # SELECT cpf, salario FROM empregados ORDER BY salario DESC LIMIT 5;
                init_idx = tokens.index('order') + 1
                col_to_order = tokens[init_idx + 1]
                idx_order = np.argsort(working_data[col_to_order])
                if 'desc' in tokens:
                    idx_order = idx_order[::-1]
                working_data = working_data[idx_order]
                
            if 'limit' in tokens:
                idx_limit = tokens.index('limit')
                limit_value = int(tokens[idx_limit + 1])
                working_data = working_data[:limit_value]
            
            return working_data[columns_to_select]

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

            return self.data
        
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
    query = input('#').strip()
    print(search_for.consult(query))