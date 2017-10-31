import threading
import Tkinter as tk
from flask import Flask
from flask import render_template
# from flask import route


app = Flask(__name__)


@app.route("/")
def analysis():
    if not app.master:
        anast = None
    elif not hasattr(app.master, "anast"):
        anast = None
    else:
        anast = app.master.anast
    return render_template("analysis.html", title='Analysis', anast=anast)


class View(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.app = app
        app.master = self.master
        print self.master

    def start(self):
        self.thread.start()

    def run(self, debug=False):
        app.run(host="0.0.0.0", port=55555, threaded=True, debug=debug)


if __name__ == '__main__':
    view = View()
    view.run(debug=True)
