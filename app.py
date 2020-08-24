import sys
from os import walk
import os
import imghdr
import csv
import argparse

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask import send_file
import pandas as pd

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    labels = app.config["LABELS"]
    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_start = not (app.config["HEAD"] == 0)
    prev_ind = app.config["PREV"]
    return render_template('tagger.html', not_end=not_end, prev=prev_ind, not_start=not_start, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next')
def next():
    # image = app.config["FILES"][app.config["HEAD"]]
    app.config["HEAD"] = app.config["HEAD"] + 1
    app.config["PREV"] = False
    # with open(app.config["OUT"],'a') as f:
    #     for label in app.config["LABELS"]:
    #         f.write(image + "," +
    #         label["id"] + "," +
    #         label["name"] + "," +
    #         str(round(float(label["xMin"]))) + "," +
    #         str(round(float(label["xMax"]))) + "," +
    #         str(round(float(label["yMin"]))) + "," +
    #         str(round(float(label["yMax"]))) + "\n")
    app.config["LABELS"] = []
    return redirect(url_for('tagger'))

@app.route('/prev')
def prev():
    app.config["HEAD"] = app.config["HEAD"] - 1
    app.config["PREV"] = True
    # restore labels
    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])
    past_labels = saved_output[saved_output['image'] == image]
    if len(past_labels) > 0:
        for index, row in past_labels.iterrows():
            app.config["LABELS"].append({"id": str(row['id']), "name": str(row['name']), "xMin": str(row['xMin']),
                                         "xMax": str(row['xMax']), "yMin": str(row['yMin']), "yMax": str(row['yMax'])})
    return redirect(url_for('tagger'))

# newly saved route
@app.route('/savenew')
def savenew():
    image = app.config["FILES"][app.config["HEAD"]]
    with open(app.config["OUT"], 'a') as f:
        for label in app.config["LABELS"]:
            f.write(image + "," +
                    label["id"] + "," +
                    label["name"] + "," +
                    str(round(float(label["xMin"]))) + "," +
                    str(round(float(label["xMax"]))) + "," +
                    str(round(float(label["yMin"]))) + "," +
                    str(round(float(label["yMax"]))) + "\n")
    return redirect(url_for('tagger'))

# modify labels route
@app.route('/modify')
def modify():
    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])
    labels_without_this_image = saved_output[saved_output['image'] != image]
    current_df_len = len(labels_without_this_image)
    for i in range(len(app.config["LABELS"])):
        labels_without_this_image.loc[current_df_len + i] = [image] + list(app.config["LABELS"][i].values())

    if current_df_len > 0:
        labels_without_this_image.to_csv(app.config["OUT"], index=False, header=False)
    else:
        labels_without_this_image.to_csv(app.config["OUT"], index=False)

    return redirect(url_for('tagger'))

@app.route("/bye")
def bye():
    return send_file("taf.gif", mimetype='image/gif')

@app.route('/add/<id>')
def add(id):
    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]:
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='specify the images directory')
    parser.add_argument("--out")
    args = parser.parse_args()
    directory = args.dir
    if directory[len(directory) - 1] != "/":
         directory += "/"
    app.config["IMAGES"] = directory
    app.config["LABELS"] = []
    app.config["PREV"] = False
    files = []
    acceptable_file_extensions = ['.png', '.jpg', '.gif']
    for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
        for f in filenames:
            if os.path.splitext(f)[1] in acceptable_file_extensions:
                files.append(f)
        break
    if files == None:
        print("No files")
        exit()
    app.config["FILES"] = files
    app.config["HEAD"] = 0
    if args.out == None:
        app.config["OUT"] = "out.csv"
    else:
        app.config["OUT"] = args.out
    print(files)
    with open("out.csv",'w') as f:
        f.write("image,id,name,xMin,xMax,yMin,yMax\n")
    app.run(debug="True")
