#!/usr/bin/python
import sys

def es_numero(valor):
    try:
        return float(valor)
    except ValueError:
        return False

def main():
    entrada = open(sys.argv[1], 'r')
    salida = open('Lineas_incorrectas.csv','w+')
    errores = open('Errores.csv','w+')
    errores.write('Fila;Campo;Valor\n')
    lineas_incorrectas, fila, columna = 0 , 0 , 0
    lineas = entrada.readlines()
    header = lineas[0].split(';')
    for linea in lineas:
        fila = fila + 1
        campos = linea.split(';')
        columna = 0
        for campo in campos:
            if '.' in campo:
                campo = campo.replace('.','')
            if ',' in campo:
                campo = campo.replace(',','.')
            if es_numero(campo):
                if '.' in campo:
                    entero, decimal = campo.split('.')
                    if len(decimal) > 6:
                        salida.write(linea)
                        lineas_incorrectas = lineas_incorrectas + 1
                        campo = campo.replace('.',',')
                        errores.write(str(fila) + ';' +
                                      header[columna] + ';' +
                                      campo  + '\n'
                                      )
            columna = columna + 1
    entrada.close()
    salida.close()
    print 'Lineas con mas de 6 decimales: ', str(lineas_incorrectas)
    print 'Verifique el arrchivo Errores_de_precision.csv'


if __name__ == "__main__":
    main()