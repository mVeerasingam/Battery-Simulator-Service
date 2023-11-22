# Battery-Simulator-Microservice 🔋
## Authors: Mark Veerasingam and Lucas Jeanes
### Description: 
ATU 3rd Year CICD 1 

A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM. 
Achieved by recieving and updating the payload from the [Java Job Manager](https://github.com/mVeerasingam/BatterySimulator_JobManager), it generates a simulation
before sending out a post request to Job Manager when the simulation is complete.
The application should handle multiple simulation requests concurrently without blocking.

[PyBaMM](https://github.com/pybamm-team/), "Python Battery Mathematical Model," is an open-source Python library designed for modeling and simulating the behavior of batteries. It provides a framework for implementing physics-based models and numerical methods to analyze various aspects of battery performance. 

### Current Features:
-   Currently, genereates a single cell Lithium Ion Battery Model, based off a LGM50 Cell's electrochemical properties.
-   Model generated from param inputs: 'upper-voltage cut off', 'lower-voltage cut off', 'nominal cell capacity' and a fixed 'current'.
-   Java Job Manager can send a post request to the microservice and that updates the payload for model generation and simulation.
-   Battery Simulator sends payload back to job manager via post request.
