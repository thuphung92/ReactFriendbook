from . import bp as api
from app.blueprints.social.models import Post
from app.blueprints.auth.models import User
from flask import make_response, request, g
from app.blueprints.auth.auth import token_auth

# show all posts
@api.get('/all_posts')
@token_auth.login_required()
def get_all_posts():
    user = g.current_user
    posts = user.followed_posts() #adjust to show all posts as show all products
    response_list=[]
    for post in posts:
        post_dict={
            "id":post.id,
            "body":post.body,
            "date_created":post.date_created,
            "date_updated":post.date_updated,
            "author":post.author.first_name + ' ' + post.author.last_name,
            "author_id": post.author.id
        }
        response_list.append(post_dict)
    return make_response({"post":response_list},200)

# show single posts
@api.get('/posts')
@token_auth.login_required()
def get_post_api():
    user = g.current_user
    data_from_request=request.get_json()
    post = Post.query.get(data_from_request['id'])
    # check to make sure the user has access to the post
    if not user.is_following(post.author) and not post.author.id == user.id:
        return make_response("Cannot get a post for someone the user is not following",403)

    if not post:
        return make_response(f"Post id: {data_from_request['id']} does not exist",404)
    response_dict={
        "id":post.id,
        "body":post.body,
        "date_created":post.date_created,
        "date_updated":post.date_updated,
        "author":post.author.first_name + ' ' + post.author.last_name,
        "author_id": post.author.id
    }
    return make_response(response_dict,200)

# create a new post
@api.post('/posts')
@token_auth.login_required()
def post_post():
    user = g.current_user

    posted_data = request.get_json()
    post_user = User.query.get(posted_data['user_id'])
    if not post_user:
        return make_response(f"User id: {posted_data['user_id']} does not exist",404)
    if user.id != post_user.id:
        return make_response("You can only post for yourself",403)

    post = Post(**posted_data)
    post.save()
    return make_response(f"Post id:{post.id} created!", 201)

# update a post
@api.patch('/posts')
@token_auth.login_required()
def patch_post():
    user = g.current_user
    posted_data = request.get_json()
    if posted_data.get('user_id'):
        post_user = User.query.get(posted_data['user_id'])
        if not post_user:
            return make_response(f"User id: {posted_data['user_id']} does not exist",404)
        if user.id != post_user.id:
            return make_response("You can only patch your own posts",403)    
    post = Post.query.get(posted_data['id'])
    if not post:
        return make_response(f"Post id: {posted_data['id']} does not exist",404)
    post.user_id=posted_data['user_id'] if posted_data.get('user_id') and posted_data['user_id']!=post.user_id else post.user_id 
    post.body=posted_data['body'] if posted_data.get('body') and posted_data['body']!=post.body else post.body 
    post.save()
    return make_response(f"Post id: {post.id} has been changed", 200)

#  delete a post
@api.delete('/posts')
@token_auth.login_required()
def delete_post():
    posted_data = request.get_json()
    post = Post.query.get(posted_data['id'])
    user = g.current_user
    if not user.id == post.user_id:
        return make_response("You can only delete your post",403)    

    if not post:
        return make_response(f"Post id: {posted_data['id']} does not exist",404)
    p_id=post.id
    post.delete()
    return make_response(f"Post id:{p_id} has been deleted",200)