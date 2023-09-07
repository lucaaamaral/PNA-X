import pyvisa as visa
import sys
import logging
from SharedLib import PNA

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")
logging.root.name="SParamCal.py"

def parameter_config(session: visa.resources.Resource, 
                     num: int, name: str, meas: str, 
                     freq_start: float = 2000000000.0, 
                     freq_stop:float = 3000000000.0,
                     sweep_points = 201, amplitude_dB:float=-20.0) -> None:
    session.write("SENSe1:SWEep:TYPE LINear")
    session.write(f"SENSe1:FREQuency:STARt {freq_start}") # TODO: test if works
    session.write(f"SENSe1:FREQuency:STOP {freq_stop}") # TODO: test if works
    PNA.resource_status(session) 
    session.write(f"SENSe1:SWEep:POINTs {sweep_points}")
    PNA.resource_status(session) 

    session.write(f"CALCulate1:PARameter:DEFine:EXTended '{name}','{meas}'")
    session.write(f"DISPlay:WINDow1:TRACe{num}:FEED '{name}'")
    session.write(f"CALCulate1:PARameter:SELect '{name}'")
    PNA.resource_status(session) 
    session.write(f"CALCulate1:PARameter:SELect '{name}'")
    session.write("CALCulate1:FORMat MLOGarithmic")
    PNA.resource_status(session) 
    session.write(f"SOURce1:POWer1:LEVel:IMMediate:AMPLitude {amplitude_dB}") # TODO: test if works
    session.write(f"SENSe1:BANDwidth:RESolution 10000.000000") # TODO: magic value
    session.write(f"SENSe1:AVERage:COUNt 20")
    session.write("SENSe1:AVERage:STATe 1")
    PNA.resource_status(session) 

def guided_calibration(session: visa.resources.Resource) -> None:

    connectors = session.query("SENSe1:CORRection:COLLect:GUIDed:CONN:CAT?").replace('"', '').split(", ")
    for i in [1, 2, 3, 4]:

        print(f"Connectors available for PORT {i}:")
        for connector in connectors:
            print(f"\t{connector}")

        selected_connector=input(f"Copy and paste one of the above available connectors for PORT {i}:\n\t-> ") # TODO: test if {i} works
        session.write(f'SENSe1:CORRection:COLLect:GUIDed:CONNector:PORT{i}:SELect "{selected_connector}"')
        
        cal_kit = session.query(f'SENS1:CORR:COLL:GUID:CKIT:CAT? "{selected_connector}"').replace('"', '').split(", ")
        if (len(cal_kit)!=0):
            print(f"Calibration kits available for PORT {i}:")
            for c_kit in cal_kit:
                print(c_kit)
            selected_cal_kit=input(f"Copy and paste one of the above available calibration kits for PORT {i}:\n\t-> ") # TODO: test {i} if works

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
    
def save_cal_set( session: visa.resources.Resource, 
                save: bool = False, my_cal_set: str = "visa_calibration") -> None:
    
    # TODO: test is this funcionality works
    cal_set_names = session.query("SENSe1:CORRection:CSET:CATalog? NAME").replace('"', '').split(", ")
    if my_cal_set in cal_set_names:
        session.write(f"SENSe1:CORRection:CSET:DELete '{my_cal_set}'")
        PNA.resource_status(session)
    session.write(f"SENSe1:CORRection:CSET:COPY '{my_cal_set}'")
    PNA.resource_status(session)

def main():

    calibrate = True

    session = PNA.initiate_comms()

    start_freq = 2000000000
    stop_freq = 3000000000
    sweep_pt = 201
    dB_amp = -20

    parameter_config(session, 1, "gain", 'S21', 
                     start_freq, stop_freq,
                     sweep_pt, dB_amp)
    parameter_config(session, 2, "InputRL", 'S11',
                     start_freq, stop_freq, 
                     sweep_pt, dB_amp)
    parameter_config(session, 3, "loss", 'S12',
                     start_freq, stop_freq, 
                     sweep_pt, dB_amp)
    parameter_config(session, 4, "OutputRL", 'S22',
                     start_freq, stop_freq, 
                     sweep_pt, dB_amp)

    if calibrate:
        guided_calibration(session)
        PNA.resource_status(session) 

    print_params(session)

    save_cal_set(session, False, "todaycal")
    sys.exit()

if __name__ == "__main__":
    main()