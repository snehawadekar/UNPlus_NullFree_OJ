import os
import sys
import psycopg2
sys.path.append('../')
import reveal_globals

def getExecOutput():
    result = []
    try:
        cur = reveal_globals.global_conn.cursor()
        query=reveal_globals.query1
        #print("query=",query)
        reveal_globals.global_no_execCall = reveal_globals.global_no_execCall + 1
        cur.execute(query)
        res = cur.fetchall() #fetchone always return a tuple whereas fetchall return list
        #print(res)
        colnames = [desc[0] for desc in cur.description] 
        cur.close()
        # result.append(tuple(colnames))
        # print(res)
        for row in res:
            #CHECK IF THE WHOLE ROW IN NONE (SPJA Case)
            null_free_row = True
            for val in row:
                if val == None:
                    null_free_row = False
            if null_free_row == True:
                return True
       
    except Exception as error:
        # reveal_globals.error='Unmasque Error: \n Executable could not be run. Error: ' +  dict(error.args[0])['M']
        print('Executable could not be run. Error: ' + str(error))
        raise error
    return False