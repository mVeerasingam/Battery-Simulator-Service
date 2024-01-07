import threading
import requests
import pybamm
from flask import Blueprint, request, jsonify

simulateCell_bp = Blueprint("cellSimulation", __name__)

return_url = "http://localhost:8083/simulateCell"
#return_url = "http://job-manager-service:8083/simulateCell"


def simulate_battery(params, hours, id, result_holder):
    try:
        # Create a Lithium Ion battery model with a DFN (doyle fuller newman) model
        model = pybamm.lithium_ion.DFN()

        # PyBaMM uses CasAdi, this is a tool for numerical optimization in general and optimal control
        # Running in "safe" mode may be best for solving ODE's for this specific project
        safe_solver = pybamm.CasadiSolver(atol=1e-6, rtol=1e-6,
                                          mode="safe")  # perform step-and-check integration in global steps of size dt_max

        # Electrochemical parameters are based off a 'LGM50' Cell. "Chen2020" is the experiment name the chemistry was referenced from
        custom_parameters = pybamm.ParameterValues("Chen2020")
        custom_parameters.update(params)  # we can update the parameters with received argument "params"

        safe_sim = pybamm.Simulation(model, parameter_values=custom_parameters, solver=safe_solver)

        seconds = hours * 60 * 60  # Pybamm solves in seconds, having the user input in hours would make more sense
        solution = safe_sim.solve([0, seconds])  # solve simulation from 0 seconds -> x amount of seconds

        # contents of the payload sent to job manager.
        time_s = solution['Time [s]'].entries
        voltage = solution['Battery voltage [V]'].entries
        current = solution['Current [A]'].entries
        dcap = solution['Discharge capacity [A.h]'].entries
        combined_data = []

        # Formats is to the simulation updates over length of simulation time
        for i in range(len(time_s)):
            data_point = {
                "time": time_s[i],
                "voltage": voltage[i],
                "current": current[i],
                "dcap": dcap[i]
            }
            combined_data.append(data_point)

        # send request back out after we finish the simulation
        requests.post(return_url, json={
            'id': id,
            'result': combined_data
        })

        result_holder["result"] = combined_data

    except pybamm.SolverError as e:
        return {"error": f"SolverError:\nVoltage cut-off values should be relative to 2.5V and 4.2V: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

 
@simulateCell_bp.route('/simulate', methods=['POST'])
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
            While I'm not entirley sure why, I suspect that.. 
            Similar to a 1C charge for a 2000mAh the battery would be 2000mA (or 2A)

            I think having the user choose would be benefiial for unique resuelts. Would need to give a prompt on the frontend
        '''

        # User inputs
        custom_parameters = {
            "Upper voltage cut-off [V]": data.get("upperVoltage", 4.2),
            "Lower voltage cut-off [V]": data.get("lowerVoltage", 2.5),
            "Nominal cell capacity [A.h]": data.get("nominalCell", 8.6),
            "Current function [A]": data.get("controlCurrent", 5),  # "Current-controlled" = fixed current
        }

        # mutable object to store the result
        result_holder = {"result": None}

        # by using threads we handle the simulations separately from the main application thread.
        # goal is to handle multiple simulation requests concur rently without blocking.
        thread = threading.Thread(target=simulate_battery, args=(custom_parameters, hours, id, result_holder))
        thread.start()  
        thread.join()
        # sim = simulate_battery(custom_parameters, hours, id)
        sim_results = result_holder["result"]

        # Check if object has required contents for a simulation
        if sim_results is not None:
            return jsonify({"jobStarted": True, "simulationType": "cell", "simulationResults": sim_results})
        else:
            return jsonify({"jobStarted": False, "simulationType": "cell", "simulationResults": sim_results})

    except pybamm.SolverError as e:
        return jsonify({"jobStarted": False, "error": f"SolverError: Voltage cut-off values should be relative to 2.5V and 4.2V: {str(e)}"})
    except Exception as e:
        return jsonify(error=str(e))