# THIRD-PARTY SOFTWARE CONFIGURATION
PATH_TO_REDIS_INSTALLATION_FOLDER='C:\\Program Files\\Redis'

# APPLICATION CONFIGURATION
ROOT = r'C:\GEFIT\gefit-AIDE_AVVITATORE'
PATH_TO_INTERPRETER = '.venv\\Scripts\\python.exe'
PATH_TO_HTTP_REDIS_SENDER = 'gefit-AIDE\\gefitvision\\utils\\HTTP_redis_sender.py'
PATH_TO_CONFIGURATION = 'gefit-AIDE\\configuration'
PATH_SAVED_AREAS = 'gefit-AIDE\\configuration\\saved_areas'
PATH_TO_RESULTS= 'gefit-AIDE\\results'
SAVED_IMAGES_PATH='gefit-AIDE\\configuration\\saved_images_and_labels'
TRAINING_DATASET_IMAGES_PATH = 'images\\train'
VALIDATION_DATASET_IMAGES_PATH = 'images\\val'

# MEDIAPIPE CONFIGURATION
CONFIDENCE_THRESHOLD_DETECT_HOLISTIC = 0.5
CONFIDENCE_THRESHOLD_TRACKING_HOLISTIC = 0.5
CONFIDENCE_THRESHOLD_DETECT_HANDS = 0.5
CONFIDENCE_THRESHOLD_TRACKING_HANDS = 0.5
MAX_NUM_HANDS = 2

#SCREEN RESOLUTION
FRAME_RESOLUTION = (2560, 1440)

#----------------------------------------------------------------------------------------------

# REALSENSE CAMERAS
CLIPPING_DISTANCE_IN_METERS = 3.0
MINIMUM_DISTANCE = 0.0
RS_BK_COLOR = 153
DEPTH_WIDTH = 1024
DEPTH_HEIGHT = 768
DEPTH_FPS = 30
COLOR_WIDTH = 1920
COLOR_HEIGHT = 1080
COLOR_FPS = 30

#AVT CAMERAS
PATH_TO_AVT_SETTINGS="gefit-AIDE\\configuration\\avt_camera_settings"
EXPOSURE_TIME_DEFAULT=28000
EXPOSURE_TIME_AUTO_DEFAULT=False
GAIN_DEFAULT=5
AUTO_GAIN_DEFAULT=False
SATURATION_DEFAULT=0.95
GAMMA_DEFAULT=0.675
AUTO_WHITE_BALANCING_DEFAULT=True
BUFFER_SIZE = 3

#BODY DETECTION
GESTURES_DICT={"NoGesture":0,
               "OK":1,
               "Gun":2,
               "MiddleFinger":3,
               "Horns":4,
               "OK-Down":5,
               "ClosedHand":6}

#QRCODE SCANNER 
QRCODE_SCAN_ENABLED=False

# OBJECT DETECTION CONFIGURATION
OBJECTS_DICT={"NOK":0,
              
              "CARCASSA_CAMBIO":1,
              "VITE_BRUGOLA":2,
              "VITE_ESAGONALE":3,
              "VITE_INSERITA_OK":4,
              "AVVITATORE":5,
              
              "VITE_INSERITA_NOK":6,
              }

LAST_OK_ID=5
IOU=0.25
CONFIDENCE_THRESHOLD=60
ENABLE_OBJ_DETECT_IN_HOLISTIC=False

#TRAINING SETUP
MAX_NUMBER_TRAINING_IMAGE_PER_OBJECT=5000
VALIDATION_IMAGES_PERCENTAGE=0.15
MODEL_SIZE='l'
STARTING_WEIGHTS_PATH='gefit-AIDE\\resources\\models'
EPOCHS= 100
PATIENCE = 20
BATCH= 4
IMGSZ= 1280
SAVE_PERIOD = 10
DEVICE= 0 #Set 0 when using GPU for training, otherwise set device='cpu'
WORKERS=4
OPTIMIZER="SGD"
DROPOUT_ENTITY=0.0
WEIGHTS_FOLDER_PATH='gefit-AIDE'
WEIGHTS_FOLDER_NAME="training_results"

CSV_SAVE_TIME=3

#---------------------------------------------------------------------------------
# COMMUNICATION SETUP
ACTIVATE_PLC_COMMUNICATION=True
SIMULATE_PLC_FOR_DEBUGGING=False
PLC_CONFIGURATION_YAML_PATH='gefit-AIDE\\configuration\\plc.yaml'
NUMBER_OF_AREAS=3
GENERALVARS_DB_RANGE=[0,49]
CAM1_DB_RANGE=[50,259]
CAM2_DB_RANGE=[260,469]
CAM3_DB_RANGE=[560,769]

CAMERAS_COMMUNICATING_WITH_PLC=[1,2]
#----------------------------------------------------------------------------------