
from flask import Flask, request, abort

app = Flask(__name__)
@app.route('/')
def index():
	return 'Yo, its working!'
if __name__ == "__main__":
	app.run()