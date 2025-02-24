import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

# Load OpenCV DNN face detector
net = cv2.dnn.readNetFromCaffe(
    "deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel"
)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

selected_faces = []
blur_sigma = 5  # Default blur strength

def detect_faces(image):
    h, w = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    boxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            boxes.append((max(0, x1), max(0, y1), min(w, x2), min(h, y2)))
    return boxes

def select_faces(frame, boxes):
    def on_mouse_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            for i, (x1, y1, x2, y2) in enumerate(boxes):
                if x1 <= x <= x2 and y1 <= y <= y2:
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    if (center_x, center_y) in selected_faces:
                        selected_faces.remove((center_x, center_y))
                    else:
                        selected_faces.append((center_x, center_y))
                    break

    cv2.namedWindow("Select Faces")
    cv2.setMouseCallback("Select Faces", on_mouse_click)

    while True:
        temp_frame = frame.copy()
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            color = (0, 255, 0) if (center_x, center_y) in selected_faces else (0, 0, 255)
            cv2.rectangle(temp_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(temp_frame, f"{i}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow("Select Faces", temp_frame)
        if cv2.waitKey(1) & 0xFF == 13:  # Press Enter to finish
            break

    cv2.destroyWindow("Select Faces")
    print("Selected faces (centers):", selected_faces)

def is_face_selected(center_x, center_y, selected_faces, tolerance=20):
    for sel_x, sel_y in selected_faces:
        if abs(center_x - sel_x) < tolerance and abs(center_y - sel_y) < tolerance:
            return True
    return False

def apply_circular_blur(image, x1, y1, x2, y2, sigma):
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    head_width = x2 - x1
    head_height = y2 - y1
    radius = int(max(head_width, head_height) * 0.55)

    mask = np.zeros_like(image, dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)

    blur_region = image[max(0, center_y-radius):min(image.shape[0], center_y+radius), 
                        max(0, center_x-radius):min(image.shape[1], center_x+radius)]
    if blur_region.size == 0:
        return image

    kernel_size = (min(max(radius // 3, 3), 15) | 1, min(max(radius // 3, 3), 15) | 1)
    blurred_region = cv2.GaussianBlur(blur_region, kernel_size, sigma)

    result = image.copy()
    region_y1, region_y2 = max(0, center_y-radius), min(image.shape[0], center_y+radius)
    region_x1, region_x2 = max(0, center_x-radius), min(image.shape[1], center_x+radius)
    mask_region = mask[region_y1:region_y2, region_x1:region_x2]
    result[region_y1:region_y2, region_x1:region_x2] = np.where(
        mask_region == 255, blurred_region, result[region_y1:region_y2, region_x1:region_x2])

    return result

def blur_faces_in_video(input_path, output_path, sigma):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception("Could not open video file")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    ret, frame = cap.read()
    if not ret:
        raise Exception("Could not read video frame")

    boxes = detect_faces(frame)
    selected_faces.clear()
    select_faces(frame, boxes)

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        boxes = detect_faces(frame)
        for (x1, y1, x2, y2) in boxes:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            if not is_face_selected(center_x, center_y, selected_faces):
                frame = apply_circular_blur(frame, x1, y1, x2, y2, sigma)

        out.write(frame)

    cap.release()
    out.release()

def blur_faces_in_image(input_path, output_path, sigma):
    image = cv2.imread(input_path)
    if image is None:
        raise Exception("Could not open image file")

    boxes = detect_faces(image)
    selected_faces.clear()
    select_faces(image, boxes)

    for (x1, y1, x2, y2) in boxes:
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        if not is_face_selected(center_x, center_y, selected_faces):
            image = apply_circular_blur(image, x1, y1, x2, y2, sigma)

    cv2.imwrite(output_path, image)

def process_folder(input_folder, output_folder, sigma):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        print(f"Processing: {filename} with blur sigma {sigma}")

        if filename.endswith(('.mp4', '.avi')):
            blur_faces_in_video(input_path, output_path, sigma)
        elif filename.endswith(('.jpg', '.png', '.jpeg')):
            blur_faces_in_image(input_path, output_path, sigma)

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder = os.path.join(folder_path, "output")
        process_folder(folder_path, output_folder, blur_sigma)
        messagebox.showinfo("Success", "Processing complete! Check the /output folder.")

def update_blur_sigma(val):
    global blur_sigma
    blur_sigma = float(val)
    blur_label.config(text=f"Blur Strength: {blur_sigma}")

# GUI Setup
root = tk.Tk()
root.title("Face Blur App")

label = tk.Label(root, text="Select a folder containing video clips or images:")
label.pack(pady=10)

select_button = tk.Button(root, text="Select Folder", command=select_folder)
select_button.pack(pady=5)

blur_label = tk.Label(root, text=f"Blur Strength: {blur_sigma}")
blur_label.pack(pady=5)

blur_slider = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, length=200, 
                       command=update_blur_sigma, resolution=0.5)
blur_slider.set(blur_sigma)  # Default value
blur_slider.pack(pady=5)

root.mainloop()