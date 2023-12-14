from flask import Flask, request, jsonify
import requests
from datetime import datetime

import json

app = Flask(__name__)

BASE_URL = "https://app.ylytic.com/ylytic/test"


@app.route("/search", methods=["GET"])
def search_comments():
    # Get query parameters from the request
    search_author = request.args.get("search_author")
    at_from = request.args.get("at_from")
    at_to = request.args.get("at_to")
    like_from = request.args.get("like_from")
    like_to = request.args.get("like_to")
    reply_from = request.args.get("reply_from")
    reply_to = request.args.get("reply_to")
    search_text = request.args.get("search_text")

    # Convert date format from URL format to JSON response format
    at_from = convert_date_format(at_from)
    at_to = convert_date_format(at_to)

    # Create parameters for the GET request to the base API
    params = {}

    if search_author:
        params["search_author"] = search_author

    if at_from:
        params["at_from"] = at_from

    if at_to:
        params["at_to"] = at_to

    if like_from:
        params["like_from"] = like_from

    if like_to:
        params["like_to"] = like_to

    if reply_from:
        params["reply_from"] = reply_from

    if reply_to:
        params["reply_to"] = reply_to

    if search_text:
        params["search_text"] = search_text

    # Make a GET request to the base API with the constructed parameters
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Check for HTTP error status codes
    except requests.exceptions.RequestException as e:
        # Handle the exception, e.g., log an error message or return an appropriate response
        return jsonify({"error": "Failed to fetch comments from the base API"}), 500

    # Check if the request to the base API was successful
    if response.status_code == 200:
        # Parse the JSON response from the base API
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            # Handle the exception, e.g., log an error message or return an appropriate response
            return (
                jsonify({"error": "Failed to parse JSON response from the base API"}),
                500,
            )

        # Extract the "comments" dictionary from the response
        comments = data.get("comments", [])

        # Filter comments based on the provided parameters
        filtered_comments = filter_comments(
            comments,
            search_author,
            at_from,
            at_to,
            like_from,
            like_to,
            reply_from,
            reply_to,
            search_text,
        )

        # Return the filtered comments as JSON response
        return jsonify(filtered_comments)
    else:
        # Handle error cases, e.g., return an error message or appropriate status code
        return jsonify({"error": "Failed to fetch comments from the base API"}), 500


def convert_date_format(date_str):
    # Convert the date string from 'dd-mm-yyyy' to 'Mon, DD Jan YYYY HH:MM:SS GMT'
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
    return date_obj.strftime("%a, %d %b %Y %H:%M:%S GMT")


def filter_comments(
    comments,
    search_author,
    at_from,
    at_to,
    like_from,
    like_to,
    reply_from,
    reply_to,
    search_text,
):
    filtered_comments = []

    for comment in comments:
        # Check if the comment matches the search criteria
        if (
            (not search_author or search_author in comment["author"])
            and (not at_from or comment["at"] >= at_from)
            and (not at_to or comment["at"] <= at_to)
            and (not like_from or comment["like"] >= int(like_from))
            and (not like_to or comment["like"] <= int(like_to))
            and (not reply_from or comment["reply"] >= int(reply_from))
            and (not reply_to or comment["reply"] <= int(reply_to))
            and (not search_text or search_text in comment["text"])
        ):
            filtered_comments.append(comment)

    return filtered_comments


if __name__ == "__main__":
    app.run(debug=True)
