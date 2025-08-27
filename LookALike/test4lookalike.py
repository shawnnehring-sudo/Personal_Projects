import torch
import face_recognition
import clip
from PIL import Image
import cv2
import numpy as np


device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load and preprocess images
person_img = preprocess(Image.open("LookALike/leonardo.jpg")).unsqueeze(0).to(device)
frog_img = preprocess(Image.open("LookALike/frog.jpg")).unsqueeze(0).to(device)
rat_img = preprocess(Image.open("LookALike/rat.jpg")).unsqueeze(0).to(device)

# Encode images
with torch.no_grad():
    person_features = model.encode_image(person_img)
    frog_features = model.encode_image(frog_img)
    rat_features = model.encode_image(rat_img)

# Normalize and compute cosine similarity
person_features /= person_features.norm(dim=-1, keepdim=True)
frog_features /= frog_features.norm(dim=-1, keepdim=True)
rat_features /= rat_features.norm(dim=-1, keepdim=True)

frog_similarity = (person_features @ frog_features.T).item()
rat_similarity = (person_features @ rat_features.T).item()

print(f"Similarity to frog: {frog_similarity:.4f}")
print(f"Similarity to rat: {rat_similarity:.4f}")