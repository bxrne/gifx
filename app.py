
from flask import Flask, render_template, request, redirect, send_file
import base64
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)
images = []
imageObjects = []
final = []
frames = []
sizes = []

def done():
    images = []
    imageObjects = []
    final = []
    frames = []
    sizes = []

def formImage(string):
    image_b64 = string.split(",")[1]
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    x = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image =  Image.fromarray(x)
    return image

def reshape(i):
    n =""
    width, height = i.size
    if width > 600 or height > 300:
        left = (width/2) - 300
        right = (width/2) + 300
        top = (height/2) -150
        bottom = (height/2) +150 
        n = i.crop((left, top, right, bottom))
    else:
        return i 
    return n

def fixColor(imgs):
    nimgs = []
    for i in imgs:
        nimgs.append(cv2.cvtColor(np.array(reshape(i)), cv2.COLOR_BGR2RGB))
    return nimgs

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploadedFiles = request.files.getlist("images")
        for upload in uploadedFiles:
            '''
            buffer 0 > Header
            buffer 1 > Filename
            buffer 2 > URI
            buffer 3 > base64 raw

            '''
            buffer = []
            read = upload.read()
            raw = base64.b64encode(read).decode()
            buffer.append(upload.content_type)
            buffer.append(upload.filename)
            buffer.append(("data:" + upload.headers['Content-Type'] + ";" + "base64," + raw))
            buffer.append(raw)
            images.append(buffer)
            imageObjects.append(formImage(buffer[2]))
            width, height = formImage(buffer[2]).size
            sizes.append(f"{width}px x {height}px")
            final = fixColor(imageObjects)
            for i in final:
                img = Image.fromarray(i, 'RGB')
                frames.append(img)
        return render_template("index.html", images=images, sizes=sizes)
    else:
        done()
        return render_template("index.html")

@app.route("/reorder", methods=["GET", "POST"])
def reorder():
    if request.method == "POST":
        res = [i for n, i in enumerate(frames) if i not in frames[:n]] 
        df = int(request.form["fps"])
        order = []
        newFrames = []
        for i in range(len(res)):
            newFrames.append(0)
        for k in request.form.getlist("rank"):
            order.append(k)
        for i in order:
            newFrames.append(res[int(i)])
        del newFrames[:2]

        newFrames[0].save("result.gif", format='GIF', append_images=newFrames[1:], save_all=True, duration=df, loop=0)
        return send_file("result.gif", as_attachment=True)
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)