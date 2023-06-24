from flask import Flask, jsonify, request
from flask_cors import CORS
from operator import itemgetter

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_post_data(data):
    """ validates the post data """

    if 'title' not in data:
        return False, "Missing data: 'title'"
    elif 'content' not in data:
        return False, "Missing data: 'content'"
    else:
        return True


def find_post_by_id(post_id):
    """ Find the post with the id `post_id`.
  If there is no post with this id, return None. """

    post = [post for post in POSTS if post['id'] == post_id]
    if len(post) != 0:
        return post
    return None


def validate_sort_and_direction(sort, direction):
    """ validates the sorting and direction query parameters """

    if sort is not None:
        if sort not in ['tile', 'content']:
            return False
    if direction is not None:
        if direction not in ['asc', 'desc']:
            return False
    return True


def post_sorting_with_direction(sort, direction):
    """ Sorts posts depending on the given parameters """

    # if sort parameter is given and direction is None, then use default direction: `reverse=True`
    if sort and not direction:
        sorted_post = sorted(POSTS, key=itemgetter(sort), reverse=True)

    #  Else if direction parameter is given without sort parameter, then use default sort parameter: `title`
    elif direction and not sort:
        if direction == 'asc':
            sorted_post = sorted(POSTS, key=itemgetter('title'))  # direction is asc
        else:
            sorted_post = sorted(POSTS, key=itemgetter('title'), reverse=True)  # direction is desc

    #  Else both sort and direction parameters are given
    else:
        if direction == 'asc':
            sorted_post = sorted(POSTS, key=itemgetter(sort))  # direction is asc
        else:
            sorted_post = sorted(POSTS, key=itemgetter(sort), reverse=True)  # direction is desc

    return sorted_post


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """Handles Get and POSTS requests.
        Displays all posts if GET request is received.
        Otherwise adds  new post if POST. """

    if request.method == 'POST':
        # Get the new post data from the user
        new_post = request.get_json()

        # Validate Post Data
        post_data = validate_post_data(new_post)
        if isinstance(post_data, tuple):
            _, error_message = post_data
            return jsonify({"Error": f"{error_message}"}), 400

        # Generate a new ID for the post
        new_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_id

        # Add the new post to the list of POSTS
        POSTS.append(new_post)

        # Return the new post data to the client
        return jsonify(new_post), 201
    else:
        # Handle the GET request

        # Gets query parameters
        sort = request.args.get('sort')
        direction = request.args.get('direction')

        # if there is no sorting parameter, then display posts as they are
        if not sort and not direction:
            return jsonify(POSTS)

        # validate the parameters for valid data
        if validate_sort_and_direction(sort=sort, direction=direction):
            print(validate_sort_and_direction(sort=sort, direction=direction))
            # Sorted Post
            sorted_post = post_sorting_with_direction(sort=sort, direction=direction)
            return jsonify(sorted_post), 200
        else:
            return jsonify({"error": "Bad Data. Sort by 'title' or 'content' and  'asc' or 'desc' for direction"}), 404


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    """ Deletes post using post_id """

    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id <{id}> not found"}), 404

    # Remove the post from the list
    found_post_index = POSTS.index(post[0])
    POSTS.pop(found_post_index)

    # Return the deleted post
    return jsonify({"message": f"Post with id <{id}> has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    """ Updates post using post id """

    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"error": f"Post with id <{id}> not found"}), 404

    # Update the POSTS with the new data
    new_data = request.get_json()
    post[0].update(new_data)

    # Return the updated post
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """ Searches post using search specified parameters and return searched posts """
    # Gets query parameters
    title = request.args.get('title')
    content = request.args.get('content')

    if not content and not title:
        return jsonify({"error": "Missing search parameter ['title' or 'content']"}), 404

    searched_posts = []
    for post in POSTS:
        # search by title, if title search parameters is given
        if title:
            if title.lower() in post['title'].lower():
                searched_posts.append(post)

        # search by content, if content search parameters is given
        if content:
            if content.lower() in post['content'].lower():
                searched_posts.append(post)

    if searched_posts:
        # creating a set of searched posts
        searched_post = list({post['id']: post for post in searched_posts}.values())
        return jsonify(searched_post), 200
    else:
        return jsonify({"error": "Search not found'"}), 404


@app.errorhandler(404)
def not_found_error(error):
    """ Handles 404 Error if user makes typo error on the url or searches a non-existent url path"""
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    """ Handles 405 error if user uses a method that is not allowed with the API """
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
