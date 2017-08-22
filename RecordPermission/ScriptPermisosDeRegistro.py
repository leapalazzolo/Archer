#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import codecs
import xml.etree.ElementTree as ET
import sys
import os

class XML(object):
    def __init__(self):
        self.lista_permisos_heredados = {}
        self.lista_permisos_automaticos = {}
        self.lista_permisos_manuales = {}
        self.archivo = None

    def parsear(self, archivo_entrada):
        self.archivo = archivo_entrada
        tree = ET.parse(archivo_entrada)
        root = tree.getroot()
        field_guid, permiso_manual, permiso_heredado, permiso_automatico, regla, nombre = None, None, None, None, None, None
        flag_permiso_manual, flag_permiso_automatico, flag_regla_permiso_manual = None, None, None
        filter_type, id_condicion = None, None
        lista_condiciones_manuales, lista_condiciones_automaticas = [], []
        namespace = '{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}'
        for nodos in root.iter():
            if 'AutomaticOptionRule' in nodos.tag:
                flag_permiso_automatico = True
                flag_regla_permiso_manual = False
                flag_permiso_manual = False
            else:
                if 'StateBaseOptionRule' in nodos.tag:
                    flag_permiso_automatico = False
                    flag_regla_permiso_manual = True
                    flag_permiso_manual = False
                else:
                    if 'ManualSelectedUserGroup' in nodos.tag:
                        flag_permiso_automatico = False
                        flag_regla_permiso_manual = False
                        flag_permiso_manual = True

            
            if nodos.get('fieldGuid') is not None:
                field_guid = nodos.get('fieldGuid')
            registro_heredado = nodos.get('InheritedFieldId')
            
            alias = nodos.find(namespace + 'Alias')
            guid = nodos.find(namespace + 'GUID')
            id_grupo = nodos.find(namespace + 'Id')
            if nodos.find(namespace + 'Name') is not None:
                nombre = nodos.find(namespace + 'Name')
            puede_eliminar = nodos.find(namespace + 'CanDelete')        #Regla
            puede_actualizar = nodos.find(namespace + 'CanUpdate')      #Regla
            puede_leer = nodos.find(namespace + 'CanRead')              #Regla
            filter_id = nodos.find(namespace + 'FilterId')
            mostrar_usuarios = nodos.find(namespace + 'DisplayUsers')
            es_cascada = nodos.find(namespace + 'IsCascade')
            es_default = nodos.find(namespace + 'IsDefault')
            creador_puede_leer = nodos.find(namespace + 'RecordCreatorRead')
            creador_puede_actualizar = nodos.find(namespace + 'RecordCreatorUpdate')
            creador_puede_eliminar = nodos.find(namespace + 'RecordCreatorDelete')
            if nodos.find(namespace + 'FilterType') is not None:
                filter_type = nodos.find(namespace + 'FilterType')
            if nodos.find(namespace + 'Id') is not None:
                id_condicion = nodos.find(namespace + 'Id')

            # Permisos Heredados
            if field_guid is not None and registro_heredado is not None:
                permiso_heredado = PermisoRegistroHeredado(field_guid)
                self.lista_permisos_heredados[field_guid] = permiso_heredado
                field_guid = None
            if registro_heredado is not None:
                permiso_heredado.agregar_permiso_heredado(registro_heredado)
            # Fin Permisos Heredados
            
            # Regla Manual
            if flag_regla_permiso_manual:
                # if 'FilterCriteria' in nodos.tag:
                #    if  nodos.find(namespace + 'Id') is not None:
                #        id_filter =  nodos.find(namespace + 'Id')
                if filter_type is not None and id_condicion is not None:
                    condicion = Condicion(id_condicion.text, filter_type.text)
                    # condicion.imprimir()
                    lista_condiciones_manuales.append(condicion)
                if field_guid is not None:
                    permiso_manual = PermisoRegistroManual(field_guid)
                    permiso_manual.imprmir()
                    self.lista_permisos_manuales[field_guid] = permiso_manual
                    field_guid = None
                if alias is not None and guid is not None and id_grupo is not None and puede_leer is not None and puede_actualizar is not None and puede_eliminar is not None:
                    regla = Regla(guid.text, nombre.text, alias.text, puede_leer.text, puede_actualizar.text, puede_eliminar.text)
                    # regla.imprimir()
                    while lista_condiciones_manuales:
                        condicion_manual = lista_condiciones_manuales.pop(0)
                        regla.agregar_condicion(condicion_manual)
                    permiso_manual.agregar_regla(regla)
            else:
                if flag_permiso_manual:
                    if puede_actualizar is not None and puede_eliminar is not None and mostrar_usuarios is not None and es_cascada is not None and es_default is not None:
                            grupo = Grupo(id_grupo.text,
                                        'Grupo/User', # No se puede determinar.
                                        puede_actualizar.text,
                                        puede_eliminar.text,
                                        mostrar_usuarios.text,
                                        es_cascada.text,
                                        es_default)
                            if field_guid in self.lista_permisos_manuales:
                                permiso_manual = self.lista_permisos_manuales[field_guid]
                            else:
                                permiso_manual = PermisoRegistroManual(field_guid)
                                self.lista_permisos_manuales[field_guid] = permiso_manual
                            permiso_manual.agregar_grupo(grupo)


class PermisoRegistro(object):
    def __init__(self, field_guid):
        self.field_guid = field_guid
        self.lista_grupos = []          # Ver si va -por herencia a Hered-
        self.lista_reglas = []

    def agregar_grupo(self, id_grupo):  # Ver si va -por herencia a Hered-
        self.lista_grupos.append(id_grupo) # Ver si va -por herencia a Hered-

    def agregar_regla(self, condicion):
        self.lista_reglas.append(condicion)


class PermisoRegistroHeredado(PermisoRegistro, object):
    def __init__(self, field_guid):
        PermisoRegistro.__init__(self, field_guid)
        self.lista_permisos_heredados = []

    def agregar_permiso_heredado(self, inherited_field_id):
        self.lista_permisos_heredados.append(inherited_field_id)
    
    def __str__(self):
        return 'Permiso Heredado \n' \
               '---------------- \n' \
               'GUID:{0} \n' \
               'Permisos: {1}\n'.format(self.field_guid, self.lista_permisos_heredados)

class PermisoRegistroAutomatico(PermisoRegistro, object):
    def __init__(self,
                 field_guid,
                 alias,
                 nombre,
                 guid,
                 filter_id,
                 creador_puede_eliminar,
                 creador_puede_leer,
                 creador_puede_actualizar
                ):
        PermisoRegistro.__init__(self, field_guid)
        self.alias = alias
        self.nombre = nombre
        self.guid = guid
        self.filter_id = filter_id
        self.creador_puede_eliminar = creador_puede_eliminar
        self.creador_puede_leer = creador_puede_leer
        self.creador_puede_actualizar = creador_puede_actualizar


    def imprimir(self): # Ver
        texto = 'Permiso Automatico:\n' + self.guid + '\n-------------------\n'
        for grupo in self.lista_grupos:
            texto += str(grupo) + '\n'
        texto += '\n ------------- \n'
        for regla in self.lista_reglas:
            texto += str(regla) + '\n'
        print texto

class PermisoRegistroManual(PermisoRegistro, object):
    def __init__(self,
                 field_guid):
        PermisoRegistro.__init__(self, field_guid)
        self.field_guid = field_guid
        self.id_ = None

    def imprmir(self): # Ver
        print '\nPermiso Manual:\n' + self.field_guid + '\n-------------------\n'
        for grupo in self.lista_grupos:
            grupo.imprimir()
        print '\n ------------- \n'
        for regla in self.lista_reglas:
            regla.imprimir()

    def agregar_id(self,
                   id_):
        self.id_ = id_


class Regla(object):
    def __init__(self, guid, nombre, alias, puede_leer, puede_actualizar, puede_eliminar):
        self.lista_condiciones = [] # Lista de filter_types
        self.lista_grupos = []
        self.guid = guid
        self.nombre = nombre
        self.alias = alias
        self.puede_leer = puede_leer
        self.puede_actualizar = puede_actualizar
        self.puede_eliminar = puede_eliminar

    def agregar_grupo(self, grupo):
        self.lista_grupos.append(grupo)

    def agregar_condicion(self, condicion):
        self.lista_condiciones.append(condicion)

    def completar(self, guid, nombre, alias):
        self.guid = guid
        self.nombre = nombre
        self.alias = alias

    def imprimir(self):
        print 'Regla: ' + self.guid
        for condicion in self.lista_condiciones:
            condicion.imprimir()
        for grupo in self.lista_grupos:
            grupo.imprimir()



class Grupo(object):
    def __init__(self,
                 id_,
                 tipo,
                 puede_eliminar,
                 puede_actualizar,
                 puede_leer=None,
                 mostrar_usuarios=None,
                 es_cascada=None,
                 es_default=None):
        self.id_ = id_
        self.tipo = tipo
        self.puede_leer = puede_leer
        self.puede_actualizar = puede_actualizar
        self.puede_eliminar = puede_eliminar
        self.mostrar_usuarios = mostrar_usuarios
        self.es_cascada = es_cascada
        self.es_default = es_default

    def imprimir(self):
        print 'Grupo -> ID {0}: {1},{2},{3}\n'.format(self.id_, self.puede_leer, self.puede_actualizar, self.puede_eliminar)


class Condicion(object):
    def __init__(self, id_, filter_type):
        self.filter_type = filter_type
        self.id_ = id_

    def imprimir(self):
        print 'Condicion -> ID: {0}\t Tipo: {1}.\n'.format(self.id_, self.filter_type)

def unir_archivos(parametros_de_entrada, archivo_salida):
    print '---------------------------------------------------------'
    lista_archivos = []
    if os.path.isdir(parametros_de_entrada):
        for carpeta, _, archivos in os.walk(parametros_de_entrada):
            for archivo in archivos:
                if 'levelDisplay' in os.path.basename(archivo):
                    lista_archivos.append(os.path.join(carpeta, archivo))
    else:
        if os.path.isfile(parametros_de_entrada):
            lista_archivos.append(parametros_de_entrada)
    lista_archivos.sort()
    ultimo_item = len(lista_archivos) - 1
    lista_archivos.insert(0, lista_archivos[ultimo_item])
    lista_archivos.pop()
    for archivo in lista_archivos:
        with open(archivo, 'r') as infile:
            for linea in infile:
                archivo_salida.write(linea)
    # texto_unido = ''.join([open(archivo).read() for archivo in lista_archivos])
        print archivo + ' unido correctamente.'
    # archivo_salida.write(texto_unido)
    print '\nArchivo unido' + ' ---> ' + archivo_salida.name
    print '---------------------------------------------------------'


def obtener_ruta_del_archivo(parametro_entrada, archivo_a_buscar):
    ruta_obtenida = None
    if os.path.isfile(parametro_entrada):
        if os.path.basename(parametro_entrada) != archivo_a_buscar:
            print 'El archivo ingresado como parametro no tiene el nombre ' + archivo_a_buscar
            print 'Se procesara igualmente.'
        ruta_obtenida = parametro_entrada
    else:
        if os.path.isdir(parametro_entrada):
            ruta_obtenida = buscar_archivo_en_carpeta(parametro_entrada, archivo_a_buscar)
    return ruta_obtenida

def buscar_archivo_en_carpeta(carpeta_raiz, archivo_a_buscar):
    archvivo_encontrado = []
    for carpeta, _, archivos in os.walk(carpeta_raiz):
        for archivo in archivos:
            if archivo_a_buscar in os.path.basename(archivo):
                archvivo_encontrado.append(os.path.join(carpeta, archivo))
    return archvivo_encontrado

def main():
    ayuda = """
            Script para comparar los eventos, reglas y permisos a la hora de realizar una migracion en RSA Archer.
            La comparacion se hara revisando los elementos mencionados del primer archivo XML pasado por parametro hacia el segundo archivo XML y se mostraran sus diferencias.
            Se creara un archivo con el resumen de eventos y reglas de cada XML ingresado y uno llamado 'Comparacion.csv' con el resultado del analisis.
            Por ultimo, se informara un resumen de la ejecucion por pantalla al finalizar.
            """
    parser = optparse.OptionParser(usage=ayuda, version="%prog 1.0")
    parser.add_option('-i',
                      '--input',
                      dest='entrada',
                      help='El archivo DataDrivenEvent.xml del paquete a migrar.')
    parser.add_option('-o',
                      '--output',
                      dest='salida',
                      help='El archivo DataDrivenEvent.xml del paquete migrado.')
    (options, args) = parser.parse_args()
    if options.entrada and options.salida:
        #ruta_archivo_origen = obtener_ruta_del_archivo(sys.argv[2], 'levelDisplay')
        # if len(ruta_archivo_origen) > 1:
        with open('levelDisplay_unido.out', 'w+') as archivo_origen_unido:
            unir_archivos(sys.argv[2], archivo_origen_unido)
            archivo_origen_unido.close()
            archivo_origen_unido = open('levelDisplay_unido.out', 'r')
            primer_archivo_xml = XML()
            primer_archivo_xml.parsear(archivo_origen_unido)
    else:
        print 'Error con los parametros de entrada.\n' \
              'Ingrese -i para la carpeta del paquete generado antes de la' \
              'migracion con el/los archivo/s levelDisplay.xml o este mismo directamente. \n' \
              'Ingrese -o para la carpeta del paquete generado luego de la migracion con' \
              'el/los archivo/s levelDisplay.xml o este mismo directamente.'

if __name__ == "__main__":
    main()