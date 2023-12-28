'''
This code was referenced from the battery sim prototype: https://github.com/MarkVeerasingam/PyBaMM_BatterySimulator_Prototype/tree/main

Authors:        Mark Veerasingam, Lucas Jeanes
Description:    A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM.
                Achieved by recieving and updating the payload from the java job manager, it generates a simulation
                before sending out a post request to Job Manager when the simulation is complete.

                The application should handle multiple simulation requests concurrently without blocking.


Features:       -   Generates a single cell Lithium Ion Battery Model, based off a LGM50 Cell's electrochemical properties.
                -   Model generated from param inputs: 'upper-voltage cut off', 'lower-voltage cut off', 'nominal cell capacity' and a fixed 'current'.
                -   Java Job Manager can send a post request to the microservice and that updates the payload for model generation and simulation.
                -   Battery Simulator sends payload back to job manager via post request.
'''