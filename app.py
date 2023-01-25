from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def datos():
    return "hola mundo"


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)
