from flask import Flask, request, jsonify,render_template, Response
import json
import aiida

app = Flask(__name__)



### process options
with open('config.json') as f:
    calculation_options = json.load(f)
input_content = {}


@app.route('/ginestra/', methods=['GET','HEAD','POST','PUT','DELETE'])
def get_ginestra_request():
### for now, only route available
### access the request of a json file

### back_to_server contains the json response to the inquiry
### initializing minimal json response
    back_to_server = {'input' : '',
                      'message' : ''
                     }
    http_status = 200 # success code
### some basic checks
### accepting only POST
    if (request.method != 'POST'):
        back_to_server['message'] = 'Expecting a POST HTML method'
        http_status = 405 # method not allowed
### accepting only JSON
    if (not request.is_json):
        back_to_server['message'] = 'Expecting json'
        http_status = 400 # bad request
    else:
        input_content = request.get_json()
        back_to_server['input'] = input_content
### needs to contain a calculation tag, and needs to be in the allowed calculations
        if input_content.get("calculation") == None:
            back_to_server['message'] = 'No "calculation" tag in json"'
            http_status = 400 # bad request
        else:
            if (not input_content['calculation'] in (calculation_options['calculation'])):
                back_to_server['message'] = 'Calculation type {} not supported. Accepted types: {}'.format(input_content['calculation'],", ".join(calculation_options['calculation']))
                http_status = 400 # bad request

### end checks - processing input

    response = jsonify(back_to_server)
    response.status_code = http_status



    return response




if __name__ == '__main__':
    app.run(host= '127.0.0.1',port='2345',debug=True)
