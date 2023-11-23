'''
This code was referenced from the battery sim prototype: https://github.com/MarkVeerasingam/PyBaMM_BatterySimulator_Prototype/tree/main

Authors:        Mark Veerasingam, Lucas Jeanes
Description:    A flask based microservice that simulates Lithium-Ion Battery models with PyBaMM.
                Achieved by recieving and updating the payload from the java job manager, it generates a simulation
                before sending out a post request to Job Manager when the simulation is complete.

                The application should handle multiple simulation requests concurrently without blocking.


Features:       -   Currently, genereates a single cell Lithium Ion Battery Model, based off a LGM50 Cell's electrochemical properties.
                -   Model generated from param inputs: 'upper-voltage cut off', 'lower-voltage cut off', 'nominal cell capacity' and a fixed 'current'.
                -   Java Job Manager can send a post request to the microservice and that updates the payload for model generation and simulation.
                -   Battery Simulator sends payload back to job manager via post request.

ToDo:
                Testing and Validation:
                -   Make tests to check if the payload has recieved/updated/sent to and from java respectivley.
                -   Test if code can handle multiple simulation requests concurrently without blocking.
                -   Validate flask requests so that all parameters are required

                Simulations:
                    ------------------------[Simulation Model Options]------------------------------------------------------
                -   Option to simulate battereis at 0°/25°/75°. Default is 25°

                -   Option to simulate a discharge or charge of a battery. (Could just reverse the discharge? simple option)

                -   Option to simulate in different models ("BaseModel", "SPM", "DFN"etc...)
                    Could display "Simulate Model 1/2 etc..." on website (no need for major detail).

                -   [idea] With validation. Have the option to input either a nominal voltage or upper and lower voltage
                    as a customisable parameter. Lithium Ion's nominal voltage is ~ 3.6V to 3.7V.
                    Nomimnal Voltage = Upper Voltage CutOff + Lower Voltage CutOff / 2.
                    Most Li-On Battery datasheets show it's nominal voltage. Having the above suggestion is good UX
                    Alternativley.
                        A simpler option is to Let the user choose a nominal voltage option between 3.6V and 3.7V they wish
                        to model off of. These options just  have the preset upper and lower voltages assigned to them.
                        This saves us trying to calc new upper and lower voltages.

                    --------------------------[Simulation Features]--------------------------------------------------------
                -   Handle multiple simulation requests concurrently without blocking.
                    Java Job Manager looks at the message queues sent from microservice 1.
                    If a message says that a simulation job is already running, it waits before pulling from message queue.
                    If a job is not running it tells this microservice to execute the next job (generate a new simulation)

                -   This is a job manager function but relevant. The project DB should have premade real life battery cells like LGM50 or Samsung-inr18650-25r
                    The simulator should be able to succesfully recieve these values and send it back without causing any issues.

                    --------------------------------[Long-Term]------------------------------------------------------------
                -   Once a model is made, look at making a definition that simulates that models drive cycle
                    User could have option to simulate battery model and or make drive cycle
                    By solving with a changing current like: https://tinyurl.com/2prwzrrh
                    It would allow a drive cycle simulation (different from the current time solved simulation).

                -   String based experiments

                -   Try implementing LiionPack for lithium ion pack simulation
'''

import threading
import requests
import pybamm
from flask import Flask, request, jsonify

app = Flask(__name__)

# url to send the data back to the Java Job Manager
return_url = "http://127.0.0.1:8083/updateBatteryResults"


def simulate_battery(params, hours, id):
    try:
        # Create a Lithium Ion battery model with a DFN model, may look at having different models in the near future
        model = pybamm.lithium_ion.DFN()

        # Casadi safe solver may be best for solving ODE's for this specific project
        safe_solver = pybamm.CasadiSolver(atol=1e-6, rtol=1e-6,
                                          mode="safe")  # perform step-and-check integration in global steps of size dt_max

        # Electrochemical parameters are based off a 'LGM50' Cell. "Chen2020" is the experiment name the chemistry was referenced from
        custom_parameters = pybamm.ParameterValues("Chen2020")
        custom_parameters.update(params)  # we can update the parameters with recieved argument "params"

        safe_sim = pybamm.Simulation(model, parameter_values=custom_parameters, solver=safe_solver)

        seconds = hours * 60 * 60  # Pybamm solves in secnods, having the user input in hours would make more sense
        solution = safe_sim.solve([0, seconds])  # solve  simulation from 0 seconds -> x ammount of seconds

        # contents of the payload sent to job manager.
        time_s = solution['Time [s]'].entries
        voltage = solution['Battery voltage [V]'].entries
        current = solution['Current [A]'].entries
        dcap = solution['Discharge capacity [A.h]'].entries
        temp = solution['Ambient temperature [K]'].entries
        combined_data = []

        # Formats is to the simulation updates over length of simulation time
        for i in range(len(time_s)):
            data_point = {
                "time": time_s[i],
                "voltage": voltage[i],
                "current": current[i],
                "dcap": dcap[i],
                "temp": temp[i]
            }
            combined_data.append(data_point)

        # send request back out after we finish the simulation
        requests.post(return_url, json={
            'id': id,
            'result': combined_data
        })

        return combined_data

    except pybamm.SolverError as e:
        return {"error": f"SolverError:\nVoltage cut-off values should be relative to 2.5V and 4.2V: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


@app.route('/simulate', methods=['POST'])
def simulate():
    try:

        data = request.get_json()  # Get data from post request

        # Update parameters based on data received (for this case, Java
        hours = data.get('time', 1)
        id = data.get('id')

        '''
        Notes @Mark: 
            Voltage: 
            Lithium Ion Batteries have a typical nominal voltage of 3.6V ~ 3.7V.
            Nominal Voltage = Upper Voltage / Lower Volage.
            The solver solves relative to this range. keeping the upper voltage 4.2V and 
            lower voltage ~2.5V - 3V produces no errors and accurate time sovled simulations.

            Current:
            "controlCurrent" is a fixed current when solving the ODE. When solving PyBaMM
            https://github.com/pybamm-team/PyBaMM/issues/124

            changing "controlCurrent" can cause the simulation to produce poor results if passing too high of a current.
            "controlCurrent" is designed to be a fixed current when solving the ODE.
            e.g.
                custom_parameters.update({ 
                "Upper voltage cut-off [V]":    4.2, 
                "Lower voltage cut-off [V]":    2.5, 
                "Nominal cell capacity [A.h]":  9, 
                "Current function [A]":         8  
                }) 

            Produces errors like:
            "At t = 549.166 and h = 3.20498e-14, the corrector convergence failed repeatedly or with |h| = hmin."

            While this doesent stop the simulation it can produce poor results for accurate simulations.

            I found setting controlCurrent to 2 is a nice sweet spot.
            While i'm not entirley sure why, I suspect that.. 
            Similar to a 1C charge for a 2000mAh the battery would be 2000mA (or 2A)

            I think having the user choose would be benefiial for unique resuelts. Would need to give a prompt on the frontend
        '''

        custom_parameters = {
            "Upper voltage cut-off [V]": data.get("upperVoltage", 4.2),
            "Lower voltage cut-off [V]": data.get("lowerVoltage", 2.5),
            "Nominal cell capacity [A.h]": data.get("nominalCell", 8.6),
            "Ambient temperature [K]": data.get("temperature", 323.15),
            "Current function [A]": data.get("controlCurrent", 5),  # "Current-controlled" = fixed current
            # find a more safer to calc a better current or c-rate potentially
        }

        # by using threads we handle the simulations separately from the main  application thread.
        # goal is to handle multiple simulation requests concurrently without blocking.
        thread = threading.Thread(target=simulate_battery, args=(custom_parameters, hours, id))
        thread.start()

        sim = simulate_battery(custom_parameters, hours, id)

        # Note. As of the moment jsonify returns sim. this is just to test if simulation values arent breaking
        # [Down the line] Simulation should be able to be viewed/graphed on the webstie and prompted with the choice to save or try again
        return jsonify({"jobStarted": True}, sim)

    except Exception as e:
        return jsonify(error=str(e))


if __name__ == '__main__':
    app.run(debug=True, port=8084)
