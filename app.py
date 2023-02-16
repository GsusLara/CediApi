from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import pandas as pd

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'PassworD'
app.config['MYSQL_DB'] = 'cediSoporte'
app.config['MYSQL_HOST'] = '10.14.11.71'

mysql = MySQL(app)

@app.route('/', methods = ['GET'])
def page():
    return("<H1>pagina web de la api</H1>")

@app.route('/recepcion', methods=['POST'])
def upload():
    #Recibe y analiza si existen archivos
    files = request.files.getlist('file')
    if files:
        consulta = mysql.connection.cursor()
        response = []
        for i in files:#Itera la lista de archivos xls
    #bloque codigo para cargar las datos de la acción en la tabla de la bd
            AccionCompleta = pd.read_excel(i)
            numeroAccion = AccionCompleta.iloc[4, 0].split()[-1]
            consulta.execute(f'SELECT COUNT(*) FROM Acciones WHERE IdAccion = \'{numeroAccion}\'')
            respuestaBd = consulta.fetchone()[0]
            if respuestaBd == 0:
                df = pd.read_excel(i, header=25)#Crea un dataframe a partir del xls y asigna la fila 25 como encabezado 
                df = df.iloc[:-2]#elimina las ultimas dos lineas del dataframe ya que no son informacion útil
                cantidadEquipos = (len(df))#toma la cantidad de equipos
                consulta.execute(f'INSERT INTO Acciones (IdAccion,  CantidadEquipos) VALUES (\'{numeroAccion}\', {cantidadEquipos});')
    #bloque de codigo para cargar los equipos en la tabla de la bd
                df['Placa'] = df['Placa'].astype(int)#convierte la columna placa en datos enteros
                descripcion = list(df['Descripción'])#crea una lista con la descripción
                placa = list(df['Placa'])#crea una lista con los numeros de placa
                serie = list(df['Número Serie'])#crea una lista con los numeros de serie
                equipos = list(zip(descripcion, placa, serie))#unifica los datos en una lista de tuplas
                for computadora in equipos:
                    consulta.execute(f'INSERT INTO Equipos (Placa, Serie, Descripcion, IdAccion) VALUES ({computadora[1]},"{computadora[2]}", "{computadora[0]}","{numeroAccion}");')
                response.append(numeroAccion)
        mysql.connection.commit()
        consulta.close()
        if len(response) != 0:
            response.append("Datos cargados Exitosamente")
            return jsonify(response),200
        else:
            return jsonify({"messaje": "Los datos ya estan en el sistema"}),210
    else:
        return jsonify({"error": "No hay archivos para procesar."}),400

@app.route('/acciones', methods=['GET'])
def infoAcciones():
    consultaAcciones = mysql.connection.cursor()
    consultaAcciones.execute("SELECT * FROM Acciones")
    datos = consultaAcciones.fetchall()
    columnas = [columna[0] for columna in consultaAcciones.description]
    lista_de_diccionarios = [dict(zip(columnas, fila)) for fila in datos]
    consultaAcciones.close()
    return jsonify(lista_de_diccionarios),200

@app.route('/equipos/<path:numeroAccion>', methods=['GET'])
def infoEquipos(numeroAccion):
    consultaEquipos = mysql.connection.cursor()
    consultaEquipos.execute(f"SELECT * FROM Equipos WHERE IdAccion = '{numeroAccion}'")
    columnas = [columna[0] for columna in consultaEquipos.description]
    listaEquipos = [dict(zip(columnas, fila)) for fila in consultaEquipos.fetchall()]
    consultaEquipos.close()
    return jsonify(listaEquipos),200

@app.route('/estadoAccion', methods=['PUT'])
def cambioEstadoAccion():
    data = request.get_json()
    numeroAccion = data['id_accion']
    nuevoEstado = data['id_estado']
    if nuevoEstado >=1 and nuevoEstado <= 5:
        consultaEstadoAccion = mysql.connection.cursor()
        consultaEstadoAccion.execute("UPDATE Acciones SET IdEstadoAccion = %s WHERE IdAccion = %s", (nuevoEstado, numeroAccion))
        mysql.connection.commit()
        consultaEstadoAccion.close()
        return jsonify({"messaje": "se actualizó la acción correctamente"}),200
    else:
        return jsonify({"error": "inesperado"}),400
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)