import pyvisa as visa
import sys, time
import logging

logger = logging.getLogger("PNA.py")

class PNA:

    manager = visa.ResourceManager()
    session: visa.Resource = None
    busy: bool = False
    error: str = None
    
    def queryError() -> str:
        tmp = PNA.error
        PNA.error = None
        return tmp

    def queryConnector() -> list:
        return PNA.session.query("SENSe1:CORRection:COLLect:GUIDed:CONN:CAT?").replace('"', '').split(", ")
    
    def queryCalkit(selected_connector:str) -> list:
        return PNA.session.query(f'SENS1:CORR:COLL:GUID:CKIT:CAT? "{selected_connector}"').replace('"', '').split(", ")
    
    def notSoGracefulExit() -> None:
        if PNA.session:
            PNA.session.close()
        PNA.manager.close()
        print("Closed visa")

    def visaAvailable() -> list:
        while PNA.busy: time.sleep(0.1)
        return PNA.manager.list_resources()
    
    def initiate(VISA_ADDRESS: str) -> None:
        while PNA.busy: time.sleep(0.1)
        PNA.busy = True
        logger.info("Initiating connection to the instrument.")

        try:
            PNA.session = PNA.manager.open_resource(VISA_ADDRESS)
            PNA.session.timeout = 12000
            PNA.session.write_termination = ''
            # print(f'\nConnected equipment identification: {PNA.identity()}\n')
            PNA.session.write("*CLS")
            PNA.session.write("CALCulate:PARameter:DELete:ALL")
            PNA.resource_status()
        except visa.errors.VisaIOError as e:
            logger.error(f"{e}")
            PNA.error = repr(e)
            PNA.session.close()

        PNA.busy = False

    def identity() -> str:
        return PNA.session.query("*IDN?")
    
    def resource_status():

        # TODO: implement rest of messages logic annd threat it properly
        # TODO: raise exception?? -> might lead to no response sent

        bitmap = {
            "all clear": 0,
            "error": 1<<2,
            "questionable summary": 1<<3,
            "message available": 1<<4,
            "standard event": 1<<5,
            "request service": 1<<6,
            "operation register": 1<<7
        }
        status = int(PNA.session.query("*STB?"))

        if (status == bitmap["all clear"]):
            pass
        elif (status & bitmap["error"]):
            PNA.error = PNA.session.query("SYSTem:ERRor?")
            logger.error(f"Mapped error {PNA.error}")
        elif (status & bitmap["questionable summary"]):
            logger.warn("resource_status: questionable summary")
            pass #TODO: implement the rest of those messsages if necessary
        elif (status & bitmap["message available"]):
            logger.warn("resource_status: message available")
            pass #TODO: implement the rest of those messsages if necessary
        elif (status & bitmap["standard event"]):
            logger.warn("resource_status: standard event")
            pass #TODO: implement the rest of those messsages if necessary
        elif (status & bitmap["request service"]):
            logger.warn("resource_status: request service")
            pass #TODO: implement the rest of those messsages if necessary
        elif (status & bitmap["operation register"]):
            logger.warn("resource_status: operation register")
            pass #TODO: implement the rest of those messsages if necessary
        else:
            logger.warn(f"resource_status: wrong status message recceived: '{status}', please verify")
            pass #TODO: implement the rest of those messsages if necessary

    class SParam:

        freq_start: float 
        freq_stop: float
        sweep_points: int 
        amplitude_dB: float
        average: int

        def configure(num: int, name: str, meas: str) -> None:
            
            PNA.session.write("SENSe1:SWEep:TYPE LINear")
            PNA.session.write(f"SENSe1:FREQuency:STARt {PNA.SParam.freq_start}")
            PNA.session.write(f"SENSe1:FREQuency:STOP {PNA.SParam.freq_stop}")
            PNA.resource_status(PNA.session) 
            PNA.session.write(f"SENSe1:SWEep:POINTs {PNA.SParam.sweep_points}")
            PNA.resource_status(PNA.session) 

            PNA.session.write(f"CALCulate1:PARameter:DEFine:EXTended '{name}','{meas}'")
            PNA.session.write(f"DISPlay:WINDow1:TRACe{num}:FEED '{name}'")
            PNA.session.write(f"CALCulate1:PARameter:SELect '{name}'")
            PNA.resource_status(PNA.session) 
            PNA.session.write(f"CALCulate1:PARameter:SELect '{name}'")

            PNA.session.write("CALCulate1:FORMat MLOGarithmic")
            PNA.resource_status(PNA.session) 
            PNA.session.write(f"SOURce1:POWer1:LEVel:IMMediate:AMPLitude {PNA.SParam.amplitude_dB}")
            PNA.session.write(f"SENSe1:BANDwidth:RESolution 10000.000000") # TODO: magic value
            PNA.session.write(f"SENSe1:AVERage:COUNt {PNA.SParam.average}") # TODO: Test if this works
            PNA.session.write("SENSe1:AVERage:STATe 1")
            PNA.resource_status(PNA.session) 

        def guided_calibration(connectors: list, calkits: list) -> None:
            # TODO: needs wotk with interacting with webpage
            for i in [1, 2, 3, 4]:
                PNA.session.write(f'SENSe1:CORRection:COLLect:GUIDed:CONNector:PORT{i}:SELect "{connectors[i-1]}"')
                PNA.session.write(f'SENSe1:CORRection:COLLect:GUIDed:CKIT:PORT{i} "{calkits[i-1]}"')
            
            PNA.session.write("SENSe1:CORRection:PREFerence:ECAL:ORIentation:STATe 0")
            PNA.session.write("SENSe1:CORRection:COLLect:GUIDed:INITiate")

            steps = int(PNA.session.query("SENSe1:CORRection:COLLect:GUIDed:STEPs?"))

            for i in range(1, steps+1):
                print(PNA.session.query(f"SENSe1:CORRection:COLLect:GUIDed:DESCription? {i}"))
                _ = input("Press enter when done") # TODO: interact with oppened session
                PNA.session.write(f"SENSe1:CORRection:COLLect:GUIDed:ACQuire STAN{i}")
            
            PNA.session.write("SENSe1:CORRection:COLLect:GUIDed:SAVE")
            PNA.resource_status(PNA.session)

        def save_cal_set(my_cal_set: str = "visa_calibration") -> None:
            
            cal_set_names = PNA.session.query("SENSe1:CORRection:CSET:CATalog? NAME").replace('"', '').split(", ")
            if my_cal_set in cal_set_names:
                PNA.session.write(f"SENSe1:CORRection:CSET:DELete '{my_cal_set}'")
                PNA.resource_status(PNA.session)
            PNA.session.write(f"SENSe1:CORRection:CSET:COPY '{my_cal_set}'")
            PNA.resource_status(PNA.session)


def initiate_comms(VISA_ADDRESS: str='TCPIP0::A-N5241A-11745.local::hislip0::INSTR') -> visa.resources.Resource:
    logger.info("Initiating connection to the instrument.")
    print("Initiating connection to the instrument.")
    if ( VISA_ADDRESS == None):
        print("Resources available:")
        for resource in visa.ResourceManager().list_resources():
            print(f"\t{resource}")
        VISA_ADDRESS=input(f"Copy and paste one of the above available devices:\n\t-> ")
    try:
        session = visa.ResourceManager().open_resource(VISA_ADDRESS)
        session.timeout = 12000
        session.write_termination = ''
        print(f'\nConnected equipment identification: {identity(session)}\n')
        # session.write("*RST")
        session.write("*CLS")
        session.write("CALCulate:PARameter:DELete:ALL")
        resource_status(session)
        return session
    except visa.errors.VisaIOError as e:
        print(f"Selected address not found, ERROR: {e}")
        sys.exit()

def identity(session: visa.resources.Resource) -> str:
    return session.query("*IDN?")

def resource_status(session: visa.resources.Resource):
    #TODO: implement rest of messages logic annd threat it properly
    bitmap = {
        "all clear": 0,
        "error": 1<<2,
        "questionable summary": 1<<3,
        "message available": 1<<4,
        "standard event": 1<<5,
        "request service": 1<<6,
        "operation register": 1<<7
    }
    status = int(session.query("*STB?"))

    if (status == bitmap["all clear"]):
        pass
    elif (status & bitmap["error"]):
        error = session.query("SYSTem:ERRor?")
        print(f"An error hass been found: {error}")
        print("Exiting the code")
        sys.exit()
    elif (status & bitmap["questionable summary"]):
        print("resource_status: questionable summary")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
    elif (status & bitmap["message available"]):
        print("resource_status: message available")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
    elif (status & bitmap["standard event"]):
        print("resource_status: standard event")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
    elif (status & bitmap["request service"]):
        print("resource_status: request service")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
    elif (status & bitmap["operation register"]):
        print("resource_status: operation register")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
    else:
        print(f"resource_status: wrong status message recceived: '{status}', please verify")
        pass #TODO: implement the rest of those messsages if necessary
        print("Exiting the code")
        sys.exit()
