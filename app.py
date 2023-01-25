from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)


@app.route('/recepcion', methods=['POST'])
def upload():
    file = request.files['file'] #se carga el archivo en la variable
    df = pd.read_excel(file)# se convierte en dataframe pro medio de pandas
    data = df.to_dict()#se convierte el df en diccionario
    return jsonify(data)# se responde en formato json


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)
