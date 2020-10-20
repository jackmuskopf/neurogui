import uuid
import logging
from flask import Blueprint, render_template, request, \
    redirect, url_for, flash
from neurogui.settings import settings
from neurogui.utils import new_id, upload_file_to_s3, \
    file_too_big, file_size, meta_table

logger = logging.getLogger(__name__)

api = Blueprint('upload-api', __name__)

@api.route("/_tests/hello")
def hello():
    return "Hello, World!"

@api.route("/upload", methods=['GET'])
def upload_form(error_message=None):
    if error_message:
        logger.info("User error {}".format(error_message))
    return render_template('upload.html', error_message=error_message)

@api.route("/upload", methods=['POST'])
def upload_file():

    if "user_file" not in request.files:
        return "No user_file key in request.files"

    file = request.files["user_file"]

    """
        These attributes are also available

        file.filename               # The actual name of the file
        file.content_type
        file.content_length
        file.mimetype
    
    """

    logger.info("Content length: {}".format(file.content_length))

    logger.info("Attemping to upload file {}".format(file.filename))

    # C.
    if file.filename == "":
        return "No file selected" # render_template('upload.html', error_message="Please select a file")

    if file_too_big(file):
        return "File too big: {}".format(file_size(file))
    
    image_id = new_id()

    # accepted_extensions = [
    #     ".nii.gz",
    #     ".nii"
    # ]

    # detected_extension = None
    # for ext in accepted_extensions:
    #     if file.filename.endswith(ext):
    #         logger.info("Detected extension {} for image {}".format(ext, image_id))
    #         detected_extension = ext
    #         break

    # if detected_extension is None:
    #     logger.info("Failed to detect extension: {}".format(file.filename))
    #     return "Did not detect valid extension; accepted extensions: {}".format(", ".join(accepted_extensions))

    logger.info("Creating image with id {}".format(image_id))

    meta_table.put_item(Item=dict(
        id=image_id, 
        filename=file.filename,
        status='received'
    ))

    output = upload_file_to_s3(
        file=file, 
        bucket=settings['ImageBucketName'], 
        key="images/{}".format(image_id)
    )
    return redirect(url_for('image-api.image', image_id=image_id))