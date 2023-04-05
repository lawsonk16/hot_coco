

def convert_imgs_rgb(folder):
    '''
    Purpose: force all images in folder to assume kosher image format
    '''
    test_images = os.listdir(folder)
    test_images = [folder + i for i in test_images]
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