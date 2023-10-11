#parsing
import pandas as pd
import json
df = pd.read_excel(r'~/Downloads/All-Messages-search-result.xlsx')

def santizite(mess):
    for i,m in enumerate(mess):

        if ']' in m:
            m = m.strip(']')
        if 'torii-request-id=' in m:
            m = m.strip('torii-request-id=')
        if '"' in m:
            mess[i] = m.strip('"')
        if '[' in m:
            mess[i] = m.strip('[')

    if '' in mess:
        mess.remove('')
    return mess

def remove_missing(mes):
    j=0
    for n,c in enumerate(mes):
        if c == '-' and n==len(mes)-1 or c=='-' and n==len(mes) or n-1==len(mes) and c=='-':
            if j==0:
                pass
            else:
                mes = mes[:n-1]+ '0' + mes[n+1:]
            j+=1
        elif c == '-' and mes[n+1] == ' ' :
            if j==0:
                pass
            else:
                mes = mes[:n-1]+ '0' + mes[n+1:]
            j+=1
    return mes

def split_string(mes):
    mess = mes.split(' ')
    mess = mess[0].split('-') + mess[1:]
    mess = mess[:1] + mess[1].split('[') + mess[2:]
    return mess

def main(df):
    new_list =[]
    j = 0
    for i,mes in enumerate(df['message']):
        
        if len(mes) > 36:
            if mes[0] == '{':

                mess = json.loads(mes)
                headers = mess['headers']
                mess = mess| headers
                del mess['headers']

                if j == 0:
                    df2 = pd.DataFrame.from_dict(mess)
                else:
                    df3 = pd.DataFrame.from_dict(mess)
                    df2 = pd.concat([df2, df3])
                j+=1
            else:

                mess = split_string(mes)
                mess = santizite(mess)
                mess_user = " ".join(mess[11:-1])

                mess = mess[:11] + [mess_user] + mess[-1:]
                new_list.append(mess)



    
    df1 = pd.DataFrame(new_list, columns = ['remote_addr','some', 'remote_user', 'Date','seconds', 'method','url','version', 'status','Content-Length', 'referer','user_agent','torii-request-id']) #  
    df = pd.concat([df1,df2])

    for column in df.columns:
        print(df[column].value_counts())
main(df)