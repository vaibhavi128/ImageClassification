import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image
import json
import requests
from io import BytesIO

# Load pre-trained model (without classification layer)
model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

def load_dataset():
    """Load the dataset of people with their images"""
    with open('dataset.json') as f:
        return json.load(f)

def get_image_embedding(img_path):
    """Get embedding vector for an image with error handling"""
    try:
        if img_path.startswith('http'):
            response = requests.get(img_path, timeout=10)
            response.raise_for_status()
            if not response.headers.get('content-type', '').startswith('image/'):
                raise ValueError("URL does not point to an image")
            img_data = BytesIO(response.content)
        else:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")
            img_data = img_path
            
        img = image.load_img(img_data, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return model.predict(x)[0]
        
    except Exception as e:
        print(f"Error processing image {img_path}: {str(e)}")
        return None

def precompute_embeddings():
    """Precompute embeddings for all dataset images with validation"""
    dataset = load_dataset()
    embeddings = {}
    for person in dataset:
        try:
            embedding = get_image_embedding(person['image_url'])
            if embedding is not None:
                embeddings[person['name']] = {
                    'embedding': embedding,
                    'age': person['age'],
                    'image_url': person['image_url']
                }
            else:
                print(f"Skipping invalid image for {person['name']}")
        except Exception as e:
            print(f"Error processing {person['name']}: {str(e)}")
    return embeddings

def find_closest_match(query_embedding, embeddings):
    """Find the closest match in the dataset using cosine similarity"""
    max_similarity = -1
    best_match = None
    
    for name, data in embeddings.items():
        similarity = np.dot(query_embedding, data['embedding']) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding'])
        )
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = {
                'name': name,
                'age': data['age'],
                'image_url': data['image_url'],
                'confidence': f"{min(100, int(similarity * 100))}%"
            }
    
    return best_match