#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import codecs
import xml.etree.ElementTree as ET
import sys
import os


class XML(object):
    def __init__(self):
        self._eventos = {}
        self._reglas = {}
        self._numero_eventos = 0
        self._numero_reglas = 0
        self._numero_permisos = 0
        self._archivo = None
        self._lista_guid_eventos = []
        self._guid_e_id_reglas = {}

    @property
    def archivo(self):
        return self._archivo

    @archivo.setter
    def archivo(self, archivo):
        self._archivo = archivo

    @property
    def eventos(self):
        return self._eventos

    @eventos.setter
    def eventos(self, eventos):
        self._eventos = eventos

    @property
    def reglas(self):
        return self._reglas

    @reglas.setter
    def reglas(self, reglas):
        self._reglas = reglas

    @property
    def numero_eventos(self):
        return self._numero_eventos

    @numero_eventos.setter
    def numero_eventos(self, numero_eventos):
        self._numero_eventos = numero_eventos

    @property
    def numero_reglas(self):
        return self._numero_reglas

    @numero_reglas.setter
    def numero_reglas(self, numero_reglas):
        self._numero_reglas = numero_reglas

    @property
    def numero_permisos(self):
        return self._numero_permisos

    @numero_permisos.setter
    def numero_permisos(self, numero_permisos):
        self._numero_permisos = numero_permisos

    @property
    def lista_guid_eventos(self):
        return self._lista_guid_eventos

    @lista_guid_eventos.setter
    def lista_guid_eventos(self, lista_guid_eventos):
        self._lista_guid_eventos = lista_guid_eventos

    @property
    def guid_e_id_reglas(self):
        return self._guid_e_id_reglas

    @guid_e_id_reglas.setter
    def guid_e_id_reglas(self, guid_e_id_reglas):
        self._guid_e_id_reglas = guid_e_id_reglas

    def parsear_xml(self, archivo_entrada):
        self.archivo = archivo_entrada
        tree = ET.parse(self.archivo)
        root = tree.getroot()
        level_guid, rule_guid, action_guid = None, None, None
        for nodos in root.iter():

            if nodos.get('levelGuid') is not None:
                level_guid = nodos.get('levelGuid')  # GUID del evento
            if nodos.get('ruleGuid') is not None:
                rule_guid = nodos.get('ruleGuid')  # GUID del evento
            if nodos.get('actionGuid') is not None:
                action_guid = nodos.get('actionGuid')  # GUID de la regla

            guid = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}GUID')
            id_ = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}Id')
            name = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}Name')
            filter_id = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}FilterId')
            active = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}IsActive')
            level_id = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}LevelId')
            type_ = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}Type')
            permiso = nodos.find('{http://schemas.datacontract.org/2004/07/ArcherTech.Common.Domain}Id')
            acciones = nodos.findall('Action')

            if guid is not None and name is not None and level_id is not None and active is not None:
                if filter_id is not None:
                    self.lista_guid_eventos.append(guid.text)
                    self.eventos[guid.text] = Evento(
                                                     guid=guid.text,
                                                     id_=id_.text,
                                                     name=name.text,
                                                     level_id=level_id.text,
                                                     level_guid=level_guid,
                                                     active=active.text,
                                                     filter_id=filter_id.text
                                                    )
                    self.numero_eventos += 1
                else:
                    if type_ is not None:
                        self.reglas[guid.text] = Regla(
                                                        guid=guid.text,
                                                        id_=id_.text,
                                                        name=name.text,
                                                        level_id=level_id.text,
                                                        level_guid=level_guid,
                                                        active=active.text,
                                                        type_=type_.text
                                                      )
                        self.guid_e_id_reglas[id_.text] = guid.text
                        self.numero_reglas += 1
            if acciones is not None and rule_guid is not None:
                for id_accion in acciones:
                    guid = self.guid_e_id_reglas[id_accion.text]
                    self.eventos[rule_guid].agregar_regla(self.reglas.get(guid))
                else:
                    if action_guid is not None and permiso is not None:
                        self.reglas[action_guid].agregar_permiso(permiso.text)
                        self.numero_permisos += 1

    def imprimir_en_archivo(self, salida_csv):
        salida_csv.write('Tipo;ID;Nombre;GUID;Nivel GUID;Nivel ID/App;Activo;Cantidad reglas;Cantidad permisos;Subtipo\n')
        for guid_evento in self.lista_guid_eventos:
            salida_csv.write(
                            self.eventos[guid_evento].objeto + ';' +
                            self.eventos[guid_evento].id + ';' +
                            self.eventos[guid_evento].name + ';' +
                            self.eventos[guid_evento].guid + ';' +
                            self.eventos[guid_evento].level_guid + ';' +
                            self.eventos[guid_evento].level_id + ';' +
                            self.eventos[guid_evento].active + ';' +
                            str(self.eventos[guid_evento].cantidad_reglas) + '\n'
                            )
            for regla in self.eventos[guid_evento].reglas:
                salida_csv.write(
                                regla.objeto + ';' +
                                regla.id + ';' +
                                regla.name + ';' +
                                regla.guid + ';' +
                                regla.level_guid + ';' +
                                regla.level_id + ';' +
                                regla.active + ';;' +
                                str(regla.cantidad_permisos) + ';' +
                                regla.type + '\n'
                               )

    def imprimir_resumen_en_pantalla(self, nombre_archivo_entrada, nombre_archivo_salida):
        print '---------------------------------------------------------'
        print nombre_archivo_entrada + ' ---> ' + nombre_archivo_salida
        print '---------------------------------------------------------'
        print 'Eventos: ', self.numero_eventos
        print 'Reglas: ', self.numero_reglas
        print 'Permisos: ', self.numero_permisos

    def comparar(self, segundo_xml, archivo_csv):
        eventos_iguales, eventos_sin_encontrar, eventos_con_distintas_reglas, reglas_iguales, reglas_sin_encontrar, reglas_con_distintos_permisos = 0, 0, 0, 0, 0, 0
        archivo_csv.write('Tipo;Nombre;GUID;Nivel GUID;Nivel Id/App;Encontrado;Reglas 1er archivo;Reglas 2do archivo;Permisos 1er archivo;Permisos 2do archivo\n')
        for guid in self.eventos:
            if guid in segundo_xml.eventos:
                evento_a_comprar = segundo_xml.eventos.get(guid)
                eventos_iguales += 1
                if self.eventos[guid].cantidad_reglas != evento_a_comprar.cantidad_reglas:
                    archivo_csv.write(
                                      self.eventos[guid].objeto + ';' +
                                      self.eventos[guid].name + ';' +
                                      self.eventos[guid].guid + ';' +
                                      self.eventos[guid].level_guid + ';' +
                                      self.eventos[guid].level_id + ';' +
                                      'Si' + ';' +
                                      str(self.eventos[guid].cantidad_reglas) + ';' +
                                      str(evento_a_comprar.cantidad_reglas) + '\n'
                                      )
                    eventos_con_distintas_reglas += 1
            else:
                archivo_csv.write(
                                  self.eventos[guid].objeto + ';' +
                                  self.eventos[guid].name + ';' +
                                  self.eventos[guid].guid + ';' +
                                  self.eventos[guid].level_guid + ';' +
                                  self.eventos[guid].level_id + ';' +
                                  'No\n'
                                  )
                eventos_sin_encontrar += 1
        for guid in self.reglas:
            if guid in segundo_xml.reglas:
                reglas_iguales += 1
                regla_a_comparar = segundo_xml.reglas[guid]
                if self.reglas[guid].cantidad_permisos != regla_a_comparar.cantidad_permisos:
                    archivo_csv.write(
                                      self.reglas[guid].objeto + ';' +
                                      self.reglas[guid].name + ';' +
                                      self.reglas[guid].guid + ';' +
                                      self.reglas[guid].level_guid + ';' +
                                      self.reglas[guid].level_id + ';' +
                                      'Si' + ';;;' +
                                      str(self.reglas[guid].cantidad_permisos) + ';' +
                                      str(regla_a_comparar.cantidad_permisos) + '\n'
                                      )
                    reglas_con_distintos_permisos += 1
            else:
                archivo_csv.write(
                                  self.reglas[guid].objeto + ';' +
                                  self.reglas[guid].name + ';' +
                                  self.reglas[guid].guid + ';' +
                                  self.reglas[guid].level_guid + ';' +
                                  self.reglas[guid].level_id + ';' +
                                  'No\n'
                                  )
                reglas_sin_encontrar += 1
        print '---------------------------------------------------------'
        print self.archivo.name + ' vs ' + segundo_xml.archivo.name + ' ---> ' + archivo_csv.name
        print '---------------------------------------------------------'
        print 'Eventos encontrados con distinta cantidad de reglas: ' + str(eventos_con_distintas_reglas)
        print 'Eventos sin encontrar: ' + str(eventos_sin_encontrar)
        print 'Reglas encontradas con distinta cantidad de permisos: ' + str(reglas_con_distintos_permisos)
        print 'Reglas sin encontrar: ' + str(reglas_sin_encontrar)


class EventoRegla(object):
    def __init__(self,
                 guid,
                 id_,
                 name,
                 level_id,
                 level_guid,
                 active,
                 objeto):
        self._objeto = objeto
        self._guid = guid
        self._id = id_
        self._name = name
        self._level_id = level_id
        self._level_guid = level_guid
        self._active = active

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def level_guid(self):
        return self._level_guid

    @property
    def level_id(self):
        return self._level_id

    @property
    def active(self):
        return self._active

    @property
    def guid(self):
        return self._guid

    @property
    def objeto(self):
        return self._objeto

    @objeto.setter
    def objeto(self, objeto):
        self._objeto = objeto

    @name.setter
    def name(self, name):
        self._name = name

    @id.setter
    def id(self, id_):
        self._id = id_

    @level_guid.setter
    def level_guid(self, level_guid):
        self._level_guid = level_guid

    @level_id.setter
    def level_id(self, level_id):
        self._level_id = level_id

    @active.setter
    def active(self, active):
        self._active = active

    @guid.setter
    def guid(self, guid):
        self._guid = guid

    def imprimir(self):
        print self.objeto + ': ' + self.id + ' | GUID:' + self.guid
        print 'Nombre: ' + self.name.encode('utf-8')
        print 'Nivel GUID: ' + self.level_guid + '| Nivel: ' + self.level_id
        print 'Activo: ' + self.active


class Evento(EventoRegla):
    def __init__(self,
                 guid,
                 id_,
                 name,
                 level_id,
                 level_guid,
                 active,
                 filter_id
                 ):
        EventoRegla.__init__(self,
                             guid,
                             id_,
                             name,
                             level_id,
                             level_guid,
                             active,
                             'Evento'
                             )
        self._filter_id = filter_id
        self._cantidad_reglas = 0
        self._reglas = []

    def imprimir(self):
        EventoRegla.imprimir(self)
        print '---------------------------------------------------'
        print 'Filtro: ' + self.filter_id
        print 'Cantidad reglas:', self.cantidad_reglas
        for regla in self.reglas:
            print 'Regla #', regla.id
            regla.imprimir()

    @property
    def cantidad_reglas(self):
        return self._cantidad_reglas

    @cantidad_reglas.setter
    def cantidad_reglas(self, cantidad):
        self._cantidad_reglas = cantidad

    def agregar_regla(self, regla):
        self.reglas.append(regla)
        self.cantidad_reglas = self.cantidad_reglas + 1

    @property
    def filter_id(self):
        return self._filter_id

    @filter_id.setter
    def filter_id(self, filter_id):
        self._filter_id = filter_id

    @property
    def reglas(self):
        return self._reglas

    @reglas.setter
    def reglas(self, reglas):
        self._reglas = reglas


class Regla(EventoRegla):
    def __init__(self,
                 guid,
                 id_,
                 name,
                 level_id,
                 level_guid,
                 type_,
                 active):
        EventoRegla.__init__(self,
                             guid,
                             id_,
                             name,
                             level_id,
                             level_guid,
                             active,
                             'Regla')
        self._type = type_
        self._permisos = []
        self._cantidad_permisos = 0

    def imprimir(self):
        print '----->'
        EventoRegla.imprimir(self)
        print 'Tipo: ' + self.type
        print 'Cantidad permisos:', self.cantidad_permisos
        linea = 'Permisos ID: '
        for permiso in self.permisos:
            linea = linea + permiso + ' '
        print linea

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type_):
        self._type = type_

    @property
    def permisos(self):
        return self._permisos

    @permisos.setter
    def permisos(self, permisos=None):
        self._permisos = permisos

    @property
    def cantidad_permisos(self):
        return self._cantidad_permisos

    @cantidad_permisos.setter
    def cantidad_permisos(self, permisos):
        self._cantidad_permisos = permisos

    def agregar_permiso(self, id_permiso):
        self.permisos.append(id_permiso)
        self.cantidad_permisos += 1

'''
class Filtro(object):
    def __init__(self, operator_logic, id, rule_guid):
        self.cantidad_condiciones = 0
        self.operator_logic = operator_logic
        self.id = id
        self.rule_guid = rule_guid
        self.condiciones = []

    def agregar_condicion(self, condicion):
        self.cantidad_condiciones += 1
        self.condiciones.append(condicion)
'''


class Condicion(object):
    def __init__(self, filter_type, id_, order, operator):
        self.filter_type = filter_type
        self.id = id_
        self.order = order
        self.operator = operator

    def __getId__(self):
        return self.id

'''
def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)

def corregir_archivo(archivo):
    patron = re.compile(r'\t\t<.*? .*?Guid="[A-Fa-f0-9_-]*">')
    with open('Temporal', 'w+') as archivo_temporal:
        for linea in archivo:
            if patron.search(linea) and 'EventRuleAction' not in linea:
                longitud = len(linea)
                linea = linea[:longitud-2] + '/>\n'
                print linea
            archivo_temporal.write(linea)
    return 'Temporal'

def parse_and_get_ns(file):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in ET.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #     to different URI namespaces in different parts of the
                #     document. This exception serves as a reminder that this
                #     solution is not robust.    Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "{%s}" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return ET.ElementTree(root), ns

'''

def obtener_ruta_del_archivo(parametro_entrada, archivo_a_buscar):
    ruta_obtenida = None
    if os.path.isfile(parametro_entrada):
        if os.path.basename(parametro_entrada) !=  archivo_a_buscar:
            print 'El archivo ingresado como parametro no tiene el nombre ' + archivo_a_buscar
            print 'Se procesara igualmente.'
        ruta_obtenida = parametro_entrada
    else:
        if os.path.isdir(parametro_entrada):
            ruta_obtenida = buscar_archivo_en_carpeta(parametro_entrada, archivo_a_buscar)
    return ruta_obtenida

def buscar_archivo_en_carpeta(carpeta_raiz, archivo_a_buscar):
    archvivo_encontrado = None
    for carpeta, subcarpeta, archivos in os.walk(carpeta_raiz):
        for archivo in archivos:
            if os.path.basename(archivo) == archivo_a_buscar:
                archvivo_encontrado = os.path.join(carpeta, archivo)
    return archvivo_encontrado

def buscar_evento_por_guid(eventos, guid):
    for evento in eventos:
        if evento.guid == guid:
            return evento
    return None


def main():
    ayuda = """
            Script para comparar los eventos, reglas y permisos a la hora de realizar una migracion en RSA Archer.
            La comparacion se hara revisando los elementos mencionados del primer archivo XML pasado por parametro hacia el segundo archivo XML y se mostraran sus diferencias.
            Se creara un archivo con el resumen de eventos y reglas de cada XML ingresado y uno llamado 'Comparacion.csv' con el resultado del analisis.
            Por ultimo, se informara un resumen de la ejecucion por pantalla al finalizar.
            """
    parser = optparse.OptionParser(usage=ayuda, version="%prog 1.2")
    parser.add_option('-i', '--input', dest='entrada', help='El archivo DataDrivenEvent.xml del paquete a migrar.')
    parser.add_option('-o', '--output', dest='salida', help='El archivo DataDrivenEvent.xml del paquete migrado.')
    (options, args) = parser.parse_args()
    if options.entrada and options.salida:
        ruta_archivo_origen = obtener_ruta_del_archivo(sys.argv[2], 'DataDrivenEvent.xml')
        ruta_archivo_salida = obtener_ruta_del_archivo(sys.argv[4], 'DataDrivenEvent.xml')
        with open(ruta_archivo_origen, 'r') as archivo_primer_xml:
            nombre_archivo_csv_primer_xml = os.path.basename(sys.argv[2]) + '.1.csv'
            datos_primer_xml = XML()
            datos_primer_xml.parsear_xml(archivo_primer_xml)
            with codecs.open(nombre_archivo_csv_primer_xml, 'w', 'utf-8') as archivo_csv_primer_xml:
                datos_primer_xml.imprimir_en_archivo(archivo_csv_primer_xml)
                datos_primer_xml.imprimir_resumen_en_pantalla(archivo_primer_xml.name, archivo_csv_primer_xml.name)
                with open(ruta_archivo_salida, 'r') as archivo_segundo_xml:
                    nombre_archivo_csv_segundo_xml = os.path.basename(sys.argv[4]) + '.2.csv'
                    datos_segundo_xml = XML()
                    datos_segundo_xml.parsear_xml(archivo_segundo_xml)
                    with codecs.open(nombre_archivo_csv_segundo_xml, 'w', 'utf-8') as archivo_csv_segundo_xml:
                        datos_segundo_xml.imprimir_en_archivo(archivo_csv_segundo_xml)
                        datos_segundo_xml.imprimir_resumen_en_pantalla(archivo_segundo_xml.name, archivo_csv_segundo_xml.name)
                        with codecs.open('Comparacion_Eventos.csv', 'w','utf-8') as archivo_csv_comparacion:
                            datos_primer_xml.comparar(datos_segundo_xml, archivo_csv_comparacion)          
    else:
        print 'Error con los parametros de entrada.\n' \
              'Ingrese -i para la carpeta del paquete generado antes de la migracion con el archivo DataDrivenEvent.xml o este mismo directamente. \n' \
              'Ingrese -o para la carpeta del paquete generado luego de la migracion con el archivo DataDrivenEvent.xml o este mismo directamente.'

if __name__ == "__main__":
        main()