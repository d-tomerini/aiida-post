from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/ginestra/', methods=['GET', 'POST'])
def add_message():
    content = request.json
    print "xxx", content
    return jsonify({"uuid":35},content)

if __name__ == '__main__':
    app.run(host= '127.0.0.1',port='2345',debug=True)
