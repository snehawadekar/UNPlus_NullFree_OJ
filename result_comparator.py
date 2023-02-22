import reveal_globals

#needs to be extended for outer joins
# extended on 21st feb
# HAsh based result comparator

def match(Q_E, res):
    # res contains op of hidden query
    res.pop(0)
    cur  = reveal_globals.global_conn.cursor()
    cur.execute(Q_E) #result of extracted query
    res1 = cur.fetchall()
    cur.close()
    
    if(len(res1) != len(res)):
        return False

    if reveal_globals.outer_join_flag: 
        cur  = reveal_globals.global_conn.cursor()
        cur.execute(" create table r_e as " + Q_E ) #extracted query op
        cur.execute(" truncate table r_e ")
        cur.close()
        
        cur = reveal_globals.global_conn.cursor()
        cur.execute(Q_E)
        resx = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        
        result1 = []
        result1.append(tuple(colnames))
        if resx is not None:
            for row in resx:
                temp = []
                for val in row:
                    if val== None:
                        temp.append('0')
                    else:
                        temp.append(str(val))
                result1.append(tuple(temp))
    
        # Header of r_e
        t = result1[0]
        t1 = '(' + t[0]
        for i in range(1,len(t)):
            t1 += ', ' + t[i]
        t1 += ')'

        # Filling the table r_e
        for i in range(1,len(result1)):
            cur = reveal_globals.global_conn.cursor()
            cur.execute('INSERT INTO r_e'+str(t1)+' VALUES '+str(result1[i])+'; ')
            cur.close()

        cur = reveal_globals.global_conn.cursor()
        cur.execute(Q_E)
        resx = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()

        result = []
        result.append(tuple(colnames))
        if res is not None:
            for row in res:
                temp = []
                for val in row:
                    if val== 'None' :
                        temp.append('0')
                    else:
                        temp.append(str(val))
                result.append(tuple(temp))
        
        cur = reveal_globals.global_conn.cursor()
        cur.execute('Create unlogged table r_h (like r_e);') #
        cur.close()
    
        # Header of r_h
        t = result[0]
        t1 = '(' + t[0]
        for i in range(1,len(t)):
            t1 += ', ' + t[i]
        t1 += ')'

        # Filling the table r_h
        for i in range(1,len(result)):
            cur = reveal_globals.global_conn.cursor()
            cur.execute('INSERT INTO r_h'+str(t1)+' VALUES '+str(result[i])+'; ')
            cur.close()
    
    else:
        cur  = reveal_globals.global_conn.cursor()
        cur.execute("create view r_e as "+ Q_E)
        cur.close()

        cur = reveal_globals.global_conn.cursor()
        cur.execute(Q_E)
        res = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()

        result = []
        result.append(tuple(colnames))
        if res is not None:
            for row in res:
                #CHECK IF THE WHOLE ROW IN NONE (SPJA Case)
                nullrow = True
                for val in row:
                    if val != None:
                        nullrow = False
                        break
                if nullrow == True:
                    continue
                temp = []
                for val in row:
                    temp.append(str(val))
                result.append(tuple(temp))
        
        cur = reveal_globals.global_conn.cursor()
        cur.execute('Create unlogged table r_h (like r_e);')
        cur.close()
    
        # Header of r_h
        t = result[0]
        t1 = '(' + t[0]
        for i in range(1,len(t)):
            t1 += ', ' + t[i]
        t1 += ')'

        # the table r_h
        for i in range(1,len(result)):
            cur = reveal_globals.global_conn.cursor()
            # result[i]= tuple(result[i][0])
            cur.execute('INSERT INTO r_h'+str(t1)+' VALUES '+str(result[i])+'; ')
            cur.close()
            
        
        

    cur  = reveal_globals.global_conn.cursor()
    cur.execute("select sum(hashtext) from (select hashtext(r_e::TEXT) FROM r_e) as T;")
    len1 = cur.fetchone()[0]
    cur.close()

    cur  = reveal_globals.global_conn.cursor()
    cur.execute("select sum(hashtext) from (select hashtext(r_h::TEXT) FROM r_h) as T;")
    len2 = cur.fetchone()[0]
    cur.close()

    cur = reveal_globals.global_conn.cursor()
    if reveal_globals.outer_join_flag:
        cur.execute('DROP table r_e;')
    else:
        cur.execute('DROP view if exists r_e;')
    cur.execute('DROP TABLE r_h;')
    cur.close()
    if(len1 == len2):
        return True
    else:
        return False




# extracted_query=reveal_globals.output1
# hidden_query=reveal_globals.query1
# cur  = reveal_globals.global_conn.cursor()
# cur.execute(hidden_query)
# res= cur.fetchall()
# cur.close()
# #call hash based result comparator
# if(match(extracted_query,res)):
#     print("matched-------------")
#     # return render_template('page2.html',res_comp="results are same")
# else:
#     print("-------------no match")
#     # return render_template('page2.html',res_comp="results are Different")


