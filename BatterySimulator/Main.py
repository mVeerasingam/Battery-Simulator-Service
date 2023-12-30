from flask import Flask
from Blueprints.Simulations.Simulation_SingleCell import simulateCell_bp

app = Flask(__name__)

app.register_blueprint(simulateCell_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8084, debug=True, threaded=True)
