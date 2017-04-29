from flask import Flask
from quran_data_generator import QuranBanglaGenerator

app = Flask(__name__)


@app.route('/')
def hello_world():
    QuranBanglaGenerator().process()
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
