import sys
import os
import glob
import xml.etree.ElementTree as ET
import shutil

def convert():
    source = "./ground_truth/"
    destination = "./convert_file/ground_truth/"

    for files in os.listdir(source):
        if files.endswith(".xml"):
            shutil.copy(source + files,destination)

    xml_files = glob.glob(destination + "*.xml")
    if len(xml_files) == 0:
        print("No .xml files in ",source)
        sys.exit()

    for xml_file in xml_files:
        with open(xml_file.replace(".xml", ".txt"),"w") as new_file:
            root = ET.parse(xml_file).getroot()
            for obj in root.findall('object'):
                label = obj.find('name').text
                bndbox = obj.find('bndbox')
                xmin = bndbox.find('xmin').text
                ymin = bndbox.find('ymin').text
                xmax = bndbox.find('xmax').text
                ymax = bndbox.find('ymax').text
                new_file.write(label + " " + str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax) + "\n")
    for files in os.listdir(destination):
        if files.endswith(".xml"):
            os.remove(destination + files)
    #print("Finish convert xml files")
