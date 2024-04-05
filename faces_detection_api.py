import tensorflow as tf
import os
import numpy as np
from PIL import Image
path2label_map = 'base/face_label_map.pbtxt'

from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

def detect_fn(image, detection_model):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections

def load_image_into_numpy_array(path):
    return np.array(Image.open(path))[:,:,[0,1,2]]

def nms(rects, thd=0.5):
    out = []
    remove = [False] * len(rects)
    for i in range(0, len(rects) - 1):
        if remove[i]:
            continue
        inter = [0.0] * len(rects)
        for j in range(i, len(rects)):
            if remove[j]:
                continue
            inter[j] = intersection(rects[i][0], rects[j][0]) / min(square(rects[i][0]), square(rects[j][0]))
        max_prob = 0.0
        max_idx = 0
        for k in range(i, len(rects)):
            if inter[k] >= thd:
                if rects[k][1] > max_prob:
                    max_prob = rects[k][1]
                    max_idx = k
        for k in range(i, len(rects)):
            if (inter[k] >= thd) & (k != max_idx):
                remove[k] = True
    for k in range(0, len(rects)):
        if not remove[k]:
            out.append(rects[k])
    boxes = [box[0] for box in out]
    scores = [score[1] for score in out]
    classes = [cls[2] for cls in out]
    return boxes, scores, classes

def intersection(rect1, rect2):
    x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]));
    y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]));
    overlapArea = x_overlap * y_overlap;
    return overlapArea


def square(rect):
    return abs(rect[2] - rect[0]) * abs(rect[3] - rect[1])

def inference_as_raw_output(path2images,
                            detection_model,
                            box_th = 0.25,
                            nms_th = 0.1,
                            path2dir = False):
    all_detections = list()
    for image_path in path2images:
        if path2dir: # if a path to a directory where images are stored was passed in
            image_path = os.path.join(path2dir, image_path.strip())
        image_np = load_image_into_numpy_array(image_path)
        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = detect_fn(input_tensor, detection_model)
        
        # checking how many detections we got
        num_detections = int(detections.pop('num_detections'))
        
        # filtering out detection in order to get only the one that are indeed detections
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        
        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
        
        # defining what we need from the resulting detection dict that we got from model output
        key_of_interest = ['detection_classes', 'detection_boxes', 'detection_scores']
        
        # filtering out detection dict in order to get only boxes, classes and scores
        detections = {key: value for key, value in detections.items() if key in key_of_interest}
        
        if box_th: # filtering detection if a confidence threshold for boxes was given as a parameter
            for key in key_of_interest:
                scores = detections['detection_scores']
                current_array = detections[key]
                filtered_current_array = current_array[scores > box_th]
                detections[key] = filtered_current_array
        
        if nms_th: # filtering rectangles if nms threshold was passed in as a parameter
            # creating a zip object that will contain model output info as
            output_info = list(zip(detections['detection_boxes'],
                                   detections['detection_scores'],
                                   detections['detection_classes']
                                  )
                              )
            boxes, scores, classes = nms(output_info)
            
            detections['detection_boxes'] = boxes # format: [y1, x1, y2, x2]
            detections['detection_scores'] = scores
            detections['detection_classes'] = classes
            all_detections.append(detections)
    return all_detections

def detect_image(path2images,
                  op_or_not = True,
                  path2dir = None):
    if op_or_not:
        path2config ='base/training_op/pipeline.config'
        path2ckpt = 'base/training_op/ckpt-21'
    else:
        path2config ='base/training/pipeline.config'
        path2ckpt = 'base/training/ckpt-51'
    configs = config_util.get_configs_from_pipeline_file(path2config)
    model_config = configs['model']
    detection_model = model_builder.build(model_config=model_config, is_training=False)
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(path2ckpt)).expect_partial()
    category_index = label_map_util.create_category_index_from_labelmap(path2label_map,use_display_name=True)
    active = False
    results = inference_as_raw_output(path2images, detection_model, path2dir = path2dir)
    # box format: [ymin, xmin, ymax, xmax]
    good_results = list()
    for i in results:
        if i['detection_boxes']:
            good_results.append({
            'box':list(i['detection_boxes'][0]),
            'type':'face',
            'score':i['detection_scores'][0]
            })
        else:
            good_results.append(None)
    return good_results

