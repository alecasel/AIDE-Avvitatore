import os
from multiprocessing import Process
from threading import Thread

from configuration.configuration import (PATH_TO_CONFIGURATION,
                                         PATH_TO_REDIS_INSTALLATION_FOLDER,
                                         ROOT,PLC_CONFIGURATION_YAML_PATH,
                                         CAM1_DB_RANGE,
                                         CAM2_DB_RANGE,
                                         CAM3_DB_RANGE,
                                         NUMBER_OF_AREAS,
                                         ACTIVATE_PLC_COMMUNICATION,
                                         )
from gefitvision.utils.utils_acquisition import get_acquisition_function
from gefitvision.utils.utils_common import (create_stop_button, read_yaml_file,
                                            start_redis_server)
from gefitvision.utils.utils_vision import get_vision_function
from gefitvision.utils.utils_communication import (read_from_redis, write_to_redis,
                                                   redis_for_plc,
                                                   extract_from_yaml_plc_data,
                                                   generate_communication_lists,
                                                   set_default_values,
                                                   start_camera_communication_with_plc)

# TODO put GUI communication in appropriate module

def communicate_with_GUI():
    while True:
        print("                              I'm communicating with GUI.", end="\r")
        print("                              I'm communicating with GUI..", end="\r")
        print("                              I'm communicating with GUI...", end="\r")
        print("                              I'm communicating with GUI   ", end="\r")


def camera_pipeline(acquisition_handler, vision_handler, camera_settings):

    # Continously communicate with GUI
    #Thread(target=communicate_with_GUI,
    #       name=f"GUI_communication_{camera_settings['id']}").start()  # TODO write thread to communicate with external GUI

    # Acquisition of frames, stream on redis,host frames via HTTP server
    Thread(target=acquisition_handler,
           kwargs={"camera_index": camera_settings['id'],
                   "camera_serial_number": camera_settings['serial_number'],
                   "destination_ip": camera_settings['communication_IP'],
                   "frames_port": camera_settings['communication_port'],
                   "flask_ip": camera_settings['streaming_IP'],
                   "flask_port": camera_settings['streaming_port']},
           name=f"Acquisition_{camera_settings['id']}").start()  # TODO stream the frames via HTTP with rectangles from setup
    
    Thread(
        target=vision_handler,
        kwargs={"camera_index": camera_settings['id'],
                "destination_ip": camera_settings['communication_IP'],
                "frames_port": camera_settings['communication_port']},
        name=f"Vision_{camera_settings['id']}").start()


if __name__ == "__main__":

    start_redis_server(PATH_TO_REDIS_INSTALLATION_FOLDER)

    # Open cameras configuration file
    cameras = read_yaml_file(
        os.path.join(
            ROOT,
            PATH_TO_CONFIGURATION,
            'cameras.yaml'))['cameras']
    
    if ACTIVATE_PLC_COMMUNICATION == True:
        #Retrieve the PLC communication params and datablock structure
        plc_yaml_path=os.path.join(ROOT,PLC_CONFIGURATION_YAML_PATH)
        data = extract_from_yaml_plc_data(plc_yaml_path)
        plc_ip, _, plc_rack, plc_slot, plc_port = data[0]['plc'].values()
        polling_time = data[0]['polling_time']
        #Extract datablock structure from yaml file
        datablock_number = data[1]['datablock_number']
        datablock_size = data[1]['datablock_size']
        raw_datablock = data[1]['datablock']
    
    # Open a process for each camera. Camera usage might be holistic, or detect, or both
    for camera in cameras:
        
        if ACTIVATE_PLC_COMMUNICATION == True:
            cam_index=camera['id']
            outputs_from_plc, inputs_to_plc, camera_in_out_paths = \
                generate_communication_lists(cam_index, NUMBER_OF_AREAS)
            if cam_index == 1:
                cam_db_range = CAM1_DB_RANGE
            elif cam_index == 2:
                cam_db_range = CAM2_DB_RANGE
            elif cam_index == 3:
                cam_db_range = CAM3_DB_RANGE
            #Initialize a variable for communication (plc_data) for the specific camera
            plc_data={}
            #Initialize the plc_data variable for the considered camera
            plc_data['GENERAL'] = raw_datablock['GENERAL']
            plc_data[f'CAMERA{cam_index}'] = raw_datablock[f'CAMERA{cam_index}']
            plc_data=set_default_values(plc_data, camera_in_out_paths)
            
            #Start a PLC communication thread for the considered camera
            Thread(target=start_camera_communication_with_plc,
                kwargs={"plc_ip":plc_ip,
                        "plc_rack":plc_rack,
                        "plc_slot":plc_slot,
                        "plc_port":plc_port,
                        "plc_data":plc_data,
                        "datablock_number": datablock_number,
                        "datablock_size": datablock_size,
                        "outputs_from_plc":outputs_from_plc,
                        "inputs_to_plc":inputs_to_plc,
                        "camera_in_out_paths":camera_in_out_paths,
                        "redis_for_plc":redis_for_plc,
                        "cam_db_range": cam_db_range,
                        "cam_index":cam_index
                        }
                            ).start()
        
        acquisition_function = get_acquisition_function(camera['model'])
        
        vision_pipeline = get_vision_function(camera['usage'])

        Process(
            target=camera_pipeline(acquisition_handler=acquisition_function,
                                   vision_handler=vision_pipeline,
                                   camera_settings=camera),
            name=f"Camera-{camera['id']}").start()
    
    Thread(target=create_stop_button, name="ButtonStopThread").start()