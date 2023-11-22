# Battery-Simulator-Microservice
## Authors: Mark Veerasingam and Lucas Jeanes
### Description: 
ATU 3rd Year CICD 1 

A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM. 
Achieved by recieving and updating the payload from the java job manager, it generates a simulation
before sending out a post request to Job Manager when the simulation is complete.
The application should handle multiple simulation requests concurrently without blocking.
