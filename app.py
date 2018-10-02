# IMPORTS
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import boto3
# CONFIG
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(os.environ['APP_SETTINGS'])

ALLOWED_EXTENSIONS = app.config["ALLOWED_EXTENSIONS"]

s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)

def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(app.config["S3_LOCATION"], file.filename)

# ROUTES
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():

    # s31 = boto3.client("s3")
    # all_objects = s31.list_objects(Bucket='europeconference')
    # print(all_objects)

    if request.method == 'POST':
        # There is no file selected to upload
        if "user_file" not in request.files:
            return "No user_file key in request.files"
        file = request.files["user_file"]
        # There is no file selected to upload
        if file.filename == "":
            return "Please select a file"
        # File is selected, upload to S3 and show S3 URL
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output = upload_file_to_s3(file, app.config["S3_BUCKET"])
            return str(output)
    else:
        return render_template("index.html")

app.run(port=8000)