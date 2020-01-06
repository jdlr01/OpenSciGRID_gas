# -*- coding: utf-8 -*-
"""
@author: wilkohe
"""
import csv
import networkx as nx
#import matplotlib.pyplot as plt

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import collections

import sys # for passing variables from main process

########### INPUT DATA ################
path=sys.argv[8]
#path="/home/wilkohe/08_automation_tool/01_main_tool"

# ggf. hier am Anfang die von QGIS berechnete Länge des Netzes übergeben und dann zu results schreiben, weil dort auch die disconnected subgrids enthalten sind. oder hier in networkx die länge der disconnectedten subgrids berechnen

# enter network name
nw_name=sys.argv[1]
#nw_name='scigrid_unmerged'
#nw_name='scigrid_germany_merged'
#nw_name='osmtgmod'
#nw_name='gridkit_germany_15012017_only_220_380_none'
#nw_name='gridkit_france_15012017_only_225_400_none'
#nw_name='gridkit_italy_15012017_only_220_380_none'
#nw_name='Western_Interconnect_USA' # Quelle: Uni Koblenz
#nw_name='gridkit_western_usa_15012017_only_220_380_none'

nodes_list_file=sys.argv[2]
#nodes_list_file="/sample_data/scigrid_vertices_germany_15012017_wkt_srid_4326_3857.csv"
#nodes_list_file="/sample_data/osmTGmod_bus_data_wkt_srid_3857.csv"
#nodes_list_file="/sample_data/gridkit_highvoltage_germany_only_220_380_none_wkt_srid_4326_3857.csv"
#nodes_list_file="/sample_data/other_countries_vertices/modified/gridkit_highvoltage_vertices_france_only_225_400_none_wkt_srid_4326_3857.csv"
#nodes_list_file="/sample_data/other_countries_vertices/modified/gridkit_highvoltage_vertices_italy_only_220_380_none_wkt_srid_4326_3857.csv"
#nodes_list_file="/sample_data/other_countries_vertices/modified/gridkit_highvoltage_vertices_western_usa_only_220_380_none_wkt_srid_4326_3857.csv"

node_id_colu=sys.argv[3]
#node_id_colu='v_id' # SciGrid, GridKit
#node_id_colu="bus_i" # OsmTGmod

edges_list_file=sys.argv[4]
#edges_list_file='/sample_data/lines/scigrid_links_merged_germany_15012017_wkt_srid_4326_3857.csv'
#edges_list_file='/sample_data/lines/scigrid_links_unmerged_germany_15012017_wkt_srid_4326_3857.csv'
#edges_list_file='/sample_data/lines/gridkit_highvoltage_links_germany_only_220_380_none_wkt_srid_4326_3857.csv'
#edges_list_file='/sample_data/lines/osm_tg_mod_branch_data_topo_wkt_srid_3857_with_lengths.csv'
#edges_list_file='/sample_data/lines/other_countries_links/other_countries_links_modified/gridkit_highvoltage_links_france_only_225_400_none_wkt_srid_4326_3857.csv'
#edges_list_file='/sample_data/lines/other_countries_links/other_countries_links_modified/gridkit_highvoltage_links_italy_only_220_380_none_wkt_srid_4326_3857.csv'
#edges_list_file='/sample_data/lines/other_countries_links/other_countries_links_modified/gridkit_highvoltage_links_western_usa_only_220_380_none_wkt_srid_4326_3857.csv'


input_link_v_id1_colu=sys.argv[5]
input_link_v_id2_colu=sys.argv[6]

#input_link_v_id1_colu='v_id_1' # SciGrid, GridKit
#input_link_v_id2_colu='v_id_2'
#input_link_v_id1_colu='f_bus' # OsmTGmod
#input_link_v_id2_colu='t_bus'

input_link_length_colu=sys.argv[7]#'length_m' #GridKit, Scigrid


#output file

csv_out_file = open(''+path+'/results/mathematical_criteria/nx_output_'+nw_name+'.csv','wb')
csv_out = csv.writer(csv_out_file, delimiter=',',quotechar="'")

############ BUILD GRAPH ##################
G = nx.Graph()

    # ADD EDGES and NODES

#with open('/home/wilkohe/08_automation_tool/mathematical_criteria/sample_data/gridkit_links_highvoltage.csv') as edge_list_with_length: 
with open(''+path+''+edges_list_file+'','r') as edge_list_with_length:

    edge_list = csv.DictReader(edge_list_with_length,quotechar="'")
#    headers = next(edge_list)

    
    for row in edge_list:
	G.add_edge(int(row[input_link_v_id1_colu]), int(row[input_link_v_id2_colu]), weight=int(float(row[input_link_length_colu])) )
#	G.add_edge(int(row[4]),int(row[5]), weight=int(float(row[21]))) ## OSMTGMOD
#    	G.add_edge(int(row[1]),int(row[2]), weight=int(float(row[10]))) ## GRIDKIT
#	G.add_edge(int(row[3]),int(row[4]), weight=int(float(row[12]))) ## GRIDKIT_filtered_220_330
#       G.add_edge(int(row[3]),int(row[4]), weight=int(row[12])) ## SCIGRID
#        G.add_edge(int(row[0]),int(row[1]), weight=int(row[2]))  ## edge_list_with_length_with_headers_disconnected   
tot_num_nodes=G.number_of_nodes()

csv_out.writerow(['--- GENERAL GRAPH INFORMATION ---'])
csv_out.writerow(['total number of nodes all graphs',tot_num_nodes])
############ FIND LARGEST CONNECTED SET  ##################
ccs=nx.connected_component_subgraphs(G)

main_graph=ccs.next()
#num_dg=0
#num_dg_nodes=0
num_gr=1  # number of graphs
for sg in ccs:   # !!! the first graph in the generator ccs is skipped here because .next() function was called before
   num_gr=num_gr + 1	
   if sg.number_of_nodes() > main_graph.number_of_nodes():
   	main_graph= sg

############ GRAPH STATISTICS ##################
num_nodes=main_graph.number_of_nodes()
num_edges=main_graph.number_of_edges()
num_dg=num_gr - 1  # number of disconnected graphs
num_dg_nodes= tot_num_nodes - num_nodes # total number of disconnected graphs nodes
tot_length=main_graph.size(weight='weight')

csv_out.writerow(['total number of graphs: ',num_gr])
csv_out.writerow(['number of disconnected graphs: ',num_dg])
csv_out.writerow(['total number of disconnected graphs nodes: ',num_dg_nodes])
csv_out.writerow(['MAIN GRAPH:'])
csv_out.writerow(['number of nodes: ',num_nodes])
csv_out.writerow(['number of edges: ',num_edges])
csv_out.writerow(['total line length [km]: ',"{0:.4f}".format(tot_length/1000)])
csv_out.writerow(['average line length[km]: ',"{0:.4f}".format(tot_length/num_edges/1000)])


######## MATHEMATICAL CRITERIA ##############
csv_out.writerow(['--- MATHEMATICAL CRITERIA ---'])


asp=nx.average_shortest_path_length(main_graph, weight=None)
aspl=nx.average_shortest_path_length(main_graph, weight='weight')

diameter=nx.diameter(main_graph,e=None)

degrees = main_graph.degree()
sum_of_degrees = sum(degrees.values())
max_deg=degrees[max(degrees, key=degrees.get)]
average_degree=sum_of_degrees/float(num_nodes)

bet_cen=nx.betweenness_centrality(main_graph, k=None, normalized=True, weight=None, endpoints=False, seed=None)  # betweenness_centrality for nodes
sum_bet_cen=sum(bet_cen.values())
av_bet_cen=sum_bet_cen/float(num_nodes)
max_bet_cen=bet_cen[max(bet_cen, key=bet_cen.get)]
min_bet_cen=bet_cen[min(bet_cen, key=bet_cen.get)]

bet_cen_edge=nx.edge_betweenness_centrality(main_graph, normalized=True, weight=None) # betweenness_centrality for edges
sum_bet_cen_edge=sum(bet_cen_edge.values())
av_bet_cen_edge=sum_bet_cen_edge/float(num_edges)
max_bet_cen_edge=max(bet_cen_edge.values())
min_bet_cen_edge=min(bet_cen_edge.values())

cluster=nx.clustering(main_graph, nodes=None, weight=None)
sum_cluster=sum(cluster.values())
av_cluster=sum_cluster/float(num_nodes)
max_cluster=max(cluster.values())
min_cluster=min(cluster.values())


csv_out.writerow(['average shortest path [number of nodes]',"{0:.4f}".format(asp)])
csv_out.writerow(['average shortest path length [km]',"{0:.4f}".format(aspl/1000)])
csv_out.writerow(['diameter [number of nodes]',diameter])
csv_out.writerow(['sum of degrees',sum_of_degrees])
csv_out.writerow(['average degree',"{0:.4f}".format(average_degree)])
csv_out.writerow(['maximum degree',"{0:.4f}".format(max_deg)])
csv_out.writerow(['average betweenness centrality value for nodes',"{0:.6f}".format(av_bet_cen)])
csv_out.writerow(['maximum betweenness centrality value for nodes',"{0:.6f}".format(max_bet_cen)])
csv_out.writerow(['minimum betweenness centrality value for nodes',"{0:.6f}".format(min_bet_cen)])
csv_out.writerow(['average betweenness centrality value for edges',"{0:.6f}".format(av_bet_cen_edge)])
csv_out.writerow(['maximum betweenness centrality value for edges',"{0:.6f}".format(max_bet_cen_edge)])
csv_out.writerow(['minimum betweenness centrality value for edges',"{0:.6f}".format(min_bet_cen_edge)])
csv_out.writerow(['average local clustering coefficient',"{0:.6f}".format(av_cluster)])
csv_out.writerow(['maximum local clustering coefficient',"{0:.6f}".format(max_cluster)])
csv_out.writerow(['minimum local clustering coefficient',"{0:.6f}".format(min_cluster)])


######## WRITE RESULTS OUTPUT LISTS ####################
array_degrees=[]
for k , v in degrees.iteritems(): 
	array_degrees.append({'node':k, 'degree': v})
fieldnames = ['node', 'degree']
test_file = open(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/degree/degree_'+nw_name+'.csv','wb')
csvwriter = csv.DictWriter(test_file, delimiter=',',quotechar="'", fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for row in array_degrees:
     csvwriter.writerow(row)
test_file.close()

array_bet_cen=[]
for k , v in bet_cen.iteritems(): 
	array_bet_cen.append({'node':k, 'bet_cen': v})
fieldnames = ['node', 'bet_cen']
test_file = open(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_nodes/betweenness_centrality_nodes_'+nw_name+'.csv','wb')
csvwriter = csv.DictWriter(test_file, delimiter=',',quotechar="'", fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for row in array_bet_cen:
     csvwriter.writerow(row)
test_file.close()

array_bet_cen_edge=[]
for k , v in bet_cen_edge.iteritems():
	array_bet_cen_edge.append({'edge':k, 'bet_cen_edge': v})
fieldnames = ['edge', 'bet_cen_edge']
test_file = open(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_edges/betweenness_centrality_edges_'+nw_name+'.csv','wb')
csvwriter = csv.DictWriter(test_file, delimiter=',',quotechar="'", fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for row in array_bet_cen_edge:
     csvwriter.writerow(row)
test_file.close()

array_cluster=[]
for k , v in cluster.iteritems(): 
	array_cluster.append({'node':k, 'clustering_coefficient': v})
fieldnames = ['node', 'clustering_coefficient']
test_file = open(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/clustering_coefficient_nodes/clustering_coefficient_nodes_'+nw_name+'.csv','wb')
csvwriter = csv.DictWriter(test_file, delimiter=',',quotechar="'", fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for row in array_cluster:
     csvwriter.writerow(row)
test_file.close()	

####### APPEND RESULTS TO NODES LISTS ####################

nodes_list=open(''+path+''+nodes_list_file+'', 'r')
nodes_list_with_criteria=open(''+path+'/results/mathematical_criteria/nodes_lists_with_mat_criteria/'+nw_name+'_vertices_with_mat_criteria.csv', 'w+')
reader=csv.DictReader(nodes_list,delimiter=',', quotechar="'")

header= reader.fieldnames
header.append('degree')
header.append('betweenness_centrality_node')
header.append('clustering_coefficient')

writer=csv.DictWriter(nodes_list_with_criteria, delimiter=',',quotechar="'", fieldnames=header)
writer.writerow(dict((fn,fn) for fn in header))


for row in reader:

	if int(row[node_id_colu]) in degrees:
		row['degree']=degrees[int(row[node_id_colu])]
#	else:
#		row['degree']=0
	
	if int(row[node_id_colu]) in bet_cen:
		row['betweenness_centrality_node']=bet_cen[int(row[node_id_colu])]
#	else:
#		row['betweenness_centrality_node']=0

	if int(row[node_id_colu]) in cluster:
		row['clustering_coefficient']=cluster[int(row[node_id_colu])]
#	else:
#		row['clustering_coefficient']=0

	writer.writerow(row)

####### APPEND RESULTS TO EDGES LISTS ####################

edges_list=open(''+path+''+edges_list_file+'', 'r')
edges_list_with_criteria=open(''+path+'/results/mathematical_criteria/links_lists_with_mat_criteria/'+nw_name+'_links_with_mat_criteria.csv', 'w+')
reader=csv.DictReader(edges_list,delimiter=',', quotechar="'")

header= reader.fieldnames
header.append('betweenness_centrality_edges')
header.append('betweenness_centrality_edges_inverted') # this column contains an entry, it indicates that the betweenness centrality value for that row has been derived from an edge in the networkx edge list with an inverted vertices order

writer=csv.DictWriter(edges_list_with_criteria, delimiter=',',quotechar="'", fieldnames=header)
writer.writerow(dict((fn,fn) for fn in header))

for row in reader:
	#print row[input_link_v_id1_colu],row[input_link_v_id2_colu]
	if (int(row[input_link_v_id1_colu]),int(row[input_link_v_id2_colu])) in bet_cen_edge:
		#print row[input_link_v_id1_colu],row[input_link_v_id2_colu], 'included'
		row['betweenness_centrality_edges']=bet_cen_edge[(int(row[input_link_v_id1_colu]),int(row[input_link_v_id2_colu]))]
	if (int(row[input_link_v_id2_colu]),int(row[input_link_v_id1_colu])) in bet_cen_edge: 
		#print row[input_link_v_id2_colu],row[input_link_v_id1_colu], 'included'
		row['betweenness_centrality_edges']=bet_cen_edge[(int(row[input_link_v_id2_colu]),int(row[input_link_v_id1_colu]))]
		row['betweenness_centrality_edges_inverted']=bet_cen_edge[(int(row[input_link_v_id2_colu]),int(row[input_link_v_id1_colu]))]
	writer.writerow(row)

###########Diagram Creation ##############
#x=degrees.values()
#a=np.array(x)

#n, bins, patches = plt.hist(a, max(x), normed=1, facecolor='green', alpha=0.75)


## add a 'best fit' line
##y = mlab.normpdf( bins, mu, sigma)
##l = plt.plot(bins, y, 'r--', linewidth=1)

#plt.xlabel('Degree')
#plt.ylabel('Probability')
#plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
#plt.axis([0, max(x), 0, 0.5])
#plt.grid(True)

#plt.show()



# Degree Distribution PDF
degrees_list = degrees.values()
len_deg=len(degrees_list)
counter=collections.Counter(degrees_list)
counter=collections.OrderedDict(sorted(counter.items()))
degree_keys=counter.keys()
degree_values=counter.values()


deg=np.array(degree_keys)
deg_freq=np.array(degree_values)
deg_pdf=deg_freq/float(len_deg)

plt.bar(deg, deg_pdf, align='center', alpha=0.5)
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.ylabel('Pr(d)')
plt.xlabel('Degree (d)')
plt.title('Degree Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/degree/degree_PDF_'+nw_name+'.pdf')


np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/degree/degree_PDF_'+nw_name+'.csv', zip(deg, deg_pdf), delimiter=',',header='Degree,Propability', fmt='%f')
plt.clf()

# Degree Cumulative Distribution CDF (inverted)
deg_cdf=np.cumsum(deg_pdf)
deg_cdf_inv=np.subtract(1,deg_cdf)

plt.plot(deg, deg_cdf_inv,marker='o')
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.xlabel('Degree (d)')
plt.ylabel('Pr(x>=d)')
plt.title('Degree Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/degree/degree_CDF_'+nw_name+'.pdf')


np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/degree/degree_CDF_'+nw_name+'.csv', zip(deg,deg_cdf_inv), delimiter=',',header='Degree, Cumulative Propability', fmt='%f')
plt.clf()


#Edge Betweeness Centrality PDF
bet_cen_edge_list = bet_cen_edge.values()
len_bce=len(bet_cen_edge_list)
counter=collections.Counter(bet_cen_edge_list)
counter=collections.OrderedDict(sorted(counter.items()))
bce_keys=counter.keys()
bce_values=counter.values()


bce=np.array(bce_keys)
bce_freq=np.array(bce_values)
bce_pdf=bce_freq/float(len_bce)

plt.plot(bce, bce_pdf,marker='o')
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.ylabel('Pr(bce)')
plt.xlabel('Degree (bce)')
plt.title('Edge Betweeness Centrality Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_edges/bce_PDF_'+nw_name+'.pdf')

np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_edges/bce_PDF_'+nw_name+'.csv', zip(bce, bce_pdf), delimiter=',',header='Edges Betweenness Centrality,Propability', fmt='%f')
plt.clf()

# Degree Cumulative Distribution CDF (inverted)
bce_cdf=np.cumsum(bce_pdf)

plt.plot(bce, bce_cdf,marker='o')
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.xlabel('Degree (bce)')
plt.ylabel('Pr(x<=bce)')
plt.title('Edge Betweenness Centrality Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_edges/bce_CDF_'+nw_name+'.pdf')

np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/betweenness_centrality_edges/bce_CDF_'+nw_name+'.csv', zip(bce, bce_cdf), delimiter=',',header='Edges Betweenness Centrality, Cumulative Propability', fmt='%f')
plt.clf()


# Clustering Coefficient Distribution PDF
cluster_list = cluster.values()
len_clust=len(cluster_list)
counter=collections.Counter(cluster_list)
counter=collections.OrderedDict(sorted(counter.items()))
cluster_keys=counter.keys()
cluster_values=counter.values()

clust=np.array(cluster_keys)
clust_freq=np.array(cluster_values)
clust_pdf=clust_freq/float(len_clust)

plt.plot(clust, clust_pdf,marker='o')
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.ylabel('Pr(c)')
plt.xlabel('Clustering Coefficient (c)')
plt.title('Cluster Coefficient Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/clustering_coefficient_nodes/clustering_coefficient_PDF_'+nw_name+'.pdf')


np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/clustering_coefficient_nodes/clustering_coefficient_PDF_'+nw_name+'.csv', zip(clust, clust_pdf), delimiter=',',header='Clustering Coefficient,Propability', fmt='%f')
plt.clf()

# Clustering Coefficient Cumulative Distribution CDF
clust_cdf=np.cumsum(clust_pdf)

plt.plot(clust, clust_cdf,marker='o')
##plt.xticks(y_pos, objects)
axes=plt.gca()
axes.set_xlim(left=0)
axes.set_ylim(bottom=0)
plt.xlabel('Clustering Coefficient (c)')
plt.ylabel('Pr(x<=c)')
plt.title('Clustering Coefficient Cumulative Distribution '+nw_name+'')
fig = plt.gcf() 
fig.savefig(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/clustering_coefficient_nodes/clustering_coefficient_CDF'+nw_name+'.pdf')


np.savetxt(''+path+'/results/mathematical_criteria/mathematical_criteria_tables/clustering_coefficient_nodes/clustering_coefficient_CDF'+nw_name+'.csv', zip(clust, clust_cdf), delimiter=',',header='Clustering Coefficient, Cumulative Propability', fmt='%f')
plt.clf()



