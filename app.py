from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """
    Handle request to the root URL ('/')

    Returns:
        str: the title of the application
    """
    return 'London Cocktail Week 2025!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
