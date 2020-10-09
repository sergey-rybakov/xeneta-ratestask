import datetime

class processor_class:
    def __init__(self,sql_obj):
        self.sql = sql_obj
        self.uploads_ok = 0

    #Left 2 methods with almost same code and SQL request functions to keep
    # capabilities of hypothetical extends and changes in resulting data sets

    def get_prices_data(self,request = {'date_from':'1970-01-01','date_to':'1970-01-01','origin':'','destination':''}):
        """
        Method for task 1 part 1
        Method returs raw data for deliveries' prices
        request: dict = {date_from:(date),date_to:(date),origin:(string),destination:(string)]}
        """

        origin_codes_merge = None
        destination_codes_merge = None

        #parent_slug support for origin and destination, works faster then subquery with several jonis inside main block

        if len(request['origin']) > 5:
            origin_codes_query = ("SELECT code "
                                "FROM ports "
                                "WHERE parent_slug = '"+str(request['origin']+"'"))

            codes = self.sql.query(origin_codes_query,(request['origin']))
            origin_codes_array = []
            for v in codes:
                origin_codes_array.append(v['code'])
            origin_codes_merge = " /*%s*/ IN ('"+"','".join(origin_codes_array)+"') "
            
        if len(request['destination']) > 5:
            destination_codes_query = ("SELECT code "
                                        "FROM ports "
                                        "WHERE parent_slug = '"+str(request['destination']+"'"))
            
            codes = self.sql.query(destination_codes_query)
            destination_codes_array = []
            for v in codes:
                destination_codes_array.append(v['code'])
            destination_codes_merge = " /*%s*/ IN ('"+"','".join(destination_codes_array)+"') "


        query = ("SELECT CAST(ROUND(AVG(prices.price)) as integer) AS average_price, prices.day AS day "
                "FROM prices ")
        if origin_codes_merge is None:
            query += "WHERE prices.orig_code = %s "
        else:
            query += "WHERE prices.orig_code "+origin_codes_merge+" "
        if destination_codes_merge is None:
            query += "AND prices.dest_code = %s "
        else:
            query += "AND prices.dest_code "+destination_codes_merge+" "
        query += ("AND prices.day >= %s "
                "AND prices.day <= %s "
                "GROUP BY prices.day "
                "ORDER BY prices.day asc")
        result = self.sql.query(query,(request['origin'],request['destination'],request['date_from'],request['date_to']))
        n = 0
        for record in result:
            result[n]['day'] =  record['day'].strftime('%Y-%m-%d')
            n += 1
        return result

    def get_prices_data_nulls(self,request = {'date_from':'1970-01-01','date_to':'1970-01-01','origin':'','destination':''}):
        """
        Method for task 1 part 2
        Method returs raw data for deliveries' prices. AVG price for days with less then 3 records displayed as NULL.
        request: JSON = [date_from:(date),date_to:(date),origin:(string),destination:(string)] 
        """
        origin_codes_merge = None
        destination_codes_merge = None

        #parent_slug support for origin and destination, works faster then subquery with several jonis inside main block

        if len(request['origin']) > 5:
            origin_codes_query = ("SELECT code "
                                "FROM ports "
                                "WHERE parent_slug = '"+str(request['origin']+"'"))

            codes = self.sql.query(origin_codes_query,(request['origin']))
            origin_codes_array = []
            for v in codes:
                origin_codes_array.append(v['code'])
            origin_codes_merge = " /*%s*/ IN ('"+"','".join(origin_codes_array)+"') "
            
        if len(request['destination']) > 5:
            destination_codes_query = ("SELECT code "
                                        "FROM ports "
                                        "WHERE parent_slug = '"+str(request['destination']+"'"))
            
            codes = self.sql.query(destination_codes_query)
            destination_codes_array = []
            for v in codes:
                destination_codes_array.append(v['code'])
            destination_codes_merge = " /*%s*/ IN ('"+"','".join(destination_codes_array)+"') "

        query = ("SELECT CASE WHEN COUNT(prices.price) >= 3 THEN CAST(ROUND(AVG(prices.price)) as integer) ELSE NULL END AS average_price, prices.day "
                "FROM prices ")
        if origin_codes_merge is None:
            query += "WHERE prices.orig_code = %s "
        else:
            query += "WHERE prices.orig_code "+origin_codes_merge+" "
        if destination_codes_merge is None:
            query += "AND prices.dest_code = %s "
        else:
            query += "AND prices.dest_code "+destination_codes_merge+" "
        query += ("AND prices.day >= %s "
                "AND prices.day <= %s "
                "GROUP BY prices.day "
                "ORDER BY prices.day asc")
       
        n = 0
        result = self.sql.query(query,(request['origin'],request['destination'],request['date_from'],request['date_to']))
        for record in result:
            result[n]['day'] =  record['day'].strftime('%Y-%m-%d')
            n += 1
        return result
    
    def upload_new_records(self,dataset):
        """
        Method for task 2 part 1 and 2
        Method returs raw data for deliveries' prices
        request: dict = [date_from:(date),date_to:(date),orig_code:(string),dest_code:(string)] 
        """
        keys = dataset.keys()
        values = dataset.values()
        return self.sql.insert('prices',keys,values)
    def check_date_format(self,date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except:
            return False