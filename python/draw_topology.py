# coding=utf-8
##########################################################
# Name: draw_topo_02.py
# Version: 0.2
# Author: Lucas Aimaretto
# Date: 14-jun-2015 
#
# - 0.1: first draft
#        This version will graph any topology based on the tags of the routers.
# - 0.2: Reorder of functions; cleaning of code.


version_script="02"

#!/usr/bin/python
import MySQLdb
import graphviz as gv
import time
import sys
import functools
from operator import itemgetter
from itertools import groupby

########################################################################
# Functions
########################################################################
# Function that builds the filename
def fnc_build_filename(vector):
	filename="topo/"
	len_vector= len(vector)
	i=1
	for tn in vector:
		if i < len_vector:
			filename=filename+tn+"_"
		else:
			filename=filename+tn

	return filename

# Function that builds the SQL query to obtain the object Id based
# on topo_name
def fnc_build_query_objetos(vector):
	query1=""
	query2=""
	len_vector = len(vector)
	i=1
	
	query1=(
		"select "
		"OBJ.name, "
		"TT.entity_id "
		"from "
		"TagStorage as TT join Object as OBJ on (TT.entity_id=OBJ.id) "
		"where "
	)
	
	for row in vector:
		obj_id=str(row[0])
		if i < len_vector:
			query2 = query2 + "tag_id = " + obj_id + " or "
		else:
			query2 = query2 + "tag_id = " + obj_id
		i=i+1

	query = query1 + query2

	return query
	
# Function that builds the SQL query to obatin the topo_ID
def fnc_build_query_topo_id(vector):
	query1=""
	query2=""
	len_vector = len(vector)
	i=1

	query1=(
		"select id from TagTree where "
	)

	for row in vector:
		obj_id="'" + row + "'"
		if i < len_vector:
			query2 = query2 + "tag = " + obj_id + " or "
		else:
			query2 = query2 + "tag = " + obj_id
		i=i+1

	query = query1 + query2

	return query
	
# Function that removes ports from a router is such port connects
# to a router that does not have a requested tag.
def fnc_remove_routers_wotag(object_vector, connex_vector):

	temp_list=[]
	for o in object_vector:
		temp_list.append(o[0])
	
	final_list=[item for item in connex_vector if item[0] in temp_list and item[5] in temp_list]
			
	return final_list
	
# Function that builds a SQL query to obtain the connections
# among routers.
def fnc_build_query_connections(vector):
	query1=""
	query2=""
	len_vector = len(vector)
	i=1
	
	query1=(
		"SELECT "
		"ro1.name AS obj1, "
		"ro1.id as obj1_id, "
		"p1.name AS port1, "
		"Link.cable, "
		"p2.name AS port2, "
		"ro2.name AS obj2, "
		"ro2.id as obj2_id, "
		"d.dict_value AS obj1type "
		"FROM Object AS ro1 "
		"JOIN Port AS p1 ON(ro1.id=p1.object_id) "
		"JOIN Link ON(p1.id=Link.porta) "
		"JOIN Port AS p2 ON(Link.portb=p2.id) "
		"JOIN Object AS ro2 ON(p2.object_id=ro2.id) "
		"LEFT JOIN Dictionary AS d ON(ro1.objtype_id=d.dict_key) "
		"WHERE ("
	)
	for row in vector:
		obj_id=str(row[1])
		if i < len_vector:
			query2 = query2 + "ro1.id = " + obj_id + " or ro2.id = " + obj_id + " or "
		else:
			query2 = query2 + "ro1.id = " + obj_id + " or ro2.id = " + obj_id
		i=i+1

	query = query1 + query2 + ")"

	return query
	

# Funcion que organiza los puertos de cada nodo
def fnc_port_list(routers):
	router_list=[]
	port_list=[]
	for router in routers:
		print router[0]
		router_id = router[0][0]
		for port in router:
			port_list.append(port[1])
		router_list.append((router_id,port_list))
		port_list=[]

	return router_list
		
# Function that creates a list which holds each router and all its ports.
# Input: object_connections
# [('CF618_JURI70_SARM', '1/1/1'), ('CF618_JURI70_SARM', '1/1/2')]
# Output
# ('CF618_JURI70_SARM_1/1/1', {'label': '1/1/1'})
# The output of this function is used as input to graphviz
def fnc_node_list(routers):
	
	temp_list=[]
	
	for row in routers:
		routerA=row[0]
		portA=row[2]
		routerB=row[5]
		portB=row[4]
		nodeA=routerA + "_" + portA
		nodeB=routerB + "_" + portB
		temp_list.append((routerA,nodeA,{'label':portA}))
		temp_list.append((routerB,nodeB,{'label':portB}))
	
	# List will be ordered and sorted always by the first field
	# which is the router name
	lista_sorted=sorted(temp_list, key=itemgetter(0))
	lista_grouped = groupby(lista_sorted, key=itemgetter(0))
		
	a = []
	for i,rou in enumerate(lista_grouped):
		a.append(list(rou[1]))
	
	return a

# Function that builds a list which holds the connections among routers.
# The output of this function is used as input to graphviz
def fnc_edge_list(vector):
	edge_list=[]
	for row in vector:
		routerA=row[0]
		portA=row[2]
		routerB=row[5]
		portB=row[4]
		cableID=row[3]
		nodeA=routerA + "_" + portA
		nodeB=routerB + "_" + portB
		if not cableID:
			cableID=""
		edge_list.append(((nodeA,nodeB),{'label':cableID}))
	return edge_list

# Verifies that an object exists
def fnc_check_for_topo(objList):
	if len(objList) == 0:
		print "La topo buscada no existe"
		return 0
	else:
		return 1

# Function to print lists
def fnc_print_list(vector):
	for vec in vector:
		print vec

########################################################################
# Program
########################################################################

db = MySQLdb.connect(host="127.0.0.1", 	# your host, usually localhost
               	     port=3306,
                     user="user", 			# your username
                     passwd="pass", 	# your password
                     db="racktables") 		# name of the data base

topo_name = raw_input(
	"\nInput the tag name.\n"
	"If you wish to graph more than one topology, separate those with a comma (,) with no space.\n"
	"Example: st206_001,st206_002: ")
if not topo_name:
	print "None has been input.\n"
	quit()
else:
	topo_name = topo_name.upper()
	topo_name = topo_name.split(",")
	
#==================================================================
#==================================================================
# query0 obtains the Id of the tag_name.

query0 = fnc_build_query_topo_id(topo_name)

cur = db.cursor()
cur.execute(query0)
topo_id = list(cur.fetchall())
if fnc_check_for_topo(topo_id) == 0: quit()

#==================================================================
#==================================================================
# query10 obtains the IDs of routers that have tag 'topo_name'
# The result is the following.

#(objeto_name, object_id)

#('ST206_STA70_SR7', 319L)
#('ST120_CMS70_SARM', 589L)
#('ST209_ST970_SARM', 590L)
#('ST203_ST470_SARM', 633L)
#('ST202_P9J70_SARM', 2503L)

query10 = fnc_build_query_objetos(topo_id)

cur = db.cursor()
cur.execute(query10)
object_list = list(cur.fetchall())

#==================================================================
#==================================================================
# query20 brings the connection among objects.
# This query also brings connections to routers that do not have the
# the requested tag.
# The result is the following.

#(Router1, port1, cableID, port1, Router2)

#('ST206_STA70_SR7', 319L, '1/2/7', None, '1/1/7', 'ST001_SA270_SAR8', 484L, 'Router7750')
#('ST206_STA70_SR7', 319L, '1/2/8', None, '1/1/2', 'ST203_ST470_SARM', 633L, 'Router7750')
#('ST206_STA70_SR7', 319L, '1/2/9', None, '1/1/2', 'ST127_CAC70_SARM', 2504L, 'Router7750')

query20=fnc_build_query_connections(object_list)
cur = db.cursor()
cur.execute(query20)
object_connections = list(cur.fetchall())

#==================================================================
#==================================================================
# The function fnc_remove_routers_wotag(.) filters out the data
# obtained with query20 in such a way that only the connections
# to routers with the requested tag will remain.
# The result is the following.

#(Router1, port1, cableID, port1, Router2)

#('ST206_STA70_SR7', 319L, '1/2/8', None, '1/1/2', 'ST203_ST470_SARM', 633L, 'Router7750')
#('ST206_STA70_SR7', 319L, '1/2/11', None, '1/1/1', 'ST120_CMS70_SARM', 589L, 'Router7750')
#('ST120_CMS70_SARM', 589L, '1/1/2', None, '1/1/1', 'ST209_ST970_SARM', 590L, 'Router')

object_connections=fnc_remove_routers_wotag(object_list,object_connections)

#==================================================================
#==================================================================
# At this instance of the run, the list object_connections[] only has
# connections to routers that do have the requested tag.
# The function fnc_edge_list(.) reorders that information
# so it will be easier to feed graphviz.

#((Router1_port1, Router2_port1), {label: cableID})

#(('ST206_STA70_SR7_1/2/8', 'ST203_ST470_SARM_1/1/2'), {'label': ''})
#(('ST206_STA70_SR7_1/2/11', 'ST120_CMS70_SARM_1/1/1'), {'label': ''})
#(('ST120_CMS70_SARM_1/1/2', 'ST209_ST970_SARM_1/1/1'), {'label': ''})

edges=fnc_edge_list(object_connections)

#===================================================================
#===================================================================
# The list edges[] holds the connections among routers that do have
# the requested tag.
# With this information we filter contruct a new list grouping ports
# per router.

#(Router1, [port1, port2])

#('ST120_CMS70_SARM', ['1/1/1', '1/1/2'])
#('ST202_P9J70_SARM', ['1/1/1', '1/1/2'])
#('ST203_ST470_SARM', ['1/1/2', '1/1/1'])
#('ST206_STA70_SR7', ['1/2/8', '1/2/11', '3/1/19', '3/1/20'])
#('ST209_ST970_SARM', ['1/1/1', '1/1/2'])

routers=fnc_node_list(object_connections)

#==================================================================
# The graph is created.
#==================================================================

g1 = gv.Digraph(comment=topo_name, format='png', engine='fdp')
#g1 = gv.Digraph(comment=topo_name, format='png', engine='dot')
i = 0

for router in routers:
	cluster_name = "cluster"+str(i)
	router_name  = router[0][0]
	c = gv.Digraph(cluster_name)
	c.body.append('label='+router_name)
	c.body.append('shape=record')
	c.node_attr.update(style='filled')
	for port in router:
		node_id=port[1]
		port_id=port[2]['label']
		c.node(node_id,label=port_id)
	g1.subgraph(c)
	i=i+1
	
for e in edges:
	edgeA=e[0][0]
	edgeB=e[0][1]
	edgeLabel=e[1]['label']
	g1.edge(edgeA,edgeB,edgeLabel)
	
filename=fnc_build_filename(topo_name)
g1.render(filename)
	


