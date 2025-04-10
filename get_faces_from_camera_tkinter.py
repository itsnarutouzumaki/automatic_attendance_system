import dlib
import numpy as np
import cv2
import os
import shutil
import time
import logging
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
from features_extraction_to_csv import process_all_faces as extract_face

detector = dlib.get_frontal_face_detector()

class Face_Register:
    def __init__(self, reg_no):
        self.reg_no = reg_no
        self.current_frame_faces_cnt = 0
        self.existing_faces_cnt = 0
        self.ss_cnt = 0

        self.win = tk.Toplevel()
        self.win.title("Face Register")
        self.win.attributes('-fullscreen', True)
        self.win.configure(bg='black')

        self.frame_left_camera = tk.Frame(self.win, bg="black")
        self.label = tk.Label(self.win, bg="black")
        self.label.pack(side=tk.LEFT)
        self.frame_left_camera.pack()

        self.frame_right_info = tk.Frame(self.win, bg="black")
        self.label_cnt_face_in_database = tk.Label(self.frame_right_info, text=str(self.existing_faces_cnt), fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_fps_info = tk.Label(self.frame_right_info, text="", fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_warning = tk.Label(self.frame_right_info, fg="red", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_face_cnt = tk.Label(self.frame_right_info, text="Faces in current frame: ", fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_img_count = tk.Label(self.frame_right_info, text="Images captured: 0", fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_msg1 = tk.Label(self.frame_right_info, text="Press 'Q' to quit", fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.label_msg2 = tk.Label(self.frame_right_info, text="Take 5 to 10 pictures for better accuracy", fg="white", bg="black", font=('Helvetica', 16, 'bold'))
        self.log_all = tk.Label(self.frame_right_info, fg="white", bg="black", font=('Helvetica', 16))

        self.font_title = tkFont.Font(family='Helvetica', size=24, weight='bold')
        self.font_step_title = tkFont.Font(family='Helvetica', size=18, weight='bold')

        self.path_photos_from_camera = "data/data_faces_from_camera/"
        self.current_face_dir = ""
        self.font = cv2.FONT_ITALIC

        self.current_frame = np.ndarray
        self.face_ROI_image = np.ndarray
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0
        self.hh = 0

        self.out_of_range_flag = False
        self.face_folder_created_flag = False

        self.frame_time = 0
        self.frame_start_time = 0
        self.fps = 0
        self.fps_show = 0
        self.start_time = time.time()

        self.cap = cv2.VideoCapture(0)

        self.win.bind('c', self.save_current_face)
        self.win.bind('q', self.quit)

    def GUI_clear_data(self):
        folders_rd = os.listdir(self.path_photos_from_camera)
        for i in range(len(folders_rd)):
            shutil.rmtree(self.path_photos_from_camera + folders_rd[i])
        if os.path.isfile("data/features_all.csv"):
            os.remove("data/features_all.csv")
        self.label_cnt_face_in_database['text'] = "0"
        self.existing_faces_cnt = 0
        self.log_all["text"] = "Face images and features_all.csv removed!"
        self.label_img_count["text"] = "Images captured: 0"

    def GUI_info(self):
        tk.Label(self.frame_right_info, text="Face Register", font=self.font_title, fg="white", bg="black").grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=2, pady=20)
        tk.Label(self.frame_right_info, text="FPS: ", fg="white", bg="black", font=self.font_step_title).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_fps_info.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        tk.Label(self.frame_right_info, text="Faces in database: ", fg="white", bg="black", font=self.font_step_title).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_cnt_face_in_database.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        tk.Label(self.frame_right_info, text="Faces in current frame: ", fg="white", bg="black", font=self.font_step_title).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        self.label_face_cnt.grid(row=3, column=2, columnspan=3, sticky=tk.W, padx=5, pady=2)
        self.label_warning.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 1: Clear face photos", fg="white", bg="black").grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        tk.Button(self.frame_right_info, text='Clear', command=self.GUI_clear_data, font=self.font_step_title).grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        tk.Label(self.frame_right_info, font=self.font_step_title, text="Step 2: Save face image", fg="white", bg="black").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=20)
        tk.Label(self.frame_right_info, text="Press 'C' to save current face", fg="white", bg="black", font=('Helvetica', 14)).grid(row=8, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        self.log_all.grid(row=9, column=0, columnspan=3, sticky=tk.W, padx=5, pady=20)
        self.label_img_count.grid(row=10, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        self.label_msg1.grid(row=11, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        self.label_msg2.grid(row=12, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        self.frame_right_info.pack()

    def pre_work_mkdir(self):
        if not os.path.isdir(self.path_photos_from_camera):
            os.mkdir(self.path_photos_from_camera)

    def check_existing_faces_cnt(self):
        if os.listdir("data/data_faces_from_camera/"):
            person_list = os.listdir("data/data_faces_from_camera/")
            person_num_list = [int(person.split('_')[1]) for person in person_list]
            self.existing_faces_cnt = max(person_num_list)
        else:
            self.existing_faces_cnt = 0

    def update_fps(self):
        now = time.time()
        if str(self.start_time).split(".")[0] != str(now).split(".")[0]:
            self.fps_show = self.fps
        self.start_time = now
        self.frame_time = now - self.frame_start_time
        self.fps = 1.0 / self.frame_time
        self.frame_start_time = now
        self.label_fps_info["text"] = str(self.fps.__round__(2))

    def create_face_folder(self):
        self.existing_faces_cnt += 1
        self.current_face_dir = self.path_photos_from_camera + f"person_{self.existing_faces_cnt}_{self.reg_no}"
        os.makedirs(self.current_face_dir)
        self.log_all["text"] = f"\"{self.current_face_dir}/\" created!"
        logging.info("\n%-40s %s", "Create folders:", self.current_face_dir)
        self.ss_cnt = 0
        self.face_folder_created_flag = True

    def save_current_face(self, event=None):
        if self.face_folder_created_flag:
            if self.current_frame_faces_cnt == 1 and not self.out_of_range_flag:
                self.ss_cnt += 1
                self.face_ROI_image = np.zeros((int(self.face_ROI_height * 2), self.face_ROI_width * 2, 3), np.uint8)
                for ii in range(self.face_ROI_height * 2):
                    for jj in range(self.face_ROI_width * 2):
                        self.face_ROI_image[ii][jj] = self.current_frame[self.face_ROI_height_start - self.hh + ii][self.face_ROI_width_start - self.ww + jj]
                self.face_ROI_image = cv2.cvtColor(self.face_ROI_image, cv2.COLOR_BGR2GRAY)
                path = f"{self.current_face_dir}/img_face_{self.ss_cnt}.jpg"
                cv2.imwrite(path, self.face_ROI_image)
                self.label_img_count["text"] = f"Images captured: {self.ss_cnt}"
                self.log_all["text"] = f"\"{path}\" saved!"
                logging.info("%-40s %s", "Save into：", path)
            else:
                self.log_all["text"] = "No face in current frame or out of range!"
        else:
            self.log_all["text"] = "Please run step 2!"

    def get_frame(self):
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                frame = cv2.resize(frame, (640,480))
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            print("Error: No video input!!!")

    def process(self):
        ret, self.current_frame = self.get_frame()
        faces = detector(self.current_frame, 0)
        if ret:
            self.update_fps()
            self.label_face_cnt["text"] = str(len(faces))
            if len(faces) != 0:
                for k, d in enumerate(faces):
                    self.face_ROI_width_start = d.left()
                    self.face_ROI_height_start = d.top()
                    self.face_ROI_height = (d.bottom() - d.top())
                    self.face_ROI_width = (d.right() - d.left())
                    self.hh = int(self.face_ROI_height / 2)
                    self.ww = int(self.face_ROI_width / 2)

                    if (d.right() + self.ww) > 640 or (d.bottom() + self.hh > 480) or (d.left() - self.ww < 0) or (d.top() - self.hh < 0):
                        self.label_warning["text"] = "OUT OF RANGE"
                        self.out_of_range_flag = True
                        color_rectangle = (255, 0, 0)
                    else:
                        self.out_of_range_flag = False
                        self.label_warning["text"] = ""
                        color_rectangle = (255, 255, 255)
                    self.current_frame = cv2.rectangle(self.current_frame, (d.left() - self.ww, d.top() - self.hh), (d.right() + self.ww, d.bottom() + self.hh), color_rectangle, 2)
            self.current_frame_faces_cnt = len(faces)

            img_Image = Image.fromarray(self.current_frame)
            img_PhotoImage = ImageTk.PhotoImage(image=img_Image)
            self.label.img_tk = img_PhotoImage
            self.label.configure(image=img_PhotoImage)

        self.win.after(20, self.process)

    def quit(self, event=None):
        self.win.quit()
        self.win.destroy()
        self.cap.release()

    def run(self):
        self.pre_work_mkdir()
        self.check_existing_faces_cnt()
        self.create_face_folder()
        self.GUI_info()
        self.process()
        self.win.mainloop()

def registerStudent(reg_no):
    logging.basicConfig(level=logging.INFO)
    Face_Register_con = Face_Register(reg_no)
    Face_Register_con.run()
    extract_face()

if __name__ == '__main__':
    registerStudent("test123")
