import json
import os
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.decorators import api_view

import utils
from .models import PinnaSession, Profile, Library, PinnaOrder
#import serializers


@api_view(['POST'])
def create_user(request):
    """
    Create PINNA user
    """
    display_name = request.DATA.get('display_name', '').strip()
    email = request.DATA.get('email', '').strip()
    password = request.DATA.get('password', '').strip()

    if (not display_name) or (not email) or (not password):
        msg = 'These fields must not be empty: '

        empty_fields = []

        if not display_name:
           empty_fields.append('display_name')

        if not email:
            empty_fields.append('email')

        if not password:
            empty_fields.append('password')

        msg += ",".join(empty_fields)

        return utils.failed_response(msg, 'empty_fields')

    if not utils.valid_email(email):
        msg = "The email is invalid"
        msg_code = "email_invalid"
        return utils.failed_response(msg, msg_code)

    try:
        checked = User.objects.get(username=email)
        msg =  'The user is existed'
        return utils.failed_response(msg, "user_existed")
    except User.DoesNotExist:
        display_name = display_name.lower().title()

        user = User.objects.create_user(email, email, password,
                                        first_name=display_name)

        # Create My Tracks and My Library
        mylib = Library.objects.create()
        Profile.objects.create(user=user, mylibrary=mylib)

        session = PinnaSession.objects.create(user=user)

        msg = 'The user %s is created successfully' %display_name
        return utils.successful_response(msg, "ok",
                                         token=session.key,
                                         userid=user.pk)


@api_view(['POST'])
def login(request):
    """
    Let User log in to their account with username and password
    """
    email = request.DATA.get("email",'').strip()
    passwd = request.DATA.get("password",'').strip()

    if (not email) or (not passwd):
        msg_code = 'empty_fields'
        msg = 'User authentication credentials were not provided.'
        return utils.invalid_auth_response(msg, msg_code)


    user = authenticate(username=email, password=passwd)
    if not user:
        msg_code = 'invalid_credentials'
        msg = 'User authentication credentials were invalid'
        return utils.invalid_auth_response(msg, msg_code)
    else:
        session = PinnaSession.objects.create(user=user)
        msg = 'Logged in successfully'
        return utils.successful_response(msg, 'ok',
                                         token=session.key,
                                         userid=user.pk)


@api_view(['POST'])
def logout(request):
    """
    Log out
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()
    else:
        utils.expire_token(session.key)
        return utils.successful_response('Logged out', 'ok')


@api_view(['PUT', 'POST'])
def update(request):
    """
    Update user data
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    user = session.user
    display_name = request.DATA.get('display_name', '').strip()
    photo_file = request.FILES.get('photo', None)

    if display_name:
        user.first_name = display_name.lower().title()

    if photo_file:
        origin_name, ext = os.path.splitext(photo_file.name)
        if not ext:
            ext = "jpg"

        aws_name = utils.slugify_name(user.username) + '/' + utils.generate_random_name(origin_name)
        aws_name += ext
        photo = utils.add_object_via_cloudfront(aws_name, photo_file, False)
        if photo:
            try:
                old_photo = user.profile.photo_s3_name
                utils.delete_s3_object(old_photo, False)
            except AttributeError:
                pass
            user.profile.display_photo = photo
            user.profile.photo_s3_name = aws_name
            user.profile.save()
        else:
            msg = "Can't upload display photo to S3"
            msg_code = "failed"
            return utils.failed_response(msg, msg_code)

    user.save()

    msg = "User %s was updated" %user.username
    msg_code = "ok"

    return utils.successful_response(msg,
                                     msg_code,
                                     display_name=user.first_name,
                                     email=user.email,
                                     photo_url=user.profile.display_photo)


@api_view(['GET'])
def get_profile(request):
    """
    Get current User data
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    user = session.user

    msg = "Data of user %s was retrieved" %user.username
    msg_code = "ok"

    followers = user.profile.followers.count()
    followings = User.objects.filter(profile__followers=user).count()

    return utils.successful_response(msg,
                                     msg_code,
                                     display_name=user.first_name,
                                     email=user.email,
                                     photo_url=user.profile.display_photo,
                                     userid=user.pk,
                                     num_followers=followers,
                                     num_followings=followings,
                                     amount=user.profile.amount)


@api_view(['POST'])
def change_password(request):
    """
    Change user password
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    old_pw = request.DATA.get('old_password', '')
    new_pw = request.DATA.get('new_password', '')

    if not (old_pw and new_pw):
        msg = "Old password or new password must be provided"
        return utils.failed_response(msg, 'empty_fields')

    if session.user.check_password(old_pw):
        session.user.set_password(new_pw)
        session.user.save()
        utils.expire_token(session.key)
        msg = "Password was changed. You have to log in again using new password"
        return utils.successful_response(msg, "ok")

    msg = "Old password is invalid"
    return utils.failed_response(msg, "invalid_password")


@api_view(['GET'])
def get_user_profile(request, user_id):
    """
    Get User data
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        msg = "User does not exist"
        return utils.failed_response(msg, "invalid_user")

    if user.is_staff or user.is_superuser:
        msg = "User does not exist"
        return utils.failed_response(msg, "invalid_user")

    msg = "Data of user %s was retrieved" %user.username
    msg_code = "ok"

    is_followed = False
    if user.profile.followers.filter(pk=session.user.pk).exists():
        is_followed = True

    followers = user.profile.followers.count()
    followings = User.objects.filter(profile__followers=user).count()

    return utils.successful_response(msg,
                                     msg_code,
                                     display_name=user.first_name,
                                     email=user.email,
                                     photo_url=user.profile.display_photo,
                                     is_followed=is_followed,
                                     num_followers=followers,
                                     num_followings=followings,
                                     amount=user.profile.amount)


@api_view(["POST"])
def follow(request, userid):
    """
    Follow a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        following = User.objects.get(pk=userid)
    except User.DoesNotExist:
        msg = "The user with id %s does not exist" %following
        return utils.failed_response(msg, "invalid_userid")

    following.profile.followers.add(session.user)
    following.profile.save()

    msg = "Followed"
    return utils.successful_response(msg, "ok")


@api_view(["POST"])
def unfollow(request, userid):
    """
    Unfollow a user
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    try:
        following = User.objects.get(pk=userid)
    except User.DoesNotExist:
        msg = "The user with id %s does not exist" %following
        return utils.failed_response(msg, "invalid_userid")

    following.profile.followers.remove(session.user)
    following.profile.save()

    msg = "Unfollowed"
    return utils.successful_response(msg, "ok")


@api_view(["GET"])
def get_followers(request, userid):
    """
    Get list of followers
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    if session.user.id == userid:
        user = session.user
    else:
        try:
            user = User.objects.get(pk=userid)
        except User.DoesNotExist:
            msg = "The user with id %s does not exist" %userid
            return utils.failed_response(msg, "invalid_userid")

    followers = user.profile.followers.all()

    data = utils.paginate_items(request, followers, "user", user=session.user)

    if len(followers) == 0:
        msg = "There is no follower found"
        return utils.failed_response(msg, "no_follower")

    msg = "There are %s followers found" %len(followers)
    return utils.successful_response(msg, "ok", **data)


@api_view(["POST"])
def add_coins(request):
    """
    Add Pinna coins to the current user's account
    """
    session = utils.check_auth_token(request)
    if not session:
        return utils.invalid_auth_response()

    coins = request.DATA.get('coins', None)
    purchase_data = request.DATA.get('purchase_data', None)
    signature = request.DATA.get('signature', None)

    if not (coins and purchase_data and signature):
        msg = "Missing: "

        misses = []
        if not coins:
            misses.append("coins")

        if not purchase_data:
            misses.append("purchase_data")

        if not signature:
            misses.append("signature")

        msg += ",".join(misses)
        return utils.failed_response(msg, "empty_fields")

    try:
        json_data = json.loads(purchase_data)
    except:
        msg = "Invalid purchase_data"
        return utils.failed_response(msg, "invalid_purchase_data")

    if not utils.verify_signature(purchase_data, signature):
        msg = "Signature does not match"
        return utils.failed_response(msg, "signature_not_match")

    order_id = json_data.get('orderId', '')
    date = datetime.fromtimestamp(json_data.get('purchaseTime')/1000)
    state = json_data.get('purchase_state', 1)
    try:
        PinnaOrder.objects.get(pk=order_id)
        msg = "The order already existed"
        return utils.failed_response(msg, "order_existed")
    except PinnaOrder.DoesNotExist:
        order = None
        try:
            order = PinnaOrder.objects.create(order_id=order_id,
                                      user=session.user,
                                      purchase_state=state,
                                      purchase_time=date,
                                      purchase_data=purchase_data)
            session.user.profile.amount += int(coins)
            session.user.profile.save()
            msg = "%s PINNA coins were added to the user account" %coins
            return utils.successful_response(msg, "ok", amount=session.user.profile.amount)
        except:
            if order:
                order.delete()
            msg = "Can't add PINNA coins to the user account"
            return utils.failed_response(msg, "failed")

