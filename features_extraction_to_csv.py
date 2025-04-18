import os
import dlib
import csv
import numpy as np
import logging
import cv2

path_images_from_camera = "data/data_faces_from_camera/"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

def return_128d_features(path_img):
    img_rd = cv2.imread(path_img)
    if img_rd is None:
        logging.error("Unable to read image: %s", path_img)
        return 0
    faces = detector(img_rd, 1)
    logging.info("%-40s %-20s", " Image with faces detected:", path_img)
    if len(faces) != 0:
        shape = predictor(img_rd, faces[0])
        face_descriptor = face_reco_model.compute_face_descriptor(img_rd, shape)
    else:
        face_descriptor = 0
        logging.warning("no face")
    return face_descriptor

def return_features_mean_personX(path_face_personX):
    features_list_personX = []
    photos_list = os.listdir(path_face_personX)
    if photos_list:
        for i in range(len(photos_list)):
            photo_path = os.path.join(path_face_personX, photos_list[i])
            if not os.path.exists(photo_path):
                logging.error("File does not exist: %s", photo_path)
                continue
            logging.info("%-40s %-20s", " / Reading image:", photo_path)
            features_128d = return_128d_features(photo_path)
            if features_128d != 0:
                features_list_personX.append(features_128d)
            os.remove(photo_path)
            logging.info("%-40s %-20s", " / Deleted image:", photo_path)
    else:
        logging.warning(" Warning: No images in %s/", path_face_personX)

    if features_list_personX:
        features_mean_personX = np.array(features_list_personX, dtype=object).mean(axis=0)
    else:
        features_mean_personX = np.zeros(128, dtype=object, order='C')

    try:
        os.rmdir(path_face_personX)
        logging.info("%-40s %-20s", " / Deleted folder:", path_face_personX)
    except OSError as e:
        logging.error("Error deleting folder %s: %s", path_face_personX, e)

    return features_mean_personX

def process_all_faces(output_csv="data/features_all.csv"):
    logging.basicConfig(level=logging.INFO)
    person_list = os.listdir(path_images_from_camera)
    person_list.sort()

    existing_data = {}
    if os.path.exists(output_csv):
        with open(output_csv, "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or len(row) < 129:
                    continue
                existing_data[row[0]] = row[1:]

    for person in person_list:
        person_folder_path = os.path.join(path_images_from_camera, person)
        logging.info("Processing folder: %s", person_folder_path)
        if not os.path.exists(person_folder_path):
            logging.error("Folder does not exist: %s", person_folder_path)
            continue

        features_mean_personX = return_features_mean_personX(person_folder_path)

        if len(person.split('_', 2)) == 2:
            person_name = person
        else:
            person_name = person.split('_', 2)[-1]

        if person_name in existing_data:
            existing_data[person_name] = features_mean_personX
            logging.info("Updated features for person %s.", person_name)
        else:
            existing_data[person_name] = features_mean_personX
            logging.info("Added new features for person %s.", person_name)

    # Ab puri file overwrite karni hai
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for person_name, features in existing_data.items():
            row = [person_name] + list(map(str, features))
            writer.writerow(row)

    logging.info("Updated all features of faces registered into: %s", output_csv)

if __name__ == "__main__":
    process_all_faces()
