from detector_helper import *
from config import *
from Embeddings_helper import *
from fastapi import FastAPI, File, UploadFile, Form
import os
import shutil

head_detector = Head_Detector(weights=head_detector_weights, half=head_weights_half_bool)
fr = Facial_Recognizer(model_name=fr_model_name, db_path_location=db_folder_location)
app = FastAPI()
os.makedirs(Uploads_directory_for_embeddings, exist_ok=True)
os.makedirs(Uploads_directory_for_processing, exist_ok=True)
os.makedirs(processed_video_directory, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}

# Function to save uploaded file
def save_file_to_disk(uploaded_file: UploadFile, destination: str) -> str:
    with open(destination, "wb") as buffer:
        buffer.write(uploaded_file.file.read())
    return destination

@app.post("/get-person-embeddings/")
def get_person_embeddings(roll_no: str = Form(...), video_file: UploadFile = File(...)):
    video_file_path = os.path.join(Uploads_directory_for_embeddings, video_file.filename)
    save_file_to_disk(video_file, video_file_path)
    
    total_frames_extract = 10
    cap = cv2.VideoCapture(video_file_path)
    ret, frame = cap.read()
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_counter = 0
    capture_frame = total_frames // total_frames_extract
    int_xtra = 10
    
    embeddings_buffer = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if (frame_counter % capture_frame) == 0:
            pred = head_detector.detect(frame)[0]  # Assuming head_detector is initialized
            print(pred)
            x1, y1, x2, y2 = map(int, pred)
            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)  # Draw a rectangle around the face
            
            # Extract face image with a margin (int_xtra)
            face_image = frame[max(0, y1 - int_xtra):min(frame.shape[0], y2 + int_xtra), 
                               max(0, x1 - int_xtra):min(frame.shape[1], x2 + int_xtra)]
            embeddings = fr.get_embeddings_from_yolo_head(face_image)
                        
            embeddings_buffer.append(embeddings)            
            # cv2.imshow("Captured_Head", face_image)
            # cv2.imshow("Frame", frame)
            
        # if cv2.waitKey(1) == ord('q'):
        #     break
        
        frame_counter += 1
        
    cap.release()
    cv2.destroyAllWindows()
        
    ids_lst = []
    for no in range(len(embeddings_buffer)):
        temp_name = roll_no + "__" + str(no + 1)
        ids_lst.append(temp_name)
        
    fr.add_into_vector_db(embeddings_buffer, ids_lst)
    
    print("Embeddings saved for ", roll_no)
    

@app.post("/run-for-video-file/")
def run_for_video_file(video_file: UploadFile = File(...)):
    print(video_file)
    filename = video_file.filename.split("/")[-1]
    video_file_path = os.path.join(Uploads_directory_for_processing, filename)
    save_file_to_disk(video_file, video_file_path)

    cap = cv2.VideoCapture(video_file_path)
    ret, frame = cap.read()
    int_xtra = 10
    roll_no_with_hits = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        preds = head_detector.detect(frame)  # Assuming head_detector is initialized
        for pred in preds:
            x1, y1, x2, y2 = map(int, pred)
            
            # Extract face image with a margin (int_xtra)
            face_image = frame[max(0, y1 - int_xtra):min(frame.shape[0], y2 + int_xtra), 
                                max(0, x1 - int_xtra):min(frame.shape[1], x2 + int_xtra)]
            embeddings = fr.get_embeddings_from_yolo_head(face_image)
            
            result = fr.vector_embeddings_search_in_chromadb(embeddings)
            print(result)
            result_id, result_distance = result['ids'][0][0], result['distances'][0][0]

            if result_distance < distance_threshold:
                print(result_id)
                roll_no, _ = result_id.split("__")
                if roll_no in roll_no_with_hits.keys():
                    roll_no_with_hits[roll_no] += 1
                else:
                    roll_no_with_hits[roll_no] = 1
                
    cap.release()
    cv2.destroyAllWindows()
    
    result_lst = [roll_no for roll_no, hits in roll_no_with_hits.items() if hits > 10]

    return {"matched_roll_nos": result_lst}

def create_video():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video capture.")
        exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
    out = cv2.VideoWriter('test_sample_video.avi', fourcc, 30, (frame_width, frame_height))

    # Duration and frame settings
    fps = 30  # Frames per second
    duration = 5  # Duration in seconds
    total_frames = fps * duration  # Total frames to capture

    frame_count = 0

    while frame_count < total_frames:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to capture frame.")
            break

        out.write(frame)

        cv2.imshow('Frame', frame)

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif frame_count > total_frames:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Video captured and saved successfully!")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
