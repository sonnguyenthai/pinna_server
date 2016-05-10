import os
import urlparse

os.environ['DJANGO_SETTINGS_MODULE'] = 'pinna_server.settings.local'

from pinna.models import Station

def update():
    for st in Station.objects.all():
        p_url = st.photo # Photo URL
        t_url = st.thumbnail # Thumbnail URL
        # if p_url:
        #     st.photo = p_url[:p_url.find('?')]
        # if t_url:
        #     st.thumbnail = t_url[:t_url.find('?')]
        # st.save()
        # print "DONE", st.name, st.thumbnail
        print st.name
        print p_url
        print t_url


update()

