import pyvisa as visa
import sys
import logging
from SharedLib import PNA

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
logging.root.name="ComPt.py"

def sweep_power(session: visa.resources.Resource, frequency: int= 2400000000, start_power: int=-20, stop_power: int=0) -> None:
    
       session.write("SENSe1:SWEep:TYPE POWer")
       session.write(f"SOURce1:POWer:START {start_power}")
       session.write(f"SOURce1:POWer:STOP {stop_power}")
       session.write(f"SENSe1:FREQuency:FIXed {frequency}")

def parameter_config(session: visa.resources.Resource) -> None:

    session.write("CALCulate1:PARameter:DEFine:EXTended 'ComPt', 'S21'")
    session.write("DISPlay:WINDow1:TRACe1:FEED 'ComPt'")
    session.write("CALCulate1:PARameter:SELect 'ComPt'")
    PNA.resource_status(session)
    session.write("CALCulate1:FORMat MLOGarithmic")
    PNA.resource_status(session)
    session.write("DISPlay:WINDow1:TRACe1:Y:SCALe:AUTO")
    PNA.resource_status(session)
    session.write("SENSe1:AVERage:COUNt 4") # TODO: magic val
    session.write("SENSe1:AVERage:STATe 1")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer:REFerence:STATe 1")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer10:X -20")
    MarkerX10 = session.query("CALCulate1:MARKer10:X?")
    MarkerY10 = session.query("CALCulate1:MARKer10:Y?")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer:STATe 1")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer1:FUNCtion:SELect TARG")
    session.write("CALCulate1:MARKer1:TARGet -2.589769") # TODO: magic number
    session.write("CALCulate1:MARKer1:FUNCtion:TRACking 1")
    print(f'Marker X?{session.query("CALCulate1:MARKer1:X?")}')
    print(f'Marker Y?{session.query("CALCulate1:MARKer1:Y?")}')
    PNA.resource_status(session)
    params = session.query("CALCulate1:PARameter:CATalog?")
    PNA.resource_status(session)
    session.write("CALCulate1:PARameter:SELect 'ComPt'") 
    session.write("FORMat:DATA ASCII,0")
    data = session.query("CALCulate1:DATA? FDATA")
    print(data)
    PNA.resource_status(session)

def main() -> None:
    session = PNA.initiate_comms()
    print(f'\nConnected equipment identification: {PNA.identity(session)}\n')
    # session.write("*RST")
    session.write("*CLS")
    session.write("CALCulate:PARameter:DELete:ALL")
    PNA.resource_status(session)
    sweep_power(session, frequency=2400000000, start_power=0, stop_power=6)
    PNA.resource_status(session)
    parameter_config(session)
    PNA.resource_status(session)
    print(f'Devices available: {session.query("CALCulate1:PARameter:CATalog?")}')

if __name__ == "__main__":
    main()