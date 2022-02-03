import os
import time
from flask import Flask, request, jsonify, make_response
import csv

# from pymongo import MongoClient

from src.utils import get_named_logger
from src.questiongenerator import QuestionGenerator
from src.questiongenerator import print_qa
from src.gcp_utils_python import get_data, save_data


logger = get_named_logger(__name__)
logger.info(f"Logging started for module {__name__}.")

app = Flask(__name__)


def write_to_csv(data, file_path):

    keys = data[0].keys()

    with open(file_path, "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    file_name = os.path.basename(file_path)
    save_data(file_path, file_name)


@app.route("/ping")
def ping():
    return "pong"


# generate question answer pairs:
@app.route("/qa", methods=["POST"])
def get_qa_pairs():
    """
    This method is used to get QA pairs.

    Sample Input:
    {
        "text_file":"/path/to/text/file",
        "num_questions":"10",
        "answer_style":"sentences", # multiple_choice, all
        "use_qa_eval":"True",
        "show_answers":"True",
        "file_location_gcs":"True"
    }
    """
    start = time.time()
    try:
        if (
            request.method == "POST"
            and request.headers["Content-Type"] == "application/json"
            and hasattr(request, "data")
        ):
            try:
                args = request.get_json()

                if args.get("file_location_gcs", "True") == "True":
                    logger.debug("File is in GCS")
                    file_name = args["text_file"]
                    file_path = "/project/articles/" + file_name
                    get_data(file_path, file_name)
                else:
                    logger.debug("File is available locally")
                    file_path = args["text_file"]

                with open(file_path, "r") as file:
                    text_file = file.read()
                qg = QuestionGenerator()
                qa_list = qg.generate(
                    text_file,
                    num_questions=int(args["num_questions"]),
                    answer_style=args["answer_style"],
                    use_evaluator=args["use_qa_eval"],
                )
                # print_qa(qa_list, show_answers=args["show_answers"])
                # return jsonify({"status": "success", "payload": qa_list}), 200

                # os.path.dirname(os.path.realpath(__file__))
                # os.path.basename(os.path.realpath(__file__))

                if args.get("file_location_gcs", "True") == "True":
                    file_path = file_path.split(".")[0] + ".csv"
                    write_to_csv(qa_list, file_path)
                    result = {
                        "status": "success",
                        "payload": "Data is written to csv file in GCS bucket",
                    }
                else:
                    result = qa_list

                response_code = 200

                logger.info(
                    "Generated "
                    + str(args["num_questions"])
                    + " questions from "
                    + str(args["text_file"])
                    + ". Time taken to process"
                    + " is {:.6}".format((time.time() - start))
                )
            except KeyError:
                result = {
                    "status": "failed",
                    "payload": "Bad content type or no JSON object in POST request or Error while generating questions from file",
                }
                response_code = 400
    except Exception as e:
        result = {
            "status": "failed",
            "payload": "An internal server error happened. Please try again later",
        }
        response_code = 500
        logger.exception(
            f"Error - {e}"
            + str(result)
            + " Time taken to process is {:.6}".format((time.time() - start))
        )
    finally:
        response = make_response(jsonify(result), response_code)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"), debug=False)

# References:
# # https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python
# # https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format

# # https://stackoverflow.com/questions/3086973/how-do-i-convert-this-list-of-dictionaries-to-a-csv-file
# # https://stackoverflow.com/questions/8685809/writing-a-dictionary-to-a-csv-file-with-one-line-for-every-key-value
# # https://stackoverflow.com/questions/8331469/python-dictionary-to-csv
# # https://stackoverflow.com/questions/10373247/how-do-i-write-a-python-dictionary-to-a-csv-file
