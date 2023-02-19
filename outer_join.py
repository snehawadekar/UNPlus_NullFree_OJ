import copy

import reveal_globals

def fn():

    for tabname in reveal_globals.global_core_relations:
        cur = reveal_globals.global_conn.cursor()
        cur.execute('alter table ' + tabname + '_restore rename to ' + tabname + '2;')
        #The above command will inherently check if tabname1 exists
        cur.execute('drop table ' + tabname + ';')
        cur.execute('alter table ' + tabname + '2 rename to ' + tabname + ';')
        cur.close()


    #part of ---  def possible_edge_sequence():
    new_join_graph=[] 
    list_of_tables=[]
    for edge in reveal_globals.global_join_graph:
        temp=[]
        if len(edge)>2:
            i=0
            while i<(len(edge))-1:
                temp=[]
                cur = reveal_globals.global_conn.cursor()
                cur.execute("SELECT COLUMN_NAME ,TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME like '"+ str(edge[i])+"' ;")
                tabname=cur.fetchone()
                cur.close()
        
                if tn not in list_of_tables:
                    list_of_tables.append(tabname[1])
                print(edge[i],tabname)
                
                temp.append(tabname)
                cur = reveal_globals.global_conn.cursor()
                cur.execute("SELECT COLUMN_NAME ,TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME like '"+ str(edge[i+1])+"' ;")
                tabname=cur.fetchone()
                cur.close()
                tn=tabname[1]
                print(tn) #####
                if tn not in list_of_tables:
                    list_of_tables.append(tn)
                print(edge[i+1],tabname)
                temp.append(tabname)
                i=i+1
                new_join_graph.append(temp)   
        else:
            for vertex in edge:
                cur = reveal_globals.global_conn.cursor()
                cur.execute("SELECT COLUMN_NAME ,TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME like '"+ str(vertex)+"' ;")
                tabname=cur.fetchone()
                cur.close()
                print(vertex,tabname)
                temp.append(tabname)
                tn=tabname[1]
                print(tn) #####
                if tn not in list_of_tables:
                    list_of_tables.append(tn)
            new_join_graph.append(temp)
            
    print(list_of_tables)   
    print(new_join_graph)


    final_edge_seq=[]
    queue=[]
    for tab in list_of_tables:
        edge_seq=[]
        temp_njg=copy.deepcopy(new_join_graph)
        queue.append(tab)
        # table_t=tab
        while len(queue)!=0:
            remove_edge=[]
            table_t=queue.pop(0)
            for edge in temp_njg:
                if edge[0][1] == table_t and edge[1][1] != table_t:
                    remove_edge.append(edge)
                    edge_seq.append(edge)
                    queue.append( edge[1][1] )
                elif edge[0][1] != table_t and edge[1][1] == table_t:
                    remove_edge.append(list(reversed(edge)))
                    edge_seq.append(list(reversed(edge)))
                    queue.append( edge[0][1] )

            for i in remove_edge:
                try:
                    temp_njg.remove(i)
                except:
                    temp_njg.remove(list(reversed(i)))
            print(temp_njg)
        final_edge_seq.append(edge_seq)
    print(final_edge_seq) 



    table_attr_dict={}
    # for each table find a projected attribute which we will check for null values
    for k in reveal_globals.global_projected_attributes:
        cur = reveal_globals.global_conn.cursor()
        cur.execute("SELECT COLUMN_NAME ,TABLE_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME like '"+ str(k)+"' ;")
        tabname=cur.fetchone()
        cur.close()
        if tabname[1] not in table_attr_dict.keys():
            print(k,tabname[1])
            table_attr_dict[tabname[1]]=k
    print(table_attr_dict)

        

    #preparing D_1
    for tabname in reveal_globals.global_core_relations:
        cur = reveal_globals.global_conn.cursor()
        cur.execute('alter table ' + tabname + ' rename to ' + tabname + '_restore;')
        # cur.close()
        # cur = reveal_globals.global_conn.cursor()
        cur.execute('create table ' + tabname + ' as select * from '  + tabname + '4;')   
        cur.close()

   

    # cur = reveal_globals.global_conn.cursor()
    # query=reveal_globals.query1
    # cur.execute(query)
    # res_hq=cur.fetchall()
    # print(res_hq)
    # cur.close()


    importance_dict={}
    for edge in new_join_graph:
        #modify d1
        # break join condition on this edge
        tuple1=edge[0]
        key=tuple1[0]
        table=tuple1[1]
        cur = reveal_globals.global_conn.cursor()
        print('Update ' + table + ' set ' + key + '= -(select '+key +' from '+ table +');')
        cur.execute('Update ' + table + ' set ' + key + '= -(select '+key +' from '+ table +');')
        cur.close()

        cur = reveal_globals.global_conn.cursor()
        query=reveal_globals.query1
        cur.execute(query)
        
        colnames = [desc[0] for desc in cur.description]
        res_hq=cur.fetchall()
        # res_hq.append((colnames))
        
        cur.close()
        print(res_hq)


        cur = reveal_globals.global_conn.cursor()
        print('Update ' + table + ' set ' + key + '= -(select '+key +' from '+ table +');')
        cur.execute('Update ' + table + ' set ' + key + '= -(select '+key +' from '+ table +');')
        cur.close()

        # make dict of table, attributes: projected val 
        loc={}
        for table in table_attr_dict.keys():
            loc[ table_attr_dict[table]]= colnames.index(table_attr_dict[table])
        print(loc)

        res_hq_dict={}
        if len(res_hq)==0:
            for k in loc.keys():
                if k not in res_hq_dict.keys():
                    res_hq_dict[k]=[None]
                else:
                    res_hq_dict[k].append(None)
        else:
            for l in range(len(res_hq)):
                for k in loc.keys():
                    if k not in res_hq_dict.keys():
                        res_hq_dict[k]=[res_hq[l][loc[k]]]
                    else:
                        res_hq_dict[k].append(res_hq[l][loc[k]])
        print(res_hq_dict)

        # importance_dict={}
        # for e in new_join_graph:
        importance_dict[tuple(edge)]={}
        table1=edge[0][1] #first table
        table2=edge[1][1]
        
        p_att_table1= None
        p_att_table2= None
        att1=table_attr_dict[table1]
        att2=table_attr_dict[table2]
        if att1 in res_hq_dict.keys():
            for i in res_hq_dict[att1]:
                if i!= None:
                    p_att_table1= 10
                    break
        if att2 in res_hq_dict.keys():
            for i in res_hq_dict[att2]:
                if i!= None:
                    p_att_table2= 10
                    break


        print(p_att_table1,p_att_table2)
        temp1=''
        temp2=''
        if p_att_table1 == None and p_att_table2== None:
            temp1='l'
            temp2='l'
        elif p_att_table1 == None and p_att_table2!= None:
            temp1='l'
            temp2='h'
        elif p_att_table1 != None and p_att_table2== None:
            temp1='h'
            temp2='l'
        elif p_att_table1 != None and p_att_table2!= None:
            temp1='h'
            temp2='h'


        importance_dict[tuple(edge)][table1]=temp1
        importance_dict[tuple(edge)][table2]=temp2

    print(importance_dict)
    reveal_globals.importance_dict=importance_dict
    # final_edge_seq = possible_edge_sequence()
    set_possible_queries = FormulateQueries(final_edge_seq)
    # print("here")


    #eliminate semanticamy non-equivalent querie from set_possible_queries
    sem_eq_queries=[]

    cur = reveal_globals.global_conn.cursor()
    query=reveal_globals.query1
    cur.execute(query)
    res_HQ=cur.fetchall()    
    cur.close()
    # print(res_HQ)
    for poss_q in set_possible_queries:
        cur = reveal_globals.global_conn.cursor()
        query=poss_q
        cur.execute(query)
        res_poss_q=cur.fetchall()
        # print(res_poss_q)
        cur.close()

        if len(res_HQ) != len(res_poss_q):
            pass
        else:
            same=1
            for var in range(len(res_HQ)):
                print(res_HQ[var] == res_poss_q[var])
                if ( res_HQ[var] == res_poss_q[var] ) == False:
                    same=0

            if same == 1:
                sem_eq_queries.append(poss_q)
    
    # print("sem_eq_queries")
    # print(sem_eq_queries)
    reveal_globals.output1=sem_eq_queries[0]


    for tabname in reveal_globals.global_core_relations:
        cur = reveal_globals.global_conn.cursor()
        # cur.execute('alter table ' + tabname + '1 rename to ' + tabname + '2;')
        #The above command will inherently check if tabname1 exists
        cur.execute('drop table ' + tabname + ';')
        cur.execute('alter table ' + tabname + '_restore rename to ' + tabname + ';')
        cur.close()

    return 



    # once dict is made compare values to null or not null 
    # and prepare importance_dict 
def FormulateQueries(final_edge_seq):

    filter_pred_on=[]
    filter_pred_where=[]
    for fp in reveal_globals.global_filter_predicates:
        cur = reveal_globals.global_conn.cursor()
        # update partsupp set ps_partkey=(select ps_partkey from partsupp)+1;
        print("select " + fp[1] + " From " + fp[0] +";")
        cur.execute("select " + fp[1] + " From " + fp[0] +";")
        restore_value=cur.fetchall()
        cur.close()

        cur = reveal_globals.global_conn.cursor()
        # update partsupp set ps_partkey=(select ps_partkey from partsupp)+1;
        print("Update " + fp[0] + " Set " + fp[1]+" = Null;")
        cur.execute("Update " + fp[0] + " Set " + fp[1]+" = Null;")
        cur.close()
        cur = reveal_globals.global_conn.cursor()
        query=reveal_globals.query1
        cur.execute(query)
        res_hq=cur.fetchall()
        print(res_hq)
        cur.close()
        if len(res_hq) == 0:
            filter_pred_where.append(fp)
        else:
            filter_pred_on.append(fp)

        print(restore_value[0][0])
        cur = reveal_globals.global_conn.cursor()
        # update partsupp set ps_partkey=(select ps_partkey from partsupp)+1;
        print("Update " + fp[0] + " Set " + fp[1]+" = "+str(restore_value[0][0])+";")
        cur.execute("Update " + fp[0] + " Set " + fp[1]+" = "+str(restore_value[0][0])+";")
        cur.close()
    print(filter_pred_on, filter_pred_where)

    set_possible_queries=[]
    ##formulate queries function using final_edge_seq
    key_dict={
        'nation':['n_nationkey','n_regionkey'],
        'region': ['r_regionkey'],
        'supplier': ['s_suppkey', 's_nationkey'],
        'partsupp': ['ps_partkey', 'ps_suppkey'],
        'part': ['p_partkey'],
        'lineitem': ['l_orderkey', 'l_partkey', 'l_suppkey'],
        'orders': ['o_orderkey', 'o_custkey'],
        'customer': ['c_custkey', 'c_nationkey']  
        }

    flat_list = [item for sublist in reveal_globals.global_join_graph for item in sublist]
    keys_of_tables = [*set(flat_list)]
    tables=reveal_globals.global_core_relations

    tables_in_joins=[]
    for key in keys_of_tables:
        for tab in tables:
            if key in key_dict[tab] and tab not in tables_in_joins:
                tables_in_joins.append(tab) 

    tables_not_in_joins=[]
    for tab in tables:
        if tab not in tables_in_joins:
            tables_not_in_joins.append(tab)

    print(tables_in_joins, tables_not_in_joins)

    importance_dict=reveal_globals.importance_dict

    for seq in final_edge_seq:

        fp_on=copy.deepcopy(filter_pred_on)
        fp_where=copy.deepcopy(filter_pred_where)
    
        query= "Select " +reveal_globals.global_select_op 
        # handle tables not participating in join
        if len(tables_not_in_joins)!=0:
            query +=" From "
            for tab in tables_not_in_joins:
                query += tab +" , "
        else:
            query +=" From "

        flag_first=True
        for edge in seq:
            # steps to determine type of join for edge
            if tuple(edge) in importance_dict.keys():
                imp_t1=importance_dict[tuple(edge)][edge[0][1]]
                imp_t2=importance_dict[tuple(edge)][edge[1][1]]
            elif tuple(list(reversed(edge))) in importance_dict.keys():
                imp_t1=importance_dict[tuple(list(reversed(edge)))][edge[0][1]]
                imp_t2=importance_dict[tuple(list(reversed(edge)))][edge[1][1]]
            else:
                print("error sneha!!!")

            print(imp_t1 , imp_t2)
            if imp_t1 == 'l' and imp_t2 == 'l':
                type_of_join= ' Inner Join '
            elif imp_t1 == 'l' and imp_t2 == 'h':
                type_of_join= ' Right Outer Join '
            elif imp_t1 == 'h' and imp_t2 == 'l':
                type_of_join= ' Left Outer Join '
            elif imp_t1 == 'h' and imp_t2 == 'h':
                type_of_join= ' Full Outer Join '

            if flag_first == True:
                query+= str(edge[0][1]) + type_of_join + str(edge[1][1]) +' ON '+ str( edge[0][0] ) +' = '+str( edge[1][0] ) 
                flag_first = False
                # check for filter predicates for both tables
                # append fp to query
                table1=edge[0][1]
                table2=edge[1][1]
                for fp in fp_on:
                    if fp[0] == table1 or fp[0] == table2:
                        predicate = ''
                        elt=fp
                        if elt[2].strip() == 'range':
                            if '-' in str(elt[4]):
                                predicate = elt[1] + " between "  + str(elt[3]) + " and " + str(elt[4])
                            else:
                                predicate = elt[1] + " between "  + " '" + str(elt[3]) + "'" + " and " + " '" + str(elt[4]) + "'"
                        elif elt[2].strip() == '>=':
                            if '-' in str(elt[3]):
                                predicate = elt[1] + " " + str(elt[2]) + " '" + str(elt[3]) + "' "
                            else:
                                predicate = elt[1] + " " + str(elt[2]) + " " + str(elt[3])
                        elif 'equal' in elt[2] or 'like' in elt[2].lower() or '-' in str(elt[4]):
                            predicate = elt[1] + " " + str(elt[2]).replace('equal', '=') + " '" + str(elt[4]) + "'"
                        else:
                            predicate = elt[1] + ' ' + str(elt[2]) + ' ' + str(elt[4])
                        query +=" and "+ predicate
                        fp_on.remove(fp)

            else:
                query+= ' ' + type_of_join + str(edge[1][1]) +' ON '+ str( edge[0][0] ) +' = '+str( edge[1][0] ) 
                # check for filter predicates for second tables
                # append fp to query

                for fp in fp_on:
                    if fp[0] == edge[1][1]:
                        predicate = ''
                        elt=fp
                        if elt[2].strip() == 'range':
                            if '-' in str(elt[4]):
                                predicate = elt[1] + " between "  + str(elt[3]) + " and " + str(elt[4])
                            else:
                                predicate = elt[1] + " between "  + " '" + str(elt[3]) + "'" + " and " + " '" + str(elt[4]) + "'"
                        elif elt[2].strip() == '>=':
                            if '-' in str(elt[3]):
                                predicate = elt[1] + " " + str(elt[2]) + " '" + str(elt[3]) + "' "
                            else:
                                predicate = elt[1] + " " + str(elt[2]) + " " + str(elt[3])
                        elif 'equal' in elt[2] or 'like' in elt[2].lower() or '-' in str(elt[4]):
                            predicate = elt[1] + " " + str(elt[2]).replace('equal', '=') + " '" + str(elt[4]) + "'"
                        else:
                            predicate = elt[1] + ' ' + str(elt[2]) + ' ' + str(elt[4])
                        query +=" and "+ predicate
                        fp_on.remove(fp)
        # add other components of the query
        # + where clause
        # + group by, order by, limit
        reveal_globals.global_where_op = ''

        for elt in fp_where:
            predicate = ''
            if elt[2].strip() == 'range':
                if '-' in str(elt[4]):
                    predicate = elt[1] + " between "  + str(elt[3]) + " and " + str(elt[4])
                else:
                    predicate = elt[1] + " between "  + " '" + str(elt[3]) + "'" + " and " + " '" + str(elt[4]) + "'"
            elif elt[2].strip() == '>=':
                if '-' in str(elt[3]):
                    predicate = elt[1] + " " + str(elt[2]) + " '" + str(elt[3]) + "' "
                else:
                    predicate = elt[1] + " " + str(elt[2]) + " " + str(elt[3])
            elif 'equal' in elt[2] or 'like' in elt[2].lower() or '-' in str(elt[4]):
                predicate = elt[1] + " " + str(elt[2]).replace('equal', '=') + " '" + str(elt[4]) + "'"
            else:
                predicate = elt[1] + ' ' + str(elt[2]) + ' ' + str(elt[4])
            if reveal_globals.global_where_op == '':
                reveal_globals.global_where_op = predicate
            else:
                reveal_globals.global_where_op = reveal_globals.global_where_op + " and " + predicate

        #assemble the rest of the query
        if reveal_globals.global_where_op != '':
            query = query + " Where " + reveal_globals.global_where_op
        if reveal_globals.global_groupby_op != '':
            query = query + " Group By " + reveal_globals.global_groupby_op
        if reveal_globals.global_orderby_op != '':
            query = query + " Order By " + reveal_globals.global_orderby_op
        if reveal_globals.global_limit_op  != '':
            query = query + " Limit " + reveal_globals.global_limit_op 


        print(query)
        print("+++++++++++++++++++++")
        set_possible_queries.append(query)

    return set_possible_queries


    





