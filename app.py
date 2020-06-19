from flask import Flask, session, render_template, request, redirect, send_file
import base64
from PIL import Image
import numpy as np
import cv2
import random
import string


app = Flask(__name__)
pillows = []


class Img:
    def __init__(self, base, header, filename, ctype):
        self.base = base
        self.header = header
        self.uri = ("data:" + self.header + ";" + "base64," + self.base)
        self.filename = filename
        self.type = ctype

    def size(self, image):
        width, height = image.size
        self.dimensions = image.size
        return (width, height)

    def dimensions(self):
        k = self.formImage()
        return self.size(k)

    def reshape(self, frame):
        n = ""
        width, height = self.size(frame)
        if width > 600 or height > 300:
            left = (width/2) - 300
            right = (width/2) + 300
            top = (height/2) - 150
            bottom = (height/2) + 150
            n = frame.crop((left, top, right, bottom))
        else:
            return frame
        return n

    def fixColor(self, i):
        return cv2.cvtColor(i, cv2.COLOR_BGR2RGB)

    def formImage(self):
        image_b64 = self.uri.split(",")[1]
        binary = base64.b64decode(image_b64)
        image = np.asarray(bytearray(binary), dtype="uint8")
        x = cv2.imdecode(image, cv2.IMREAD_COLOR)
        x = self.fixColor(x)
        frame = Image.fromarray(x)
        k = self.reshape(frame)
        return k

    def retpil(self):
        return self.formImage()


def reorder(data, rank):
    rank = rank
    data = data
    new = []
    count = 0
    for o in rank:
    	new.insert(int(o), data[count])
    	count += 1

    return new


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploadedFiles = request.files.getlist("images")
        images = []
        for upload in uploadedFiles:
            read = upload.read()
            image = Img(base64.b64encode(read).decode(
            ), upload.headers['Content-Type'], upload.filename, upload.content_type)

            obj = image.retpil()
            pillows.append(obj)
            images.append(image)

        return render_template("index.html", imgs=images)
    else:

        return render_template("index.html")


@app.route("/make", methods=["GET", "POST"])
def make():
    if request.method == "POST":
        duration = int(request.form["fps"])
        newOrder = request.form.getlist("rank")

        pox = reorder(pillows, newOrder)

        pox[0].save("result.gif", format='GIF', append_images=pox[1:],
                    save_all=True, duration=duration, loop=0)
        return send_file("result.gif", as_attachment=True)
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
