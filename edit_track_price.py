## This script will edit the price of all tracks whose price == 0
##

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'pinna_server.settings.local'

from pinna import models

def update_price(price):
    i = 0
    for track in models.Track.objects.all():
        if track.price == 0:
            track.price += price
            track.save()
            i += 1
    print "Edited %s tracks" %i

def add_coins(username, coins):
    user = models.User.objects.get(username=username)
    user.profile.amount += coins
    user.profile.save()
    print "Done: ", user.profile.amount

def remove_invalid_users():
    for user in models.User.objects.all():
        try:
            user.profile
        except models.Profile.DoesNotExist:
            print "Deleting %s ..." %user.username
            user.delete()

if __name__ == "__main__":
    #update_price(15)
    #add_coins('vanhung1710@gmail.com', 1000)
    remove_invalid_users()