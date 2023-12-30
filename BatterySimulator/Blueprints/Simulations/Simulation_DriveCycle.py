import threading
import requests
import pybamm
import pandas as pd
from flask import Blueprint, request, jsonify

simulateDriveCycle_bp = Blueprint("driveCycleSimulation", __name__)

return_url = "http://localhost:8083/simulateDriveCycle"

def simulate(custom_parameters, id, result_holder):
    try:
        model = pybamm.lithium_ion.DFN()

        drive_cycle = pd.read_csv(r"BatterySimulator\DriveCycle_Data\US06.csv", comment="#", header=None).to_numpy()
        current_interpolant = pybamm.Interpolant(drive_cycle[:, 0], drive_cycle[:, 1], pybamm.t)

        var_pts = {
            "x_n": 30,
            "x_s": 30,
            "x_p": 30,
            "r_n": 10,
            "r_p": 10,
        }
        safe_solver = pybamm.CasadiSolver(atol=1e-6, rtol=1e-6, mode="safe")

        custom_parameters.update({
            "Upper voltage cut-off [V]": request.json.get("upperVoltage", 4.2),
            "Lower voltage cut-off [V]": request.json.get("lowerVoltage", 2.5),
            "Nominal cell capacity [A.h]": request.json.get("nominalCell", 8.6),
            "Current function [A]": current_interpolant,
            # Add other parameters as needed
        })

        safe_sim = pybamm.Simulation(model, parameter_values=custom_parameters, solver=safe_solver)
        solution = safe_sim.solve()

        voltage = solution["Battery voltage [V]"].entries
        current = solution["Current [A]"].entries
        dcap = solution["Discharge capacity [A.h]"].entries
        combined_data = []

        for i in range(len(voltage)):
            data_point = {
                "voltage": voltage[i],
                "current": current[i],
                "dcap": dcap[i]
            }
            combined_data.append(data_point)

        requests.post(return_url, json={
            'id': id,
            'result': combined_data
        })

        result_holder["result"] = combined_data

    except pybamm.SolverError as e:
        result_holder["result"] = None
        print(f"SolverError: Voltage cut-off values should be relative to 2.5V and 4.2V: {str(e)}")
    except Exception as e:
        result_holder["result"] = None
        print(f"Error: {str(e)}")

@simulateDriveCycle_bp.route('/simulate', methods=['POST'])
def simulate_drive_cycle():
    try:
        data = request.get_json()

        custom_parameters = pybamm.ParameterValues("Chen2020")
        job_id = data.get('id')

        result_holder = {"result": None}

        thread = threading.Thread(target=simulate, args=(custom_parameters, job_id, result_holder))
        thread.start()
        thread.join()

        sim_results = result_holder["result"]

        if sim_results is not None:
            return jsonify({"jobStarted": True, "simulationResults": sim_results})
        else:
            return jsonify({"jobStarted": False, "simulationResults": sim_results})

    except Exception as e:
        return jsonify(error=str(e))