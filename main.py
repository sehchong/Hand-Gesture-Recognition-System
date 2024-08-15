import tkinter as tk
import cv2
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pickle
import mediapipe as mp
import os
import pyttsx3
from asl_display import ASLDisplayFrame
from testing_gesture import TestingApp
from msg_history import MessageHistoryFrame
import datetime

def load_model(file_path):
    model_dict = pickle.load(open(file_path, 'rb'))
    return model_dict['model']

right_model = load_model('./Model/right_trained_model.p')
left_model = load_model('./Model/left_trained_model.p')

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'K',
    10: 'L', 11: 'M', 12: 'N', 13: 'O', 14: 'P', 15: 'Q', 16: 'R', 17: 'S', 18: 'T',
    19: 'U', 20: 'V', 21: 'W', 22: 'X', 23: 'Y', 24: 'SPACE'
}

cap = None  # Initialize cap globally
predicted_character = ""  # Initialize the predicted character variable

time_limit = 5000
save_timer = None

# Function to exit the program
def exit_program():
    if cap is not None:
        cap.release()
    root.quit()

# Function to open the ASL Display frame
def open_asl_display():
    asl_display_root = tk.Toplevel()
    asl_display_frame = ASLDisplayFrame(asl_display_root)
    asl_display_frame.mainloop()

# Function to open the Testing Gesture frame
def open_testing_display():
    testing_display_root = tk.Toplevel()
    testing_frame = TestingApp(testing_display_root)
    testing_frame.mainloop()

# Function to open the Message History frame
def open_msg_history():
    msg_history_root = tk.Toplevel()
    message_history_frame = MessageHistoryFrame(msg_history_root)
    message_history_frame.update_message_history()
    message_history_frame.mainloop()

# Function to start the camera with ASL recognition
def start_camera():
    global cap, save_timer
    if cap is None:
        cap = cv2.VideoCapture(0)
        camera_frame_label.config(width=640, height=480)  # Resize the camera frame
        camera_frame_label.update_idletasks()  # Update the label
        update_camera_frame()
        
        # Start the timer for saving characters within the time limit
        save_timer = root.after(time_limit, save_characters)

# Function to stop the camera
def stop_camera():
    global cap, save_timer
    if cap is not None:
        cap.release()
        cap = None
        camera_frame_label.config(image=None)

        # Cancel the save timer
        root.after_cancel(save_timer)

# Function to update the camera frame
def update_camera_frame():
    global camera_frame_label, results, prediction
    global predicted_character  # Declare as global
    if cap is not None:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

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
                        prediction = left_model.predict([np.asarray(data_aux)])
                    else:
                        prediction = right_model.predict([np.asarray(data_aux)])

                    predicted_character = labels_dict[int(prediction[0])]

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            camera_frame_label.create_image(0, 0, anchor='nw', image=photo)
            camera_frame_label.photo = photo
            camera_frame_label.after(10, update_camera_frame)  # Update the frame every 10 milliseconds

# Function to check if hand landmarks are present
def is_hand_present(results):
    return results.multi_hand_landmarks is not None and len(results.multi_hand_landmarks) > 0

# Function to save characters to the system_message_textbox
def save_characters():
    global system_message_textbox, predicted_character, save_timer, reset_timer, prediction
    if cap is not None and is_hand_present(results):
        if int(prediction[0]) == 24:  # Check if the predicted character is space
            system_message_textbox.insert(tk.END, " ")  # Insert a space
        else:
            system_message_textbox.insert(tk.END, predicted_character)

        system_message_textbox.see(tk.END)  # Scroll to the end

        # Reset the timer for the next character
        save_timer = root.after(time_limit, save_characters)
    else:
        # Cancel the existing timer and set a new one
        root.after_cancel(save_timer)
        save_timer = root.after(time_limit, save_characters)

# Function to clear texts in the system_message_textbox
def clear_texts():
    global system_message_textbox  # Declare as global
    system_message_textbox.delete(1.0, tk.END)

# Function to handle key events (e.g., "p" key for saving characters)
def key_event(event):
    if event.char == "p":
        save_characters()

# Function to update the message history file
def update_message_history():
    messages = system_message_textbox.get(1.0, tk.END)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
    entry = f"{timestamp}: {messages.strip()}"  # Create a message entry with timestamp
    
    with open("history_messages.txt", "a") as history_file:
        history_file.write(entry + "\n")
    # Display the success message
    success_message_label.config(text="Message successfully saved")
    success_message_label.after(3000, clear_success_message)  # Clear the success message after 3000 milliseconds (3 seconds)

def clear_success_message():
    # Clear the success message
    success_message_label.config(text="")

def text_to_speech():
    messages = system_message_textbox.get(1.0, tk.END)

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    # Set Properties
    engine.setProperty('rate', 150)

    # Convert the text to speech
    engine.say(messages)

    # Wait for the speech to finish
    engine.runAndWait()

# Create the main window
root = tk.Tk()
root.title("Hand Gesture Recognition System")
root.state("zoomed")

# Bind the key event handler to the root window
root.bind("<Key>", key_event)

# Create a Frame for the top row of buttons
top_frame = tk.Frame(root)
top_frame.pack(pady=10, fill="x")

# Create top left and right frames
top_left_frame = tk.Frame(top_frame)
top_right_frame = tk.Frame(top_frame)

# Place left and right frames in the grid
top_left_frame.grid(row=0, column=0, padx=50, pady=5, sticky="nsew")
top_right_frame.grid(row=0, column=1, padx=450, pady=5, sticky="nsew")

# Create buttons for the top row
msg_history_button = tk.Button(top_left_frame, text="Message History", height=3, width=20, command=open_msg_history, font=("Helvetica", 14))
asl_button = tk.Button(top_left_frame, text="ASL Display", height=3, width=20, command=open_asl_display, font=("Helvetica", 14))
testing_button = tk.Button(top_left_frame, text="Testing Page", height=3, width=20, command=open_testing_display, font=("Helvetica", 14))
exit_button = tk.Button(top_right_frame, text="Exit", height=3, width=15, command=exit_program, font=("Helvetica", 14))

# Arrange the top row buttons in a grid layout
msg_history_button.grid(row=0, column=0, padx=10)
asl_button.grid(row=0, column=1, padx=10)
testing_button.grid(row=0, column=2, padx=10)
exit_button.grid(row=0, column=0, padx=10)

# Create a separator line
separator = ttk.Separator(root, orient="horizontal")
separator.pack(fill="x", padx=10, pady=10)

# Create a Frame for the Camera and System Message components
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill="y", expand=True)

# Create bottom left and right frames
bottom_left_frame = tk.Frame(bottom_frame)
bottom_right_frame = tk.Frame(bottom_frame)

# Place left and right frames in the grid
bottom_left_frame.grid(row=0, column=0, padx=50, pady=5, sticky="nsew")
bottom_right_frame.grid(row=0, column=1, padx=50, pady=5, sticky="nsew")

# Create labels and Entry fields for Camera and System Message
camera_label = tk.Label(bottom_left_frame, text="Camera:", font=("Helvetica", 14))
camera_label.grid(row=0, column=1, pady=5)

# Create a Frame to display the camera frame with an initial size of 85x32
camera_frame_label = tk.Canvas(bottom_left_frame, width=640, height=480, bg="black")
camera_frame_label.grid(row=1, column=1, pady=5)

# Create a Frame for camera buttons
camera_buttons_frame = tk.Frame(bottom_left_frame)
camera_buttons_frame.grid(row=2, column=1, pady=10)

# Create buttons for camera control and message clearing
start_camera_button = tk.Button(camera_buttons_frame, text="Start Camera", height=3, width=20, command=start_camera, font=("Helvetica", 12))
stop_camera_button = tk.Button(camera_buttons_frame, text="Stop Camera", height=3, width=20, command=stop_camera, font=("Helvetica", 12))
start_camera_button.pack(side="left", padx=10)
stop_camera_button.pack(side="left", padx=10)

# Create a System Message label and textbox
system_message_label = tk.Label(bottom_right_frame, text="System Message:", font=("Helvetica", 14))
system_message_label.grid(row=0, column=0, pady=5)
system_message_textbox = tk.Text(bottom_right_frame, width=30, height=8)
system_message_textbox.grid(row=1, column=0, pady=5)
system_message_textbox.config(font=("Helvetica", 32))  # Set the font size to 24px

# Create a Frame for message buttons
message_buttons_frame = tk.Frame(bottom_right_frame)
message_buttons_frame.grid(row=2, column=0, pady=10)

# Create buttons for message control
#save_characters_button = tk.Button(message_buttons_frame, text="Save Characters", height=3, width=16, command=save_characters, font=("Helvetica", 12))
clear_texts_button = tk.Button(message_buttons_frame, text="Clear Texts", height=3, width=16, command=clear_texts, font=("Helvetica", 12))
save_history_button = tk.Button(message_buttons_frame, text="Save Messages", height=3, width=16, command=update_message_history, font=("Helvetica", 12))
text_speech_button = tk.Button(message_buttons_frame, text="Text-to-Speech", height=3, width=16, command=text_to_speech, font=("Helvetica", 12))
#save_characters_button.pack(side="left", padx=10)
clear_texts_button.pack(side="left", padx=10)
save_history_button.pack(side="left", padx=10)
text_speech_button.pack(side="left", padx=10)

# Create a label for displaying the success message
success_message_frame = tk.Frame(bottom_right_frame)
success_message_frame.grid(row=3, column=0, pady=10)
success_message_label = tk.Label(success_message_frame, text="", font=("Helvetica", 14), fg="green")
success_message_label.pack(side="left", padx=10, pady=10)

# Start the Tkinter main loop
root.mainloop()