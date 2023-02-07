from flask import Flask, request, jsonify
import pandas as pd
import mysql.connector

mydb = mysql.connector.connect(
  host="10.14.11.71",
  user="root",
  password="PassworD",
  database="cediSoporte"
)
consulta = mydb.cursor()
app = Flask(__name__)

@app.route('/', methods = ['GET'])
def page():
    return("<H1>pagina web de la api</H1>")


@app.route('/recepcion', methods=['POST'])
def upload():
    files = request.files.getlist('file')
    if files:#si existen archivos
        info = []#Inicializa una lista vacía para guardar la información
        for i in files:#Itera la lista de archivos xls
            df = pd.read_excel(i, header=25)#Crea un dataframe a partir del xls y asigna la fila 25 como encabezado 
            df = df.iloc[:-2]#elimina las ultimas dos lineas del dataframe ya que no son informacion útil
            df['Placa'] = df['Placa'].astype(int)#convierte la columna placa en datos enteros
            descripcion = list(df['Descripción'])#crea una lista con la descripción
            placa = list(df['Placa'])#crea una lista con los numeros de placa
            serie = list(df['Número Serie'])#crea una lista con los numeros de serie
            salida = list(zip(descripcion, placa, serie))#unifica los datos en una lista de tuplas
            info.append(salida)# Agrega los datos del archivo excel a la nueva lista de salida
            accion = str(i.filename)#toma el nombre del archivo 
            equipos = (len(df))#toma la cantidad de equipos
            consulta.execute(f'INSERT INTO Acciones (idAccion, FechaEntrada, FechaSalida, CantidadEquipos, IdEstadoAccion, IdAsignaciones) VALUES (\'{accion}\', NOW(), NULL, {equipos}, 1, 3);')
            mydb.commit()
        return ('todo bien') # Devuelve la lista de dalida con la información util de todos los archivos Excel cargados
    else:
        return jsonify({"error": "No hay archivos para procesar."})# Si no hay archivos para procesar, devuelve un error

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)