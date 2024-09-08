from deepface import DeepFace
from deepface.models.FacialRecognition import FacialRecognition
import cv2
import numpy as np
import chromadb
from config import *


class Facial_Recognizer:
    def __init__(self, model_name, db_path_location):
        self.model: FacialRecognition = DeepFace.build_model(task="facial_recognition", model_name=model_name)
        self.target_size = self.model.input_shape
            
        self.vector_db = chromadb.PersistentClient(path=db_path_location)
        self.vector_db_collection = self.vector_db.get_or_create_collection(name="facial_embeddings",
                                                                             metadata={"hnsw:space": "cosine"} # l2 is the default
                                                                            )

        # Model Initialization
        self.init_model()
        
    def add_into_vector_db(self, embeddings_lst, ids_lst):
        self.vector_db_collection.add(embeddings = embeddings_lst,
                                      ids = ids_lst)
        
    def vector_embeddings_search_in_chromadb(self, embedding):
        result = self.vector_db_collection.query(
            query_embeddings = [embedding],
            n_results = 3
        )
        return result
                
    def init_model(self):
        img = cv2.imread("Lenna_(test_image).png")
        face = self.extract_face(img)
        face_img, _ = self.get_face_and_regions(face)
        self.get_embeddings(face_img)
            
    def extract_face(self, image):
        try:
            face = DeepFace.extract_faces(image)[0]
            return face
        except Exception as e:
            return None
    
    def run_for_face_frame(self, frame):
        face = self.extract_face(frame)
        face_img, _ = self.get_face_and_regions(face)
        self.get_embeddings(face_img)
        
    def get_face_and_regions(self, face_dict):
        face_image = face_dict["face"]
        face_area = face_dict['facial_area']
        x1, y1, x2, y2 = face_area['x'], face_area['y'], face_area['x'] + face_area['w'], face_area['y'] + face_area['h']
        
        face_image = cv2.resize(face_image, self.target_size)
        face_image = np.expand_dims(face_image, axis=0)  # to (1, 224, 224, 3)
        return face_image, [x1, y1, x2, y2]
    
    def get_embeddings_from_yolo_head(self, face):
        face_image = cv2.resize(face, self.target_size)
        face_image = np.expand_dims(face_image, axis=0)
        img_representation = self.model.forward(face_image)
        img_representation = np.array(img_representation).tolist()
        return img_representation
    
    def get_embeddings(self, face):
        img_representation = self.model.forward(face)
        img_representation = np.array(img_representation).tolist()
        return img_representation
        
    def compare_embeddings(self, emb1, emb2):
        return np.linalg.norm(np.array(emb1)- np.array(emb2))

        
