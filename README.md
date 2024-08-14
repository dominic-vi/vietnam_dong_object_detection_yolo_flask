## Vietnam Dong Detection App with YOLOv8 & Flask

### 1. Clone this repo to your machine
    git clone https://github.com/dominic-vi/vietnam_dong_object_detection_yolo_flask.git

### 2. Install modules needed to run the app
    pip install -r requirements.txt

### 3. You're going to need YOLOv8's finetuned weight file added to the weight directory
It should look something like this (if you don't have a weight directory feel free to create one)

    ├── static                    
    │   ├── style.css
    ├── templates                    
    │   ├── index.html
    │   ├── video.html
    ├── weights                    
    │   ├── [place your weight file here (.pt)]
    ├── app.py                    
    ├── requirements.txt 

### 4. Run the app
    flask --app app run