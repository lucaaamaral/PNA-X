import pyvisa as visa
import sys
import logging
from SharedLib import PNA
import matplotlib.pyplot as plt
from datetime import datetime
import time

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
    session.write("SENSe1:AVERage:COUNt 4") # TODO: magic value
    session.write("SENSe1:AVERage:STATe 1")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer:REFerence:STATe 1")
    PNA.resource_status(session)
    session.write(f"CALCulate1:MARKer10:X MIN") # TODO: magic value
    MarkerX10 = session.query("CALCulate1:MARKer10:X?") # pcap shows -20
    MarkerY10 = session.query("CALCulate1:MARKer10:Y?") # pcap shows -1.589, 0
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer:STATe 1")
    PNA.resource_status(session)
    session.write("CALCulate1:MARKer1:FUNCtion:SELect TARG")
    session.write("CALCulate1:MARKer1:TARGet -2.589769") # TODO: magic number / MarkerY10-1
    session.write("CALCulate1:MARKer1:FUNCtion:TRACking 1")
    print(f'Marker X?{session.query("CALCulate1:MARKer1:X?")}')
    print(f'Marker Y?{session.query("CALCulate1:MARKer1:Y?")}')
    PNA.resource_status(session)

def plot_data(session: visa.resources.Resource, freq: int,
              start_power:int, stop_power: int, 
              meas_offset: float = 0) -> None:
    params = session.query("CALCulate1:PARameter:CATalog?")
    PNA.resource_status(session)
    session.write("CALCulate1:PARameter:SELect 'ComPt'") 
    session.write("FORMat:DATA ASCII,0")
    data = session.query("CALCulate1:DATA? FDATA")
    PNA.resource_status(session)

    data = data.split(",")
    delta = (stop_power - start_power) / len(data)
    ComPt = []
    power = []
    for i in range(len(data)):
        data[i] = float(data[i]) + meas_offset
        ComPt.append(data[0]-1)
        power.append(start_power + delta*i)

    plt.plot(power, data, label="measured gain")
    plt.plot(power, ComPt, label="compression target")
    plt.xlabel(f"Power (dBm)")
    plt.ylabel("Gain")
    plt.title("Compression point")
    plt.legend()

    timestamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%H-%M")
    filename = f"{timestamp}-measurement.txt"

    plt.savefig(f"{timestamp}-measurement.png")
    plt.show()

    with open(filename, "w") as file:
        file.write(f"VAR\tFREQ(real)=\t{freq:.2e}\n")
        file.write(f"BEGIN\tmeasure-{timestamp}\n")
        file.write(f"%\tCOLUMN1_m(real)\tCOLUMN2_m(real)\n")
        for i in range(len(data)):
                file.write(f"\t{power[i]:.3e}\t{data[i]:.3e}\n")
        file.write(f"END\n")


def main() -> None:

    start_pow = -10
    end_pow = 7
    offset = 3

    session = PNA.initiate_comms()
    sweep_power(session, frequency=2400000000, start_power=start_pow, stop_power=end_pow)
    PNA.resource_status(session)
    parameter_config(session)
    PNA.resource_status(session)
    plot_data(session, 2400000000, start_power=start_pow, stop_power=end_pow, meas_offset=offset)

if __name__ == "__main__":
    main()