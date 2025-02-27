import os
import cv2
import numpy as npy
import tensorflow as tf
import sys


sys.path.append("..")


from utils import label_map_util
from utils import visualization_utils as visual_util


OBJ_DETECT_MODEL = 'inference_graph'


OS_PATH = os.getcwd()



PATH_TO_CKPT_FILE = os.path.join(OS_PATH,OBJ_DETECT_MODEL,'frozen_inference_graph.pb')


PATH_LABELS = os.path.join(OS_PATH,'training','labelmap.pbtxt')


NUM_CLASSES = 14

# Number of classes of cards I want the webcam to detect.





labels_map = label_map_util.load_labelmap(PATH_LABELS)
avail_categories = label_map_util.convert_label_map_to_categories(labels_map, max_num_classes=14, use_display_name=True)
avail_category_index = label_map_util.create_category_index(avail_categories)


detectn_graph = tf.Graph()
with detectn_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT_FILE, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detectn_graph)





image_tensor = detectn_graph.get_tensor_by_name('image_tensor:0')



detect_boxes = detectn_graph.get_tensor_by_name('detection_boxes:0')



detection_scores = detectn_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detectn_graph.get_tensor_by_name('detection_classes:0')


num_detections = detectn_graph.get_tensor_by_name('num_detections:0')


video = cv2.VideoCapture(0)
ret = video.set(3,1280)
ret = video.set(4,720)

while(True):



    ret, frame = video.read()
    frame_expanded = npy.expand_dims(frame, axis=0)


    (boxes, scores, classes, num) = sess.run(
        [detect_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})


    visual_util.visualize_boxes_and_labels_on_image_array(
        frame,
        npy.squeeze(boxes),
        npy.squeeze(classes).astype(npy.int32),
        npy.squeeze(scores),
        avail_category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.60)


    cv2.imshow('Poker Cards detector', frame)


    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
