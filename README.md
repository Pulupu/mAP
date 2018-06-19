## Data prepare

1. move the ground_truth files into ground_truth/

2. move the prediction files into predicted/

Notice:

- For the same image, the files which under **ground_truth/** and **predicted/** should be the same name.
```python
ground_truth/test1.json
predicted/test1.json
```
- Only for pascal voc format
## Run
```bash
python mAP.py
```
