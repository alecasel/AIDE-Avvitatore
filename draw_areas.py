import os
import queue
from threading import Thread

import cv2

from gefitvision.utils.utils_acquisition import (get_acquisition_function,
                                                 subscribe_to_redis_stream)
from gefitvision.utils.utils_common import (create_stop_button,
                                            draw_rectangles, read_yaml_file,
                                            save_rectangles_yaml,
                                            start_redis_server,
                                            tkinter_selection_box)

rectangles = []
current_rectangle = None
rectangle_id = 1

def on_mouse(event, x, y, flags, params):
    global current_rectangle, rectangles, rectangle_id, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        current_rectangle = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        cv2.rectangle(
            frame, current_rectangle[0], (x, y), (255, 0, 0), thickness=2)
        cv2.imshow("Draw Your Working Areas", frame)
        confirm = tkinter_selection_box("Confirm the rectangle? (Y/n): ")
        if confirm.lower() == "y":
            rectangle_name = tkinter_selection_box("Choose rectangle name: ")
            if rectangle_name and not rectangle_name.isspace():
                color = tkinter_selection_box("Choose rectangle color: ")
                if color.lower() == "blue":
                    rectangle_color = (255, 0, 0)
                elif color.lower() == "red":
                    rectangle_color = (0, 0, 255)
                elif color.lower() == "green":
                    rectangle_color = (0, 255, 0)
                else:
                    rectangle_color = (0, 0, 0)
                rectangles.append(
                    (camera_index, rectangle_id, current_rectangle[0], (x, y), rectangle_name, rectangle_color))
                rectangle_id += 1
                current_rectangle = None
            else:
                pass


def main():

    try:
        from configuration.configuration import (
            FRAME_RESOLUTION, PATH_SAVED_AREAS, PATH_TO_CONFIGURATION,
            PATH_TO_REDIS_INSTALLATION_FOLDER, ROOT)
    except:
        from configuration import (FRAME_RESOLUTION, PATH_SAVED_AREAS,
                                   PATH_TO_CONFIGURATION,
                                   PATH_TO_REDIS_INSTALLATION_FOLDER, ROOT)

    start_redis_server(PATH_TO_REDIS_INSTALLATION_FOLDER)
    
    global camera_index
    camera_index = int(tkinter_selection_box("Choose your camera ID: "))

    all_cameras_settings = read_yaml_file(
        os.path.join(
            ROOT,
            PATH_TO_CONFIGURATION,
            'cameras.yaml'))['cameras']

    for item in all_cameras_settings:
        if item.get("id") == camera_index:
            camera_settings = item
            break

    acquisition_function = get_acquisition_function(camera_settings['model'])

    # Create a queue to share data between the redis frame subscriptor and the vision engine
    img_queue = queue.LifoQueue()

    t1 = Thread(target=acquisition_function,
                kwargs={"camera_index": camera_settings['id'],
                        "camera_serial_number": camera_settings['serial_number'],
                        "destination_ip": camera_settings['communication_IP'],
                        "frames_port": camera_settings['communication_port'],
                        "flask_ip": camera_settings['streaming_IP'],
                        "flask_port": camera_settings['streaming_port']},
                name=f"StreamFramesDrawing_{camera_settings['id']}")  # TODO stream the frames via HTTP with rectangles from setup
    t1.start()

    # Start the acquisition thread
    t2 = Thread(
        target=subscribe_to_redis_stream,
        kwargs={
            "camera_id": camera_index,
            "queue": img_queue,
            "destinatary_ip": camera_settings['communication_IP'],
            "frames_port": camera_settings['communication_port'],
        },
        name="AcquireFramesDrawing_")
    t2.start()

    Thread(target=create_stop_button, name="ButtonStopThread").start()

    cv2.namedWindow("Draw Your Working Areas", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Draw Your Working Areas",
                          cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Draw Your Working Areas", on_mouse)

    global frame

    while True:

        # Frame capture
        frame = img_queue.get()
        # Discard all other images in the queue
        while not img_queue.empty():
            img_queue.get()

        frame = cv2.resize(frame, dsize=FRAME_RESOLUTION)

        cv2.putText(frame, "Click and drag to draw a working area. Press S to save when finished, press Q to esc.",
                    (20, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

        if current_rectangle is not None and len(current_rectangle) == 2:
            cv2.rectangle(
                frame, current_rectangle[0], current_rectangle[1], (255, 0, 0), thickness=2)

        frame = draw_rectangles(frame, rectangles)
        cv2.imshow("Draw Your Working Areas", frame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break
        elif key == ord("s"):

            if not os.path.exists(os.path.join(
                    ROOT, PATH_SAVED_AREAS)):
                os.makedirs(os.path.join(
                    ROOT, PATH_SAVED_AREAS))

            if bool(rectangles):
                filename = f"areas_{camera_index}"
                areas_yaml_filepath = os.path.join(
                    ROOT, PATH_SAVED_AREAS, f"{filename}.yaml")
                areas_jpg_filepath = os.path.join(
                    ROOT, PATH_SAVED_AREAS, f"{filename}.jpg")
                save_rectangles_yaml(rectangles, areas_yaml_filepath)
                cv2.imwrite(areas_jpg_filepath, frame)
            break

    cv2.destroyAllWindows()
    exit()


if __name__ == '__main__':
    main()