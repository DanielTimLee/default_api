from app import app

if __name__ == '__main__':
    app.run(port=8001, debug=True, use_debugger=True, threaded=True)
