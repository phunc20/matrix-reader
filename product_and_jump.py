import argparse
import numpy as np
#import matplotlib.pyplot as plt
from PIL import Image

import pytesseract


def binarize(img, q=0.5):
    img_bool = (img >= np.quantile(np.unique(img), q))
    img_bool = img_bool.astype(np.uint8)
    return img_bool


def trouver_col_sep(squeezed_vec):
    start_duration = []
    previous = 0
    for ind, present in enumerate(squeezed_vec):
        if previous == 0:
            if present == 1:
                start = ind
                duration = 1
        else: # i.e. if previous == 1
            if present == 1:
                duration += 1
            else: # i.e. if present == 0
                start_duration.append([start, duration])
        previous = present
    # Had squeezed_vec ends with 0: ok
    # Had squeezed_vec ends with 1: NOT ok
    # Because we forget to record the last (start ,duration) pair.
    #if squeezed_vec[-1] == 1:
    #    start_duration.append((start, duration))
    
    # On purpose we drop out the last pair. It's better this way.
    start_duration = np.array(start_duration)
    #print(start_duration)

    if start_duration[0,0] == 0:
        start_duration = start_duration[1:,:]

    #print("start_duration = {}".format(start_duration))
    
    in_order_duration = np.sort(start_duration[:,1])
    jumps = in_order_duration[1:] - in_order_duration[:-1]
    #np.argmax(jumps)
    #in_order_duration[np.argmax(jumps)+1]
    #print("in_order_duration = {}".format(in_order_duration))
    #print("jumps = {}".format(jumps))
    

    is_multi_col = True
    ind_max_jump = np.argmax(jumps)
    max_jump = jumps[ind_max_jump]
    #ind_previous_max_jump = np.argmax(jumps[:ind_max_jump])
    previous_max_jump = np.max(jumps[:ind_max_jump])
    # We do not want ind_previous_max_jump to be zero:
    previous_max_jump = max(1, previous_max_jump)
    threshold_multi_col = 1/15
    #print("max_jump = {}".format(max_jump))
    #print("previous_max_jump = {}".format(previous_max_jump))

    is_multi_col = previous_max_jump/max_jump <= threshold_multi_col
    if not is_multi_col:
        # i.e. if the image matrix contains only one col
        # or only one row.
        return [0, squeezed_vec.size]
    else:
        qualified_duration = in_order_duration[ind_max_jump+1]
        list_sep = [0]
        qualified_s_d = start_duration[start_duration[:,1] >= qualified_duration]
        list_in_middle = (qualified_s_d[:,0] + qualified_s_d[:,1]/2).astype(np.int)
        list_in_middle = list(list_in_middle.reshape((-1,)))
        list_sep += list_in_middle
        list_sep.append(squeezed_vec.size)
        return list_sep



def trouver_row_sep(squeezed_vec):
    start_duration = []
    previous = 0
    for ind, present in enumerate(squeezed_vec):
        if previous == 0:
            if present == 1:
                start = ind
                duration = 1
        else: # i.e. if previous == 1
            if present == 1:
                duration += 1
            else: # i.e. if present == 0
                start_duration.append([start, duration])
        previous = present
    # Had squeezed_vec ends with 0: ok
    # Had squeezed_vec ends with 1: NOT ok
    # Because we forget to record the last (start ,duration) pair.
    #if squeezed_vec[-1] == 1:
    #    start_duration.append((start, duration))
    # On purpose we drop out the last pair. It's better this way.
    start_duration = np.array(start_duration)

    if start_duration[0,0] == 0:
        start_duration = start_duration[1:,:]

    #print("start_duration = {}".format(start_duration))
    list_sep = (start_duration[:,0] + start_duration[:,1]/2).astype(np.int).reshape((-1,))
    #print("list_sep = {}".format(list_sep))
    list_sep = [0] + list(list_sep) + [squeezed_vec.size]
    return list_sep



def A_str2tex(A_str, delimiter='p', output_format='tex', np_sep=',', csv_sep=','):
    '''
    Input:
        A_str: 2-D or 1-D ndarray of dtype='|U20', i.e. dtype as unicode string.
        delimiter: pmatrix or bmatrix.

        np_sep: either ',' or ', ', e.g. [1,2,3] or [1, 2, 3]
            default to ','
        csv_sep: ' ' or ',' or ';', e.g.
                 1 3.14 5.21 -7.9
                 1,3.14,5.21,-7.9
                 1;3.14;5.21;-7.9
    output:
        final_str: the corresponding vector/matrix in tex/py/etc. code.
    '''
    assert A_str.ndim in {1, 2}, "The input ndarray must be 1-D or 2-D."
    if output_format == 'tex':
        prefix = r'$\begin{' + '{}matrix'.format(delimiter) + '}\n'
        indent = ' '*4
        corps = ''
        suffix = r'\end{' + '{}matrix'.format(delimiter) + r'}$'
    elif output_format == 'np':
        prefix = 'np.array(['
        indent = ' '*len('np.array([')
        corps = ''
        suffix = ' '*len('np.array(') + '])'
    elif output_format == 'csv':
        prefix = ''
        corps = ''
        suffix = ''
    
    if A_str.ndim == 2:
        if output_format == 'tex':
            for i in range(A_str.shape[0]):
                corps += indent + ' & '.join(s for s in A_str[i]) \
                         + r' \\' + '\n'
        elif output_format == 'np':
            for i in range(A_str.shape[0]):
                corps += indent + '[' + np_sep.join(s for s in A_str[i]) \
                         + '],\n'
            # The very 1st one should not be preceded by indent.
            # We fix that now.
            corps = corps[len(indent):]
        elif output_format == 'csv':
            for i in range(A_str.shape[0]):
                corps += csv_sep.join(s for s in A_str[i]) \
                         + '\n'
    #elif A_str.ndim == 1:
    #    corps += r' \\ '.join(s for s in ndarray) + '\n'
    final_str = prefix + corps + suffix
    #print(final_str)
    return final_str


#def img2A_str(img_fpath, output_format):
def img2A_str(img_fpath):
    #img = Image.open(args['input']).convert('L')
    img = Image.open(img_fpath).convert('L')
    img = np.array(img)

    img_bool = binarize(img)

    squeezed_to_1_row = np.prod(img_bool, axis=0)
    squeezed_to_1_col = np.prod(img_bool, axis=1)

    col_sep = trouver_col_sep(squeezed_to_1_row)
    row_sep = trouver_row_sep(squeezed_to_1_col)
    
    # We will call the final result A,
    # which is a 2-D ndarray storing the indivisual values of the matrix in the img
    A = np.zeros((len(row_sep)-1, len(col_sep)-1))
    #A_str = np.empty(A.shape, dtype='|U20')
    A_str = np.empty((len(row_sep)-1, len(col_sep)-1), dtype='|U20')
    
    config = ('-l eng --oem 1 --psm 3')
    
    for i in range(A_str.shape[0]):
        for j in range(A_str.shape[1]):
            img_i_j = img[row_sep[i]:row_sep[i+1], col_sep[j]:col_sep[j+1]]
            
            # Read img_i_j by tesseract and then store the result in A.
            # In case of failure, always store the number 271828.1828409045 instead.
            try:
                str_i_j = pytesseract.image_to_string(img_i_j, config=config)
                #print(repr(str_i_j))  # This is for bebugging. (Cf. below for repr)
                #if '.' not in str_i_j:
                #    A[i, j] = int(str_i_j)
                #else:
                #    A[i, j] = float(str_i_j)
                # Four useless lines since the dtype of an ndarray is predetermined.
                #A[i,j] = float(str_i_j)

                if str_i_j[0] == '—':
                    str_i_j = '-' + str_i_j[1:]
                str_i_j = str_i_j.replace(' ', '')
                str_i_j = str_i_j.replace('Q', '0')
                float(str_i_j)
                A_str[i,j] = str_i_j
            except:
                #A[i,j] = 271828.1828409045
                A_str[i,j] = str(271828.1828409045)
            
        
    #A_str2tex(A_str, output_format='np', np_sep=', ')
    #if 'output_format' in args:
    #    print(A_str2tex(A_str, output_format=args['output_format'],))
    #else:
    #    print(A_str2tex(A_str,))


    #print(A_str2tex(A_str, output_format=args['output_format'],))
    #return A_str2tex(A_str, output_format=output_format,)
    return A_str

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', required=True,
                    help='path to the image: .png, .jpg all allowed')
    ap.add_argument('-of', '--output_format', required=False,
                    default='tex', help='tex, numpy, etc.')
    args = vars(ap.parse_args())
    #print(args)

    A_str = img2A_str(args['input'], args['output_format'])
    print(A_str2tex(A_str, output_format='np'))




