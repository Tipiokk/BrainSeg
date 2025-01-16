import numpy as np
from matplotlib import pyplot as plt
from skimage.transform import rotate

from brainseg.image import resize_and_pad_center
from brainseg.polygon import rescale_polygon, translate_to_origin
from brainseg.viz.draw import draw_polygon


def fill_subpart_from_mask(big_image, subpart_image, mask, origin_coords):
    x, y = origin_coords
    subpart_width, subpart_height = subpart_image.shape[:2]
    big_width, big_height = big_image.shape[:2]

    # Calculate the region that can be copied from the big image to the subpart
    min_x = max(x, 0)
    min_y = max(y, 0)
    max_x = min(x + subpart_width, big_width)
    max_y = min(y + subpart_height, big_height)

    # Calculate the offset of the region in the big image
    x_offset = max(0, -x)
    y_offset = max(0, -y)

    # Calculate the corresponding region in the subpart
    subpart_region = subpart_image[x_offset:x_offset+(max_x-min_x), y_offset:y_offset+(max_y-min_y)]
    # print(locals())

    # Copy the valid region from the big image to the subpart image where the mask is True
    valid_mask = mask[x_offset:x_offset+(max_x-min_x), y_offset:y_offset+(max_y-min_y)]
    big_image[min_x:max_x, min_y:max_y][valid_mask] = subpart_region[valid_mask]

    return big_image


def extend_2d_array(array, new_width, new_height, fill_value=0):
    """
    Extends the width and height of a 2-D array to the specified dimensions.

    Parameters:
        array (list of lists or numpy.ndarray): The original 2-D array.
        new_height (int): The desired height of the extended array.
        new_width (int): The desired width of the extended array.
        fill_value (any): The value to fill the extended portions with (default is 0).

    Returns:
        numpy.ndarray: The extended 2-D array.
    """
    # Convert to numpy array if the input is not already one
    array = np.array(array)
    current_height, current_width, *other_dims = array.shape

    # Ensure new dimensions are at least as large as the current dimensions
    if new_height < current_height or new_width < current_width:
        raise ValueError("New dimensions must be greater than or equal to the current dimensions."
                         f"{new_height}_{current_height}, {new_width}_{current_width}"
                         )

    # Create a new array with the desired dimensions filled with the fill_value
    extended_array = np.full((new_height, new_width, *other_dims), fill_value, dtype=array.dtype)

    # Copy the original array into the top-left corner of the new array
    extended_array[:current_height, :current_width] = array

    return extended_array


def extend_2d_array_with_margin(array, new_width, new_height, margin=(0, 0), fill_value=0):
    """
    Extends the width and height of a 2-D array to the specified dimensions, with margins.

    Parameters:
        array (list of lists or numpy.ndarray): The original 2-D array.
        new_height (int): The desired height of the extended array.
        new_width (int): The desired width of the extended array.
        margin (tuple): A tuple (margin_top, margin_left) defining the compensation before.
                        The remaining margin will go at the end.
        fill_value (any): The value to fill the extended portions with (default is 0).

    Returns:
        numpy.ndarray: The extended 2-D array.
    """
    # Convert to numpy array if the input is not already one
    array = np.array(array)
    current_height, current_width, *other_dims = array.shape

    # Ensure new dimensions are at least as large as the current dimensions
    if new_height < current_height or new_width < current_width:
        raise ValueError("New dimensions must be greater than or equal to the current dimensions."
                         f"{new_height}_{current_height}, {new_width}_{current_width}"
                         )

    # Extract margin information
    margin_top, margin_left = margin
    margin_bottom = new_height - current_height - margin_top
    margin_right = new_width - current_width - margin_left

    # Ensure margins are valid
    if margin_bottom < 0 or margin_right < 0:
        raise ValueError("Margins result in dimensions smaller than the original array.")

    # Create a new array with the desired dimensions filled with the fill_value
    extended_array = np.full((new_height, new_width, *other_dims), fill_value, dtype=array.dtype)

    # Place the original array within the new array with margins
    extended_array[
        margin_top:margin_top + current_height,
        margin_left:margin_left + current_width
    ] = array

    return extended_array


def relu(x):
    return max(0, x)


def image_manual_correction(image, params, polygons, background=0, scale=1., swap_xy=False, margin=(0, 0)):
    if swap_xy:
        image = image.transpose((1, 0, 2))

    sh = image.shape
    res_image = np.zeros((sh[0] + margin[0], sh[1] + margin[1], sh[2]), dtype=np.uint8)
    if background != 0:
        res_image.fill(background)

    for polygon, param in zip(polygons, params):
        poly = rescale_polygon(polygon, scale)
        minx, miny, maxx, maxy = map(int, poly.bounds)

        if param is None:
            flip, rotation_angle, shift_x, shift_y = False, 0, 0, 0
            center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2
        else:
            center_x, center_y, flip, rotation_angle, shift_x, shift_y = param
            center_x, center_y = center_x * scale, center_y * scale
        shift_x, shift_y = shift_x * scale, shift_y * scale
        # center_x, center_y = poly.centroid.coords[0]
        # center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2
        width, height = maxx - minx, maxy - miny
        size = int(1.5 * max(width, height))
        half_size = int(size / 2)

        # the problem is that here, the width height can mismatch the subimage.shape
        # In this case, we need to pad the subimage
        subimage = image[relu(minx):relu(maxx), relu(miny):relu(maxy)]
        # padding
        subimage = extend_2d_array_with_margin(subimage, height, width, margin=(relu(-minx), relu(-miny)))
        subimage_mask = np.zeros(subimage.shape[:2], dtype=bool)
        subimage_mask = draw_polygon(subimage_mask, translate_to_origin(poly))

        # resize to enable rotation to work without overlapping
        subimage_mask = resize_and_pad_center(subimage_mask, size, size)
        subimage = resize_and_pad_center(subimage, size, size)

        if flip:
            subimage_mask = subimage_mask[::-1]
            subimage = subimage[::-1]

        a, b = subimage_mask, subimage
        if rotation_angle != 0:
            subimage_mask = rotate(subimage_mask, rotation_angle)
            subimage = rotate(subimage, rotation_angle)

        subimage_mask = subimage_mask.astype(bool)

        fill_subpart_from_mask(res_image, subimage, subimage_mask,
                               (int(center_x - half_size + shift_x), int(center_y - half_size + shift_y)))

    if swap_xy:
        res_image = res_image.transpose((1, 0, 2))

    return res_image
