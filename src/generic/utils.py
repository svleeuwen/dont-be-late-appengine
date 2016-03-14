import logging
import os
import re
import unicodedata
import uuid
from collections import namedtuple

from google.appengine.api import images, app_identity, blobstore

MAX_DEEPLINK_LENGTH = 40


def generate_slug(s_in):
    s = unicode(s_in)
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore')
    s = re.sub(r'[^a-zA-Z0-9\ \-_]', '', s.lower())  # strip non alphanumeric
    s = re.sub(r'[-\s]+', '-', s)  # convert spaces to hyphens
                                   # and remove repeating hyphens
    s = s[:MAX_DEEPLINK_LENGTH]
    if s.isdigit():
        s = "s_%s" % s
    return s


def valid_slug(value):
    match = re.match('^[-a-zA-Z0-9_]+\Z', value)
    return bool(match)


Thumbnail = namedtuple('Thumbnail', ['url', 'width', 'height'])

IMAGE_INFO = {
    images.JPEG: ('image/jpeg', '.jpg'),
    images.PNG: ('image/png', '.png'),
}

def store_image(image_data, output_encoding=images.JPEG):
    """
    Store an image in Google Cloud Storage

    Args:
        image_data: data string
        output_encoding: jpeg or png

    Returns:
        image url
    """
    filename = str(uuid.uuid4()) + IMAGE_INFO.get(output_encoding)[1]
    mime_type = IMAGE_INFO.get(output_encoding)[0]
    return store_file(image_data, filename, 'images', mime_type)


def store_file(file_data, file_name, folder_name, mime_type=None):
    """
    Store file in Google Cloud Storage

    Args:
        file_data: data string
        file_name:
        folder_name:
        mime_type:

    Returns:
        file url
    """

    bucket = app_identity.get_default_gcs_bucket_name()
    if not bucket:
        raise EnvironmentError('Please set up Google Cloud Storage')

    path = '/' + os.path.join(bucket, folder_name, file_name)

    with cloudstorage.open(path, 'w') as gcs_file:
        gcs_file.write(file_data)

    blobstore_key = blobstore.create_gs_key('/gs' + path)
    return images.get_serving_url(blobstore_key, secure_url=True)


def handle_image_upload(image_data, resize_width=1600, resize_height=1600,
                        crop_to_fit=False, only_downsize=True, output_encoding=None, resize=True):
    """
    Resize uploaded image to correct dimensions

    Args:
        image_data: data string
        resize_width: resize width
        resize_height: resize height
        crop_to_fit: crop to given width and height
        only_downsize: do not upscale images smaller than given
        output_encoding: jpeg or png
        resize: perform resize
    Returns:
        named tuple Thumnail(url, width, height)
    """
    logging.debug('Resize image to width: {} and height: {}'.format(resize_width, resize_height))

    # check if image type is supported
    # if not, only upload it to datastore
    width = height = 0
    image_type = get_image_type(image_data)
    if image_type not in images.OUTPUT_ENCODING_TYPES:
        url = store_image(image_data)
        return Thumbnail(url, width, height)

    if output_encoding is None:
        output_encoding = image_type

    image = images.Image(image_data)
    if resize:
        if only_downsize:
            resize_width = min(resize_width, image.width)
            resize_height = min(resize_height, image.height)
        image.resize(resize_width,
                     resize_height,
                     crop_to_fit)
        image_data = image.execute_transforms(output_encoding=output_encoding,
                                              quality=95)
    width, height = image.width, image.height
    url = store_image(image_data)
    return Thumbnail(url, width, height)


def get_image_type(image_data):
    try:
        image = images.Image(image_data)
        return image.format
    except images.NotImageError:
        raise


def handle_image_crop(image_data, width, height, crop_x, crop_y, crop_w, crop_h, output_encoding=images.JPEG):
    """
    Crop uploaded image

    Args:
        image_data: data string
        width: scaled width
        height: scaled height
        crop_x: crop offset x
        crop_y: crop offset y
        crop_w: cropped width
        crop_h: cropped height
        output_encoding: jpeg or png

    Returns:
        named tuple Thumnail(url, width, height)
    """
    image = images.Image(image_data)
    image.resize(width, height)
    image.crop(
        crop_x / width,
        crop_y / height,
        (crop_w + crop_x) / width,
        (crop_h + crop_y) / height
    )
    image_cropped = image.execute_transforms(output_encoding=output_encoding, quality=95)
    url = store_image(image_cropped)
    return Thumbnail(url, image.width, image.height)


def update_csp_policy(policy_key, value, current_csp_policy, response_headers, overwrite=False, delete=False):
    """
    Update the csp_policy and update the CSP header accordingly

    Args:
        policy_key: str name, for example 'style-src'
        value: str value
        current_csp_policy: current policy defined in main.py
        response_headers: handler response headers
        overwrite: overwrite the policy value in stead of appending
        delete: remove the policy entirely
    """
    csp_policy = current_csp_policy.copy()
    policy = csp_policy.get(policy_key, '')
    if overwrite:
        policy = value
    else:
        policy += value

    if delete:
        del csp_policy[policy_key]
    elif not policy:
        return
    else:
        csp_policy[policy_key] = policy

    # update in header
    report_only = False
    if 'reportOnly' in csp_policy:
        report_only = csp_policy.get('reportOnly')
        csp_policy = csp_policy.copy()
        del csp_policy['reportOnly']
    header_name = ('Content-Security-Policy%s' %
                   ('-Report-Only' if report_only else ''))
    policies = []
    for (k, v) in csp_policy.iteritems():
        policies.append('%s %s' % (k, v))
    response_headers[header_name] = '; '.join(policies)
