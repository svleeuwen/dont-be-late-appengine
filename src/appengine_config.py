from google.appengine.ext import vendor
import os


# Add any libraries installed in the "lib" folder.
vendor_dir_test = 'third_party/py/lib'
vendor_dir_prod = 'lib'


def add_google_dir(vendor_dir):
    # add vendorized protobuf to google namespace package
    import google
    google.__path__.append(os.path.join(vendor_dir, 'google'))

if os.path.isdir(vendor_dir_test):
    vendor.add(vendor_dir_test)
    add_google_dir(vendor_dir_test)
else:
    vendor.add(vendor_dir_prod)
    add_google_dir(vendor_dir_prod)
