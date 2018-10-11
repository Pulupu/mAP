## Data prepare

1. move the ground_truth files into ground_truth/

2. move the prediction files into predicted/

Notice:

- For the same image, the files which under **ground_truth/** and **predicted/** should be the same name.
```python
ground_truth/test1.xml
predicted/test1.json
```
- xml format is the PASCAL VOC format
- json format example:
```python
[{"topleft": {"y": 156, "x": 827}, "label": "metal_side", "confidence": 0.79, "bottomright": {"y": 316, "x": 1108}},
 {"topleft": {"y": 201, "x": 652}, "label": "metal_side", "confidence": 0.84, "bottomright": {"y": 405, "x": 866}},
 ...]
```
## Run
```bash
python mAP.py
```
