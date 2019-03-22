from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


@app.route('/ginestra/', methods=['GET', 'POST'])
def add_message():
    content = request.json
    print "xxx", content
    return jsonify(content)
	
@app.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(username)


if __name__ == '__main__':
    app.run(host= '127.0.0.1',port='2345',debug=True)
