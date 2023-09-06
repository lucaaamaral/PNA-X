import pyvisa as visa
import sys
import logging

logger = logging.getLogger("PNA.py")

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
