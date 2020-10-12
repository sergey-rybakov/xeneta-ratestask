from .ext.sql_class import sql_class
from .ext.processor_class import processor_class
from .ext.currency_class import currency_class

sql = sql_class({'host':'host.docker.internal','dbname':'postgres','user':'postgres','password':'ratestask','port':5432})
sql.debug = True
processor = processor_class(sql)
currency = currency_class('2bfc8da9739d4a11b8e2e8cba02e8dfe')