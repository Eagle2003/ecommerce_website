from flask_mysql_connector import MySQL
from flask import current_app
from datetime import timedelta

mysql = MySQL(current_app)

class Query () :

    def __init__(self, table, dictionary=True, multiple=False) :
        self.TABLE = table
        self.cursor = mysql.connection.cursor(dictionary=dictionary)
        self.QUERY = {
        "BASE" : None,
        "FILTER": [],
        "SORT" : [],
        "GROUP" : None,
        "COLUMNS" :[],
        "INNER JOIN" : [],
        }
        self.lastInsertId = None
        self.RESULT = None
        self.multiple = multiple
        self.found_rows = None
    
    def get(self, columns='*', limit=None, offset=None, distinct=False, found_rows=False) : 
        if not type(columns) == str : 
            for column in columns :
                if type(column) == str : self.QUERY["COLUMNS"] += [f" {self.TABLE}.{column}"]
                elif type(column) == list : self.QUERY["COLUMNS"] += [f" {column[0]} "]
                elif type(column) == tuple : self.QUERY["COLUMNS"] += [f" {self.TABLE}.{column[0]} AS {column[1]} "]
            self.QUERY["BASE"] = f"SELECT {'SQL_CALC_FOUND_ROWS' if found_rows else '' } {'DISTINCT' if distinct else ''} {', '.join(self.QUERY['COLUMNS'])} FROM {self.TABLE} "
        else :
            self.QUERY["BASE"] = f"SELECT {'SQL_CALC_FOUND_ROWS' if found_rows else '' } {'DISTINCT' if distinct else ''} {columns} FROM {self.TABLE} "
        self.QUERY["LIMIT"] = limit
        self.QUERY["OFFSET"] = offset
        self.found_rows = found_rows
        return self
    
    def insert(self, **kwargs) :
        # saanatize the inputs 
        kwargs = {k : self._escape(v) for k,v in kwargs.items() }
        self.QUERY['BASE'] = f"INSERT INTO {self.TABLE} ({', '.join(kwargs)}) VALUES ({ ', '.join(kwargs.values())})"
        self.execute()
        self.lastInsertId = self.cursor.lastrowid
        return self
    
    def insertMany(self, columns, *args : list) :
        self.QUERY['BASE'] = f"INSERT INTO {self.TABLE} ({', '.join(columns)}) VALUES " 
        # add the inputs
        inputs = []
        for row in args :
            print(row)
            row = [self._escape(v) for v in row ]
            inputs.append(f"({ ', '.join(row)})")
        self.QUERY['BASE'] += ", ".join(inputs)       
        self.execute()
        self.lastInsertId = self.cursor.lastrowid
        return self

    def update(self, **kwargs):
        updates = []
        for column, val in kwargs.items(): 
            column = column.split("__")
            value = self._escape(val)
            if len(column) == 1  :
                updates.append(f" {column[0]} =  {value} ")
            elif column[1] == "sub" : 
                updates.append(f" {column[0]} = {column[0]} - {value} ")
            elif column[1] == "add":
                updates.append(f" {column[0]} = {column[0]} + {value} ")
            elif column[1] == "mult" :
                updates.append(f" {column[0]} = {column[0]} * {value} ")
            elif column[1] == "div" :
                updates.append(f" {column[0]} = {column[0]} / {value} ")
            elif column[1] == "exp" : 
                updates.append(f" {column[0]} =  {val} ")



        update_str = f"UPDATE {self.TABLE} SET " + ", ".join(updates)
        self.QUERY['BASE'] = update_str
        return self

    def delete(self):
        self.QUERY['BASE'] = f"DELETE FROM {self.TABLE} "
        return self

    def union(self, *queries, **kwargs):
        queries = map(lambda query : query.fakeExecute(), queries)
        self.QUERY['LIMIT'] = kwargs.get("limit", None)
        self.QUERY['OFFSET'] = kwargs.get("offset", None)
        self.QUERY['BASE'] = " UNION ".join(queries)
        return self
        
    def join (self, joinQuery, condition, distinct=False) : 
        self.QUERY['COLUMNS'] += joinQuery.QUERY['COLUMNS']
        self.QUERY['FILTER'] += joinQuery.QUERY['FILTER']
        self.QUERY['INNER JOIN'] += [(joinQuery.TABLE, condition)]
        join_lst = [f" INNER JOIN {j[0]} ON {j[1]} " for j  in self.QUERY['INNER JOIN'] ]
        self.QUERY["BASE"] = f"SELECT  {'SQL_CALC_FOUND_ROWS' if self.found_rows else '' } {'DISTINCT' if distinct else ''} {', '.join(self.QUERY['COLUMNS'])} FROM {self.TABLE}  {''.join(join_lst)}"
        joinQuery.cursor.close()
        return self   

    def filter(self, **kwargs):
        filters = []
        
        for field, val in kwargs.items() : 
            value = self._escape(val)
            field = field.split("__")
            column = f"{self.TABLE}.{field[0]}"
            if len(field)==1 :
                filters.append(f" {column} = {value} ")
            elif field[-1] == 'ltHour':
                filters.append(f" {column} >  (NOW() - INTERVAL {val} hour)")
            elif field[-1] == "gtHour" :
                filters.append(f" {column} <  (NOW() - INTERVAL {val} hour) ")
            elif field[-1] == 'ltTimer' and type(value) == timedelta :
                filters.append(f" {column} >  (NOW() - INTERVAL {val.total_seconds()} seconds)")
            elif field[-1] == "gtTime" and type(value) == timedelta  :
                filters.append(f" {column} <  (NOW() - INTERVAL {val.total_seconds()} seconds) ")
            elif field[-1] == "gt" : 
                filters.append(f" {column} > {value} ")
            elif field[-1] == 'lt':
                filters.append(f" {column} < {value} ")
            elif field[-1] == 'gte':
                filters.append(f" {column} >= {value} ")
            elif field[-1] == 'lte':
                filters.append(f" {column} <= {value} ")
            elif field[-1] == 'lt':
                filters.append(f" {column} != {value} ")
            elif field[-1] == 'in':
                filters.append(f" {column} IN {value} ")
            elif field[-1] == 'not_in':
                filters.append(f"NOT {column} IN {value} ")
            elif field[-1] == 'like':
                filters.append(f" {column} LIKE {value} ")
  

        filter_str = " || ".join(filters)
        self.QUERY['FILTER'].append(filter_str) 
        
        return self
    
    def searchFor(self,columns, key) :
        key = self._escape(key)
        columns = ", ".join(columns)
        self.QUERY['FILTER'].append(f" MATCH ({columns}) AGAINST ({key})")
        return self
    
    def group(self, column) :
        self.QUERY['GROUP'] = self._escape(column)
        return self

    def sort(self, column, order='DESC') :
        self.QUERY['SORT'].append(f" {self.TABLE}.{column} {order}")
        return self
    
    #Fetch methods
    def fetchall(self, flatten=False, **kwargs) : 
        self.execute()
        self.RESULT = self.cursor.fetchall()
        if self.found_rows : self.found_rows = self._found_rows()
        if not self.multiple : self.cursor.close()
        self.RESULT = self._load(self.RESULT, **kwargs)
        if flatten : self.RESULT = sum(self.RESULT, ()) 
        return self.RESULT 

    def fetchone(self, flatten=False, **kwargs):
        self.execute()
        self.RESULT = self.cursor.fetchone()
        if self.RESULT : self.RESULT = self._load([self.RESULT], **kwargs)[0]
        if not self.multiple : self.cursor.close()
        if flatten : self.RESULT = sum(self.RESULT, []) 
        return self.RESULT

     #Strings together the SQL stament
    
    def fetchList(self, **kwargs):
        self.execute()
        self.RESULT = self.cursor.fetchall()
        self.RESULT = [ v[0]]
        if not self.multiple : self.cursor.close()
        self.RESULT = self._load(self.RESULT, **kwargs)
        return self.RESULT 

    def getInsertID(self) : 
       return self.cursor.insert_id()

    #Get all the available rows
    def _found_rows(self):
        self.execute("SELECT found_rows() as count")
        return self.cursor.fetchone()['count']

    #Commits all the transactions
    def commit(*_) :
        mysql.connection.commit()

    def _compile(self):
        if not self.QUERY['BASE'] : raise Exception("Invalid Query base stament has been initlaized")
        #Construct the base of the query
        q = self.QUERY['BASE'] 
        #Add he filters
        if len(self.QUERY['FILTER']) : q += " WHERE "+" && ".join(self.QUERY['FILTER'])
        #GroupBy if required
        if self.QUERY['GROUP'] : q += f"GROUP BY {self.QUERY['GROUP']} " 
        #ORDER by 
        if len(self.QUERY['SORT'])  : q += "ORDER BY " + ", ".join(self.QUERY["SORT"])
        #LIMIT And OFFSET
        if self.QUERY.get('LIMIT', None) : q += f" LIMIT {self.QUERY['LIMIT']} "
        #offset
        if self.QUERY.get('OFFSET', None) : q += f"OFFSET {self.QUERY['OFFSET']}"
        return q 

    #Escapes any unwated caharcters
    def _escape(self, value) : 
        if type(value) == str :
            value = self.cursor._connection.converter.escape(value)
            return f'"{value}"'
        elif type(value) == bool :
            return "true" if value else "false"
        elif type(value) == list or type(value) == tuple :
            value = tuple(map(self._escape, value))
            return  f"( {', '.join(value)} )"
        else : 
            value = self.cursor._connection.converter.escape(value)
            return f"{value}"
    #Loads the data my applying a function to it
    def _load(self, data, **kwargs) : 
        for row in data  :
            for key, loader in kwargs.items():
                row[key] = loader(row[key])
        return data
    


    def fakeExecute(self):
        self.cursor.close()
        return self._compile()

    #The execution with rollback
    def execute(self, q=None) :
        q = q if  q else self._compile() 
        current_app.logger.info("Query : "+q)
        try : 
            self.cursor.execute(q)
            return self
        except Exception as e : 
            mysql.connection.rollback()
            raise e
    
    

    



            



        

    

        


    


        