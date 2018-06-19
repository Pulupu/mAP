import glob
import sys
import json
import os
import shutil

def convert():
    source = "./predicted/"
    destination = "./convert_file/predicted/"

    for files in os.listdir(source):
        if files.endswith(".json"):
            shutil.copy(source + files,destination)

    json_files = glob.glob(destination + "*.json")
    if len(json_files) == 0:
        print("No .json files in ",source)
        sys.exit()

    for json_file in json_files:
        with open(json_file.replace(".json", ".txt"),"w") as new_file:
            data = json.load(open(json_file))
            for obj in data:
                label = obj['label']
                confidence = obj['confidence']
                topleft_x = obj['topleft']['x']
                topleft_y = obj['topleft']['y']
                bottomright_x = obj['bottomright']['x']
                bottomright_y = obj['bottomright']['y']
                new_file.write(label + " " + str(confidence) + " " + str(topleft_x) + " " + str(topleft_y) + " " + str(bottomright_x) + " " + str(bottomright_y) + "\n")
    for files in os.listdir(destination):
        if files.endswith(".json"):
            os.remove(destination + files)
    #print("Finish convert json files")
