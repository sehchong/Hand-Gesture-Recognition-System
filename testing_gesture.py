import tkinter as tk
import cv2
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pickle
import mediapipe as mp
import os
import time

class TestingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASL Hand Gesture Recognition")
        self.cap = None
        self.predicted_character = ""
        self.prev_time = 0

        self.right_model_dict = self.load_model('./Model/right_trained_model.p')
        self.left_model_dict = self.load_model('./Model/left_trained_model.p')

        self.right_model = self.right_model_dict['model']
        self.left_model = self.left_model_dict['model']

        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3, min_tracking_confidence=0.3)

        self.labels_dict = {
            0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'K',
            10: 'L', 11: 'M', 12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T',
            19: 'U', 20: 'V', 21: 'W', 22: 'X', 23: 'Y'
        }

        self.interpretations_dict = {
            'A': 'Apple', 'B': 'Banana', 'C': 'Cat', 'D': 'Dog', 'E': 'Elephant', 'F': 'Fish',
            'G': 'Giraffe', 'H': 'Horse', 'I': 'Ice Cream', 'K': 'Kangaroo', 'L': 'Lion',
            'M': 'Monkey', 'N': 'Nurse', 'O': 'Octopus', 'P': 'Penguin', 'Q': 'Queen',
            'R': 'Rainbow', 'S': 'Sun', 'T': 'Tiger', 'U': 'Umbrella', 'V': 'Violin',
            'W': 'Watermelon', 'X': 'Xylophone', 'Y': 'Yoga'
        }

        self.setup_gui()
    
    # Function to load two models for left and right hands
    def load_model(self, file_path):
        self.model_dict = pickle.load(open(file_path, 'rb'))
        return self.model_dict

    def setup_gui(self):
        # Create a Canvas for the Camera Frame
        self.canvas_camera_frame = tk.Canvas(self.root, width=640, height=480, bg="black")
        self.canvas_camera_frame.pack(side=tk.TOP, padx=10, pady=10, anchor="center")

        # Create a information label
        information_label_frame = tk.Frame(self.root)
        information_label_frame.pack(side=tk.TOP, anchor="w")
        information_label = tk.Label(information_label_frame, text="Information Box:", font=("Helvetica", 12))
        information_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Create the Information Box
        information_frame = tk.Frame(self.root, bg="lightgray")
        information_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        recognized_alphabet_label = tk.Label(information_frame, text="Recognized Alphabet:", font=("Helvetica", 12))
        recognized_alphabet_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.recognized_alphabet_value = tk.StringVar()
        recognized_alphabet_value_label = tk.Label(information_frame, textvariable=self.recognized_alphabet_value, font=("Helvetica", 12))
        recognized_alphabet_value_label.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        interpretation_label = tk.Label(information_frame, text="Interpretation:", font=("Helvetica", 12))
        interpretation_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.interpretation_value = tk.StringVar()
        interpretation_value_label = tk.Label(information_frame, textvariable=self.interpretation_value, font=("Helvetica", 12))
        interpretation_value_label.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        fps_label = tk.Label(information_frame, text="FPS:", font=("Helvetica", 12))
        fps_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.fps_value = tk.StringVar()
        fps_value_label = tk.Label(information_frame, textvariable=self.fps_value, font=("Helvetica", 12))
        fps_value_label.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        hands_label = tk.Label(information_frame, text="Hands:", font=("Helvetica", 12))
        hands_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.hands_value = tk.StringVar()
        hands_value_label = tk.Label(information_frame, textvariable=self.hands_value, font=("Helvetica", 12))
        hands_value_label.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        # Create "Start Camera" button
        start_camera_button = tk.Button(self.root, text="Start Camera", command=self.start_camera, font=("Helvetica", 12))
        start_camera_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Create "Stop Camera" button
        stop_camera_button = tk.Button(self.root, text="Stop Camera", command=self.stop_camera, font=("Helvetica", 12))
        stop_camera_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.update_information_labels()  # Start updating information labels

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.update_camera_frame()

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def update_camera_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = self.hands.process(frame_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style())

                    data_aux = []
                    x_ = []
                    y_ = []

                    for hand_landmarks in results.multi_hand_landmarks:
                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y

                            x_.append(x)
                            y_.append(y)

                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_aux.append(x - min(x_))
                            data_aux.append(y - min(y_))

                    # Duplicate the data_aux to match the model's expectations
                    data_aux.extend(data_aux)

                    x1 = int(min(x_) * frame.shape[1]) - 10
                    y1 = int(min(y_) * frame.shape[0]) - 10

                    x2 = int(max(x_) * frame.shape[1]) - 10
                    y2 = int(max(y_) * frame.shape[0]) - 10

                    if len(data_aux) == 84:  # Ensure there are 84 features (42 duplicated features)
                        if hand_landmarks.landmark[9].x < hand_landmarks.landmark[0].x:
                            prediction = self.left_model.predict([np.asarray(data_aux)])
                        else:
                            prediction = self.right_model.predict([np.asarray(data_aux)])

                        self.predicted_character = self.labels_dict[int(prediction[0])]

                    interpretation = self.interpretations_dict.get(self.predicted_character, "Unknown")
                    self.interpretation_value.set(interpretation)  # Update interpretation

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                    cv2.putText(frame, self.predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

                    self.recognized_alphabet_value.set(self.predicted_character)  # Update recognized alphabet

                    # Calculate FPS
                    current_time = time.time()
                    fps = 1 / (current_time - self.prev_time)
                    self.fps_value.set(int(fps))  # Update FPS
                    self.prev_time = current_time

                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas_camera_frame.create_image(0, 0, anchor='nw', image=photo)
                self.canvas_camera_frame.photo = photo
                self.canvas_camera_frame.after(10, self.update_camera_frame)  # Update the frame every 10 milliseconds

    def update_information_labels(self):
        # Determine if the hand is on the right, left, or both
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(frame_rgb)
                if results.multi_handedness:
                    hands_list = [res.classification[0].label for res in results.multi_handedness]
                    if all(hand == 'Right' for hand in hands_list):
                        self.hands_value.set("Left Hand")
                    else:
                        self.hands_value.set("Right Hand")
                else:
                    self.hands_value.set("Unknown")

        self.root.after(1000, self.update_information_labels)  # Update hand information every 1000 milliseconds

if __name__ == "__main__":
    root = tk.Tk()
    app = TestingApp(root)
    root.mainloop()