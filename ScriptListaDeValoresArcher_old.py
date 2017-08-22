#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import os
import optparse

encabezado_archivo_entrada = '"Aplicación.Nombre";"GUID";"Valor/Tipo;Ponderación valor"\n'
encabezado_archivo_comparacion = '"Diferencia";"Aplicación.Nombre del campo";"Número de valores"\n'


def pasar_a_linea_csv(tupla):
    linea = ''
    for item in tupla:
        linea += item + ';'
    linea = linea[:-1]
    return linea

def imprimir_en_archivo(tupla, header, valores, archivo_salida):
    linea = pasar_a_linea_csv(tupla)
    imprimir_en_csv(header, archivo_salida)
    imprimir_en_csv(linea, archivo_salida)
    imprimir_en_csv(valores, archivo_salida)

def imprimir_en_csv(linea, archivo):
    archivo.write('%s' % linea)
    archivo.write('\n')


def unir_archivos(parametros_de_entrada, archivo_salida):
    print '---------------------------------------------------------'
    cortar_linea = re.compile(r'</xs:complexType><xs:simpleType')
    cortar_linea_2 = re.compile(r'</xs:complexType><xs:complexType')
    lista_archivos = []
    if os.path.isdir(parametros_de_entrada):
        for carpeta, _, archivos in os.walk(parametros_de_entrada):
            for archivo in archivos:
                if 'archerschema' in os.path.basename(archivo):
                    lista_archivos.append(os.path.join(carpeta, archivo))
    else:
        if os.path.isfile(parametros_de_entrada):
            lista_archivos.append(parametros_de_entrada)
    lista_archivos.sort()
    for archivo in lista_archivos:
        with open(archivo, 'r') as infile:
            for line in infile:
                if cortar_linea.search(line):
                    line = re.sub('</xs:complexType><xs:simpleType',
                                  r'</xs:complexType>\n<xs:simpleType',
                                  line)
                if cortar_linea_2.search(line):
                    line = re.sub('</xs:complexType><xs:complexType',
                                  r'</xs:complexType>\n<xs:complexType',
                                  line)
                archivo_salida.write(line)
            print archivo + ' unido correctamente.'
    print '\nArchivo unido' + ' ---> ' + archivo_salida.name
    print '---------------------------------------------------------'

def main():
    ayuda = """
                Script para comparar las listas de valores a la hora de realizar una migracion en RSA Archer.
                La comparacion se hara revisando los elementos mencionados del primer archivo XSD o carpeta con ellos pasado por parametro hacia el segundo archivo XSD o carpeta con ellos y se mostraran sus diferencias.
                Se creara un archivo con el resumen de la comparacion de lista de valores llamado Comparacion_ListasdeValores.csv con el resultado del analisis.
                Por ultimo, se informara un resumen de la ejecucion por pantalla al finalizar.
                """
    parser = optparse.OptionParser(usage=ayuda, version="%prog 1.2")
    #parser.add_option('-c',
    #                  '--compare',
    #                   dest='compare',
    #                   help='Compara 2 salidas del script (Archivos de salida \
    #                   de la ejecucion con la opcion "-p").',
    #                   action='store_true')
    # parser.add_option('-m',
    #                   '--merge',
    #                   dest='merge',
    #                   help='Une 2 o mas archivos de entrada XSD.',
    #                   action='store_true')
    # parser.add_option('-p',
    #                   '--parse',
    #                   dest='parse',
    #                   help='Realiza el parseo del XSD de entrada.',
    #                   action='store_true')
    parser.add_option('-i',
                      '--input',
                      dest='input',
                      help='Ingrese la carpeta donde se encuentran los archivos archerschema.xsd \
                            obtenidos antes de realizar la migracion.',
                      action='store_true')
    parser.add_option('-o',
                      '--output',
                      dest='output',
                      help='Ingrese la carpeta donde se encuentran los archivo archerschema.xsd \
                      obtenidos luego de realizar la migracion.',
                      action='store_true')
    (options, args) = parser.parse_args()
    if options.input and options.output:
        nombre_primer_xsd = sys.argv[2] + '_unido_1.out'
        nombre_segundo_xsd = sys.argv[4] + '_unido_2.out'
        nombre_primer_archivo_parseado = sys.argv[2] + '_parseado_1.out'
        nombre_segundo_archivo_parseado = sys.argv[4] + '_parseado_2.out'
        with open(nombre_primer_xsd, 'w+') as primer_archivo_xsd:
            unir_archivos(sys.argv[2], primer_archivo_xsd)
            primer_archivo_xsd.close()
            with open(nombre_segundo_xsd, 'w+') as segundo_archivo_xsd:
                unir_archivos(sys.argv[4], segundo_archivo_xsd)
                segundo_archivo_xsd.close()
                with open(nombre_primer_archivo_parseado, 'w+') as primer_archivo_xsd_datos:
                    primer_archivo_xsd = open(nombre_primer_xsd, 'r')
                    parsear_archivo(primer_archivo_xsd, primer_archivo_xsd_datos)
                    primer_archivo_xsd_datos.close()
                    primer_archivo_xsd.close()
                    with open(nombre_segundo_archivo_parseado, 'w+') as segundo_archivo_xsd_datos:
                        segundo_archivo_xsd = open(nombre_segundo_xsd, 'r')
                        parsear_archivo(segundo_archivo_xsd, segundo_archivo_xsd_datos)
                        segundo_archivo_xsd_datos.close()
                        segundo_archivo_xsd.close()
                        with open('Comparacion_ListasdeValores.csv', 'w+') as archivo_comparacion:
                            primer_archivo_xsd_datos = open(nombre_primer_archivo_parseado, 'r')
                            comparar_archivos(primer_archivo_xsd_datos,
                                              nombre_segundo_archivo_parseado,
                                              archivo_comparacion)
     #   else:
     #       if len(sys.argv) == 3 and options.parse:
     #               archivo_entrada = open(sys.argv[2], 'r')
      #              archivo_salida = open(os.path.basename(sys.argv[2]) + '.out', 'w+')
      #              parsear_archivo(archivo_entrada,archivo_salida)
    else:
        if len(sys.argv) == 4 and options.compare:
            with open('Comparacion.csv', 'w+') as archivo_comparacion:
                archivo_entrada_paseado = open(sys.argv[2], 'r')
                #f2 = open(sys.argv[3], 'r')
                comparar_archivos(archivo_entrada_paseado, sys.argv[3], archivo_comparacion)
        #else:
         #   print 'Modos de uso:\n' \
          #      '1. Ingrese la opcion "-p" y la ruta del archivo de Archer para parsearlo.\
          #      Salida esperada: Archivo.out\n' \
           #     '2. Ingrese la opcion "-m" y 2 o mas rutas de archivos de Archer\
           #     para fusionarlos o 3 o más rutas.\
           #     Salida esperada: Archivo.out\n' \
            #    '3. Ingrese la opcion "-c" y 2 rutas de archivos procesados por este script \
            #    para comparar diferencias.\
            #    Salida esperada: Comparacion.csv'


def comparar_archivos(datos_primer_archivo, ruta_datos_segundo_archivo, outfile):
    valores = []
    valores_de_la_lista_1 = []
    valores_de_la_lista_2 = []
    campo1, campo2 = [], []
    campos_iguales, campos_distintos, campos_sin_encontrar = 0, 0, 0
    outfile.write(encabezado_archivo_comparacion)
    for line1 in datos_primer_archivo:
        if line1 == encabezado_archivo_entrada:
            campo1, valores = [], []
        else:
            if line1[-12:-2] == 'ValuesList':
                nombre_campo, guid_campo, _ = line1.split(";")
                campo1.append(nombre_campo)
                campo1.append(guid_campo)
            else:
                if line1 != '\n':#and line1.split(';') >= 3:
                    valores_de_la_lista_1 = line1.split(';')
                    valores.append(valores_de_la_lista_1)
                else:
                    if line1 == '\n':
                        campo1.append(valores)
                        with open(ruta_datos_segundo_archivo, 'r') as datos_segundo_archivo:
                            encontrado = False
                            line2 = datos_segundo_archivo.readline()
                            while encontrado is False and line2:
                                if line2 == encabezado_archivo_entrada:
                                    campo2, valores = [], []
                                else:
                                    if line2[-12:-2] == 'ValuesList':
                                        nombre_campo, guid_campo, _ = line2.split(";")
                                        campo2.append(nombre_campo)
                                        campo2.append(guid_campo)
                                    else:
                                        if line2 != '\n':# and line2.split(';') >= 3:
                                            valores_de_la_lista_2 = line2.split(';')
                                            valores.append(valores_de_la_lista_2)
                                        else:
                                            if line2 == '\n':
                                                campo2.append(valores)
                                                if campo1[1] == campo2[1]:
                                                    if len(campo1[2]) == len(campo2[2]):
                                                        campos_iguales += 1
                                                    else:
                                                        campos_distintos += 1
                                                        outfile.write('"Cambio de valores";' +
                                                                      campo1[0] +
                                                                      ';De ' +
                                                                      str(len(campo1[2])) +
                                                                      ' campos a '
                                                                      + str(len(campo2[2])) +
                                                                      ' campos.;\n')
                                                    encontrado = True
                                line2 = datos_segundo_archivo.readline()
                            if encontrado is False:
                                outfile.write('"No encontrado";' + campo1[0] + '\n')
                                campos_sin_encontrar += 1
    print 'Campos correctos: ', campos_iguales
    print 'Campos incorrectos: ', campos_distintos
    print 'Campos sin encontrar: ', campos_sin_encontrar

def extaer_campo(line):
    cantidad_valores = 0
    campo, valores = [], []
    if line == encabezado_archivo_entrada:
        cantidad_valores = 0
    else:
        if line[-11:-2] == 'ValuesList':
            nombre_campo, guid_campo = line[-14:].split(";")
            campo.append(nombre_campo)
            campo.append(guid_campo)
        else:
            if line.split(';') >= 4:
                cantidad_valores += 1
                nombre_lista, valor, guid, _ = line.split(';')
                valores.append(nombre_lista)
                valores.append(valor)
                valores.append(guid)
            else:
                if line == '':
                    campo.append(valores)
                    campo.append(cantidad_valores)
                    cantidad_valores = 0
                    #print campo
                    return campo
    return None

def parsear_archivo(archivo_entrada, archivo_salida):
    cantidad_campos = 0
    cantidad_valores = 0
    #obtener_nombre_campo = re.compile(r'&lt;Name&gt;(.*?)&lt;/Name&gt')
    obtener_nombre_campos = re.compile(r'</archer:ValuesListValueDefinition>.*?'
                                       r'</xs:simpleType><xs:complexType '
                                       'name=(".*?").*'
                                       #'archer:Id=("[\d]*") '
                                       #'archer:Guid=("[A-Za-z0-9_-]*").*?'
                                       #'archer:Type=("ValuesList")'
                                       r'</xs:sequence></xs:complexType>'
                                      )
    obtener_datos_campos = re.compile(r'<xs:simpleType '
                                      'name=(".*?").*'
                                      #'archer:Id=("[\d]*") '
                                      r'archer:Guid=("[A-Za-z0-9_-]*").*?'
                                      r'archer:Type=("ValuesList")'
                                     )
    obtener_lista_de_valores_con_ponderacion = re.compile(r'.*</archer:ValuesList.*>.*'
                                                          r'c:Name=(".*?").*?'
                                                          r'c:Id=("[A-Za-z0-9_-]*").*?'
                                                          r'value=(".*?").*?archer:'
                                                          r'Value=("\d+\.\d*")?'
                                                          #r' archer:Id=("[\d]*")'
                                                         )
    obtener_lista_de_valores = re.compile(r'.*</archer:ValuesList.*>.*'
                                          r'c:Name=(".*?").*?'
                                          r'c:Id=("[A-Za-z0-9_-]*").*?'
                                          r'value=(".*?")'
                                          #r'archer:Id=("[\d]*") '
                                         )
    #obtener_lineas_validas = re.compile(r'&lt;/[\bCalculationFormula\b|\bValuesList\b].*?"&gt;')
    #obtener_lineas_validas = re.compile(r'.*archer:ValuesListDefinition>.*')

    valores = ''
    datos_campo = ''
    cantidad_lineas = 0
    tupla = []
    campo_nombre = []
    flag_imprimir_en_archivo = False
    print '---------------------------------------------------------'
    print 'Parseando '+ ' ---> ' + archivo_entrada.name
    for line in archivo_entrada:
        cantidad_lineas += 1
        if len(line) < 10000:#and linea_valida is not None: #and linea_valida is not None:
            if cantidad_lineas % 10000 == 0:
                print '.',
            campo = obtener_datos_campos.findall(line)
            if campo:
                #print 'a'
                if flag_imprimir_en_archivo is True:
                    cantidad_campos += 1
                    imprimir_en_archivo(datos_campo[0],
                                        encabezado_archivo_entrada,
                                        valores,
                                        archivo_salida)
                flag_imprimir_en_archivo = True
                datos_campo = campo
                valores = '' # ultimo cambio
            else:
                lista_de_valores = obtener_lista_de_valores_con_ponderacion.findall(line)
                if lista_de_valores:
                    #print 'b'
                    #ultimo_valor_actualizado_fue_campo = False
                    cantidad_valores += 1
                    for tupla in lista_de_valores:
                        valores += pasar_a_linea_csv(tupla) + '\n'
                        #linea = pasar_a_linea_csv(lista)
                        #imprimir_en_csv(linea,archivo_salida)
                else:
                    lista_de_valores = obtener_lista_de_valores.findall(line)
                    if lista_de_valores:
                        #print lista_de_valores
                        #print 'c'
                        cantidad_valores += 1
                        #ultimo_valor_actualizado_fue_campo = False
                        for tupla in lista_de_valores:
                            valores += pasar_a_linea_csv(tupla) + '\n'
                    else:
                        campo_nombre = obtener_nombre_campos.findall(line)
                        if campo_nombre:
                            tupla = [campo_nombre[0], datos_campo[0][1], datos_campo[0][2]]
                            cantidad_campos += 1
                            imprimir_en_archivo(tupla,
                                                '"Aplicacion.Nombre";"GUID";"Valor/Tipo;Ponderación valor"',
                                                valores,
                                                archivo_salida)
                            #valores_campo_anterior = valores
                            valores = ''
                            flag_imprimir_en_archivo = False

    cantidad_campos += 1

    print '\nCampos: ', cantidad_campos
    print 'Valores: ', + cantidad_valores
    print 'Archivo parseado ' + ' ---> ' + archivo_salida.name

if __name__ == "__main__":
    main()
