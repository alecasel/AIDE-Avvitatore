import os
import queue
from threading import Thread

import cv2

from gefitvision.utils.utils_acquisition import (get_acquisition_function,
                                                 subscribe_to_redis_stream)
from gefitvision.utils.utils_common import (create_color_dict,
                                            create_stop_button,
                                            create_tkinter_listbox,
                                            draw_rectangles, read_yaml_file,
                                            start_redis_server,
                                            tkinter_selection_box)
from gefitvision.utils.utils_training import save_frame, write_labels_line,delete_redundant_files
from gefitvision.utils.utils_vision import (draw_rectangle_to_image,
                                            get_central_point_and_dim)


def on_mouse(event, x, y, flags, params):
    global current_rectangle, rectangles, rectangle_id, frame_with_boxes

    if event == cv2.EVENT_MOUSEMOVE:
        cv2.setWindowTitle("Draw Your Bounding Boxes", f'x: {x}, y: {y}')

    if event == cv2.EVENT_LBUTTONDOWN:
        current_rectangle = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        cv2.rectangle(
            frame_with_boxes, current_rectangle[0], (x, y), (255, 0, 0), thickness=2)
        cv2.imshow("Draw Your Bounding Boxes", frame_with_boxes)
        confirm = tkinter_selection_box("Confirm the rectangle? (Y/n): ")
        if confirm.lower() == "y":
            rectangle_name, selected_index = create_tkinter_listbox(
                items=object_list)
            if rectangle_name and not rectangle_name.isspace():
                rectangle_color = color_dict[rectangle_name]
                rectangles.append(
                    (camera_index,
                     rectangle_id,
                     current_rectangle[0],
                     (x, y),
                     rectangle_name,
                     rectangle_color))
                rectangle_id += 1
                current_rectangle = None
            else:
                pass


def main():

    global frame_with_boxes
    global color_dict, object_list
    global rectangles, current_rectangle, rectangle_id

    rectangles = []
    current_rectangle = None
    rectangle_id = 1

    reset = False

    start_redis_server(PATH_TO_REDIS_INSTALLATION_FOLDER)

    object_list = list(OBJECTS_DICT.keys())
    color_dict = create_color_dict(object_list)
    
    global camera_index
    camera_index = int(tkinter_selection_box("Choose your camera ID: "))

    path_to_areas_yaml_file = os.path.join(
        ROOT, PATH_SAVED_AREAS, f"areas_{camera_index}.yaml")

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

    # Acquire frames subscribing to redis server
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

    #cv2.namedWindow("Draw Your Bounding Boxes", cv2.WND_PROP_FULLSCREEN)
    cv2.namedWindow("Draw Your Bounding Boxes", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Draw Your Bounding Boxes",
                          cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Draw Your Bounding Boxes", on_mouse)

    while True:

        # Frame capture
        frame = img_queue.get()
        # Discard all other images in the queue
        while not img_queue.empty():
            img_queue.get()

        frame = cv2.resize(frame, dsize=FRAME_RESOLUTION)

        # Draw rectangles
        frame_with_areas = draw_rectangle_to_image(
            frame, areas_yaml_file=path_to_areas_yaml_file)

        cv2.putText(frame_with_areas, "Click and drag to draw a bounding box. Press S to save when finished, press Q to esc.",
                    (20, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

        if current_rectangle is not None and len(current_rectangle) == 2:
            cv2.rectangle(
                frame_with_areas, current_rectangle[0], current_rectangle[1], (255, 0, 0), thickness=2)

        if reset == True:
            rectangles = []
            # draw_rectangles(frame, rectangles)
            save_frame(frame=frame,
                       path=os.path.join(
                           ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}"),
                       max_number_images=MAX_NUMBER_TRAINING_IMAGE_PER_OBJECT,
                       img_format="jpg",
                       prefix=f"CAM{camera_index}",
                       forced_name=frame_name)
            reset = False

        frame_with_boxes = draw_rectangles(frame_with_areas, rectangles)

        cv2.imshow("Draw Your Bounding Boxes", frame_with_boxes)

        key = cv2.waitKey(1)

        if key == ord("q"):
            break
        elif key == ord("s"):
            if bool(rectangles):

                delete_redundant_files(os.path.join(
                           ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}"),
                           os.path.join(
                           ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}_Boxes"))

                frame_name = save_frame(frame=frame_with_boxes,
                                        path=os.path.join(
                                            ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}_Boxes"),
                                        max_number_images=MAX_NUMBER_TRAINING_IMAGE_PER_OBJECT,
                                        img_format="jpg",
                                        prefix=f"CAM{camera_index}",
                                        forced_name=None)

                for rect in rectangles:
                    
                    object_id = OBJECTS_DICT[rect[4]]
                    
                    x0=rect[2][0]
                    y0=rect[2][1]
                    x1=rect[3][0]
                    y1=rect[3][1]

                    start_point=(x0,y0)
                    end_point=(x1,y1)
                    
                    box_centre_and_size=get_central_point_and_dim(start_point,
                                                                  end_point,
                                                                  FRAME_RESOLUTION)

                    label = (object_id,
                             box_centre_and_size[0],
                             box_centre_and_size[1],
                             box_centre_and_size[2],
                             box_centre_and_size[3])
                    
                    write_labels_line(
                        path=os.path.join(
                            ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}"),
                        filename=frame_name,
                        label=label)

                reset = True

    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        from configuration.configuration import (
            FRAME_RESOLUTION, MAX_NUMBER_TRAINING_IMAGE_PER_OBJECT,
            OBJECTS_DICT, PATH_SAVED_AREAS, PATH_TO_CONFIGURATION,
            PATH_TO_REDIS_INSTALLATION_FOLDER, ROOT, SAVED_IMAGES_PATH)
    except:
        from configuration import (FRAME_RESOLUTION,
                                   MAX_NUMBER_TRAINING_IMAGE_PER_OBJECT,
                                   OBJECTS_DICT, PATH_SAVED_AREAS,
                                   PATH_TO_CONFIGURATION,
                                   PATH_TO_REDIS_INSTALLATION_FOLDER, ROOT,
                                   SAVED_IMAGES_PATH)
    main()
