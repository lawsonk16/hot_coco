# hot_coco.mods
Contains packages to prepare your data for a variety of experiments, organized by the way in which you would like to modify the data. These functions help deal with common scenarios you may encounter when using remote sensing data and coco annotations files.

---
---

## categories
description: 
- map_to_supercategories: allows you to map every annotation in your dataset to its supercategory, creating a more generalized dataset. Requires that your dataset includes supercategory information
- make_ids_match: given two files describing the same dataset, ensure that the category ids match across the two files. Can be useful to ensure data collected in phases, or the same dataset as converted by two different individuals or groups actually match one another.
- reduce: reduce the list of categories included here and delete any irrelevant categories


---
---

## classification
description: create a classification dataset using a coco detection dataset
- from_gt: given a set of images and annotations, create a classification dataset with a folder for images of each category. The items are chipped out of the images according to their bounding box, with an option to pad each box by a set number of pixels.

---
---

## images
description: functions to chip images and ensure that the information represented in a given file about the labels on on image and its qualities is accurate. 
- add_gsd_to_chips: given a full image ground truth file with gsd values and a set of chips on those images without them, add the gsd values to the chip data
- chip: chip large images, and produce a label file matching the new smaller images. Simple, non-overlapping chipping, but it's a starting place.
- clip_anns_to_ims: ensure that all the annotations on a given image are actually within that image's dimension. Remote sensing data sometimes contains annotations off-image, which can get in the way of certain model training procedures
- convert_rgb: convert all the images in a given folder to rgb imagery, in the case that you are getting an error about image formamtting - as most certainly can happen with remote sensing data
- gsd_norm: normalize all of the images in a given folder to a particular gsd value gien that each image has a recorded gsd value, and resize all of the annotations on those images accordingly


---
---

## splits
description:



