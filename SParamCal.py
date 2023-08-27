import pyvisa as visa
import sys
import logging
from SharedLib import PNA

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
logging.root.name="SParamCal.py"

def parameter_config(session: visa.resources.Resource, num: int, name: str, meas: str) -> None:
    session.write("SENSe1:SWEep:TYPE LINear")
    session.write("SENSe1:FREQuency:STARt 2000000000.000000")
    session.write("SENSe1:FREQuency:STOP 3000000000.000000")
    PNA.resource_status(session) 
    session.write("SENSe1:SWEep:POINTs 201")
    PNA.resource_status(session) 

    session.write(f"CALCulate1:PARameter:DEFine:EXTended '{name}','{meas}'")
    session.write(f"DISPlay:WINDow1:TRACe{num}:FEED '{name}'")
    session.write(f"CALCulate1:PARameter:SELect '{name}'")
    PNA.resource_status(session) 
    session.write(f"CALCulate1:PARameter:SELect '{name}'")
    session.write("CALCulate1:FORMat MLOGarithmic")
    PNA.resource_status(session) 
    session.write("SOURce1:POWer1:LEVel:IMMediate:AMPLitude -20.000000")
    session.write("SENSe1:BANDwidth:RESolution 10000.000000")
    session.write("SENSe1:AVERage:COUNt 20")
    session.write("SENSe1:AVERage:STATe 1")
    PNA.resource_status(session) 

def guided_calibration(session: visa.resources.Resource) -> None:

    connectors = session.query("SENSe1:CORRection:COLLect:GUIDed:CONN:CAT?").split(", ")
    # connectors = connectors.split(", ")
    for i in [1, 2, 3, 4]:

        print(f"Connectors available for PORT {i}:")
        for connector in connectors:
            print(f"\t{connector}")

        selected_connector=input(f"Copy and paste one of the above available connectors for PORT:\n\t-> ")
        print(f"Calibration kits available for PORT {i}:")
        for cal_kit in session.query(f'SENS1:CORR:COLL:GUID:CKIT:CAT? "{selected_connector}"').split(", "):
            print(cal_kit)
        selected_cal_kit=input("Copy and paste one of the above available calibration kits for PORT:\n\t-> ")

        session.write(f'SENSe1:CORRection:COLLect:GUIDed:CONNector:PORT{i}:SELect "{selected_connector}"')
        session.write(f'SENSe1:CORRection:COLLect:GUIDed:CKIT:PORT{i} "{selected_cal_kit}"')
    
    session.write("SENSe1:CORRection:PREFerence:ECAL:ORIentation:STATe 0")
    session.write("SENSe1:CORRection:COLLect:GUIDed:INITiate")

    steps = int(session.query("SENSe1:CORRection:COLLect:GUIDed:STEPs?"))
    for i in range(1, steps+1):
       print(session.query(f"SENSe1:CORRection:COLLect:GUIDed:DESCription? {i}"))
       _ = input("Press enter when done")
       session.write(f"SENSe1:CORRection:COLLect:GUIDed:ACQuire STAN{i}")
    
    session.write("SENSe1:CORRection:COLLect:GUIDed:SAVE")
    PNA.resource_status(session)

def print_params(session: visa.resources.Resource):

    for i in [1, 2, 3, 4]:
        session.write(f"DISPlay:WINDow1:TRACe{i}:Y:SCALe:AUTO")
    
    print(f'Parameter catalog: {session.query("CALCulate1:PARameter:CATalog?")}')

    for name in ["InputRL", "loss", "gain", "OutputRL"]:
        session.write(f"CALCulate1:PARameter:SELect '{name}'")
        session.write("FORMat:DATA ASCII,0")

        PNA.resource_status(session) 

        print(f"{name} data below:\n")
        data = session.query("CALCulate1:DATA? FDATA")

        print(data)
        PNA.resource_status(session)
    
def main():

    calibrate = True

    session = PNA.initiate_comms()

    session.timeout = 12000
    session.write_termination = ''

    print(f'\nConnected equipment identification: {PNA.identity(session)}\n')
    # session.write("*RST")
    session.write("*CLS")

    # print(f'Parameter catalog: {session.query("CALCulate1:PARameter:CATalog?")}')

    session.write("CALCulate:PARameter:DELete:ALL")

    if calibrate:
        PNA.resource_status(session) 
     
    parameter_config(session, 1, "gain", 'S21')
    parameter_config(session, 2, "InputRL", 'S11')
    parameter_config(session, 3, "loss", 'S12')
    parameter_config(session, 4, "OutputRL", 'S22')

    print(f'Parameter catalog: {session.query("CALCulate1:PARameter:CATalog?")}')


    if calibrate:
        guided_calibration(session)
        PNA.resource_status(session) 

    print_params(session)

    sys.exit()

    session.clear()


if __name__ == "__main__":
    main()