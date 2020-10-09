from flask import Flask,request, json, jsonify, Response
import datetime
from app import sql
from app import processor
from app import currency

app = Flask(__name__)
app.config['TESTING'] = True
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def index():
    if len(sql.last_error) > 0:
         return jsonify(ok=0,error='Database connection unavaliable'),503
    return "Try these links for GET API:<br/><br/><a href='/rates'>/rates</a><br/><a href='/rates_null?&date_from=2016-01-01&date_to=2016-01-31&origin=CNSHK&destination=NOBVK'>/rates_null</a>"

@app.route('/rates', methods=['GET'])
def rates():
    if len(sql.last_error) > 0:
        return  jsonify(ok=0,error='Database connection unavaliable'),503
    resp = ''
    errors = []
    #check required GET params
    required_params = ['date_from','date_to','origin','destination']
    for param in required_params:
        if request.args.get(param) is None:
            errors.append("GET parameter '"+param+"' is mandatory")
    if len(errors) == 0:
        if False == processor.check_date_format(request.args.get('date_from')):
            errors.append("GET parameter 'date_from' is having an incorrect format. Correct format: YYYY-MM-DD")
        if False == processor.check_date_format(request.args.get('date_to')):
            errors.append("GET parameter 'date_from' is having an incorrect format. Correct format: YYYY-MM-DD")
    if len(errors) > 0:
         resp = jsonify(ok=0,error=errors),400
    else:
        data = processor.get_prices_data({'date_from':request.args.get('date_from'),'date_to':request.args.get('date_to'),'origin':request.args.get('origin'),'destination':request.args.get('destination')})
        if data != False:
            resp = jsonify(ok=1,data=data),200
        else:
            resp = jsonify(ok=1,data=[]),200

    return resp

@app.route('/rates_null', methods=['GET'])
def rates_null():
    if len(sql.last_error) > 0:
        return jsonify(ok=0,error='Database connection unavaliable'),503
    resp = ''
    errors = []

    #check up with required GET params

    required_params = ['date_from','date_to','origin','destination']
    for param in required_params:
        if request.args.get(param) is None:
            errors.append("GET parameter '"+param+"' is mandatory")
    if len(errors) == 0:
        if False == processor.check_date_format(request.args.get('date_from')):
            errors.append("GET parameter 'date_from' is having an incorrect format. Correct format: YYYY-MM-DD")
        if False == processor.check_date_format(request.args.get('date_to')):
            errors.append("GET parameter 'date_from' is having an incorrect format. Correct format: YYYY-MM-DD")
    if len(errors) > 0:
        resp = jsonify(ok=0,error=errors),400
    else:
        data = processor.get_prices_data_nulls({'date_from':request.args.get('date_from'),'date_to':request.args.get('date_to'),'origin':request.args.get('origin'),'destination':request.args.get('destination')})
        if data != False:
            resp = jsonify(ok=1,data=data),200
        else:
            resp = jsonify(ok=1,data=[]),200
    return resp

@app.route('/rates_upload', methods=['POST'])
def rates_upload():
    if len(sql.last_error) > 0:
        return jsonify(ok=0,error='Database connection unavaliable'),503
    js_data = request.json
    if js_data is not None and request.is_json:
        
        total_records = len(js_data)

        if total_records > 0:
            cur_record = 0
            currencies = currency.get_rates()
            required_params = ['date_from','date_to','origin_code','destination_code','price']
            errors = []

            #check up request records' structure

            for record in js_data:
                record = dict(record)
                for param in required_params:
                    if record.get(param) is None:
                        errors.append("Record("+str(cur_record)+"): '"+param+"' is mandatory")
                    if len(errors) == 0:
                        if False == processor.check_date_format(record['date_from']):
                            errors.append("Record("+str(cur_record)+"): Incorrect format 'date_from' field. Correct format: YYYY-MM-DD")
                        if False == processor.check_date_format(record['date_to']):
                            errors.append("Record("+str(cur_record)+"): Incorrect format 'date_from' field. Correct format: YYYY-MM-DD")
                        if len(record['origin_code']) != 5:
                            errors.append("Record("+str(cur_record)+"): Incorrect format of 'origin_code' field. It should have 5 symbols")
                        if len(record['destination_code']) != 5:
                            errors.append("Record("+str(cur_record)+"): Incorrect format if 'destination_code' field. It should have 5 symbols")
            
            for record in js_data:
                if(cur_record < total_records):
                    if len(errors) == 0:

                        #records having currency param

                        if record['currency'] is not None:
                            if currencies[str(record['currency'])] is not None:
                                js_data[cur_record]['price'] = round(float(record['price']) / float(currencies[str(record['currency'])]))
                                del js_data[cur_record]['currency']
                        
                        #record goes into multiply rows

                        d1 = datetime.datetime.strptime(record['date_from'], "%Y-%m-%d")
                        d2 = datetime.datetime.strptime(record['date_to'], "%Y-%m-%d")
                        if abs((d2 - d1).days) > 0:
                            null_day = 0
                            date = datetime.datetime.strptime(record['date_from'], "%Y-%m-%d")
                            while (d2 - d1).days - null_day:
                                date += datetime.timedelta(days=1)
                                js_data.append({'day':date.strftime('%Y-%m-%d'),'price':record['price'], 'orig_code':record['origin_code'], 'dest_code':record['destination_code']})
                                null_day += 1
                        js_data[cur_record]['day'] = record['date_from']
                        js_data[cur_record]['orig_code'] = record['origin_code']
                        js_data[cur_record]['dest_code'] = record['destination_code']
                        del js_data[cur_record]['date_from']
                        del js_data[cur_record]['date_to']
                        del js_data[cur_record]['origin_code']
                        del js_data[cur_record]['destination_code']
                cur_record += 1

            #writing results orders only when no errors
            
            if len(errors) == 0:
                for record in js_data:
                    if True == processor.upload_new_records(record):
                        processor.uploads_ok += 1
                resp = jsonify(ok=1,result='Records uploaded: '+str(len(js_data))+"/"+str(processor.uploads_ok)),200
                return resp  
            else:
                resp = jsonify(ok=0,error=errors),400
        else:
            resp = jsonify(ok=0,error='Recieved Json is empty'),400
    else:
        resp = jsonify(ok=0,error='Request should contain JSON'),400
    return resp
with app.test_client() as c:
    rv = c.post('/rates_upload', json=[
        {'date_from':'2026-05-01', 'date_to':'2026-05-05', 'price':95600, 'currency':'RUB', 'origin_code':'FIKTK', 'destination_code':'NOBGO'},
        {'date_from':'2026-05-06', 'date_to':'2026-05-12', 'price':130600, 'currency':'RUB', 'origin_code':'FIKTK', 'destination_code':'GBIMM'},
        {'date_from':'2026-05-13', 'date_to':'2026-05-16', 'price':110600, 'currency':'RUB', 'origin_code':'GBIMM', 'destination_code':'FIKTK'}
    ])
    json_data = rv.get_json()
    assert jsonify(json_data)

if __name__ == '__main__':
    app.run()