import pandas as pd
import json
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from tabulate import tabulate
import sys
import os

cwd = os.getcwd() + '/hot_coco'
if os.path.exists(cwd):
    sys.path.append(cwd)


import display as display

def get_ann_df(ann_fp):

    with open(ann_fp, 'r') as f:
        content = json.load(f)
          
    ann_df = pd.DataFrame(content['annotations'])

    cat_name_dict = {}
    for c in content['categories']:
        cat_name_dict[c['id']] = c['name']

    im_name_dict = {}
    for i in content['images']:
        im_name_dict[i['id']] = i['file_name']

    im_w_dict = {}
    for i in content['images']:
        im_w_dict[i['id']] = i['width']

    im_h_dict = {}
    for i in content['images']:
        im_h_dict[i['id']] = i['height']

    ann_df['category_name'] = ann_df['category_id'].map(cat_name_dict)
    ann_df['image_name'] = ann_df['image_id'].map(im_name_dict)
    ann_df['image_width'] = ann_df['image_id'].map(im_w_dict)
    ann_df['image_height'] = ann_df['image_id'].map(im_h_dict)

    return ann_df

def get_im_df(ann_fp):

    # get annotations dataframe for reference
    ann_df = get_ann_df(ann_fp)

    #initialize imagery dataframe
    with open(ann_fp, 'r') as f:
        content = json.load(f)
    im_df = pd.DataFrame(content['images'])

    # add simple column
    im_df['pixel_area'] = im_df['width']*im_df['height']

    # add counts for annotations per category on each image 
    unique_ims = im_df['file_name'].unique()
    unique_cats = ann_df['category_name'].unique()
    im_ann_counts = {}

    for i in unique_ims:
      im_ann_counts[i] = {}
      for c in unique_cats:
        im_ann_counts[i][c] = ann_df[(ann_df['category_name']==c) & (ann_df['image_name']==i)]['id'].nunique()

    im_anns_df = pd.DataFrame(im_ann_counts).transpose()

    # Get the total number of categories and annotations on each image
    total_cats = np.count_nonzero(im_anns_df, axis=1)
    total_anns = im_anns_df.sum(axis=1)

    im_anns_df['Total Categories'] = total_cats
    im_anns_df['Total Annotations'] = total_anns

    im_anns_df['file_name'] = im_anns_df.index

    im_df = im_df.merge(im_anns_df, on='file_name')

    im_df = im_df.set_index('file_name')
  
    return im_df

def get_cat_cm(ann_df, im_df):
    '''
    Create a confusion matrix indicating how many images each combination of classes appears on
    '''

    category_list = ann_df['category_name'].unique()

    category_cm = {}
    for c_a in category_list:
      category_cm[c_a] = {}
      for c_b in category_list:
        category_cm[c_a][c_b] = len(set(im_df['id'][im_df[c_a]]).intersection(set(im_df['id'][im_df[c_b]])))

    category_cm_df = pd.DataFrame(category_cm)
    return category_cm_df

def get_cat_df(ann_fp, im_df):

    # establish basic information
    with open(ann_fp, 'r') as f:
        content = json.load(f)
    ann_df = get_ann_df(ann_fp)
    category_cm_df = get_cat_cm(ann_df, im_df)

    # create dataframe
    cat_df = pd.DataFrame(content['categories'])
    cat_df.sort_values(['supercategory', 'name'],inplace=True)
    cat_df.set_index('name', inplace=True)

    # add columns for how many images each category appears in, how many total anns are in the dataset
    ims_with_cats = pd.Series([category_cm_df.loc[c, c] for c in category_cm_df.index], index = category_cm_df.index)
    cat_df['Images with Category'] = ims_with_cats
    cat_df['Total In Dataset'] = ann_df['category_name'].value_counts()
    cat_df['Images with Category'] = cat_df['Images with Category'].fillna(0).astype('int')
    cat_df['Total In Dataset'] = cat_df['Total In Dataset'].fillna(0).astype('int')

    return cat_df

def cat_coexist_heatmap(ann_df, im_df):
    '''
    Create a heatmap indicating how many images each pair of categories appears on together
    '''
    cat_cm_df = get_cat_cm(ann_df, im_df)
    t = [cat_cm_df.loc[c,c] for c in cat_cm_df.index]
    fig, ax = plt.subplots(figsize=(15,15))
    a = sns.heatmap(cat_cm_df.div(t).transpose(), annot=cat_cm_df, ax=ax)
    a = plt.suptitle('Heat Map: How Often Categories Appear on Images Together', fontsize=20, x = 0.43, y=0.91)
    a = plt.title('Colored By Percentage, Values Indicate the Total Number of Images', fontsize=12)
    a = plt.xlabel('Reference Category')
    a = plt.ylabel('Master Category')

    return

def print_category_counts(ann_df, fig_size, font_size):

    plot = ann_df['category_name'].value_counts().plot(kind='barh', 
                                                       figsize=fig_size, 
                                                       fontsize=font_size,
                                                       title = 'Dataset Annotation Totals By Object Class')
    return

def show_ims_most_anns_cats(im_df, ann_fp, img_fp, fig_size):

    # Create 2 sorted dataframes prioritizing the number of categories on that image or the number of annotations
    im_anns_cats_df = im_df.sort_values(['Total Categories', 'Total Annotations'], ascending=False)
    im_anns_anns_df = im_df.sort_values(['Total Annotations', 'Total Categories'], ascending=False)

    # Get the image names with the most annotations and the most categories
    im_most_cats = im_anns_cats_df.index[0]
    im_most_anns = im_anns_anns_df.index[0]

    im_id_anns = im_df['id'][im_df.index == im_most_anns].values[0]
    im_id_cats = im_df['id'][im_df.index == im_most_cats].values[0]

    display.specific_gt(im_ids = [im_id_anns, im_id_cats], json_path = ann_fp, 
                image_folder = img_fp, fig_size = (max(fig_size)+1,max(fig_size)+1), text_on = True, 
                fig_titles=[f'Image with the Most Annotations: {im_most_anns}', 
                            f'Image with the Most Categories: {im_most_cats}'])
    return


def eda(ann_fp, img_fp, fig_size = (10,7), font_size = 10, return_dfs = False):
    '''
    Give the user some general information about their dataset
    '''
    ann_df = get_ann_df(ann_fp)
    im_df = get_im_df(ann_fp)

    # number of unique things in the dataset
    n_ims = im_df.index.nunique()
    n_anns = ann_df['id'].nunique()
    n_cats = ann_df['category_name'].nunique()

    meta_df = pd.DataFrame([[n_ims, n_anns, n_cats]], columns=['Total Images','Total Annotations','Total Categories'])

    print(tabulate(meta_df, headers='keys', tablefmt='psql', showindex=False))

    # create a bar graph of various category counts
    print_category_counts(ann_df, fig_size, font_size)

    
    # Show the images with the most total annotations and most categories represented
    show_ims_most_anns_cats(im_df, ann_fp, img_fp, fig_size)

    # Display a heatmap of how often various categories coexist on imagery
    cat_coexist_heatmap(ann_df, im_df)

    if return_dfs:
      return ann_df, im_df
    return