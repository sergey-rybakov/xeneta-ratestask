import psycopg2, psycopg2.extras

class sql_class:
    def __init__(self,sql_auth = {'host':'localhost','dbname':'','user':'','password':'','port':''}):
        self.debug = False
        self.last_error = {}
        self.last_query = ''
        try:
            self.instance = psycopg2.connect("dbname='"+sql_auth['dbname']+"' user='"+sql_auth['user']+"' host='"+sql_auth['host']+"' password='"+sql_auth['password']+"' port='"+str(sql_auth['port'])+"'")
            if sql_auth['dbname'] != "":
                c = self.instance.cursor()
                c.execute("SET search_path TO public,"+sql_auth['dbname'])
                c.close()
        except Exception as error:
            self.last_error['error_text'] = 'Error connecting to the database at '+sql_auth['host']+':'+sql_auth['dbname']
            self.last_error['connection_error'] = error
            print(error)

    def query(self,query,values = None):
        self.last_query = query
        try:
            c = self.instance.cursor()
            if values is None:
                c.execute(query)
            else:
                c.execute(query,values)
            res = c.fetchall()
            col_names = []
            result = []
            for col in c.description:
                col_names.append(col[0])
            for row in res:
                i = 0
                row_tmp = {}
                for cn in col_names:
                    row_tmp[cn] = row[i]
                    i += 1
                result.append(row_tmp)
            return result
        except Exception as e:
            if self.debug == True:
                print('SQL request error:')
                self.last_error['query_error'] = format(e)
                print(query,self.last_error)
            return False
    
    def insert(self,table,keys,values):
        replaces = []
        keys = list(keys)
        values = list(values)
        while len(replaces) < len(values):
             replaces.append('%s')
        query = "INSERT INTO "+table+" ("+",".join(keys)+") VALUES ("+", ".join(replaces)+")"
        self.last_query = query
        try:
            c = self.instance.cursor()
            c.execute(query,values)
            self.instance.commit()
            if c.rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            if self.debug == True:
                print('SQL request error:')
                self.last_error['query_error'] = format(e)
                print(query,self.last_error)
            return False