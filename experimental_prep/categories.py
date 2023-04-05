def map_to_supercategories(anns, new_fp):
    '''
    PURPOSE: Given some inout coco json, map all the annotations to their 
    supercategories for a more generalized experiment
    IN:
      - ann: str, fp to coco annotation file
      - new_fp: str, fp to new coco annotation file
    
    OUT: Nothing, the new file will be created at the specified path
    '''

    # open the annotations
    with open(anns, 'r') as f:
        gt = json.load(f)
    
    ### Categories ###
    old_cats = gt['categories']

    # create the new set of categories
    new_cs = []
    new_cats = []

    for c in old_cats:
      new_c = c['supercategory']
      new_cs.append(new_c)
    # sort the list of possible categories so they always end up in a predictable order
    new_cs = sorted(list(set(new_cs)))

    for i, c in enumerate(new_cs):
      cat = {'id': i + 1, 'name': c, 'supercategory': 'None'}
      new_cats.append(cat)

    # ### Annotations ###
    old_anns = gt['annotations']
    new_anns = []


    for a in tqdm(old_anns):
        new_ann = a.copy()
        a_cat = a['category_id']
        for c in old_cats:
            if c['id'] == a_cat:
                a_cat_name = c['supercategory']
                for nc in new_cats:
                    if nc['name'] == a_cat_name:
                        a_cat_id = nc['id']
                        new_ann['category_id'] = a_cat_id
                        new_anns.append(new_ann)

    ### New File ###
    # Create new json, with blank annotations
    new_json = gt.copy()
    new_json['annotations'] = new_anns
    new_json['categories'] = new_cats

    # ensure the fp does not already exist
    if os.path.exists(new_fp):
        os.remove(new_fp)

    # write out new anns
    with open(new_fp, 'w') as f:
        json.dump(new_json, f)
    
    return 

def make_cat_ids_match(src_anns, match_anns):
    '''
    IN: 
      - src_anns: str, path to the annotations whose category ids will provide
                  the mapping
      - match_anns: str, path to annotations whose categories will be remapped
    OUT: None, the categories will be remapped in place
    PURPOSE: Given two sets of coco annotations whose categories match, 
    ensure that the ids of each category are the same by forcing 
    match_anns categories to match src_anns categories
    '''
    # Open the annotations
    with open(src_anns, 'r') as f:
        src_gt = json.load(f)
    with open(match_anns, 'r') as f:
        match_gt = json.load(f)
    
    # Get the lists of categories
    src_cats = src_gt['categories']
    match_cats = match_gt['categories']

    # Create a mapping from one set of ids to the other
    cat_map = {}
    for c in match_cats:
        cat_map[c['id']] = get_category_id_from_name(c['name'], src_gt)

    # Remap the annotations in match_anns
    new_annotations = []
    for a in match_gt['annotations']:
        new_a = a.copy()
        new_a['category_id'] = cat_map[a['category_id']]
        new_annotations.append(new_a)
    
    match_gt['annotations'] = new_annotations
    match_gt['categories'] = src_cats
    
    # Save out a new file
    os.remove(match_anns)
    with open(match_anns, 'w') as f:
        json.dump(match_gt, f)

    return 

def json_fewer_cats(old_json, cat_list, ims_no_anns = False, renumber_cats = True):
    '''
    PURPOSE: Create a json with a subset of object categories
    IN:
        -old_json: gt coco json
        -cat_list: list of int category ids to be included in new coco gt json
        -ims_no_anns: if False (default), remove images without annotations from 'images', else keep all original images
    OUT: (new_name) path to new json file 
    '''
    # Name new json by the number of categories being included
    new_name = old_json.replace('.', '_{}.'.format(len(cat_list)))
    
    # Open original gt json
    with open(old_json, 'r') as f:
        contents = json.load(f)
        
    # Pull out key sections of old gt 
    annotations = contents['annotations']
    images = contents['images']
    cats = contents['categories']
    
    # Create new json, with blank annotations
    new_json = contents.copy()
    new_json['annotations'] = []
    
    # Feedback
    print(len(annotations), 'annotations found')
    
    # Process annotations, keeping only those which are in the desired categories
    count = 0
    for a in annotations:
        cat_id = a['category_id']
        if cat_id in cat_list:
            new_json['annotations'].append(a)
        count += 1
    
    # If desired, only keep images that have annotations on them
    if not ims_no_anns:
        new_json['images'] = []
        print(len(images), "images in original data")
        # Check each image for annotations
        for i in images:
            anns = []
            im_id = i['id']
            for a in new_json['annotations']:
                if a['image_id'] == im_id:
                    anns.append(a)
            if len(anns) > 1:
                new_json['images'].append(i)
        print(len(new_json['images']), "images in new data")
    
    # If desired, make sure that categories are sequentially numbered
    if renumber_cats:
        final_annotations = []
        cat_id = 1
        new_cats = []
        for cat in cats:
            old_id = cat['id']
            if old_id in cat_list:
                new_cat = cat.copy()
                
                for a in new_json['annotations']:
                    if a['category_id'] == old_id:
                        new_ann = a.copy()
                        new_ann['category_id'] = cat_id
                        final_annotations.append(new_ann)
                
                new_cat['id'] = cat_id
                cat_id += 1
                new_cats.append(new_cat)
        new_json['annotations'] = final_annotations
        
    new_json['categories'] = new_cats
    
    
    # Feedback
    print(len(new_json['annotations']), 'annotations in new file at', new_name)
    
    # Ensure no .json funny business will happen
    if os.path.exists(new_name):
        os.remove(new_name)
    
    # Save new file
    with open(new_name, 'w') as f:
        json.dump(new_json, f)
    
    return new_name