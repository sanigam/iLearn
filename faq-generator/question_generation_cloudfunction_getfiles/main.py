def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    name = "World"
    request_json = request.get_json()
    if request.args and "message" in request.args:
        return request.args.get("message")
    elif request_json and "message" in request_json:
        return request_json["message"]
    else:
        return f"Hello {name}!"


from google.cloud import storage
from datetime import date, datetime, timedelta
from flask import jsonify

# PROJECT_ID = "advance-conduit-336823"
# BUCKET_NAME = "advance-conduit-336823-uploaded-files"

PROJECT_ID = "learn-339101"
BUCKET_NAME = "learn-339101-uploaded-files"


def get_latest_uploads(request):
    # function to get the list of all files/blobs uploaded today

    # Instantiate your client
    # first establish your client
    storage_client = storage.Client(PROJECT_ID)

    # Define bucket_name and any additional paths via prefix
    # get your blobs
    bucket_name = BUCKET_NAME
    # prefix = 'special-directory/within/your/bucket' # optional

    # Iterate the blobs returned by the client
    blob_names = [
        (blob.name, blob.updated)
        for blob in storage_client.list_blobs(
            bucket_name,
            # prefix = prefix,
        )
        if blob.name.split(".")[1] == "txt"
    ]

    # Sort the list on the second tuple value

    # # sort and grab the latest value, based on the updated key
    # latest = sorted(blobs, key=lambda tup: tup[1])[-1][0]
    # string_data = latest.download_as_string()

    # One-liner
    # # assumes storage_client as above
    # # latest is a string formatted response of the blob's data
    # latest = sorted([(blob, blob.updated) for blob in storage_client.list_blobs(bucket_name, prefix=prefix)], key=lambda tup: tup[1])[-1][0].download_as_string()

    # sort and grab the latest value, based on the updated key
    sorted_blob_names = sorted(blob_names, key=lambda tup: tup[1], reverse=True)

    latest_blob_names = []

    # if len(sorted_blobs) > 0:
    #     iter_blobs = range(len(sorted_blobs))
    #     i = iter(iter_blobs)
    #     while (sorted_blobs[i][1]).replace(tzinfo=None) > (
    #         datetime.today().replace(tzinfo=None)
    #     ) - timedelta(days=1):

    #         latest.append(sorted_blobs[i])
    #         i = iter(iter_blobs)

    for blob in sorted_blob_names:
        if blob[1].replace(tzinfo=None) > (
            datetime.today().replace(tzinfo=None)
        ) - timedelta(days=1):

            latest_blob_names.append(blob[0])

    return jsonify(latest_blob_names)


# References:
# # https://stackoverflow.com/questions/55509340/how-to-access-the-latest-uploaded-object-in-google-cloud-storage-bucket-using-py
# # https://cloud.google.com/storage/docs/viewing-editing-metadata#storage-view-object-metadata-python
# # https://cloud.google.com/storage/docs/listing-objects
# # https://googleapis.dev/python/storage/1.17.0/index.html
# # https://googleapis.dev/python/storage/latest/blobs.html

# # https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python?rq=1
# # https://stackoverflow.com/questions/3278999/how-can-i-compare-a-date-and-a-datetime-in-python

# # https://stackoverflow.com/questions/15307623/cant-compare-naive-and-aware-datetime-now-challenge-datetime-end
