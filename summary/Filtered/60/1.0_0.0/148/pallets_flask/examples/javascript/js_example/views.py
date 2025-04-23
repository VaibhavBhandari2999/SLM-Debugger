from flask import jsonify
from flask import render_template
from flask import request

from js_example import app


@app.route("/", defaults={"js": "fetch"})
@app.route("/<any(xhr, jquery, fetch):js>")
def index(js):
    return render_template(f"{js}.html", js=js)


@app.route("/add", methods=["POST"])
def add():
    """
    Function to add two numbers.
    
    Parameters:
    a (float): The first number to add. Defaults to 0 if not provided.
    b (float): The second number to add. Defaults to 0 if not provided.
    
    Returns:
    dict: A dictionary containing the 'result' of the addition.
    
    This function retrieves two numbers from a form request, adds them together, and returns the result as a JSON response.
    """

    a = request.form.get("a", 0, type=float)
    b = request.form.get("b", 0, type=float)
    return jsonify(result=a + b)
