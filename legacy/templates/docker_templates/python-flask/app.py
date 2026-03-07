from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/health')
def health_check():
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
