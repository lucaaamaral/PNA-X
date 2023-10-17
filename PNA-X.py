import time, json, signal, logging, sys
from web_api.simpleapi import SimpleApi
from routines.SharedLib.PNA import PNA

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
logging.root.name="PNA-X.py"

def signal_handler(signum, frame):
    print(f"Requested exit")
    SimpleApi.shutdown_requested = True
    PNA.notSoGracefulExit()
    logging.debug("Exiting code")
    sys.exit()

signal.signal(signal.SIGINT, signal_handler)

def style_css(payload:str):
    print(f'Recebido payload: {payload}')
    try: 
        with open('web-pages/style.css', 'r', encoding='utf-8') as file:
            return SimpleApi.http_resource['css'] + file.read().encode('utf-8')
    except:
        print('INDEX file not found, sending 404')
        return SimpleApi.http_header['404']
    
def start_html(payload:str):
    print(f'Recebido payload: {payload}')
    try: 
        with open('web-pages/index.html', 'r', encoding='utf-8') as file:
            return SimpleApi.http_resource['html'] + file.read().encode('utf-8')
    except:
        print('INDEX file not found, sending 404')
        return SimpleApi.http_header['404']
    
def SParamCal_html(payload:str):
    print(f'Recebido payload: {payload}')
    try: 
        with open('web-pages/SParamCal.html', 'r', encoding='utf-8') as file:
            return SimpleApi.http_resource['html'] + file.read().encode('utf-8')
    except:
        print('INDEX file not found, sending 404')
        return SimpleApi.http_header['404']
    
def ComPt_html(payload:str):
    print(f'Recebido payload: {payload}')
    try: 
        with open('web-pages/ComPt.html', 'r', encoding='utf-8') as file:
            return SimpleApi.http_resource['html'] + file.read().encode('utf-8')
    except:
        print('INDEX file not found, sending 404')
        return SimpleApi.http_header['404']
    
def getConnectorOpt(payload:str):
    print(f'Recebido payload: {payload}')

    # conectores = PNA.queryConnector() # TODO uncomment     
    conectores = ["opt1","opt2","opt3"]
    ans = ""
    for con in conectores:
        ans = ans + f',{{"name":"{con}"}}'
    ans = ans[1:]
    print (ans)
    return SimpleApi.http_resource['html'] + f"[{ans}]".encode('utf-8')
    
def getCalkitOpt(payload:str):
    print(f'Recebido payload: {payload}')

    # calkit = PNA.queryCalkit(payload) # TODO uncomment     
    calkit = ["opt1","opt2","opt3"]
    ans = ""
    for con in calkit:
        ans = ans + f',{{"name":"{con}"}}'
    ans = ans[1:]
    print (ans)
    return SimpleApi.http_resource['html'] + f"[{ans}]".encode('utf-8')

def getVisaAvailable(payload: str):
    print(f'Recebido payload: {payload}')
    ans:str = ''
    for visa in  PNA.visaAvailable():
        ans = ans + f',{{"name":"{visa}"}}'
    ans = ans[1:]
    if (len(ans) == 0):
        ans = f'{{"name": "Error loading visa devices"}}'
    
    return SimpleApi.http_resource['json'] + f'[{ans}]'.encode('utf-8') + b'\r\n\r\n'

def postVisaConnect(payload: str):
    print(f'Recebido payload: {payload}')
    # PNA.initiate(payload) # TODO: uncoment
    # error = PNA.queryError()
    error = None
    if error == None:
        return SimpleApi.http_header['200']
    else:
        return SimpleApi.http_header['404'] + error.encode('utf-8')


def start_sparam(payload: str):
    print(f'Recebido payload: {payload}')

    data = json.loads(payload)

    try:
        # visa = data['visa']
        init_freq =         float(data['init_freq'])
        init_freq_unit =    data['init_freq_unit']
        end_freq =          float(data['end_freq'])
        end_freq_unit =     data['end_freq_unit']
        sweep_pt =          int(data['sweep_pt'])
        power =             int(data['power'])
        average =           int(data['average'])
        # ports_number = data['ports_number']
        conn_1 = data['conn_1']
        ckit_1 = data['ckit_1']
        conn_2 = data['conn_2']
        ckit_2 = data['ckit_2']
        conn_3 = data['conn_3']
        ckit_3 = data['ckit_3']
        conn_4 = data['conn_4']
        ckit_4 = data['ckit_4']
        calibrate = data['calibrate']
        save = data['save']


        if not (init_freq_unit in ['Hz', 'kHz', 'MHz', 'GHz'] and end_freq_unit in ['Hz', 'kHz', 'MHz', 'GHz']):
            return SimpleApi.http_header['400']

    except:
        return SimpleApi.http_header['400']

    
    if (init_freq_unit == 'Hz'): pass
    elif (init_freq_unit == 'kHz'): init_freq *= 1000
    elif (init_freq_unit == 'MHz'): init_freq *= 1000000
    elif (init_freq_unit == 'GHz'): init_freq *= 1000000000
    PNA.SParam.freq_start = init_freq

    if (end_freq_unit == 'Hz'): pass
    elif (end_freq_unit == 'kHz'): end_freq *= 1000
    elif (end_freq_unit == 'MHz'): end_freq *= 1000000
    elif (end_freq_unit == 'GHz'): end_freq *= 1000000000
    PNA.SParam.freq_stop = end_freq

    PNA.SParam.sweep_points = sweep_pt
    PNA.SParam.amplitude_dB = power
    PNA.SParam.average = average

    try:
        # TODO: this congigure function could be simplified but testing is needed
        PNA.SParam.configure(num=1, name='gain', meas='S21')
        PNA.SParam.configure(num=2, name='InputRL', meas='S11')
        PNA.SParam.configure(num=3, name='loss', meas='S12')
        PNA.SParam.configure(num=4, name='OutputRL', meas='S22')

        if calibrate == "true":
            # TODO: this function still requires waaaay much work to interact with the webpage - > code 100?
            PNA.SParam.guided_calibration(connectors=[conn_1, conn_2, conn_3, conn_4], 
                                        calkits=[ckit_1, ckit_2, ckit_3, ckit_4])

        if save == "true":
            PNA.SParam.save_cal_set(my_cal_set="visa_calibration"); 
    except Exception as e:
        return SimpleApi.http_header['417'] + str(e).encode('utf-8')
    
    PNA.session.close()       

    if PNA.error == None:
        return SimpleApi.http_header['200']
    else:
        return SimpleApi.http_header['404'] + PNA.error.encode('utf-8')

def last_img (payload:str):
    print(f'Recebido payload: {payload}')

    try:
        PNA.ComPt.last_image = 'web-pages/imagem.webp' # TODO: remove this line
        with open(PNA.ComPt.last_image, 'rb') as file:
            return SimpleApi.http_resource['png'] + file.read()
    except: return SimpleApi.http_header['404']


def start_compt(payload: str):
    print(f'Recebido payload: {payload}')

    data = json.loads(payload)

    try:
        freq =         int(float(data['freq']))
        freq_unit =    data['freq_unit']
        average =      int(data['average'])
        start_pow =    int(data['start_pow'])
        stop_pow =     int(data['stop_pow'])
        offset =       float(data['offset'])

        if not (freq_unit in ['Hz', 'kHz', 'MHz', 'GHz']):
            return SimpleApi.http_header['400']
    except Exception as e:
        return SimpleApi.http_header['400']

    if (freq_unit == 'Hz'): pass
    elif (freq_unit == 'kHz'): freq *= 1000
    elif (freq_unit == 'MHz'): freq *= 1000000
    elif (freq_unit == 'GHz'): freq *= 1000000000

    PNA.ComPt.frequency = freq
    PNA.ComPt.average = average
    PNA.ComPt.start_power = start_pow
    PNA.ComPt.stop_power = stop_pow
    PNA.ComPt.offset = offset
    PNA.ComPt.frequency = freq

    try:
        PNA.ComPt.sweep_power()
        PNA.ComPt.parameter_config()
        PNA.ComPt.plot_data()
    except Exception as e:
        return SimpleApi.http_header['417'] + str(e).encode('utf-8')

    if (PNA.error == None):
        return SimpleApi.http_header['200']
    else:
        return SimpleApi.http_header['400'] + str(PNA.error).encode('utf-8')


if __name__ == '__main__':
    server = SimpleApi()

    # GUI resources
    server.configure_endpoints('GET', '/', start_html)
    server.configure_endpoints('GET', '/style.css', style_css)
    server.configure_endpoints('GET', '/sparam', SParamCal_html)
    server.configure_endpoints('GET', '/compt', ComPt_html)
    server.configure_endpoints('GET', '/last_img', last_img)

    # VISA endpoints
    server.configure_endpoints('GET', '/visaAvailable', getVisaAvailable)
    server.configure_endpoints('POST', '/connectTo', postVisaConnect)
    server.configure_endpoints('GET', '/connector', getConnectorOpt)
    server.configure_endpoints('POST', '/calkit', getCalkitOpt)

    # Start function
    server.configure_endpoints('POST', '/start_sparam', start_sparam)
    server.configure_endpoints('POST', '/start_compt', start_compt)


    server.begin_workers()
    

    while not SimpleApi.shutdown_requested:
        time.sleep(1)

# TODO: error handling from visa to UI
