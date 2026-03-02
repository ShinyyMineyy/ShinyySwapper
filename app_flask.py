"""
Flask Web Application for Face Swapper
Modern, professional HTML interface
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import cv2
import sys
import uuid
import shutil
import json
import time
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
from SinglePhoto import FaceSwapper

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for public access
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['SAVED_FACES_FOLDER'] = 'saved_faces'
app.config['TASKS_FOLDER'] = 'tasks'

# Available models (fixed)
AVAILABLE_MODELS = {
    'shinyyanalyzer': {'name': 'Shinyy Analyzer', 'desc': 'Best accuracy', 'type': 'analysis'}
}

AVAILABLE_SWAP_MODELS = {
    'shinyyswapper.onnx': {'name': 'Shinyy Swapper', 'desc': 'Best quality'}
}

# Initialize swappers dict
swappers = {}
current_model = 'shinyyanalyzer'
current_swap_model = 'shinyyswapper.onnx'

# Initialize default face swapper
print(f"Initializing FaceSwapper with {current_model} and {current_swap_model}...")
swappers[f"{current_model}_{current_swap_model}"] = FaceSwapper(config={
    'face_analysis_model': current_model,
    'model_name': current_swap_model
})
print(f"✓ {current_model} + {current_swap_model} loaded successfully.")

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['SAVED_FACES_FOLDER'], exist_ok=True)
os.makedirs(app.config['TASKS_FOLDER'], exist_ok=True)

def save_task(session_id, task_type, status='processing', total=0, current=0, result=None):
    task_path = os.path.join(app.config['TASKS_FOLDER'], f'{session_id}.json')
    task_data = {
        'session_id': session_id,
        'type': task_type,
        'status': status,
        'total': total,
        'current': current,
        'result': result,
        'timestamp': time.time()
    }
    with open(task_path, 'w') as f:
        json.dump(task_data, f)

def update_task(session_id, status=None, current=None, result=None):
    task_path = os.path.join(app.config['TASKS_FOLDER'], f'{session_id}.json')
    if os.path.exists(task_path):
        with open(task_path, 'r') as f:
            task_data = json.load(f)
        if status: task_data['status'] = status
        if current is not None: task_data['current'] = current
        if result: task_data['result'] = result
        with open(task_path, 'w') as f:
            json.dump(task_data, f)

def get_task(session_id):
    task_path = os.path.join(app.config['TASKS_FOLDER'], f'{session_id}.json')
    if os.path.exists(task_path):
        with open(task_path, 'r') as f:
            return json.load(f)
    return None

def delete_task(session_id):
    task_path = os.path.join(app.config['TASKS_FOLDER'], f'{session_id}.json')
    if os.path.exists(task_path):
        os.remove(task_path)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    for filename in os.listdir(app.config['TASKS_FOLDER']):
        if filename.endswith('.json'):
            with open(os.path.join(app.config['TASKS_FOLDER'], filename), 'r') as f:
                tasks.append(json.load(f))
    return jsonify({'tasks': sorted(tasks, key=lambda x: x['timestamp'], reverse=True)})

@app.route('/saved-faces', methods=['GET'])
def get_saved_faces():
    faces = []
    for f in os.listdir(app.config['SAVED_FACES_FOLDER']):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            faces.append(f'/saved-faces/{f}')
    return jsonify({'faces': faces})

@app.route('/saved-faces/<filename>')
def get_saved_face(filename):
    return send_file(os.path.join(app.config['SAVED_FACES_FOLDER'], filename))

@app.route('/save-face', methods=['POST'])
def save_face():
    try:
        file = request.files.get('face')
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        
        filename = f'{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}'
        path = os.path.join(app.config['SAVED_FACES_FOLDER'], filename)
        file.save(path)
        
        return jsonify({'success': True, 'path': f'/saved-faces/{filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-face', methods=['POST'])
def delete_face():
    try:
        data = request.json
        filename = data.get('filename', '').replace('/saved-faces/', '')
        path = os.path.join(app.config['SAVED_FACES_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    images = []
    videos = []
    for session in os.listdir(app.config['OUTPUT_FOLDER']):
        session_path = os.path.join(app.config['OUTPUT_FOLDER'], session)
        if os.path.isdir(session_path):
            for f in os.listdir(session_path):
                file_path = os.path.join(session_path, f)
                mtime = os.path.getmtime(file_path)
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append({'url': f'/output/{session}/{f}', 'time': mtime})
                elif f.lower().endswith('.mp4'):
                    videos.append({'url': f'/output/{session}/{f}', 'time': mtime})
    
    # Sort by time, most recent first
    images.sort(key=lambda x: x['time'], reverse=True)
    videos.sort(key=lambda x: x['time'], reverse=True)
    
    return jsonify({
        'images': [img['url'] for img in images],
        'videos': [vid['url'] for vid in videos]
    })

@app.route('/admin/outputs', methods=['GET'])
def admin_outputs():
    sessions = []
    for session in os.listdir(app.config['OUTPUT_FOLDER']):
        session_path = os.path.join(app.config['OUTPUT_FOLDER'], session)
        if os.path.isdir(session_path):
            files = [f for f in os.listdir(session_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4'))]
            if files:
                mtime = max([os.path.getmtime(os.path.join(session_path, f)) for f in files])
                sessions.append({
                    'id': session,
                    'files': files,
                    'timestamp': mtime * 1000
                })
    sessions.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify({'sessions': sessions})

@app.route('/admin/cleanup', methods=['POST'])
def admin_cleanup():
    try:
        deleted = 0
        cutoff = time.time() - (24 * 60 * 60)  # 24 hours ago
        
        # Cleanup old outputs
        for session in os.listdir(app.config['OUTPUT_FOLDER']):
            session_path = os.path.join(app.config['OUTPUT_FOLDER'], session)
            if os.path.isdir(session_path):
                mtime = os.path.getmtime(session_path)
                if mtime < cutoff:
                    shutil.rmtree(session_path, ignore_errors=True)
                    deleted += 1
        
        # Cleanup old tasks
        for task_file in os.listdir(app.config['TASKS_FOLDER']):
            if task_file.endswith('.json'):
                task_path = os.path.join(app.config['TASKS_FOLDER'], task_file)
                mtime = os.path.getmtime(task_path)
                if mtime < cutoff:
                    os.remove(task_path)
        
        return jsonify({'success': True, 'deleted': deleted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/models', methods=['GET'])
def get_models():
    return jsonify({
        'analysis_models': AVAILABLE_MODELS,
        'swap_models': AVAILABLE_SWAP_MODELS,
        'current_analysis': current_model,
        'current_swap': current_swap_model
    })

@app.route('/switch-model', methods=['POST'])
def switch_model():
    global current_model, current_swap_model
    try:
        data = request.json
        analysis_model = data.get('analysis_model', current_model)
        swap_model = data.get('swap_model', current_swap_model)
        
        if analysis_model not in AVAILABLE_MODELS:
            return jsonify({'error': 'Invalid analysis model'}), 400
        if swap_model not in AVAILABLE_SWAP_MODELS:
            return jsonify({'error': 'Invalid swap model'}), 400
        
        model_key = f"{analysis_model}_{swap_model}"
        
        if model_key not in swappers:
            print(f"Loading {analysis_model} + {swap_model}...")
            try:
                swappers[model_key] = FaceSwapper(config={
                    'face_analysis_model': analysis_model,
                    'model_name': swap_model
                })
                print(f"✓ {analysis_model} + {swap_model} loaded.")
            except Exception as load_error:
                error_msg = str(load_error)
                print(f"✗ Failed to load {analysis_model} + {swap_model}: {error_msg}")
                return jsonify({'error': f'Model loading failed: {error_msg}'}), 500
        
        current_model = analysis_model
        current_swap_model = swap_model
        return jsonify({
            'success': True,
            'analysis_model': current_model,
            'swap_model': current_swap_model
        })
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Switch model error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        source_files = request.files.getlist('source')
        target_files = request.files.getlist('target')
        enhance_type = request.form.get('enhance_type', 'none')

        if not source_files or not target_files:
            return jsonify({'error': 'Please upload both source and target images'}), 400

        session_id = str(uuid.uuid4())
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(session_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        total = len(source_files) * len(target_files)
        save_task(session_id, 'image', 'processing', total=total)

        # Save uploaded files
        source_paths = []
        for f in source_files:
            if f.filename:
                path = os.path.join(session_folder, f'src_{secure_filename(f.filename)}')
                f.save(path)
                source_paths.append(path)

        target_paths = []
        for f in target_files:
            if f.filename:
                path = os.path.join(session_folder, f'tgt_{secure_filename(f.filename)}')
                f.save(path)
                target_paths.append(path)
        
        # Save enhance type
        if enhance_type != 'none':
            with open(os.path.join(session_folder, 'enhance.txt'), 'w') as ef:
                ef.write(enhance_type)

        # Return session ID immediately for streaming
        return jsonify({'session_id': session_id, 'total': total, 'enhance': enhance_type != 'none'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/swap-stream/<session_id>')
def swap_stream(session_id):
    def generate():
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        
        source_paths = sorted([os.path.join(session_folder, f) for f in os.listdir(session_folder) if f.startswith('src_') and os.path.exists(os.path.join(session_folder, f))])
        target_paths = sorted([os.path.join(session_folder, f) for f in os.listdir(session_folder) if f.startswith('tgt_') and os.path.exists(os.path.join(session_folder, f))])
        
        if not source_paths or not target_paths:
            yield f"data: {json.dumps({'error': 'Source or target files not found'})}\n\n"
            return
        
        enhance_file = os.path.join(session_folder, 'enhance.txt')
        enhance_type = 'none'
        if os.path.exists(enhance_file):
            with open(enhance_file, 'r') as f:
                enhance_type = f.read().strip()
        
        enhance_faces = enhance_type == 'faces'
        enhance_full = enhance_type == 'full'
        
        total = len(source_paths) * len(target_paths)
        count = 0
        
        for i, src_path in enumerate(source_paths):
            for j, tgt_path in enumerate(target_paths):
                try:
                    yield f"data: {json.dumps({'status': 'swapping', 'current': count + 1, 'total': total})}\n\n"
                    
                    model_key = f"{current_model}_{current_swap_model}"
                    
                    # For full enhancement: both face and full image
                    # For faces only: just face enhancement
                    enhance_face = enhance_faces or enhance_full
                    enhance_full_img = enhance_full
                    
                    result = swappers[model_key].swap_faces(
                        src_path, 1, tgt_path, 1,
                        enhance_quality=enhance_face,
                        enhance_full_image=enhance_full_img
                    )
                    
                    out_path = os.path.join(output_folder, f'result_{i}_{j}.jpg')
                    cv2.imwrite(out_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    
                    count += 1
                    update_task(session_id, current=count)
                    yield f"data: {json.dumps({'image': f'/output/{session_id}/result_{i}_{j}.jpg', 'index': count})}\n\n"
                except Exception as e:
                    print(f"Swap failed: {e}")
                    yield f"data: {json.dumps({'error': str(e), 'index': count})}\n\n"
        
        update_task(session_id, status='completed', result=f'/output/{session_id}/')
        shutil.rmtree(session_folder, ignore_errors=True)
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/swap-video', methods=['POST'])
def swap_video():
    try:
        source_files = request.files.getlist('source')
        video_files = request.files.getlist('video')
        speed_mode = request.form.get('speed_mode', 'default')
        enhance_type = request.form.get('enhance_type', 'none')

        if not source_files or not video_files:
            return jsonify({'error': 'Please upload both source face and video'}), 400

        session_id = str(uuid.uuid4())
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(session_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        save_task(session_id, 'video', 'processing')

        source_path = os.path.join(session_folder, f'src_{secure_filename(source_files[0].filename)}')
        source_files[0].save(source_path)
        
        for video_file in video_files:
            video_path = os.path.join(session_folder, f'vid_{secure_filename(video_file.filename)}')
            video_file.save(video_path)
        
        if enhance_type != 'none':
            with open(os.path.join(session_folder, 'enhance.txt'), 'w') as ef:
                ef.write(enhance_type)

        return jsonify({'session_id': session_id, 'speed_mode': speed_mode})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/swap-video-stream/<session_id>/<speed_mode>')
def swap_video_stream(session_id, speed_mode):
    def generate():
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        
        source_path = [f for f in os.listdir(session_folder) if f.startswith('src_')]
        if not source_path:
            yield f"data: {json.dumps({'error': 'Source file not found'})}\n\n"
            return
        source_path = os.path.join(session_folder, source_path[0])
        
        if not os.path.exists(source_path):
            yield f"data: {json.dumps({'error': 'Source file does not exist'})}\n\n"
            return
        
        enhance_file = os.path.join(session_folder, 'enhance.txt')
        enhance_type = 'none'
        if os.path.exists(enhance_file):
            with open(enhance_file, 'r') as f:
                enhance_type = f.read().strip()
        
        enhance_faces = enhance_type == 'faces'
        enhance_full = enhance_type == 'full'
        
        if speed_mode == 'speed':
            frame_skip = 2
            scale_factor = 0.75
        elif speed_mode == 'extra_speed':
            frame_skip = 3
            scale_factor = 0.6
        else:
            frame_skip = 1
            scale_factor = 1.0
        
        video_files = [f for f in os.listdir(session_folder) if f.startswith('vid_')]
        if not video_files:
            yield f"data: {json.dumps({'error': 'Video file not found'})}\n\n"
            return
        
        for vid_idx, video_file in enumerate(video_files):
            video_path = os.path.join(session_folder, video_file)
            
            frames_dir = os.path.join(session_folder, f'frames_{vid_idx}')
            swapped_dir = os.path.join(session_folder, f'swapped_{vid_idx}')
            os.makedirs(frames_dir, exist_ok=True)
            os.makedirs(swapped_dir, exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            yield f"data: {json.dumps({'status': 'extracting', 'video_idx': vid_idx})}\n\n"
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if scale_factor < 1.0:
                    new_w = int(orig_w * scale_factor)
                    new_h = int(orig_h * scale_factor)
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                cv2.imwrite(os.path.join(frames_dir, f'frame_{frame_count:05d}.jpg'), frame)
                frame_count += 1
            cap.release()
            
            yield f"data: {json.dumps({'status': 'processing', 'total_frames': frame_count, 'video_idx': vid_idx})}\n\n"
            
            last_swapped = None
            stabilizer = None
            
            # Initialize stabilizer for temporal smoothing
            from core.VideoStabilizer import VideoStabilizer
            stabilizer = VideoStabilizer(window_size=7)
            
            for f_idx in range(frame_count):
                frame_path = os.path.join(frames_dir, f'frame_{f_idx:05d}.jpg')
                out_frame = os.path.join(swapped_dir, f'frame_{f_idx:05d}.jpg')
                
                if f_idx % frame_skip == 0:
                    try:
                        model_key = f"{current_model}_{current_swap_model}"
                        
                        # For full enhancement: both face and full image
                        # For faces only: just face enhancement
                        enhance_face = enhance_faces or enhance_full
                        enhance_full_img = enhance_full
                        
                        result = swappers[model_key].swap_faces(
                            source_path, 1, frame_path, 1,
                            enhance_quality=enhance_face,
                            enhance_full_image=enhance_full_img
                        )
                        
                        # Apply temporal stabilization
                        if stabilizer is not None:
                            try:
                                frame = cv2.imread(frame_path)
                                from insightface.app import FaceAnalysis
                                face_app = FaceAnalysis(name='buffalo_l')
                                face_app.prepare(ctx_id=-1, det_size=(640, 640))
                                faces = face_app.get(frame)
                                if faces:
                                    face = sorted(faces, key=lambda x: x.bbox[0])[0]
                                    bbox = face.bbox.astype(int)
                                    result = stabilizer.stabilize_frame(result, bbox)
                            except:
                                pass
                        
                        cv2.imwrite(out_frame, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        last_swapped = result
                    except:
                        shutil.copy(frame_path, out_frame)
                        last_swapped = cv2.imread(frame_path)
                else:
                    if last_swapped is not None:
                        cv2.imwrite(out_frame, last_swapped, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    else:
                        shutil.copy(frame_path, out_frame)
                
                if f_idx % 5 == 0 or f_idx == frame_count - 1:
                    yield f"data: {json.dumps({'status': 'frame', 'current': f_idx + 1, 'total': frame_count})}\n\n"
            
            yield f"data: {json.dumps({'status': 'encoding', 'video_idx': vid_idx})}\n\n"
            
            output_video = os.path.join(output_folder, f'result_{vid_idx}.mp4')
            frames = sorted([f for f in os.listdir(swapped_dir) if f.endswith('.jpg')])
            
            if frames:
                first_frame = cv2.imread(os.path.join(swapped_dir, frames[0]))
                h, w = first_frame.shape[:2]
                
                # Use H.264 codec for browser compatibility
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
                out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
                
                # Fallback to mp4v if avc1 fails
                if not out.isOpened():
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
                
                for frame_name in frames:
                    frame = cv2.imread(os.path.join(swapped_dir, frame_name))
                    out.write(frame)
                out.release()
                
                yield f"data: {json.dumps({'video': f'/output/{session_id}/result_{vid_idx}.mp4'})}\n\n"
            
            shutil.rmtree(frames_dir, ignore_errors=True)
            shutil.rmtree(swapped_dir, ignore_errors=True)
        
        update_task(session_id, status='completed', result=f'/output/{session_id}/')
        shutil.rmtree(session_folder, ignore_errors=True)
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/output/<session_id>/<filename>')
def get_output(session_id, filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], session_id, filename))

@app.route('/preview-compression', methods=['POST'])
def preview_compression():
    try:
        data = request.json
        image_url = data.get('image')
        scale = int(data.get('scale', 80))
        quality = int(data.get('quality', 70))
        format_type = data.get('format', 'JPEG')
        
        if not image_url:
            return jsonify({'error': 'No image provided'}), 400
        
        img_path = image_url.replace('/output/', app.config['OUTPUT_FOLDER'] + os.sep).replace('/', os.sep)
        img = cv2.imread(img_path)
        if img is None:
            return jsonify({'error': 'Image not found'}), 404
        
        h, w = img.shape[:2]
        new_w = int(w * scale / 100)
        new_h = int(h * scale / 100)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        session_id = 'preview'
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_folder, exist_ok=True)
        
        ext = '.jpg' if format_type == 'JPEG' else f'.{format_type.lower()}'
        out_path = os.path.join(output_folder, f'preview{ext}')
        
        if format_type == 'JPEG':
            cv2.imwrite(out_path, resized, [cv2.IMWRITE_JPEG_QUALITY, quality])
        elif format_type == 'PNG':
            cv2.imwrite(out_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, 9 - (quality // 11)])
        elif format_type == 'WEBP':
            cv2.imwrite(out_path, resized, [cv2.IMWRITE_WEBP_QUALITY, quality])
        
        file_size = os.path.getsize(out_path)
        
        return jsonify({
            'preview': f'/output/{session_id}/preview{ext}?t={uuid.uuid4().hex[:8]}',
            'size': file_size,
            'dimensions': f'{new_w}x{new_h}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress-images', methods=['POST'])
def compress_images():
    try:
        data = request.json
        images = data.get('images', [])
        scale = int(data.get('scale', 80))
        quality = int(data.get('quality', 70))
        format_type = data.get('format', 'JPEG')
        
        if not images:
            return jsonify({'error': 'No images provided'}), 400
        
        session_id = str(uuid.uuid4())
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_folder, exist_ok=True)
        
        results = []
        for idx, img_url in enumerate(images):
            img_path = img_url.replace('/output/', app.config['OUTPUT_FOLDER'] + os.sep).replace('/', os.sep)
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            h, w = img.shape[:2]
            new_w = int(w * scale / 100)
            new_h = int(h * scale / 100)
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            ext = '.jpg' if format_type == 'JPEG' else f'.{format_type.lower()}'
            out_path = os.path.join(output_folder, f'compressed_{idx}{ext}')
            
            if format_type == 'JPEG':
                cv2.imwrite(out_path, resized, [cv2.IMWRITE_JPEG_QUALITY, quality])
            elif format_type == 'PNG':
                cv2.imwrite(out_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, 9 - (quality // 11)])
            elif format_type == 'WEBP':
                cv2.imwrite(out_path, resized, [cv2.IMWRITE_WEBP_QUALITY, quality])
            
            results.append(f'/output/{session_id}/compressed_{idx}{ext}')
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/detect-faces', methods=['POST'])
def detect_faces():
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image provided'}), 400
        
        session_id = str(uuid.uuid4())
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_folder, exist_ok=True)
        
        save_task(session_id, 'multi', 'detecting')
        
        image_path = os.path.join(session_folder, f'target_{secure_filename(file.filename)}')
        file.save(image_path)
        
        model_key = f"{current_model}_{current_swap_model}"
        face_data, img = swappers[model_key].detect_all_faces(image_path)
        
        # Check if no faces detected
        if not face_data or len(face_data) == 0:
            shutil.rmtree(session_folder, ignore_errors=True)
            delete_task(session_id)
            return jsonify({'error': 'No faces detected in the image. Please use a clearer photo with visible faces.'}), 400
        
        # Save face crops
        faces = []
        for face_info in face_data:
            face_filename = f'face_{face_info["index"]}.jpg'
            face_path = os.path.join(session_folder, face_filename)
            cv2.imwrite(face_path, face_info['crop'])
            
            faces.append({
                'index': face_info['index'],
                'bbox': face_info['bbox'],
                'url': f'/uploads/{session_id}/{face_filename}'
            })
        
        return jsonify({
            'session_id': session_id,
            'faces': faces,
            'image_url': f'/uploads/{session_id}/target_{secure_filename(file.filename)}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<session_id>/<filename>')
def get_upload(session_id, filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], session_id, filename))

@app.route('/swap-multi-stream/<session_id>')
def swap_multi_stream(session_id):
    def generate():
        try:
            session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
            output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
            
            # Get target image
            target_files = [f for f in os.listdir(session_folder) if f.startswith('target_')]
            if not target_files:
                yield f"data: {json.dumps({'error': 'Target not found'})}\n\n"
                return
            
            target_path = os.path.join(session_folder, target_files[0])
            
            # Get all source files
            source_files = sorted([f for f in os.listdir(session_folder) if f.startswith('src_')])
            
            if not source_files:
                yield f"data: {json.dumps({'error': 'No sources found'})}\n\n"
                return
            
            # Verify all source files exist
            for source_file in source_files:
                source_path = os.path.join(session_folder, source_file)
                if not os.path.exists(source_path):
                    yield f"data: {json.dumps({'error': f'Source file not found: {source_file}'})}\n\n"
                    return
            
            total_faces = len(source_files)
            
            # Check enhance type
            enhance_file = os.path.join(session_folder, 'enhance.txt')
            enhance_type = 'none'
            if os.path.exists(enhance_file):
                with open(enhance_file, 'r') as f:
                    enhance_type = f.read().strip()
            
            enhance_faces = enhance_type == 'faces'
            enhance_full = enhance_type == 'full'
            
            current_result_path = target_path
            
            # Use original swap_faces method for each face sequentially
            for idx, source_file in enumerate(source_files, 1):
                face_idx = int(source_file.split('_')[1])
                source_path = os.path.join(session_folder, source_file)
                
                yield f"data: {json.dumps({'status': 'swapping', 'current': idx, 'total': total_faces, 'face_index': face_idx})}\n\n"
                
                try:
                    model_key = f"{current_model}_{current_swap_model}"
                    
                    # For full enhancement: both face and full image
                    # For faces only: just face enhancement
                    enhance_face = enhance_faces or enhance_full
                    enhance_full_img = enhance_full
                    
                    result = swappers[model_key].swap_faces(
                        source_path, 1,
                        current_result_path, face_idx,
                        enhance_quality=enhance_face,
                        enhance_full_image=enhance_full_img
                    )
                    
                    # Save as temp for next iteration
                    temp_path = os.path.join(session_folder, f'temp_{idx}.jpg')
                    cv2.imwrite(temp_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    current_result_path = temp_path
                    
                    yield f"data: {json.dumps({'status': 'completed', 'current': idx, 'total': total_faces, 'face_index': face_idx})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'error': f'Face {face_idx}: {str(e)}'})}\n\n"
            
            # Save final
            final_path = os.path.join(output_folder, 'result_multi.jpg')
            shutil.copy(current_result_path, final_path)
            update_task(session_id, status='completed', result=f'/output/{session_id}/result_multi.jpg')
            shutil.rmtree(session_folder, ignore_errors=True)
            
            yield f"data: {json.dumps({'done': True, 'result': f'/output/{session_id}/result_multi.jpg'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/swap-multi', methods=['POST'])
def swap_multi_faces():
    try:
        session_id = request.form.get('session_id')
        mappings_json = request.form.get('mappings')
        enhance_type = request.form.get('enhance_type', 'none')
        
        if not session_id or not mappings_json:
            return jsonify({'error': 'Invalid request'}), 400
        
        mappings = json.loads(mappings_json)
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_folder, exist_ok=True)
        
        # Save source files
        for mapping in mappings:
            face_index = mapping['face_index']
            source_file = request.files.get(f'source_{face_index}')
            if source_file:
                source_path = os.path.join(session_folder, f'src_{face_index}_{secure_filename(source_file.filename)}')
                source_file.save(source_path)
        
        if enhance_type != 'none':
            with open(os.path.join(session_folder, 'enhance.txt'), 'w') as ef:
                ef.write(enhance_type)
        
        return jsonify({'success': True, 'session_id': session_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
