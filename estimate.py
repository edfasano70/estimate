# modulo de rutinas del programa condominio
import json
# import condo
import fpdf
from fpdf import FPDF
import yagmail
import sqlite3 as lite
import sys
import os
import colorama
from colorama import *
import cfonts
from cfonts import render, say
colorama.init(autoreset=True)

#CONSOLE WIDGETS

def console_menu(title,options,exit_caption='Exit',exit_on_null=True,orientation='vertical'):
	#	Función:
	# 		Crea un menú por consola de selección simple
	# 	Entradas:
	# 		title: str <- título del menú
	# 		options: list <- contiene pares de opción y comando a ejecutar
	# 		exitOption: str <- nombre que va a tener la opción de salida del menú
	# 		nullExit: bool <- si es true se sale del menú solo pulsando ENTER
	# 	Regresa:
	# 		bool <- TRUE si se seleccionó una opción válida
	res=False
	i=0
	error=False
	if orientation=='vertical':
		print('\n'+title)
		print('-'*len(title))
		for p in options:
			i+=1
			print(i,'·',p[0])
		print(0,'· '+exit_caption)
		sel=input('\n» ')
	elif orientation=='horizontal':
		print('\n'+title,end='')
		for p in options:
			i+=1
			print(i,'·',p[0],' ')
		print(0,'· '+exit_caption,' ')
		sel=input(' » ')

	if sel=='':
		if exit_on_null:
			sel=0
		else:
			sel=-1
	try:
		sel=int(sel)
	except:
		sel=-1
	if sel>=0 and sel<=i:
		pass
	else:
		sel=-1
	return sel

def console_input(msg,type='str',default=''):
	# 	Función:
	# 		Solicita un dato por consola
	# 	Entradas:
	# 		type: str <- str, int, float, date <-pendiente de momento
	# 		msg: str <- mensaje a desplegar
	# 	Salidas:
	# 		value: resultado 
	cs=Style.BRIGHT+Fore.GREEN
	icon='[ ? ]'
	if default!='': msg+=' [{}] '.format(default)
	print(cs+icon+Style.RESET_ALL+' : '+msg+' ',end='')
	value=input()
	if value=='': value=default
	return value

def console_captcha(msg='Write following characters',num_chars=4):
	# 	Función:
	# 		Solicita la resolución de un captcha por consola
	# 	Entradas:
	# 		msg: str <- mensaje a desplegar
	# 	Salidas:
	# 		value: True si es coreccto 
	from random import randint

	res=False
	cs=Style.BRIGHT+Fore.GREEN
	icon='[ ? ]'

	chars='abcdefghijklmnopqrstuvwxyz0123456789'
	challenge=''
	for i in range(0,num_chars):
		challenge+=chars[randint(0,len(chars)-1)]

	print(cs+icon+Style.RESET_ALL+' : '+msg+' [{}] '.format(challenge),end='')
	value=input()
	if value==challenge: res=True
	return res

def console_msgbox(type,msg,enter=False):
	# 	Función:
	# 		Imprime mensaje tipo "alertBox" por consola
	# 	Entradas:
	# 		type: str <- ok,error,alert
	# 		msg: str <- mensaje a desplegar
	# 		enter: bool <- indica si requiere pulsar ENTER para continuar. Default False
	# 	Salidas:
	# 		No 
	cs=Style.BRIGHT
	if type=='ok':
		cs+=Fore.GREEN
		icon='[ → ]'
	elif type=='error':
		cs+=Fore.RED
		icon='[ X ]'
	elif type=='alert':
		cs+=Fore.YELLOW
		icon='[ ! ]'
	else:
		cs=''
	print(cs+icon+Style.RESET_ALL+' : '+msg+' ')
	if enter:
		input()

def console_progressbar(curr, total, full_progbar):
	frac = curr/total
	filled_progbar = round(frac*full_progbar)
	print('\r', '#'*filled_progbar + '-'*(full_progbar-filled_progbar), '[{:>7.2%}]'.format(frac), end='')

#END OF CONSOLE WIDGETS

#CONSOLE FUNCTIONS

def clear():
	# Función:
	# 	Borra la consola
	if os.name == "nt":
		os.system("cls")
	else:
		os.system("clear")

def terminal_size():
    import fcntl, termios, struct
    th, tw, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return tw, th

#END OF CONSOLE FUNCTIONS

#DICTIONARY FUNCTIONS

def rm_dict_key(dict_name,dict_key):
	#	Función:
	#		Remueve una clave de un diccionario trabajando directamente sobre el mismo
	if dict_name.get(dict_key,False):
		dict_name.pop(dict_key)

def assign_value_2_dictkey(dict_name,dict_key,value=None): 
	#	Función:
	#		Asigna el valor por defecto a una clave en un diccionario y si no existe la crea
	if dict_name.get(dict_key,None)==None:
		dict_name[dict_key]=value
	# dict_name[dict_key]=value

#END OF DICTIONARY FUNCTIONS

#GENERAL PURPOSE FUNCTIONS

def date_time_now():
	from datetime import datetime
	now=datetime.now()
	return now.strftime('%Y-%m-%d %H:%M')

def is_number(value):
	# 	Función: 
	# 		Devuelve True si s es del object tipo int o float
	# 	Entrada:
	# 		value: obj <-valor a checkear
	# 	Regresa:
	# 		bool: True si value es int o float
	res=False
	if type(value)==type(1):
		res=True
	elif type(value)==type(1.0):
		res=True
	return res

def dict_factory(cursor, row):
    # 	Función:
    # 		Necesaria para que fetch en la base de datos devuelva dict
    # 	Entrada:
    # 		cursor: apuntador del resultado
    # 		row: datos regresados
    # 	Regresa:
    # 		dict: con los resultados en formato dict
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#END OF GENERAL PURPOSE FUNCTIONS

#DATABASE FUNCTIONS

def row_get(database,table,id_name='id',id_value=None):
	# 	Función:
	#		Obtiene una línea de datos de una base de datos SQLite
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		table    - string - nombre de la tabla
	#		id_name  - string - nombre de la columna de apuntador normalmente 'id'
	#		id_value - string - valor a buscar
	# 	Regresa:
	#		dict - valores retornados
	if id_value==None:
		sql='SELECT * FROM {} LIMIT 1'.format(table)
	else:
		sql='SELECT * FROM {} WHERE {} = {} LIMIT 1'.format(table,id_name,id_value)
	return row_query_get(database,sql)

def row_query_get(database,sql):
	# 	Función:
	# 		Obtiene una línea de datos de una base de datos SQLite mediante un query
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		sql: string <- query que genera la búsqueda
	# 	Regresa:
	#		dict - valores retornados
	con = lite.connect(database)
	con.row_factory = lite.Row #
	cur = con.cursor()
	cur.execute(sql)
	row = cur.fetchone()
	if row!=None:
		row=dict(zip(row.keys(), row)) #
	con.close()
	return row

	#row_query_get() pasaría a ser getQuery()[0]

def query_get(database,sql):
	# 	Función:
	# 		Obtiene una tabla de resultados de una base de datos SQLite mediante un query
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		sql: string <- query que genera la búsqueda
	# 	Regresa:
	#		dict - valores retornados
	data=[]
	con = lite.connect(database)
	con.row_factory = lite.Row #
	cur = con.cursor()
	cur.execute(sql)
	tmp=cur.fetchall()
	con.close()
	for r in tmp:	
		row=dict(zip(r.keys(), r))
		data.append(row)
	return data

def query_exec(database,sql):
	# 	Función:
	# 		Obtiene una tabla de resultados de una base de datos SQLite mediante un query
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		sql: string <- query que genera la búsqueda
	# 	Regresa:
	#		dict - valores retornados
	con = lite.connect(database)
	cur = con.cursor()
	cur.execute(sql)
	con.close()

def database_table_list(database):
	# 	Función:
	# 		Obtiene lista de tablas en una base de datos SQLite
	# 	Entrada:
	# 		database: string <- nombre de la base de datos
	# 	Regresa:
	# 		tuple: valores retornados
	sql="SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'"
	query=query_get(database,sql)
	res=[]
	for q in query:
		res.append(q['name'])
	return res

def row_insert(database,table,data):
	# 	Función:
	# 		Inserta una línea de datos de una base de datos SQLite
	# 	Entrada:
	# 		database: str <- nombre de la base de datos
	# 		table: str <- nombre de la tabla
	# 		data: dict <- datos en forma de pares key-value
	# 	Regresa:
	# 		bool: True si se ingresó el dato correctamente
	res = True
	keys=data.keys()
	tmp=''
	for k in keys:
		tmp+=k+','
	keys=tmp[0:len(tmp)-1]
	tmp=''
	values=data.values()
	for v in values:
		tmp+="'"+str(v)+"',"
	data=tmp[0:len(tmp)-1]
	con = lite.connect(database)
	cur = con.cursor()
	sql='INSERT INTO {} ({}) VALUES ({})'.format(table,keys,data)
	try:
		cur.execute(sql)
		con.commit()
	except:
	 	res = False
	con.close()
	return res

def row_change_id(database,table,old_id,new_id):
	# 	Función:
	# 		cambia el id  a una línea de datos de una base de datos SQLite
	# 	Entrada:
	# 		database: str <- nombre de la base de datos
	# 		table: str <- nombre de la tabla
	# 		old_id: integer <- id a cambiar
	# 		new_id: integer <- id nuevo
	# 	Regresa:
	# 		bool: True si se ingresó el dato correctamente OJO::: hay que revisar
	res = True
	con = lite.connect(database)
	with con:
		cur = con.cursor()
		sql="UPDATE {} SET id={} WHERE id={}".format(table,new_id,old_id)
		try:
			cur.execute(sql)
		except:
		 	res = False
	if con: con.close()
	return res

def row_update(database,table,data): 
	# 	Función: 
	# 		cambia los datos de una fila en una tabla
	# 	Entrada:
	# 		database: str <- nombre de la base de datos
	# 		table: str <- nombre de la tabla
	#		data: dict <- data en forma de pares key-value
	# 	Regresa:
	# 		bool: True si se ingresó el dato correctamente OJO::: hay que revisar
	res = True
	keys=data.keys()
	subs=''
	for k in keys:
		subs+="{} = '{}',".format(k,data[k])
	subs=subs[0:len(subs)-1]
	con = lite.connect(database)
	sql="UPDATE {} SET {} WHERE id='{}'".format(table,subs,data['id'])
	with con:
		cur = con.cursor()
		try:
			cur.execute(sql)
			con.commit()
		except:
		 	res = False
	if con: con.close()
	return res

def row_delete(database,table,id_name,id_value):
	# 	Función:
	#		Borra una fila de datos de una tabla
	# 	Entrada:
	# 		database - string - nombre de la base de datos
	# 		table    - string - nombre de la tabla
	# 		id_name  - string - nombre de la columna de apuntador normalmente 'id'
	# 		id_value - string - valor a buscar
	# 	Regresa:
	# 		bool - True si se ingresó el dato correctamente
	con = lite.connect(database)
	cur = con.cursor()
	cur.execute('DELETE FROM {} WHERE {} = {}'.format(table,id_name,id_value))
	con.commit()
	con.close()

def table_max_id(database,table,id_name): 
	# 	Descripción: Devuelve el máximo valor de la columna en una base de datos SQLite
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		table    - string - nombre de la tabla
	#		id_name  - string - nombre de la columna de apuntador normalmente 'id'
	# 	Regresa:
	#		int - valor máximo
	res=row_query_get(database,'SELECT MAX({}) AS max FROM {}'.format(id_name,table)).get('max',0)
	if res==None: res=0
	return res

def table_drop(database,table):
	# 	Descripción: Borra la tabla completa valores y estructura
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		table    - string - nombre de la tabla
	query='DROP TABLE IF EXISTS {}'.format(table)
	query_exec(database,query)

def table_delete_all_rows(database,table):
	# 	Descripción: Borra recursivamente todos las filas de una tabla
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		table    - string - nombre de la tabla
	sql='SELECT * FROM {}'.format(table)
	rows=query_get(database,sql)
	for r in rows:
		# print(r['id'])
		row_delete(database,table,'id',r['id'])

def row_id_exist(database,table,id_name,id_value): 
	# 	Descripción: Verifica que un registro exista en una base de datos SQLite
	# 	Entrada:
	#		database - string - nombre de la base de datos
	#		table    - string - nombre de la tabla
	#		id_name  - string - nombre de la columna de apuntador normalmente 'id'
	#		id_value - string - valor a buscar
	# 	Regresa:
	#		bool - True si existe
	res=False
	count=row_query_get(database,'SELECT COUNT(id) AS count FROM {} WHERE {} = {}'.format(table,id_name,id_value)).get('count')
	if count>0:
		res=True
	return res

def table_defrag(database,table):
	# 	Función: 
	#		'Defragmenta' la tabla poniendo todos los id consecutivos
	# 	Entrada:
	#		database: str <- nombre de la base de datos
	#		table: str <- nombre de la tabla
	con = lite.connect(database)
	cur = con.cursor()
	sql='SELECT id FROM {}'.format(table)
	cur.execute(sql)
	rows = cur.fetchall()
	con.close()
	i=1
	for r in rows:
		if r[0]!=i:
			row_change_id(database,table,r[0],i)
		i+=1

def table_export_csv(database,table,filename='out.csv'): #EXPERIMENTAL!!!
	# Función: 
	#	Exporta una tabla especificada a  un archivo delimitado por comas CSV
	# Entrada:
	# 	database: str <- nombre de la base de datos
	# 	table: str <- nombre de la tabla
	# 	filename: str <- nombre del archivo a importar
	# Regresa:
	# 	DEBERIA regresar bool - True si se cargó sin problemas el archivo
	# Pendientes:
	#	validar si el archivo existe, número de registros cargados, etc
	con = lite.connect(database)
	con.row_factory = lite.Row
	cur = con.cursor()
	sql='SELECT * FROM {}'.format(table)
	cur.execute(sql)
	rows = cur.fetchall()
	con.close()

	fic = open(filename, "w")
	tmp=''
	for c in rows[0].keys():
		tmp+='"{}",'.format(c)
	tmp=tmp[0:-1]+os.linesep
	fic.write(tmp)
	for row in rows:
		tmp=''
		for c in row:
			tmp+='"{}",'.format(c)
		tmp=tmp[0:-1]+os.linesep
		fic.write(tmp)
	fic.close()

def table_import_csv(database,table,filename): #EXPERIMENTAL!!!
	# 	Función: 
	#		importa un archivo delimitado por comas CSV a la base de datos y tabla especificada
	# 	Entrada:
	# 		database: str <- nombre de la base de datos
	# 		table: str <- nombre de la tabla
	# 		filename: str <- nombre del archivo a importar
	# 	Regresa:
	# 		DEBERIA regresar bool - True si se cargó sin problemas el archivo
	# 	Pendientes:
	#		validar si el archivo existe, número de registros cargados, etc
	fic = open(filename, "r")
	lines = fic.readlines()
	fic.close()
	headerFlag=True
	for line in lines:
		line=line.replace('\'','').replace('\n','')
		if headerFlag:
			headerFlag=False
			keys=[]
			for l in line.split(','):
				keys.append(l)
		else:
			values=line.split(',')
			data={}
			for i in range(0,len(keys)):
				data[keys[i]]=values[i]
			if row_id_exist(database,table,data['id']):
				data['id']=str(table_max_id(database,table)+1)
			print(data)
			row_insert(database,table,data)

#END OF DATABASE FUNCTIONS

def validateInput(value,params={'type':'str'}):
	res=True
	msg=''
	type=params['type']
	if type=='str':
		value=str(value)
		#verificamos los caracteres permitidos
		allowed_chars=params.get('allowed_chars','ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ ')
		tmp=value.upper()
		tmp2=''
		tmp3=''
		for i in range(0,len(value)):
			if tmp[i] not in allowed_chars:
				if value[i] not in tmp3: tmp3+=value[i]
				res=False
			else:
				tmp2+=value[i]

		value=tmp2
		if tmp3!='': console_msgbox('error','Existen caracteres NO PERMITIDOS> "{}"'.format(tmp3))

		#verificamos capitalización
		if params.get('capitalize',None)=='upper':
			value=value.upper()
		elif params.get('capitalize',None)=='lower':
			value=value.lower()
		elif params.get('capitalize',None)=='capitalize':
			value=value.capitalize()

		#verificamos longitud minima y maxima
		lenght_min=params.get('lenght_min',None)
		lenght_max=params.get('lenght_max',None)
		if lenght_min!=None:
			if len(value)<lenght_min: #,0):
				res=False
				console_msgbox('error','Debe tener al menos {} caracteres'.format(params.get('lenght_min',0)))
		if lenght_max!=None:
			if len(value)>lenght_max: #,100):
				value=value[0:lenght_max] #,100)]
				console_msgbox('alert','Supera la longitud máxima de {} caracateres'.format(params.get('lenght_max',20)))

	elif type=='int':
		value=str(value)
		#verificamos los caracteres permitidos
		allowed_chars='0123456789'
		tmp=''
		for i in range(0,len(value)):
			if value[i] not in allowed_chars:
				res=False
				tmp+=value[i]
		if tmp!='': console_msgbox('error','Existen caracteres NO PERMITIDOS> "{}"'.format(tmp))

		if res:
			value=int(value)
			#verificamos valor mínimo y máximo
			value_min=params.get('min',None)
			value_max=params.get('max',None)
			if value_min!=None:
				if value<value_min: #,0):
					res=False
					console_msgbox('error','Por debajo del valor mínimo [{}]'.format(value_min))
			if value_max!=None:
				if value>value_max: #,100):
					res=False
					console_msgbox('error','Supera el valor máximo [{}]'.format(value_max))
			
	elif type=='float':
		value=str(value)
		#verificamos los caracteres permitidos
		allowed_chars='0123456789.'
		tmp=''
		for i in range(0,len(value)):
			if value[i] not in allowed_chars:
				res=False
				tmp+=value[i]
		if tmp!='': console_msgbox('error','Existen caracteres NO PERMITIDOS> "{}"'.format(tmp))

		#verificamos que exista 1 '.' como máximo
		if value.count('.')>1:
			res=False
			console_msgbox('error','Formato numérico ERRONEO'.format(tmp3))			
		if res:
			value=float(value)
			#verificamos valor minimo y maximo
			value_min=params.get('min',None)
			value_max=params.get('max',None)
			if value_min!=None:
				if value<value_min: #,0):
					res=False
					console_msgbox('error','Por debajo del valor mínimo [{}]'.format(value_min))
			if value_max!=None:
				if value>value_max: #,100):
					res=False
					console_msgbox('error','Supera el valor máximo [{}]'.format(value_max))
				
	elif type=='date':
		pass
	elif type=='bool':
		pass
	elif type=='email':
		pass
	else:
		pass

	return res, value, msg

