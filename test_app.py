from app import create_app

flask_app = create_app("test")

if __name__ == "__main__":
    flask_app.run(debug=True, port=5003, host='0.0.0.0')
