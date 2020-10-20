import boto3
import os
import logging
from flask import Flask, render_template, url_for
from neurogui import upload, image

# https://pypi.org/project/JSON-log-formatter/

logging.basicConfig(
	# filename='example.log',
	level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')),
	format='{"timestamp":"%(asctime)s", "name":"%(name)s", "level": "%(levelname)s", "message":"%(message)s"}'
)

app = Flask(__name__)

app.register_blueprint(upload.api)
app.register_blueprint(image.api)

@app.route('/')
def home():
	return render_template('index.html')

# to refresh css when testing locally
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True,host='0.0.0.0',port=port)