# hot_coco
A set of custom packages for machine learning with [coco](https://cocodataset.org/#format-data) datasets and focused on remote sensing, including visualizations, data transformations, and experimental prep

## datasets
description: contains the code to convert the dota, coco, and fair1m datasets to the coco format
 - dota_to_coco
 - fair1m_to_coco
 - xview_to_coco

## display
description: contains the functions you need to display random or specific (indicated using image ID values) images and their annotations, in various styles. Displays are given for ground truth, detections, and both together. Ground truth annotations are referred to using 'gt' in function names and detections are referred to using 'dt' in function names.

 - random_gt: pick a number of random images and display the bounding box annotations on them
 - specific_gt: pick a specific set of images and display the bounding box annotations on them
 - random_gt_cp: pick a number of random images and display the centerpoint (cp) annotations on them
 - specific_gt_cp: pick a specific set of images and display the centerpoint (cp) annotations on them
---
 - random_dt
 - specific_dt
---
 - random_gt_dt
 - specific_gt_dt
