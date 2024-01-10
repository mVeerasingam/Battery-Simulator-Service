# Battery-Simulator-Microservice 🔋💥
## Authors: Mark Veerasingam and Lucas Jeanes
### Description: 
ATU 3rd Year CICD 1 Project

A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM. 
Achieved by recieving and updating the payload from the [Java Job Manager](https://github.com/mVeerasingam/BatterySimulator_JobManager), it generates a simulation
before sending out a post request to Job Manager when the simulation is complete.
The application should handle multiple simulation requests concurrently without blocking.

[PyBaMM](https://github.com/pybamm-team/)(Python Battery Mathematical Model) is developed by Ionworks, The Faraday Institution and NumFocus. Partnering with universities like Oxford and University of Michigan, both recognised leaders in Battery Technology R&D. PyBaMM is an mathematical simulation framework that offers a platform for formulating and solving differential equations related to electrochemical behaviours of batteris andfor simulating battery experiments. https://pybamm.org/

### Current Features:
-   Currently, genereates a single cell Lithium Ion Battery Model, based off a LGM50 Cell's electrochemical properties.
-   Model generated from param inputs: 'upper-voltage cut off', 'lower-voltage cut off', 'nominal cell capacity' and a fixed 'current'.
-   Java Job Manager can send a post request to the microservice and that updates the payload for model generation and simulation.
-   Battery Simulator sends payload back to job manager via post request.

![Battery Simulator](https://github.com/mVeerasingam/Battery-Simulator-Service/raw/main/BatterySim_CICD.drawio.png)

### Supporting Microservices
[Battery Job Manager 🔋🔄]([https://github.com/mVeerasingam/Battery_Sim_CICD.draw.io](https://github.com/mVeerasingam/BatterySimulator-JobManager))

```
Battery-Simulator-Service
├─ .idea
│  ├─ batterySimulator.iml
│  ├─ inspectionProfiles
│  │  └─ profiles_settings.xml
│  ├─ misc.xml
│  ├─ modules.xml
│  └─ vcs.xml
├─ batterySim.png
├─ BatterySimulator
│  ├─ Blueprints
│  │  └─ Simulations
│  │     ├─ Simulation_DriveCycle.py
│  │     ├─ Simulation_SingleCell.py
│  │     └─ __pycache__
│  │        ├─ Simulation_DriveCycle.cpython-311.pyc
│  │        └─ Simulation_SingleCell.cpython-311.pyc
│  ├─ Dockerfile
│  ├─ DriveCycle_Data
│  │  └─ US06.csv
│  ├─ Main.py
│  └─ requirements.txt
├─ README.md
└─ ToDo.txt

```
