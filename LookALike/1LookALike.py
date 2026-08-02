import torch
import face_recognition
import clip
from PIL import Image
import cv2
import numpy as np
#NOT THIS ONE USE THE OTHER ONE
def get_picture():
    cap = cv2.VideoCapture(0)
    pict = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow('MyWindow', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            pict = frame.copy()
            cv2.imwrite("Personal_Projects/LookALike/pers_pict.jpg", pict)
            break

    cap.release()
    cv2.destroyAllWindows()

    if pict is not None:
        # Detect face locations
        face_locations = face_recognition.face_locations(pict)

        if face_locations:
            # Use the first detected face
            top, right, bottom, left = face_locations[0]
            face_image = pict[top:bottom, left:right]
            face_pil = Image.fromarray(face_image)
            face_pil = face_pil.convert("L")
            face_pil.save("Personal_Projects/LookALike/pers_pict.jpg")
        else:
            print("No face detected. Saving full image instead.")
            Image.fromarray(pict).save("Personal_Projects/LookALike/pers_pict.jpg")

def compare_picture():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Text prompts
    texts = ["a human that looks like a frog", "a human that looks like a rat"]
    text_tokens = clip.tokenize(texts).to(device)

    def encode_avg(images):
        tensors = []
        for f in images:
            img = Image.open(f)
            tensors.append(model.encode_image(preprocess(img).unsqueeze(0).to(device)).squeeze(0))
        return torch.mean(torch.stack(tensors), dim=0)

    # Person image
    face_img = Image.open("Personal_Projects/LookALike/pers_pict.jpg").convert("RGB")
    face_tensor = preprocess(face_img).unsqueeze(0).to(device)

    with torch.no_grad():
        # Encode person
        person_features = model.encode_image(face_tensor).squeeze(0)
        person_features /= person_features.norm()

        # Image-to-Image Comparison
        frog_features = encode_avg(["Personal_Projects/LookALike/frog1.jpg", "Personal_Projects/LookALike/frog2.jpg", "Personal_Projects/LookALike/frog3.jpg"])
        rat_features  = encode_avg(["Personal_Projects/LookALike/rat1.jpg",  "Personal_Projects/LookALike/rat2.jpg",  "Personal_Projects/LookALike/rat3.jpg"])
        frog_features /= frog_features.norm()
        rat_features  /= rat_features.norm()

        image_frog_sim = torch.nn.functional.cosine_similarity(person_features, frog_features, dim=0).item()
        image_rat_sim  = torch.nn.functional.cosine_similarity(person_features, rat_features, dim=0).item()

    # Print results
    print(f"[Image] Similarity to frog: {image_frog_sim:.4f}")
    print(f"[Image] Similarity to rat:  {image_rat_sim:.4f}")
    print()


    if image_frog_sim > image_rat_sim:
        print("🐸 You look more like a frog!")
    else:
        print("🐭 You look more like a rat!")


get_picture()
compare_picture()