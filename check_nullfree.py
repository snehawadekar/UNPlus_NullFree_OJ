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
        if res is not None:
            for row in res:
                #CHECK IF THE WHOLE ROW IN NONE (SPJA Case)
                nullrow = True
                for val in row:
                    if val != None:
                        nullrow = False
                        # break
                if nullrow == True:
                    continue
                else:
                    #return true if found one null free result else, continue
                    return True
    except Exception as error:
        # reveal_globals.error='Unmasque Error: \n Executable could not be run. Error: ' +  dict(error.args[0])['M']
        print('Executable could not be run. Error: ' + str(error))
        raise error
    return False