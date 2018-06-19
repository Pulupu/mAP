import os
import glob
import json
import shutil
import sys
import convert_darkflow_json as cj
import convert_voc_xml as cx

MINOVERLAP = 0.5

def box_IoU(boxA,boxB):
    IoU = -1
    #topleft and bottomright (x,y) coordinates of the intersection rectangle
    x1 = max(boxA[0],boxB[0])
    y1 = max(boxA[1],boxB[1])
    x2 = min(boxA[2],boxB[2])
    y2 = min(boxA[3],boxB[3])
    #width and height of the intersection rectangle
    iw = x2 - x1 + 1
    ih = y2 - y1 + 1
    #make sure width and height are both bigger than 0
    if iw > 0 and ih > 0:
        interArea = iw * ih
        boxA_area = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxB_area = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        unionArea = boxA_area + boxB_area - interArea
        IoU = interArea / unionArea
    return IoU

def voc_ap(recall, precision):
    recall.insert(0, 0.0)
    recall.append(1.0)
    mrecall = recall[:]
    precision.insert(0, 0.0)
    precision.append(0.0)
    mprecision = precision[:]
    #Compute a version of the measured precision/recall curve with precision monotonically decreasing, by setting the precision for recall r to the maximum precision obtained for any recall r' > r
    #from pascal VOC2010 official website
    for i in range(len(mprecision)-2, -1, -1):
        mprecision[i] = max(mprecision[i], mprecision[i+1])

    #i_list save the index where the recall's value changes
    i_list = []
    for i in range(1, len(mrecall)):
        if mrecall[i] != mrecall[i-1]:
            i_list.append(i)

    ap = 0.0
    for i in i_list:
        ap += ((mrecall[i]-mrecall[i-1]) * mprecision[i])
    return ap, mrecall, mprecision
try:
    shutil.rmtree("./convert_file")
except IOError:
    print("First use")
else:
    print("Clean the previous data")

#make dirs
file_paths = ["./predicted","./ground_truth","./convert_file","./convert_file/predicted","./convert_file/ground_truth","./convert_file/predicted/tmp","./convert_file/ground_truth/tmp"]
for file_path in file_paths :
    if not os.path.exists(file_path):
        os.makedirs(file_path)
#convert darkflow json files and voc xml files to txt files
cj.convert()
cx.convert()

ground_truth_files = glob.glob("./convert_file/ground_truth/*.txt")
ground_truth_files.sort()
predicted_files = glob.glob("./convert_file/predicted/*.txt")
predicted_files.sort()

gt_label = []
gt_num_per_class = {}
#converts every txt file to json file, add 'used' attribute for avoiding multiple detections of the same object
for file in ground_truth_files:
    gt_bbox = []
    gt_file_name = os.path.basename(file).split(".")[0]
    with open(file) as f:
        for line in f.readlines():
            label, topleft_x, topleft_y, bottomright_x, bottomright_y = line.split()
            bbox = topleft_x + " " + topleft_y + " " + bottomright_x + " " + bottomright_y
            gt_bbox.append({"label":label, "bbox":bbox, "used":False})
            if label not in gt_label:
                gt_label.append(label)
                gt_num_per_class[label] = 1
            else:
                gt_num_per_class[label] += 1
        with open("./convert_file/ground_truth/tmp/" + gt_file_name + "_gt.json", 'w') as out:
            json.dump(gt_bbox, out)
#makes every prediction box sorts by label and decreasing confidence in the file
for label in gt_label:
    p_bbox = []
    for file in predicted_files:
        p_file_name = os.path.basename(file).split(".")[0]
        with open(file) as f:
            for line in f.readlines():
                tmp_label, confidence, topleft_x, topleft_y, bottomright_x, bottomright_y = line.split()
                if tmp_label == label:
                    bbox = topleft_x + " " + topleft_y + " " + bottomright_x + " " + bottomright_y
                    p_bbox.append({"confidence":confidence, "file_name":p_file_name, "bbox":bbox})
    p_bbox.sort(key=lambda x:x['confidence'], reverse=True)
    with open("./convert_file/predicted/tmp/" + label + "_p.json", 'w') as out:
        json.dump(p_bbox, out)
#Calculate ap
sum_AP = 0.0
result_text = ""
for label in gt_label:
    p_file = "./convert_file/predicted/tmp/" + label + "_p.json"
    p_data = json.load(open(p_file))

    tp = [0] * len(p_data)
    fp = [0] * len(p_data)

    for index, prediction_obj in enumerate(p_data):
        file_name = prediction_obj["file_name"]
        gt_file = "./convert_file/ground_truth/tmp/" + file_name + "_gt.json"
        gt_data = json.load(open(gt_file))

        IoU_max = -1
        gt_match = -1

        p_bbox = [float(x) for x in prediction_obj["bbox"].split()]
        for gt_obj in gt_data:
            if gt_obj["label"] == label:
                gt_bbox = [float(x) for x in gt_obj["bbox"].split()]
                IoU = box_IoU(p_bbox,gt_bbox)
                if IoU > IoU_max:
                    IoU_max = IoU
                    gt_match = gt_obj

        if IoU_max > MINOVERLAP:
            if not bool(gt_match["used"]):
                tp[index] = 1
                gt_match["used"] = True
                with open(gt_file, 'w') as f:
                    f.write(json.dumps(gt_data))
            else:
                fp[index] = 1
        else:
            fp[index] = 1


    sum = 0
    for index, value in enumerate(tp):
        tp[index] += sum
        sum += value
    sum = 0
    for index, value in enumerate(fp):
        fp[index] += sum
        sum += value
    recall = tp[:]
    for index, value in enumerate(tp):
        recall[index] = float(tp[index]) / gt_num_per_class[label]
    precision = tp[:]
    for index, value in enumerate(tp):
        precision[index] = float(tp[index]) / (fp[index] + tp[index])
    ap, mrecall, mprecision = voc_ap(recall, precision)
    sum_AP += ap
    text = "{0:.2f}%  ".format(ap * 100) + label + " AP"
    result_text += text + "\n"

mAP = sum_AP / len(gt_label)
result_text += "{0:.2f}%  mAP".format(mAP * 100)
with open("./result.txt", 'w') as result:
    result.write(result_text)
print(result_text)
