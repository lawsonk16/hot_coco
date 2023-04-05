import json
import os

def centerpoints_xy(anns_fp, output_fp = False):
    '''

    Parameters
    ----------
    anns_fp : str,
        file path to a set of coco ground truth annotations
    output_fp : boolean, optional
        If an output fp is specified, that's where the modified anns will be 
        writen. Else, a version of the fp with -cp added before .json will be 
        used. The default is False.

    Modifies the file using the bbox key to add centerpoint values to each 
    annotation using the format ['object_center'] = [xc, yc]
    -------

    '''
    
    with open(anns_fp, 'r') as f:
      anns = json.load(f)
    annotations = anns['annotations']
    new_anns = []
    for a in annotations:
      new_a = a.copy()
      [x,y,w,h] = a['bbox']
      xc = int(x+(w/2))
      yc = int(y+(h/2))
      new_a['object_center'] = [xc, yc]
      new_anns.append(new_a)
    anns['annotations'] = new_anns
    if output_fp:
        if os.path.exists(output_fp):
            os.remove(output_fp)
        with open(output_fp, 'w') as f:
          json.dump(anns, f, indent = 5)
    else:
        output_fp = anns_fp.replace('.json', '-cp.json')
        if os.path.exists(output_fp):
            os.remove(output_fp)
        with open(output_fp, 'w') as f:
          json.dump(anns, f, indent = 5)
     
    return