import bottle
import beaker.middleware
import json
import jsonpickle
import foursquare
from bottle import route, redirect, post, run, request, hook, template, static_file
from instagram import client, subscriptions

bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

CONFIG = {
    'client_id': '6175f60283394342b0a720fb596ae0b6',
    'client_secret': '67534712185146dc8ca6bbe94aabff7b',
    'redirect_uri': 'http://localhost:8515/app'
}

FOURSQURE_CLIENT_ID = 'CA1FI3A2KJ3ZDRIUF5DJUZIXXES24XFVICYON34GBBOKBXSB'
FOURSQURE_CLIENT_SECRET = 'FRHDILCEV0Y0E1WR3VWPWT03X0N01AKZU5SJVHK4M0NE2HF0'

unauthenticated_api = client.InstagramAPI(**CONFIG)


# ######
# HOOKS
#######

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


#########
# HELPERS
#########

def search_location(place):
    fs = foursquare.Foursquare(client_id=FOURSQURE_CLIENT_ID, client_secret=FOURSQURE_CLIENT_SECRET)
    results = fs.venues.search(params={'near': place})
    return results


def get_page():
    return template('index')


def venues_search(lat, lng, category=None):
    fs = foursquare.Foursquare(client_id=FOURSQURE_CLIENT_ID, client_secret=FOURSQURE_CLIENT_SECRET)
    results = fs.venues.search(params={'ll': lat + ',' + lng})
    return results

########
# ROUTES
########

# json api resources
#
# /geolocation
#     > here (default) or any lat lng location
#     > geolocation based foursquare lookup
#     > show x different places / category from instagram
#
# /geolocation/*category*
#     > show 1 image / page
#
# /geolocation/*category*/*venue*
#     > 3 different view types for viewing x photos at venue
#
# ~~~
# /location/*placename*
#     > term based foursquare lookup
#     > show x different places / category from instagram
#
# /location/*placename*/*category*


############
# API ROUTES
############

# @route('/api/venues/<lat>/<lng>')
# def get_venues(lat, lng):
#     return True

@route('/api/venues/<lat>/<lng>', defaults={'category': None})
@route('/api/venues/<lat>/<lng>/<category>')
def get_venues(lat, lng, category=None):
    print lat
    print lng
    print category
    #
    # if category:
    #     True
    # else:
    #     False

    venues = venues_search(lat, lng, category)

    v = []
    if venues:
        for x in range(0, 3):

            # for key, value in venues['venues'][x].iteritems():
            #     print key, value

            print "---"
            print "ID", venues['venues'][x]['id']

            access_token = request.session['access_token']
            collection = []
            if not access_token:
                return 'Missing Access Token'
            try:
                api = client.InstagramAPI(access_token=access_token)

                location = api.location_search(foursquare_v2_id=venues['venues'][x]['id'])
                print "loc", location[0].id

                media = api.location_recent_media(location_id=location[0].id)
                print "media", media[0]

                for lst in media:
                    for medium in lst:
                        dict = {'type': medium.type, 'image': medium.get_standard_resolution_url(), 'likes': medium.like_count,
                                'comments': medium.comment_count}
                        collection.append(dict)

                        # print media
            except Exception as e:
                print(e)

            print "collection", collection

            venues['venues'][x]['instagram'] = collection[0]
            v.append(venues['venues'][x])

    return json.dumps(v)


@route('/api/venue/<id>')
def get_venue(id):
    return True


############
# APP ROUTES
############

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["likes", "comments"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)


@route('/app')
def on_callback():
    code = request.GET.get("code")
    if not code:
        access_token = request.session['access_token']
        if not access_token:
            return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token)
        request.session['access_token'] = access_token
        print ("access token=" + access_token)
    except Exception as e:
        print(e)
    return get_page()


@route('/location_recent_media')
def location_recent_media():
    access_token = request.session['access_token']
    content = "<h2>Location Recent Media</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.location_recent_media(location_id=514276)
        photos = []
        for media in recent_media:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
        content += ''.join(photos)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/media_search')
def media_search():
    access_token = request.session['access_token']
    content = "<h2>Media Search</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        media_search = api.media_search(lat="37.7808851", lng="-122.3948632", distance=1000)
        photos = []
        for media in media_search:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
        content += ''.join(photos)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/location/name/<name>')
def location_by_name(name):
    locations = search_location(name)

    # print locations.items
    # print type(locations)

    for key in locations:
        # print "key %s, value %s" % (key, locations[key])
        print "key %s" % (key)

    p = []
    for place in locations['venues']:
        # if place.id:
        dict = {"id": place["id"]}
        p.append(dict)
        for key in place:
            print "key %s" % (key)

    print p
    # return json.dumps(locations['venues'])
    return json.dumps(p)


@route('/location_search/<lat>/<lng>')
def location_search(lat, lng):
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        location_search = api.location_search(lat=lat, lng=lng, distance=5000)
        # print location_search
        locations = []
        for location in location_search:
            dict = {'id': location.id, 'name': location.name, 'lat': location.point.latitude,
                    'lng': location.point.longitude}
            locations.append(dict)
    except Exception as e:
        print(e)
    # return json.dumps([{ 'locations': locations}, {'limit_remaining': api.x_ratelimit_remaining }])
    print locations
    return json.dumps(locations)


@route('/location_media/<id>')
def location_media(id):
    access_token = request.session['access_token']
    collection = []
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        media = api.location_recent_media(location_id=id)
        for lst in media:
            for medium in lst:
                dict = {'type': medium.type, 'image': medium.get_standard_resolution_url(), 'likes': medium.like_count,
                        'comments': medium.comment_count}
                collection.append(dict)

                # print media
    except Exception as e:
        print(e)
    # return jsonpickle.encode(media)
    return json.dumps(collection)


bottle.run(app=app, host='localhost', port=8515, reloader=True)