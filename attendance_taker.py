import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
import logging
import sqlite3
import datetime
from xls_attendance.marking_attendance_in_xls import mark_attendance
from xls_attendance.voice_call_of_name import call_name

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()
current_date = datetime.datetime.now().strftime("%Y_%m_%d")
table_name = "attendance"
create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (name TEXT, UNIQUE(name))"
cursor.execute(create_table_sql)
conn.commit()
conn.close()

class Face_Recognizer:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()
        self.frame_cnt = 0
        self.face_features_known_list = []
        self.face_name_known_list = []
        self.last_frame_face_centroid_list = []
        self.current_frame_face_centroid_list = []
        self.last_frame_face_name_list = []
        self.current_frame_face_name_list = []
        self.last_frame_face_cnt = 0
        self.current_frame_face_cnt = 0
        self.current_frame_face_X_e_distance_list = []
        self.current_frame_face_position_list = []
        self.current_frame_face_feature_list = []
        self.last_current_frame_centroid_e_distance = 0
        self.reclassify_interval_cnt = 0
        self.reclassify_interval = 10

    def get_face_database(self):
        if os.path.exists("data/features_all.csv"):
            csv_rd = pd.read_csv("data/features_all.csv", header=None)
            for i in range(csv_rd.shape[0]):
                features_someone_arr = []
                self.face_name_known_list.append(csv_rd.iloc[i][0])
                for j in range(1, 129):
                    if csv_rd.iloc[i][j] == '':
                        features_someone_arr.append('0')
                    else:
                        features_someone_arr.append(csv_rd.iloc[i][j])
                self.face_features_known_list.append(features_someone_arr)
            logging.info("Faces in Database： %d", len(self.face_features_known_list))
            return 1
        else:
            logging.warning("'features_all.csv' not found!")
            return 0

    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now

    @staticmethod
    def return_euclidean_distance(feature_1, feature_2):
        feature_1 = np.array(feature_1)
        feature_2 = np.array(feature_2)
        dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
        return dist

    def centroid_tracker(self):
        for i in range(len(self.current_frame_face_centroid_list)):
            e_distance_current_frame_person_x_list = []
            for j in range(len(self.last_frame_face_centroid_list)):
                self.last_current_frame_centroid_e_distance = self.return_euclidean_distance(
                    self.current_frame_face_centroid_list[i], self.last_frame_face_centroid_list[j])
                e_distance_current_frame_person_x_list.append(self.last_current_frame_centroid_e_distance)
            last_frame_num = e_distance_current_frame_person_x_list.index(min(e_distance_current_frame_person_x_list))
            self.current_frame_face_name_list[i] = self.last_frame_face_name_list[last_frame_num]

    def draw_note(self, img_rd):
        cv2.putText(img_rd, "Face Recognizer", (50, 50), self.font, 1.5, (255, 255, 255), 2)
        cv2.putText(img_rd, f"Frame: {self.frame_cnt}", (50, 100), self.font, 1, (0, 255, 0), 2)
        cv2.putText(img_rd, f"FPS: {self.fps:.2f}", (50, 140), self.font, 1, (0, 255, 0), 2)
        cv2.putText(img_rd, f"Faces: {self.current_frame_face_cnt}", (50, 180), self.font, 1, (0, 255, 0), 2)
        cv2.putText(img_rd, "Press Q to Quit", (50, 220), self.font, 1, (100, 100, 255), 2)


    def attendance(self, name):
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO attendance (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

    def extract_and_drop_table(self):
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM attendance")
        rows = cursor.fetchall()
        registration_numbers = [row[0] for row in rows]
        cursor.execute("DROP TABLE IF EXISTS attendance")
        conn.commit()
        conn.close()
        return registration_numbers

    def process(self, stream):
        if self.get_face_database():
            end_time = time.time() + 300
            while stream.isOpened() and time.time() < end_time:
                self.frame_cnt += 1
                flag, img_rd = stream.read()
                kk = cv2.waitKey(1)

                faces = detector(img_rd, 0)
                self.last_frame_face_cnt = self.current_frame_face_cnt
                self.current_frame_face_cnt = len(faces)
                self.last_frame_face_name_list = self.current_frame_face_name_list[:]
                self.last_frame_face_centroid_list = self.current_frame_face_centroid_list
                self.current_frame_face_centroid_list = []

                if (self.current_frame_face_cnt == self.last_frame_face_cnt) and (
                        self.reclassify_interval_cnt != self.reclassify_interval):
                    self.current_frame_face_position_list = []

                    if "unknown" in self.current_frame_face_name_list:
                        self.reclassify_interval_cnt += 1

                    if self.current_frame_face_cnt != 0:
                        for k, d in enumerate(faces):
                            self.current_frame_face_position_list.append(
                                (faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)))
                            self.current_frame_face_centroid_list.append(
                                [(faces[k].left() + faces[k].right()) / 2,
                                 (faces[k].top() + faces[k].bottom()) / 2])
                            img_rd = cv2.rectangle(img_rd,
                                                   (d.left(), d.top()),
                                                   (d.right(), d.bottom()),
                                                   (255, 255, 255), 2)

                    if self.current_frame_face_cnt != 1:
                        self.centroid_tracker()

                    for i in range(self.current_frame_face_cnt):
                        img_rd = cv2.putText(img_rd, self.current_frame_face_name_list[i],
                                             self.current_frame_face_position_list[i], self.font, 0.8, (0, 255, 255), 2)

                    self.draw_note(img_rd)
                else:
                    self.current_frame_face_position_list = []
                    self.current_frame_face_X_e_distance_list = []
                    self.current_frame_face_feature_list = []
                    self.reclassify_interval_cnt = 0

                    if self.current_frame_face_cnt == 0:
                        self.current_frame_face_name_list = []
                    else:
                        self.current_frame_face_name_list = []
                        for i in range(len(faces)):
                            shape = predictor(img_rd, faces[i])
                            self.current_frame_face_feature_list.append(
                                face_reco_model.compute_face_descriptor(img_rd, shape))
                            self.current_frame_face_name_list.append("unknown")

                        for k in range(len(faces)):
                            self.current_frame_face_centroid_list.append(
                                [(faces[k].left() + faces[k].right()) / 2,
                                 (faces[k].top() + faces[k].bottom()) / 2])
                            self.current_frame_face_X_e_distance_list = []
                            self.current_frame_face_position_list.append(
                                (faces[k].left(), int(faces[k].bottom() + (faces[k].bottom() - faces[k].top()) / 4)))

                            for i in range(len(self.face_features_known_list)):
                                if str(self.face_features_known_list[i][0]) != '0.0':
                                    e_distance_tmp = self.return_euclidean_distance(
                                        self.current_frame_face_feature_list[k],
                                        self.face_features_known_list[i])
                                    self.current_frame_face_X_e_distance_list.append(e_distance_tmp)
                                else:
                                    self.current_frame_face_X_e_distance_list.append(999999999)

                            similar_person_num = self.current_frame_face_X_e_distance_list.index(
                                min(self.current_frame_face_X_e_distance_list))

                            if min(self.current_frame_face_X_e_distance_list) < 0.4:
                                self.current_frame_face_name_list[k] = self.face_name_known_list[similar_person_num]
                                self.attendance(self.face_name_known_list[similar_person_num])

                        self.draw_note(img_rd)

                remaining_time = int(end_time - time.time())
                cv2.putText(img_rd, f"Time Left: {remaining_time // 60}:{remaining_time % 60:02}", (50, 260), self.font, 1,
                            (0, 255, 0), 2)

                if kk == ord('q'):
                    break

                self.update_fps()

                cv2.namedWindow("camera", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("camera", img_rd)

    def run(self, courseId):
        cap = cv2.VideoCapture(0)
        self.process(cap)
        cap.release()
        cv2.destroyAllWindows()
        registration_numbers = self.extract_and_drop_table()
        call_name(mark_attendance(courseId, registration_numbers))

def attendance_taker(courseId):
    logging.basicConfig(level=logging.INFO)
    Face_Recognizer_con = Face_Recognizer()
    Face_Recognizer_con.run(courseId)

if __name__ == "__main__":
    attendance_taker("CSE101")
