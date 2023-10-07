import time
from web_api.simpleapi import SimpleApi
from routines.SharedLib.PNA import PNA

def SParamCal_html(payload:str):
    print(f'Recebido payload: {payload}')
    try: 
        with open('web-pages/SParamCal.html', 'r', encoding='utf-8') as file:
            return SimpleApi.http_resource['html'] + file.read().encode('utf-8')
    except:
        print('----- INDEX file not found, sending 404')
        return SimpleApi.http_header['404']

def checkConector(payload:str):
    print(f'Recebido payload: {payload}')
    conectores = "opt1,opt2,opt3".split(",")
    ans = ""
    for con in conectores:
        ans = ans + f',{{"name":"{con}"}}'
    ans = ans[1:]
    print (ans)
    return SimpleApi.http_resource['html'] + f"[{ans}]".encode('utf-8')

def visaAvailable(payload: str):
    print(f'Recebido payload: {payload}')
    ans:str = ''
    for visa in ['teste1', 'teste2']: #PNA.visaAvailable(): # EIEIEIEIEIEIEIEIEIEIII MUDAR AQUI TODO!!!!!
        ans = ans + f',{{"name":"{visa}"}}'
    ans = ans[1:]
    if (len(ans) == 0):
        ans = f'{{"name": "Error loading visa devices"}}'
    print (ans)
    return SimpleApi.http_resource['json'] + f'[{ans}]'.encode('utf-8') + b'\r\n\r\n'


if __name__ == '__main__':
    server = SimpleApi()
    server.configure_endpoints('GET', '/teste', SParamCal_html)
    server.configure_endpoints('POST', '/conector', checkConector)
    server.configure_endpoints('GET', '/visaAvailable', visaAvailable)
    server.begin_workers()
    
