from flask import Flask, jsonify, request

from route_inspector.route_evaluation import store_evaluation
from route_inspector.route_inspector import compute_route
from route_inspector.route_tracking import track_route

app = Flask(__name__)


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
    route = compute_route(input_params)
    result_dict = {'text': route, 'route_id': 1}
    return jsonify(result_dict)



@app.route('/start_route', methods=['GET'])
def notify_route_start():
    """Notifies the system that the route was started. We need that to estimate the crowdedness of the route
    :return:
    """
    route_id = request.args.get("route_id")
    track_route()


@app.route('/evaluate_route', methods=['POST'])
def evaluate_route():
    """
    :return:
    """
    user_feedback = request.get_json(force=True)
    store_evaluation(user_feedback)
    return 'OK'


if __name__ == '__main__':
    app.run()
