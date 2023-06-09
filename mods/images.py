import os
import json
from PIL import Image
from tqdm import tqdm
from matplotlib import pyplot as plt

### support ###

def get_im_gsd_from_id(im_id, gt_content):
    '''
    PURPOSE: Get the GSD of an image based on its id in a coco file
    IN:
     - im_id: int, image id for the image in question
     - gt_content: the content from a coco ground truth file
    OUT:
     - pt: either the image's GSD or None if it isn'available
    '''
    images = gt_content['images']

    for i in images:
        if i['id'] == im_id:
            return i['gsd']
    print(f'GSD Missing: Image {im_id}')
    return None 

def get_anns_in_box(box, anns):
    b_anns = []
    
    # Get image coordinates
    i_x1 = box[0]
    i_y1 = box[1]
    i_x2 = i_x1 + box[2]
    i_y2 = i_y1 + box[3]
    
    # Check each individual annotation
    for a in anns:
        b = a['bbox']
        x1 = b[0]
        y1 = b[1]
        x2 = x1 + b[2]
        y2 = y1 + b[3]
        
        # Annotations will be assigned by centerpoint
        xc = (x1 + x2)/2
        yc = (y1 + y2)/2
        
        # Check if centerpoint is within chip
        if xc > i_x1 and xc < i_x2 and yc > i_y1 and yc < i_y2:
            # adjust coordinates to this chip
            n_x1 = x1 - i_x1
            n_y1 = y1 - i_y1
            n_x2 = n_x1 + b[2]
            n_y2 = n_y1 + b[3]
            
            # Ensure this new annotation is fully on-chip
            if n_x1 < 0:
                n_x1 = 0
            if n_y1 < 0:
                n_y1 = 0
            if n_x2 > i_x2:
                n_x2 = i_x2
            if n_y2 > i_y2:
                n_y2 = i_y2
            
            # Calculate new width and height after key checks
            n_w = n_x2 - n_x1
            n_h = n_y2 - n_y1
            
            new_a = a.copy()
            new_a['bbox'] = [n_x1, n_y1, n_w, n_h]
            
            b_anns.append(new_a)
    return b_anns 

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

def get_im_ids(gt_json):
    '''
    IN: gt coco json file
    OUT: list of all int image ids in that file
    '''
    im_ids = []
    
    # Open file
    with open(gt_json, 'r') as f:
        gt = json.load(f)
        
    images = gt['images']
    
    # Gather image id from every image
    for i in images:
        im_ids.append(i['id'])
    
    # Double check that it is unique
    im_ids = list(set(im_ids))
    
    return im_ids

def get_im_name_from_id(im_id, gt_content):
    images = gt_content['images']

    for i in images:
        if i['id'] == im_id:
            return i['file_name']



def get_im_info(im_id, gt_content):
    '''
    PURPOSE: Get the info of an image based on its id in a coco file
    IN:
     - im_id: int, image id for the image in question
     - gt_content: the content from a coco ground truth file
    OUT:
     - i: either the image's info or None if it isn'available
    '''
    images = gt_content['images']

    for i in images:
        if i['id'] == im_id:
            return i
    return None

### functions ###

def chip(coco_gt, image_folder, new_image_folder, chip_size):
    '''
    Purpose: Take a coco style json and associated image folder, 
    and create a new coco json and image folder containing new images 
    of the specified size
    '''
    
    # Open gt json
    with open(coco_gt, 'r') as f:
        gt_og = json.load(f)
    
    # New data
    new_images = []
    new_anns = []
    
    # Create new save locations
    gt_new_path = coco_gt.replace('.', '_{}.'.format(chip_size))
   
    if not os.path.exists(new_image_folder):
        os.mkdir(new_image_folder)
    
    chip_num = 0
    
    # Iterate through data one image at a time
    image_ids = get_im_ids(coco_gt)
    images_processed = 0
    for im_id in tqdm(image_ids):
        # Get all original annotations on this image
        im_anns = anns_on_image(im_id, gt_og)
        
        # Open the image
        im_str = get_im_name_from_id(im_id, gt_og)
        im_name = image_folder + im_str
        if os.path.exists(im_name):
            img = plt.imread(im_name)
            
            # Get image dimensions
            try:
              (x,y,c) = img.shape
            except:
              (x,y) = img.shape
            num_x = int(x/chip_size)
            num_y = int(y/chip_size)
            
            # Process each individual chip on this image
            for x_i in range(num_x):
                for y_i in range(num_y):
                    
                    # Get chip coords
                    c_x1 = x_i * chip_size
                    c_y1 = y_i * chip_size
                    bbox = [c_y1, c_x1, chip_size, chip_size]
                    
                    # If there are annotations on this image, save out a chip
                    anns = get_anns_in_box(bbox, im_anns)
                    if len(anns) > 0:
                        chip_name = str(chip_num) + '_' + str(im_id) + '_{}_{}_{}_{}'.format(c_x1, c_y1, chip_size, chip_size) + '.png'
                        chip_path = new_image_folder + chip_name
                        
                        # Update image annotation
                        new_image = {
                            'file_name' : chip_name,
                            'width' : chip_size,
                            'height' : chip_size,
                            'id' : chip_num,
                            'license' : 1
                        }
                        new_images.append(new_image)
                        
                        # Update object annotations
                        for a in anns:
                            new_a = a.copy()
                            new_a['image_id'] = chip_num
                            new_anns.append(new_a)
                        
                        
                        chip_num += 1
                        image_chip = img[c_x1:c_x1 + chip_size, c_y1:c_y1 + chip_size]
                        
                        if not os.path.exists(chip_path):
                            try:
                                plt.imsave(chip_path, image_chip)
                            except:
                                continue
            
                            
            images_processed += 1
        else:
            print(f'Issue with {im_id}')
        
    # Save out new gt file
    new_gt = gt_og.copy()
    new_gt['images'] = new_images
    new_gt['annotations'] = new_anns
    
    if os.path.exists(gt_new_path):
        os.remove(gt_new_path)
    
    with open(gt_new_path, 'w') as f:
        json.dump(new_gt, f)
        
    print('New ground truth:', gt_new_path)
    print('New images:', new_image_folder)
    
    return

def clip_anns_to_ims(coco_gt):
    '''
    Parameters
    ----------
    coco_gt : str,
        file path to a set of coco ground truth annotations

    Modifies the file in place to remove any annotations whose centerpoints 
    are off the image, which can be common in overhead imagery datasets for some
    reason
    -------

    '''
    #Open the file
    with open(coco_gt, 'r') as f:
      anns = json.load(f)
    new_anns = []
    
    # check the annotations
    for a in tqdm(anns['annotations']):
        new_ann = a.copy()
        x1,y1,w,h = a['bbox']
        x2 = x1+w
        y2 = y1+h

        im_id = a['image_id']
        for i in anns['images']:
          if i['id'] == im_id:
            im_w = i['width']
            im_h = i['height']
            
        # check coordinates which are too large 
        if (y2 > im_h) or (x2 > im_w):
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            if (x1 < im_h) and (y2 < im_h):
                if (xc < im_h) and (yc < im_h):
                  if (x2 > im_w):
                    w = im_w - x1
                    x2 = x1 + w
                  if (y2 > im_h):
                    h = im_h - y1
                    y2 = y1 + h
        # check coordinates which are too small         
        if (y1 < 0) or (x2 < 0):
            xc = (x1+x2)/2
            yc = (y1+y2)/2
            if (xc > 0) and (yc > 0):
              if y1 < 0:
                y1 = 0
                h = y2 - y1
              if x1 < 0:
                x1 = 0
                w = x2 - x1
        
        # make sure that after all modifications the annotation still has
        # a width and a height
        if (w > 0) and (h > 0):
                    new_ann['bbox'] = [x1,y1,w,h]
                    new_anns.append(new_ann)
    anns['annotations'] = new_anns
    
    # save out the modified annotations
    if os.path.exists(coco_gt):
      os.remove(coco_gt)
    with open(coco_gt, 'w') as f:
      anns = json.dump(anns, f, indent = 3)
      
    return

def add_gsd_to_chips(full_gt_fp, chip_gt_fp):

    '''
    PURPOSE: Given a set of full image annotations with gsd values and chipped
    annotations without them, add the gsd values to the corresponding chipped
    annotations for experimental use
    IN:
     - full_gt_fp: str, file path to coco ground truth for full images with gsd
     - chip_gt_fp: str, file path to coco ground triuth for chips without gsd
    OUT:
     - chip_anns_gsd: str, file path to new chip coco gt file with gsd included
    '''

    with open(full_gt_fp, 'r') as f:
        data_full = json.load(f)

    with open(chip_gt_fp, 'r') as f:
        data_chip = json.load(f)
    images_chip = data_chip['images']

    new_images_c = []

    # process each chipped image one by one
    for i_c in tqdm(images_chip, desc = 'Adding GSD to Images'):
        # copy the data
        new_i_c = i_c.copy()

        # get the full image info from the chip name
        im_name_c = i_c['file_name']

        full_im_id = int(im_name_c.split('_')[1])

        # add gsd
        new_i_c['gsd'] = get_im_gsd_from_id(full_im_id, data_full)
        new_images_c.append(new_i_c)

    data_chip['images'] = new_images_c

    chip_anns_gsd = chip_gt_fp.split('.')[0] + '_gsd.json'

    if os.path.exists(chip_anns_gsd):
        os.remove(chip_anns_gsd)

    with open(chip_anns_gsd, 'w') as f:
        json.dump(data_chip, f)

    return chip_anns_gsd

def convert_rgb(image_folder):
    '''
    Purpose: force all images in folder to assume kosher image format
    '''
    test_images = os.listdir(image_folder)
    test_images = [image_folder + i for i in test_images]
    count  = 0
    for i in test_images:   
        img = Image.open(i).convert('RGB')
        img.save(i)
        count += 1
        if count % 250 == 0:
            print(count)
    
    return

def gsd_norm(target_gsd, image_dir, ann_path, new_exp_dir):
    # Create new experimental directory
    if not os.path.exists(new_exp_dir):
      os.mkdir(new_exp_dir)

    new_im_dir = new_exp_dir + 'images/'
    new_json = new_exp_dir + ann_path.split('_')[-1]

    if not os.path.exists(new_im_dir):
      os.mkdir(new_im_dir)

    with open(ann_path, 'r') as f:
      gt = json.load(f)
    
    new_gt = gt.copy()
    new_gt['images'] = []
    new_gt['annotations'] = []

    im_ids = get_im_ids(ann_path)

    for im_id in tqdm(im_ids):

        im_info = get_im_info(im_id, gt)
        
        
        new_im_info = im_info.copy()

        #pull old image information
        old_im_h = im_info['height']
        old_im_w = im_info['width']
        # Get old gsd
        old_gsd = im_info['gsd']
        
        anns = anns_on_image(im_id, gt)
        
        try:
            if old_gsd is not None:

                # Create new image height and width
                new_im_h = int(float((old_im_h*old_gsd)/target_gsd))
                new_im_w = int(float((old_im_w*old_gsd)/target_gsd))

                new_im_info['height'] = new_im_h
                new_im_info['width'] = new_im_w
                new_im_info['gsd'] = target_gsd

                new_gt['images'].append(new_im_info)
                
                new_path = new_im_dir + im_info['file_name']
                old_path = image_dir + im_info['file_name']
                
                img = Image.open(old_path)
                
                img = img.resize((new_im_w, new_im_h))
                
                img.save(new_path)

                for a in anns:
                    new_a = a.copy()

                    # get current annotation bbox for each annotation
                    [old_x1, old_y1, old_w, old_h] = a['bbox']

                    # Created scaled versions of the bbox
                    scaled_x1 = old_x1/old_im_w
                    scaled_w = old_w/old_im_w

                    scaled_y1 = old_y1/old_im_h
                    scaled_h = old_h/old_im_h

                    # Create new bbox
                    x1 = scaled_x1 * new_im_w
                    w = scaled_w * new_im_w

                    y1 = scaled_y1 * new_im_h
                    h = scaled_h * new_im_h

                    new_a['bbox'] = [x1, y1, w, h]

                    new_gt['annotations'].append(new_a)

                
        except:
            print(im_id, 'problem')
            

    with open(new_json, 'w') as f:
        json.dump(new_gt, f)

    return