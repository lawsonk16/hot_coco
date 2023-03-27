# hot_coco
A set of custom packages for machine learning with [coco](https://cocodataset.org/#format-data) datasets and focused on remote sensing, including visualizations, data transformations, and experimental prep

## datasets
description: contains the code to convert the dota, coco, and fair1m datasets to the coco format
future work: add additional versions of dota and fair1m 
 - dota_to_coco
 - fair1m_to_coco
 - xview_to_coco

...
...

## display
description: contains the functions you need to display random or specific (indicated using image ID values) images and their annotations, in various styles. Displays are given for ground truth, detections, and both together. Ground truth annotations are referred to using 'gt' in function names and detections are referred to using 'dt' in function names.
future work: add display functions for all annotation styles, or styles in concert

 - random_gt: pick a number of random images and display the bounding box ground truth annotations on them
 - specific_gt: pick a specific set of images and display the bounding box ground truth annotations on them
 - random_gt_cp: pick a number of random images and display the centerpoint (cp) grund truth annotations on them
 - specific_gt_cp: pick a specific set of images and display the centerpoint (cp) ground truth annotations on them
...
 - random_dt: pick a number of random images and display the bounding box detections on them
 - specific_dt: pick a specific set of images and display the bounding box detections on them
...
 - random_gt_dt: pick a number of random images and display the bounding box detections and ground truth annotations on them
 - specific_gt_dt: pick a specific set of images and display the bounding box detections and ground truth annotations on them

...
...
