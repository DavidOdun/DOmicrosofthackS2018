#!/usr/bin/env python3

import cv2
import ellmanager as emanager
import io
import json
import logging
import model
import numpy as numpy
import os
import picamera
import shutil
import subprocess
import sys
import termios
import time
from guizero import App, Text
from PIL import Image

SCRIPT_DIR = os.path.split(os.path.realpath(__file__))[0]

def run_shell(cmd):
    """
    Used for running shell commands
    """
    output = subprocess.check_output(cmd.split(' '))
    logging.debug('Running shell command')
    return str(output.rstrip().decode())

def main():
    # Import Notes:
    # 1) if the resolution to capture images changes in Unity, it needs to change here to be searched for and found
    # 2) Need to delay this one by a second or 2 to make sure we are never calling models on images that are not here yet.
    # 3) How is this script being called?
    # 4) Gui!
    # Define Globals
   
    image_val = 0
    picW = 256
    picH = 256
    previous_dir = os.path.dirname(SCRIPT_DIR)

    # Intialize Log Properties
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') 
    
    # Began running and stay running the entire project.
    logging.debug('Starting Our Seamless Journey')

    # Get the Label Names for the Model
    with open("categories.txt", "r") as categories_file:
        categories = categories_file.read().splitlines()

    # Format the Path of the image to look for specific sized images
    images_dir = "{0}/UnityImages".format(previous_dir)
    good_images_dir = "{0}/GoodImages".format(previous_dir)
    word_list_path = "{0}/wordlist.txt".format(SCRIPT_DIR)

    # Check if the Unity Images files exists, if not change up and make it
    print('Previous Directory: {0}'.format(previous_dir))
    if not os.path.exists(images_dir):
        os.chdir(previous_dir)
        os.makedirs(images_dir)
        os.chdir(SCRIPT_DIR)

    if not os.path.exists(good_images_dir):
        os.chdir(previous_dir)
        os.makedirs(good_images_dir)
        os.chdir(SCRIPT_DIR)

    # If we are starting a new iteration of the program. Delete the old verision of the list.
    if os.path.exists(word_list_path):
        os.remove(word_list_path)

    while (True):
        image_path = 'screen_{0}x{1}_{2}.jpg'.format(picW, picH, image_val)
        full_image_path = '{0}/{1}'.format(images_dir, image_path)
   
        while not os.path.exists(full_image_path):
            print('It seems we dont have this image yet, we are waiting on it')
            time.sleep(1)

        # Now that we know the image file path, prepare it for object Detection
        print('This is where we proccess')
        prep_image2 = Image.open(full_image_path)
        prep_image2.show()
        prep_image = cv2.imread(full_image_path)
        input_shape = model.get_default_input_shape()
        input_data = emanager.prepare_image_for_model(prep_image, input_shape.columns, input_shape.rows)
        predictions = model.predict(input_data)
        top_5 = emanager.get_top_n(predictions, 5)
        

        if (len(top_5) < 1):
            print("We got nothing in this!")
            # Delete the Image File afterwards
            os.remove(full_image_path)
        else:
            # Get the word that the picture recongized
            word = categories[top_5[0][0]]
            output = "We actually got something back! Word: {0}! ImageNumber: {1}".format(word, image_val)
            print(output) 
            
            # Move the Image From the current folder to the Good Images Folder
            good_images_path = "{0}/{1}".format(good_images_dir, image_path)
            shutil.move(full_image_path, good_images_path)

            # Attach the recongizined word name to a file or just show it
            with open(word_list_path, "a+") as f:
                f.write("{}\n".format(word))

            time.sleep(1)


        # Increment the next image to look for
        image_val = image_val + 1

    

if __name__ == '__main__':
    main()
