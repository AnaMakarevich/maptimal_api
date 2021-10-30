from flask import request, jsonify
from app import app

from route_inspector.route_evaluation import store_evaluation
from route_inspector.route_inspector import compute_route
from route_inspector.route_tracking import track_route


@app.route('/')
def index_page():
    return 'API is up!'


@app.route('/get_route', methods=["POST"])
def get_route():
    """API endpoint that accepts start and end points as request, including
    standard parameters available to the Google Map user with additional parameters
    that indicate preferences: i.e. if the route should be safer, greener or less crowded.
    :return:
    Optimised route along with the route id which is necessary to send evaluation after the route is completed.
    """
    input_params = request.get_json(force=True)
    route, route_evaluation_result, route_id = compute_route(input_params)
    result_dict = {'route': route, 'route_id': route_id, 'route_evaluation': route_evaluation_result}
    return jsonify(result_dict)


@app.route('/start_route', methods=['GET'])
def notify_route_start():
    """Notifies the system that the route was started. We need that to estimate the crowdedness of the route
    :return:
    """
    route_id = request.args.get("route_id")
    track_route(route_id)
    return 'OK'


@app.route('/evaluate_route', methods=['POST'])
def evaluate_route():
    """
    :return:
    """
    user_feedback = request.get_json(force=True)
    store_evaluation(user_feedback)
    return 'OK'
