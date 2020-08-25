# Simple Image Annotator

## Updates

This version has added the following functionalities:

* Move back to previous images: once moved back, saved labels will overlay on the same image
  * Labels can be changed for any images. Latest outputs will be saved in the `.csv` file.
* Click "Save" to saved labels
* Allow users to change label name after a bounding box has been drawn (just move your cursor to the input box and it will change white, allowing you to edit)

TODO:
* ~~Automatically saved labels if users forget to click "Save" but click "next" instead~~
  * This functionality, once implemented, will mess up with the "load saved labels" function. Also, users are expected to explicitly click "save" to save their changes. Otherwise, labels will not be saved by blindly clicking "next" (it is believed that users have no intention to save too).
* ~~Ability to keep the same bounding box but change label texts~~
* Allow users to upload image(s) for labeling
* Possibly integration with database for persistence

## Description
All image annotators I found either didn't work or had some overhead in the setup. So, I tried to make this one simple to run and simple to use.
![action](./actionshot.png)

## Install
* Install Flask
```
$ pip install Flask
```

## Getting started
* cd into this directory after cloning the repo
* start the app
```
$ python app.py /images/directory
```
* you can also specify the file you would like the annotations output to (out.csv is the default)
```
$ python app.py /images/directory --out test.csv
```
* open http://127.0.0.1:5000/tagger in your browser
    * only tested on Chrome

## Output
* in keeping with simplicity, the output is to a csv file with the following fields
    * *id* - id of the bounding box within the image
    * *name* - name of the bounding box within the image
    * *image* - image the bounding box is associated with
    * *xMin* - min x value of the bounding box
    * *xMax* - max x value of the bounding box
    * *yMin* - min y value of the bounding box
    * *yMax* - max y value of the bounding box

## HOWTOs
* draw a bounding box
  * click on the image in the location of the first corner of the bounding box you would like to add
  * click again for the second corner and the box will be drawn
* add a label for a box
  * for the box you would like to give a label, find its id (noted in the top left corner of the box)
  * find the label with the corresponding number
  * enter the name you want in the input field
  * press enter
* move to next image
  * click the blue arrow button at the bottom of the page (depending on the size of the image you may have to scroll down)
* remove label
  click the red button on the label you would like to remove
* check generated data
  * at the top level of the directory where the program was run, there should be a file called out.csv that contains the generate data
