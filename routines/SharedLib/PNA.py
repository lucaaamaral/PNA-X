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
            raise Exception(PNA.error)
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

            # TODO: interact with oppened PNA.session
            # BIIIIIIIG TODO
            for i in range(1, steps+1):
                print(PNA.session.query(f"SENSe1:CORRection:COLLect:GUIDed:DESCription? {i}"))
                _ = input("Press enter when done") # TODO: interact with oppened PNA.session
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

    class ComPt:

        frequency: int
        start_power: int
        stop_power: int
        average: int
        offset: float
        last_image: str
        last_datafile: str

        def sweep_power() -> None:
            # Requires three variables to be set:
            # # frequency
            # # start_power
            # # stop_power
            PNA.session.write("SENSe1:SWEep:TYPE POWer")
            PNA.session.write(f"SOURce1:POWer:START {PNA.ComPt.start_power}")
            PNA.session.write(f"SOURce1:POWer:STOP {PNA.ComPt.stop_power}")
            PNA.session.write(f"SENSe1:FREQuency:FIXed {PNA.ComPt.frequency}")
            PNA.resource_status()

        def parameter_config() -> None:
            # Requires one variable to be set:
            # # average
            PNA.session.write("CALCulate1:PARameter:DEFine:EXTended 'ComPt', 'S21'")
            PNA.session.write("DISPlay:WINDow1:TRACe1:FEED 'ComPt'")
            PNA.session.write("CALCulate1:PARameter:SELect 'ComPt'")
            PNA.resource_status()
            PNA.session.write("CALCulate1:FORMat MLOGarithmic")
            PNA.resource_status()
            PNA.session.write("DISPlay:WINDow1:TRACe1:Y:SCALe:AUTO")
            PNA.resource_status()
            PNA.session.write(f"SENSe1:AVERage:COUNt {PNA.ComPt.average}")
            PNA.session.write("SENSe1:AVERage:STATe 1")
            PNA.resource_status()
            PNA.session.write("CALCulate1:MARKer:REFerence:STATe 1")
            PNA.resource_status()
            PNA.session.write(f"CALCulate1:MARKer10:X MIN") # TODO: magic value
            MarkerX10 = PNA.session.query("CALCulate1:MARKer10:X?") # pcap shows -20
            MarkerY10 = PNA.session.query("CALCulate1:MARKer10:Y?") # pcap shows -1.589, 0
            PNA.resource_status()
            PNA.session.write("CALCulate1:MARKer:STATe 1")
            PNA.resource_status()
            PNA.session.write("CALCulate1:MARKer1:FUNCtion:SELect TARG")
            PNA.session.write("CALCulate1:MARKer1:TARGet -2.589769") # TODO: magic number / MarkerY10 - 1 ?
            PNA.session.write("CALCulate1:MARKer1:FUNCtion:TRACking 1")
            print(f'Marker X?{PNA.session.query("CALCulate1:MARKer1:X?")}') # TODO: remove this print
            print(f'Marker Y?{PNA.session.query("CALCulate1:MARKer1:Y?")}')
            PNA.resource_status()

        def plot_data() -> None:
            # Requires four variables to be set:
            # # frequency
            # # start_power
            # # stop_power
            # # offset
            import matplotlib.pyplot as plt
            from datetime import datetime
            
            # params = PNA.session.query("CALCulate1:PARameter:CATalog?") # TODO: query to verify if parameters are corectly set
            # PNA.resource_status()
            PNA.session.write("CALCulate1:PARameter:SELect 'ComPt'") 
            PNA.session.write("FORMat:DATA ASCII,0")
            data = PNA.session.query("CALCulate1:DATA? FDATA")
            PNA.resource_status()

            data = data.split(",")
            delta = (PNA.ComPt.start_power - PNA.ComPt.stop_power) / len(data)
            ComPt = []
            power = []
            for i in range(len(data)):
                data[i] = float(data[i]) + PNA.ComPt.offset
                ComPt.append(data[0]-1)
                power.append(PNA.ComPt.start_power + delta*i)

            # print(data)

            plt.plot(power, data, label="measured gain")
            plt.plot(power, ComPt, label="compression target")
            plt.xlabel(f"Power (dBm)")
            plt.ylabel("Gain")
            plt.title("Compression point")
            plt.legend()
            # plt.show()

            # TODO: return the processed data to the javascript to plot in a HTML canvas style

            timestamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%H-%M")
            filename = f"{timestamp}-measurement.txt"

            plt.savefig(f"{timestamp}-measurement.png")
            PNA.ComPt.last_image = f"{timestamp}-measurement.png"
            PNA.ComPt.last_datafile = f"{timestamp}-measurement.txt"
    
            with open(filename, "w") as file:
                file.write(f"VAR\tFREQ(real)=\t{PNA.ComPt.frequency:.2e}\n")
                file.write(f"BEGIN\tmeasure-{timestamp}\n")
                file.write(f"%\tCOLUMN1_m(real)\tCOLUMN2_m(real)\n")
                for i in range(len(data)):
                        file.write(f"\t{power[i]:.3e}\t{data[i]:.3e}\n")
                file.write(f"END\n")
