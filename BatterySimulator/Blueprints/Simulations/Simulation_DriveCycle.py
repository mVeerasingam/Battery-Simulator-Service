import threading
import requests
import pybamm
import pandas as pd
from flask import Blueprint, request, jsonify

simulateDriveCycle_bp = Blueprint("driveCycleSimulation", __name__)

return_url = "http://localhost:8083/simulateDriveCycle"
#return_url = "http://job-manager-service:8083/simulateDriveCycle"

def simulate(id, result_holder, params):
    model = pybamm.lithium_ion.DFN()
    custom_parameters = pybamm.ParameterValues("Chen2020")
    
    var_pts = {
        "x_n": 30,
        "x_s": 30,
        "x_p": 30,
        "r_n": 10,
        "r_p": 10,
    }
    safe_solver = pybamm.CasadiSolver(atol=1e-6, rtol=1e-6, mode="safe")
    
    custom_parameters.update(params)

    safe_sim = pybamm.Simulation(model, parameter_values=custom_parameters, solver=safe_solver, var_pts=var_pts)
    solution = safe_sim.solve()

    time_s = solution["Time [s]"].entries
    voltage = solution["Battery voltage [V]"].entries
    current = solution["Current [A]"].entries
    dcap = solution["Discharge capacity [A.h]"].entries
    combined_data = []

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

@simulateDriveCycle_bp.route('/simulate', methods=['POST'])
def simulate_driveCycle():
    try:
        data = request.get_json()

        id = data.get('id')
        
        drive_cycle = pd.read_csv(r"DriveCycle_Data/US06.csv", comment="#", header=None).to_numpy()
        #drive_cycle = pd.read_csv(r"BatterySimulator\DriveCycle_Data\US06.csv", comment="#", header=None).to_numpy()
        current_interpolant = pybamm.Interpolant(drive_cycle[:, 0], drive_cycle[:, 1], pybamm.t)

        # User inputs
        custom_parameters = {
            "Upper voltage cut-off [V]": data.get("upperVoltage", 4.2),
            "Lower voltage cut-off [V]": data.get("lowerVoltage", 2.5),
            "Nominal cell capacity [A.h]": data.get("nominalCell", 8.6),
            "Current function [A]": current_interpolant
        }

        result_holder = {"result": None}

        thread = threading.Thread(target=simulate, args=(id, result_holder, custom_parameters))
        thread.start()  
        thread.join()

        sim_results = result_holder["result"]
        if sim_results is not None:
            return jsonify({"jobStarted": True, "simulationType": "driveCycle", "simulationResults": sim_results})
        else:
            return jsonify({"jobStarted": False, "simulationType": "driveCycle", "simulationResults": sim_results})
        
    except pybamm.SolverError as e:
        return jsonify({"jobStarted": False, "error": f"SolverError: Voltage cut-off values should be relative to 2.5V and 4.2V: {str(e)}"})
    except Exception as e:
        return jsonify({"jobStarted": False, "error": f"Error: {str(e)}"})