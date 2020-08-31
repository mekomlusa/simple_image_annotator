import sys
from os import walk
import os
import imghdr
import csv
import argparse

from flask import Flask, redirect, url_for, request, flash
from flask import render_template
from flask import send_file
import pandas as pd
from pathlib import Path

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_PATH'] = './uploaded_images/'
app.secret_key = os.urandom(24)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # upload images & save
    if request.method == 'POST' and 'photos' in request.files:
        for f in request.files.getlist('photos'):
            f.save(os.path.join(app.config['UPLOAD_PATH'], f.filename))
            app.config["FILES"].append(f.filename)

        return redirect(url_for('tagger'))
    return render_template('upload.html')

@app.route('/tagger')
def tagger():
    if (app.config["HEAD"] == len(app.config["FILES"])):
        return redirect(url_for('bye'))
    directory = app.config['IMAGES']
    image = app.config["FILES"][app.config["HEAD"]]
    
    if not app.config["EDITING"]:
        labels = render_saved_labels()
        app.config["LABELS"] = labels
    else:
        labels = app.config["LABELS"]

    not_end = not(app.config["HEAD"] == len(app.config["FILES"]) - 1)
    not_start = not (app.config["HEAD"] == 0)

    already_has_labels = len(labels) > 0
    return render_template('tagger.html', not_end=not_end, has_label=already_has_labels, not_start=not_start, directory=directory, image=image, labels=labels, head=app.config["HEAD"] + 1, len=len(app.config["FILES"]))

@app.route('/next')
def next():
    app.config["HEAD"] = app.config["HEAD"] + 1
    return redirect(url_for('tagger'))

@app.route('/prev')
def prev():
    app.config["HEAD"] = app.config["HEAD"] - 1
    return redirect(url_for('tagger'))

# newly saved route
@app.route('/savenew')
def savenew():
    image = app.config["FILES"][app.config["HEAD"]]
    if len(app.config["LABELS"]) > 0:
        with open(app.config["OUT"], 'a') as f: # normal cases
            for label in app.config["LABELS"]:
                f.write(image + "," +
                        label["id"] + "," +
                        label["name"] + "," +
                        str(round(float(label["xMin"]))) + "," +
                        str(round(float(label["xMax"]))) + "," +
                        str(round(float(label["yMin"]))) + "," +
                        str(round(float(label["yMax"]))) + "\n")
    else: # remove all
        saved_output = pd.read_csv(app.config["OUT"])
        labels_without_this_image = saved_output[saved_output['image'] != image]
        labels_without_this_image = labels_without_this_image.reset_index(drop=True)
        labels_without_this_image.to_csv(app.config["OUT"], index=False)

    flash('Saved successfully!', 'success')
    app.config["EDITING"] = False

    return redirect(url_for('tagger'))

@app.route('/clearall')
def clearall():
    app.config["LABELS"] = []

    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])

    if image in saved_output['image'].values:
        labels_without_this_image = saved_output[saved_output['image'] != image]
        labels_without_this_image = labels_without_this_image.reset_index(drop=True)
        labels_without_this_image.to_csv(app.config["OUT"], index=False)
        flash('Cleared all successfully!', 'success')
        #app.config["EDITING"] = False

    return redirect(url_for('tagger'))

# modify labels route
@app.route('/modify')
def modify():
    image = app.config["FILES"][app.config["HEAD"]]
    saved_output = pd.read_csv(app.config["OUT"])
    labels_without_this_image = saved_output[saved_output['image'] != image].copy(deep=True)
    labels_without_this_image = labels_without_this_image.reset_index(drop=True)
    
    current_df_len = len(labels_without_this_image) + 1
    for i in range(len(app.config["LABELS"])):
        labels_without_this_image.loc[current_df_len + i] = [image] + list(app.config["LABELS"][i].values())

    labels_without_this_image.to_csv(app.config["OUT"], index=False)

    flash('Saved successfully!', 'success')
    app.config["EDITING"] = False

    return redirect(url_for('tagger'))

@app.route('/add/<id>')
def add(id):
    app.config["EDITING"] = True

    xMin = request.args.get("xMin")
    xMax = request.args.get("xMax")
    yMin = request.args.get("yMin")
    yMax = request.args.get("yMax")
    app.config["LABELS"].append({"id":id, "name":"", "xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax})
    return redirect(url_for('tagger'))

@app.route('/remove/<id>')
def remove(id):
    app.config["EDITING"] = True
    
    index = int(id) - 1
    del app.config["LABELS"][index]
    for label in app.config["LABELS"][index:]: # reindex for display
        label["id"] = str(int(label["id"]) - 1)
    return redirect(url_for('tagger'))

@app.route('/label/<id>')
def label(id):
    app.config["EDITING"] = True

    name = request.args.get("name")
    app.config["LABELS"][int(id) - 1]["name"] = name
    return redirect(url_for('tagger'))

@app.route('/image/<f>')
def images(f):
    images = app.config['IMAGES']
    return send_file(images + f)

def render_saved_labels():
    """
    Render saved labels from json/csv as per choice indicated. Choice will be the keys from the config file.
    """
    image = app.config["FILES"][app.config["HEAD"]]
    saved_labels_list = []

    saved_output = pd.read_csv(app.config["OUT"])
    past_labels = saved_output[saved_output['image'] == image]
    if len(past_labels) > 0:
        past_labels = past_labels.sort_values(by=['id', 'image'], ascending=[True, False])
        for _, row in past_labels.iterrows():
            saved_labels_list.append({"id": str(row['id']), "name": str(row['name']), "xMin": str(row['xMin']),
                                        "xMax": str(row['xMax']), "yMin": str(row['yMin']), "yMax": str(row['yMax'])})
    
    return saved_labels_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='specify the images directory', required=False)
    parser.add_argument("--out")
    args = parser.parse_args()

    app.config["LABELS"] = []
    app.config["HEAD"] = 0
    app.config["FILES"] = []
    app.config["EDITING"] = False

    if args.dir is not None:
        directory = args.dir
        if directory[len(directory) - 1] != "/":
             directory += "/"
        app.config["IMAGES"] = directory

        files = []
        acceptable_file_extensions = ['.png', '.jpg', '.gif', '.jpeg']
        for (dirpath, dirnames, filenames) in walk(app.config["IMAGES"]):
            for f in filenames:
                if os.path.splitext(f)[1] in acceptable_file_extensions:
                    files.append(f)
            break
        if files == None:
            print("Error: No files. Exiting.")
            exit()
        app.config["FILES"] = files
    else:
        Path(app.config['UPLOAD_PATH']).mkdir(parents=True, exist_ok=True) # create upload folder if not exist already
        app.config['IMAGES'] = app.config['UPLOAD_PATH']

    if args.out == None:
        app.config["OUT"] = "out.csv"
    else:
        app.config["OUT"] = args.out

    if not os.path.exists(app.config["OUT"]):
        with open(app.config["OUT"],'w') as f:
            f.write("image,id,name,xMin,xMax,yMin,yMax\n")

    app.run(debug="True")
