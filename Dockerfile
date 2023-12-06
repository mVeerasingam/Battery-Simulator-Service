# Note -Mark:
# I Specifically contairised 3.11 as I encountered issues on python 3.12 installation of PyBaMM.
# C:\Users\markv\Documents\Repos\PyBaMM_BatterySimulator_Prototype> & C:/Python312/python.exe c:/Users/markv/Documents/Repos/PyBaMM_BatterySimulator_Prototype/Simulator_v24_Release.py
# Running code produced "Error: Could not find parameter Chen2020"

FROM python:3.11-slim

RUN pip install --upgrade pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8084

CMD ["python", "./BatterySimulatorController.py"]
