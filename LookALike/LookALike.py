import torch
import face_recognition
import clip
from PIL import Image
import cv2
import numpy as np

def stats_frog(frog):
    #Outlier Accounted
    frog_mean = 0.7014659615
    frog_stdev = 0.03186672265

    #Regular
    #frog_mean = 0.6982667593
    #frog_stdev = 0.03545862435

    z_frog = (frog - frog_mean) / frog_stdev
    return z_frog
def stats_rat(rat):
    #Outlier Accounted
    rat_mean = 0.6506051429
    rat_stdev = 0.0395626362

    #Regular
    #rat_mean = 0.6470937963
    #rat_stdev = 0.04437098984

    z_rat = (rat - rat_mean) / rat_stdev
    return z_rat

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
            cv2.imwrite("LookALike/pers_pict.jpg", pict)
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
            face_pil.save("LookALike/pers_pict.jpg")
        else:
            print("No face detected. Saving full image instead.")
            Image.fromarray(pict).save("LookALike/pers_pict.jpg")

def compare_picture():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)


    def encode_avg(images):
        tensors = []
        for f in images:
            img = Image.open(f)
            tensors.append(model.encode_image(preprocess(img).unsqueeze(0).to(device)).squeeze(0))
        return torch.mean(torch.stack(tensors), dim=0)

    # Person image
    face_img = Image.open("LookALike/pers_pict.jpg").convert("RGB")
    face_tensor = preprocess(face_img).unsqueeze(0).to(device)

    with torch.no_grad():
        # Encode person
        person_features = model.encode_image(face_tensor).squeeze(0)
        person_features /= person_features.norm()

        # Image-to-Image Comparison
        frog_features = encode_avg(["LookALike/frog1.jpg", "LookALike/frog2.jpg", "LookALike/frog3.jpg"])
        rat_features  = encode_avg(["LookALike/rat1.jpg",  "LookALike/rat2.jpg",  "LookALike/rat3.jpg"])
        frog_features /= frog_features.norm()
        rat_features  /= rat_features.norm()

        image_frog_sim = torch.nn.functional.cosine_similarity(person_features, frog_features, dim=0).item()
        image_rat_sim  = torch.nn.functional.cosine_similarity(person_features, rat_features, dim=0).item()

    z_frog = stats_frog(image_frog_sim)
    z_rat = stats_rat(image_rat_sim)
    # Print results
    print(f"[Image] Similarity to frog: {image_frog_sim:.4f}")
    print(f"[Image] Similarity to rat:  {image_rat_sim:.4f}")
    #print()


    if z_frog > z_rat:
        print("🐸 You look more like a frog!")
    else:
        print("🐭 You look more like a rat!")
    print (f"here is thestandard deviation for rat",z_rat)
    print(f"here is thestandard deviation for frog",z_frog)


get_picture()
compare_picture()