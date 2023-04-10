import os
import random
import shutil
import json
from tqdm import tqdm


### support ###

def get_im_id_from_name(im_name, gt_content):
    images = gt_content['images']

    for i in images:
        if i['file_name'] == im_name:
            return i['id']
    print('Missing Image', im_name)
    return None

def anns_on_image(im_id, contents):
    '''
    IN: 
        - im_id: int id for 'id' in 'images' of coco json
        - json_path: path to coco gt json
    OUT:
        - on_image: list of annotations on the given image
    '''
    
    # Pull out annotations
    anns = contents['annotations']
    
    # Create list of anns on this image
    on_image = []
    for a in anns:
        if a['image_id'] == im_id:
            on_image.append(a)
    
    return on_image

### functions ###

def train_test(chip_folder, test_percentage, gt, chip_size):
    
    all_chips = os.listdir(chip_folder)

    random.shuffle(all_chips)
    num_chips = len(all_chips)
    print("Num chips", num_chips)

    test_ind = int(num_chips*test_percentage)
    print("Test_ind", test_ind)

    # Select images for test and train
    test_chips = all_chips[:test_ind]
    train_chips = all_chips[test_ind:]
    
    # Make new gt
    train_data_name = 'train_' + str(chip_size) + '_gt.json'
    test_data_name = 'test_' + str(chip_size) + '_gt.json'
    gt_from_im_list(gt, train_chips, train_data_name)
    gt_from_im_list(gt, test_chips, test_data_name)


    print(train_data_name, test_data_name)
    return train_data_name, test_data_name

def train_val_test(image_folder, gt, val_precentage = 0.1, test_percentage = 0.2, data_tag = ""):
    
    data_folder = '/'.join(image_folder.split('/')[:-2]) + '/'

    all_images = os.listdir(image_folder)

    random.shuffle(all_images)
    num_images = len(all_images)
    print("Num images", num_images)

    test_ind = int(num_images*test_percentage)
    val_ind = int(num_images*val_precentage) + test_ind

    # Select images for test and train
    test_images = all_images[:test_ind]
    val_images = all_images[test_ind:val_ind]
    train_images = all_images[val_ind:]
    
    # Make new gt
    train_data_name = data_folder + 'train_' + data_tag + '_gt.json'
    val_data_name = data_folder + 'val_' + data_tag + '_gt.json'
    test_data_name = data_folder + 'test_' + data_tag + '_gt.json'

    # Create new gt files
    gt_from_im_list(gt, train_images, train_data_name)
    gt_from_im_list(gt, val_images, val_data_name)
    gt_from_im_list(gt, test_images, test_data_name)
    print('gt created')
    
    # Create new image folders
    train_folder = data_folder + 'train_images/'
    val_folder = data_folder + 'val_images/'
    test_folder = data_folder + 'test_images/'

    # Move all image files as appropriate
    os.mkdir(val_folder)
    os.mkdir(test_folder)

    for i in val_images:
        src = image_folder + i
        dst = val_folder + i
        shutil.move(src, dst)
    
    for i in test_images:
        src = image_folder + i
        dst = test_folder + i
        shutil.move(src, dst) 

    os.rename(image_folder, train_folder)      

    return data_folder 

def exp_by_percentage(data_tag, keep_percent, ims_list, anns_list):
    '''
    IN:
      - data_tag: str, describes the dataset
      - keep_percent: int, percentage of each set of images to keep
      - ims_list: list of str, paths to images (same order as anns_list)
      - anns_list: list of str, paths to annotation files (same order as ims_list)
    OUT: None
    '''

    # make new experimental directory
    new_exp_dir = f'{data_tag}_mini_{keep_percent}'

    if not os.path.exists(new_exp_dir):
        os.mkdir(new_exp_dir)

    for i, anns in enumerate(anns_list):
        ### Images ###
        # get a list of images to keep
        ims = os.listdir(ims_list[i])
        random.shuffle(ims)
        keep_ims = int(len(ims)*(float(keep_percent/100.0)))
        new_ims = ims[:keep_ims]

        # create a new image directory
        new_image_dir = f'{new_exp_dir}/{ims_list[i]}'
        if not os.path.exists(new_image_dir):
            os.mkdir(new_image_dir)
        # move the images
        for im in tqdm(new_ims, desc = 'moving images'):
            src = ims_list[i] + im
            dst = new_image_dir + im
            shutil.copy2(src, dst)

        ### Annotations ###
        new_ann_path = f'{new_exp_dir}/{anns}'
        gt_from_im_folder(anns, new_image_dir, new_ann_path)
        
def gt_from_im_list(full_gt, img_list, new_gt_path):
    # Read in full gt
    with open(full_gt, 'r') as f:
        gt = json.load(f)

    # Initialize key storage containers
    contents = gt.copy()
    contents['images'] = []
    contents['annotations'] = []
    images = []
    annotations = []

    # Process one image at a time
    for image in tqdm(img_list):
        i = get_im_id_from_name(image, gt)
        anns = anns_on_image(i, gt) 
        annotations.extend(anns)
        for im_info in gt['images']:
            if im_info['id'] == i:
                images.append(im_info)

    # Load new data into appropriate format and save
    contents['images'] = images
    contents['annotations'] = annotations

    if os.path.exists(new_gt_path):
        os.remove(new_gt_path)

    with open(new_gt_path, 'w') as f:
        json.dump(contents, f)

    return

def gt_from_im_folder(full_gt, img_folder, new_gt_path):
    # Read in full gt
    with open(full_gt, 'r') as f:
        gt = json.load(f)

    # Initialize key storage containers
    contents = gt.copy()
    contents['images'] = []
    contents['annotations'] = []
    images = []
    annotations = []

    # Process one image at a time
    ims = os.listdir(img_folder)

    for image in tqdm(ims, desc = 'building annotations file'):
        i = int(image.split('_')[0])
        anns = anns_on_image(i, gt) 
        annotations.extend(anns)
        for im_info in gt['images']:
            if im_info['id'] == i:
                images.append(im_info)

    # Load new data into appropriate format and save
    contents['images'] = images
    contents['annotations'] = annotations

    if os.path.exists(new_gt_path):
        os.remove(new_gt_path)

    with open(new_gt_path, 'w') as f:
        json.dump(contents, f)

    return