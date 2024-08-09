from flask import Flask, render_template, request, redirect, url_for, Response
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from threading import Event, Lock
from ultralytics import YOLO
from PIL import Image
import base64
import cv2
import os


app = Flask(__name__)
socketio = SocketIO(app)


thread = None
thread_lock = Lock()
thread_event = Event()


# Load the YOLOv8 model
model = YOLO(r'weights\yolov8n.pt')


@app.route('/')
def home():
    return render_template('index.html')


#Image upload for prediction
@app.route('/imgpred', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Save the uploaded image to a temporary location
            image_path = r"static/uploaded_image.jpg"
            file.save(image_path)
            # Run inference on the uploaded image
            results = model(image_path)  # results list
            # Visualize the results
            for i, r in enumerate(results):
                # Plot results image
                im_bgr = r.plot()  # BGR-order numpy array
                im_rgb = Image.fromarray(im_bgr[..., ::-1])  # RGB-order PIL image
                # Save the result image
                result_image_path = r"static/result_image.jpg"
                im_rgb.save(result_image_path)
            # Remove the uploaded image
            os.remove(image_path)
            # Render the HTML template with the result image path
            return render_template('index.html', image_path=result_image_path)
    # If no file is uploaded or GET request, render the form
    return render_template('index.html', image_path=None)

#Video upload
@app.route('/vidpred', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            video_path = os.path.join('static', 'uploaded_video.mp4')
            file.save(video_path)

    return render_template('index.html')


#Predict with SocketIO
def background_thread(event):
	#cap=cv2.VideoCapture(1)
	cap=cv2.VideoCapture(r"static\uploaded_video.mp4")
	global thread
	try:
		while(cap.isOpened() and event.is_set()):
			ret,img=cap.read()
			if ret:
				result = model.predict(img)
				img= result[0].plot()
				img = cv2.resize(img,(712,712))
				frame = cv2.imencode('.jpg', img)[1].tobytes()
				frame= base64.encodebytes(frame).decode("utf-8")
				message(frame)
				socketio.sleep(0.0)
			else:
				break
	finally:
		event.clear()
		thread = None


@socketio.on('send_message')
def message(json, methods=['GET','POST']):
	socketio.emit('image', json )

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on("start")
def start():
    global thread
    with thread_lock:
        if thread is None:
            thread_event.set()
            thread = socketio.start_background_task(background_thread, thread_event)

@socketio.on("stop")
def stop():
	global thread
	thread_event.clear()
	with thread_lock:
		if thread is not None:
			thread.join()
			thread = None
   

#Prediction from live stream video 
@app.route('/live_feed')
def live_feed():
    return Response(generate_live_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_live_frames():
    cap = cv2.VideoCapture(0)  # 0 represents the default webcam

    while True:
        success, frame = cap.read()
        if success:
            # Perform prediction on the frame using your YOLO model
            results = model(frame)
            annotated_frame = results[0].plot()
            # Convert the annotated frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            # Yield the frame bytes as part of the response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            break
        
    cap.release()


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True,  host='0.0.0.0', allow_unsafe_werkzeug=True)