# Note -Mark:
# I Specifically contairised 3.11 as I encountered issues on python 3.12 installation of PyBaMM.
# C:\Users\markv\Documents\Repos\PyBaMM_BatterySimulator_Prototype> & C:/Python312/python.exe c:/Users/markv/Documents/Repos/PyBaMM_BatterySimulator_Prototype/Simulator_v24_Release.py
# Running code produced "Error: Could not find parameter Chen2020"

FROM python:3.11-alpine
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./BatterySimulatorController.py