# Battery-Simulator-Microservice 🔋💥
## Authors: Mark Veerasingam and Lucas Jeanes
### Description: 
ATU 3rd Year CICD 1 Project

A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM. 
Achieved by recieving and updating the payload from the [Java Job Manager](https://github.com/mVeerasingam/BatterySimulator-JobManager/tree/master), it generates a simulation
before sending out a post request to Job Manager when the simulation is complete.
The application should handle multiple simulation requests concurrently without blocking.

[PyBaMM](https://github.com/pybamm-team/)(Python Battery Mathematical Model) is developed by Ionworks, The Faraday Institution and supported by Non profits like NumFocus. Partnering with universities like Oxford and University of Michigan, both recognised leaders in Battery Technology R&D. PyBaMM is an mathematical simulation framework that offers a platform for formulating and solving differential equations related to electrochemical behaviours of batteris andfor simulating battery experiments. https://pybamm.org/

### Current Features:
-   Genereates a single cell Lithium Ion Battery Model, based off a LGM50 Cell's electrochemical properties.
-   Generates a drive cycle of the based of the same cell.
-   Model generated from param inputs: 'upper-voltage cut off', 'lower-voltage cut off', 'nominal cell capacity' and a fixed 'current'.
-   Java Job Manager can send a post request to the microservice and that updates the payload for model generation and simulation.
-   Battery Simulator sends payload back to job manager via post request.

## Instructions:
### Running the application From Docker:
- [Pull the Lithium Ion Battery Simulator Artifact Repository from Docker Hub](https://hub.docker.com/repository/docker/mveerasingam/batterysimulator_jobmanagerservice/general)
  - We found an issue when trying the command
    
    `docker pull mveerasingam/batterysimulator_jobmanagerservice`
    
    Produced an **Error response from daemon: manifest for mveerasingam/batterysimulator_jobmanagerservice:latest not found: manifest unknown: manifest unknown**
    
- You can pull each of the images individually
  
```docker pull mveerasingam/batterysimulator_jobmanagerservice:battery-simulator-database```

```docker pull mveerasingam/batterysimulator_jobmanagerservice:battery-simulator-flask```

```docker pull mveerasingam/batterysimulator_jobmanagerservice:battery-simulator-job-manager```

```docker pull mveerasingam/batterysimulator_jobmanagerservice:battery-simulator-queue-service```

```docker pull mveerasingam/batterysimulator_jobmanagerservice:rabbitmq```

- We've updated the [Docker Compose File in Job Manager to Containerise the above images from Docker](https://github.com/mVeerasingam/BatterySimulator-JobManager/blob/master/docker-compose.yml)

## Running on Localhost
- Change the return url to return the commented out localhost in Simulation_DriveCycle.py and Simulation_SingleCell.py
- Note: The function of this microservice is dependent on the Job Manager.
- Change the drive_cycle read_csv file in Simulation_DriveCycle.py (line 67)

![Battery Simulator](https://github.com/mVeerasingam/Battery-Simulator-Service/raw/main/BatterySim_CICD.drawio.png)

### Supporting Microservices
[Battery Job Manager 🔋🔄]([https://github.com/mVeerasingam/Battery_Sim_CICD.draw.io](https://github.com/mVeerasingam/BatterySimulator-JobManager))
[Battery Simulator Queue Service](https://github.com/mVeerasingam/BatterySimulator-QueueService)
[Battery Simulator DB Operations](https://github.com/mVeerasingam/BatterySimulator_DatabaseOperations)

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
- [Battery Simulator Job Manager](https://github.com/mVeerasingam/BatterySimulator-JobManager)
- [Battery Simulator DB Operations](https://github.com/mVeerasingam/BatterySimulator_DatabaseOperations)
- [Battery Simulator Queue Service](https://github.com/mVeerasingam/BatterySimulator-QueueService/tree/master)
