import itertools

import numpy as np

def reconstruct_volume(gen_conf, train_conf, patches) :
    dataset = train_conf['dataset']
    dataset_info = gen_conf['dataset_info'][dataset]
    expected_shape = dataset_info['dimensions']
    extraction_step = train_conf['extraction_step']
    patch_shape = train_conf['patch_shape']
    output_shape = train_conf['output_shape']
    num_classes = gen_conf['num_classes']
    patch_shape_equal_output_shape = patch_shape == output_shape

    if !patch_shape_equal_output_shape :
        expected_shape[0] -= 2 * output_shape[0]
        expected_shape[1] -= 2 * output_shape[1]
        expected_shape[2] -= 2 * output_shape[2]

    rec_volume = perform_voting(patches, patch_shape, expected_shape, num_classes)

    if !patch_shape_equal_output_shape :
        rec_volume = pad_both_sides(rec_volume, output_shape)

    return rec_volume

def perform_voting(patches, patch_shape, expected_shape, num_classes) :
    vote_img = np.zeros(expected_shape + (num_classes, ))

    coordinates = generate_indexes(
        patch_shape, extraction_step, expected_shape)

    for count, coord in enumerate(coordinates) :
        selection = [slice(coord[i] - patch_shape[i+1], coord[i]) for i in range(len(coord))]
        selection = selection + [slice(None)]
        vote_img[selection] += patches[count]

    return np.argmax(vote_img, axis=3)

def generate_indexes(patch_shape, extraction_step, expected_shape) :
    ndims = len(patch_shape)

    poss_shape = [patch_shape[i] + extraction_step[i] * ((expected_shape[i] - patch_shape[i]) // extraction_step[i]) for i in range(ndims)]

    idxs = [range(patch_shape[i], poss_shape[i] + 1, extraction_step[i]) for i in range(ndims)]

    return itertools.product(*idxs)

def pad_both_sides(vol, pad_size) :
    pad_per_dim = ((pad_size[0], pad_size[0]), (pad_size[1], pad_size[1]), (pad_size[2], pad_size[2]))
    return np.pad(vol, pad_per_dim, 'constant', constant_values=0)