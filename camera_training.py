import os

from ultralytics import YOLO

from gefitvision.utils.utils_common import tkinter_selection_box
from gefitvision.utils.utils_training import (create_training_folders,
                                              write_train_yaml_file)


def main():
    try:
        from configuration.configuration import (
            BATCH, DEVICE, DROPOUT_ENTITY, EPOCHS, IMGSZ, MODEL_SIZE,
            OBJECTS_DICT, OPTIMIZER, PATIENCE, ROOT, SAVED_IMAGES_PATH,
            SAVE_PERIOD, STARTING_WEIGHTS_PATH, TRAINING_DATASET_IMAGES_PATH,
            VALIDATION_DATASET_IMAGES_PATH, VALIDATION_IMAGES_PERCENTAGE,
            WEIGHTS_FOLDER_NAME, WORKERS)
    except:
        from configuration import (BATCH, DEVICE, DROPOUT_ENTITY, EPOCHS,
                                   IMGSZ, MODEL_SIZE, OBJECTS_DICT, OPTIMIZER,
                                   PATIENCE, ROOT, SAVED_IMAGES_PATH,
                                   SAVE_PERIOD,STARTING_WEIGHTS_PATH,
                                   TRAINING_DATASET_IMAGES_PATH,
                                   VALIDATION_DATASET_IMAGES_PATH,
                                   VALIDATION_IMAGES_PERCENTAGE,
                                   WEIGHTS_FOLDER_NAME, WORKERS)

    camera_index = int(tkinter_selection_box(
        "Choose the camera to be trained: "))

    write_train_yaml_file(os.path.join(ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}"),
                          f"dataset_generic_CAM{camera_index}.yaml",
                          os.path.join(ROOT, SAVED_IMAGES_PATH,
                                       f"Camera_{camera_index}"),
                          TRAINING_DATASET_IMAGES_PATH,
                          VALIDATION_DATASET_IMAGES_PATH,
                          OBJECTS_DICT)

    camera_dataset_path = os.path.join(
        ROOT, SAVED_IMAGES_PATH, f"Camera_{camera_index}")

    create_training_folders(camera_dataset_path,
                            VALIDATION_IMAGES_PERCENTAGE)
    
    pretrained_weights_path=os.path.join(
        ROOT,
        STARTING_WEIGHTS_PATH,
        f'yolov8{MODEL_SIZE}.pt'
    )
    
    model = YOLO(model=pretrained_weights_path)  # load a pretrained model (recommended for training)

    model.train(
        data=os.path.join(ROOT,
                          SAVED_IMAGES_PATH,
                          f"Camera_{camera_index}",
                          f"dataset_generic_CAM{camera_index}.yaml"),
        epochs=EPOCHS,
        patience=PATIENCE,
        batch=BATCH,
        imgsz=IMGSZ,
        device=DEVICE,
        save_period=SAVE_PERIOD,
        workers=WORKERS,
        project=WEIGHTS_FOLDER_NAME,
        name=f'_weights_CAM{camera_index}',
        exist_ok=True,
        pretrained=False,
        optimizer=OPTIMIZER,
        rect= False,
        dropout=DROPOUT_ENTITY,
        )
    
    if os.path.exists('yolov8n.pt'):
        print("Deleting downloaded yolo weights..")
        os.remove('yolov8n.pt')

if __name__ == '__main__':

    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(os.path.dirname(current))
    sys.path.append(parent)

    main()
