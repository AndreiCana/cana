from flask import Flask, request, jsonify
import cv2
import threading

app = Flask(__name__)

# Dicționar pentru a păstra starea redării pentru fiecare client
client_state = {}

def play_video(video_path, num_monitors):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    monitor_cols = int(num_monitors ** 0.5)
    monitor_rows = (num_monitors + monitor_cols - 1) // monitor_cols
    monitor_frame_width = frame_width // monitor_cols
    monitor_frame_height = frame_height // monitor_rows
    windows = [cv2.namedWindow(f"Monitor {i}", cv2.WINDOW_NORMAL) for i in range(num_monitors)]
    for window in windows:
        cv2.resizeWindow(window, frame_width, frame_height)
    
    while client_state['playing']:
        ret, frame = cap.read()
        if not ret:
            break
        
        for i in range(num_monitors):
            col = i % monitor_cols
            row = i // monitor_cols
            start_x = col * monitor_frame_width
            start_y = row * monitor_frame_height
            end_x = start_x + monitor_frame_width
            end_y = start_y + monitor_frame_height
            monitor_frame = frame[start_y:end_y, start_x:end_x, :]
            cv2.imshow(f"Monitor {i}", monitor_frame)
        
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'): 
            break
    
    cap.release()
    cv2.destroyAllWindows()

@app.route('/start', methods=['POST'])
def start_playback():
    global client_state
    data = request.json
    video_path = data.get('video_path')
    num_monitors = data.get('num_monitors')
    
    if not video_path or num_monitors is None:
        return jsonify({'message': 'Bad request'}), 400
    
    client_state['playing'] = True
    threading.Thread(target=play_video, args=(video_path, num_monitors)).start()
    return jsonify({'message': 'Playback started'}), 200

@app.route('/stop', methods=['POST'])
def stop_playback():
    global client_state
    client_state['playing'] = False
    cv2.destroyAllWindows()
    return jsonify({'message': 'Playback stopped'}), 200

if __name__ == '__main__':
    client_state['playing'] = False
    app.run(host='0.0.0.0', port=12345)
