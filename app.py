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
def get_page():
    return template('index')

def venues_search_place(place):
    fs = foursquare.Foursquare(client_id=FOURSQURE_CLIENT_ID, client_secret=FOURSQURE_CLIENT_SECRET)
    results = fs.venues.search(params={'near': place})
    return results

def venues_search_geolocation(lat, lng, category=None):
    fs = foursquare.Foursquare(client_id=FOURSQURE_CLIENT_ID, client_secret=FOURSQURE_CLIENT_SECRET)
    results = fs.venues.search(params={'ll': lat + ',' + lng})
    return results

def venues_images(foursquare_venue_id):
    access_token = request.session['access_token']
    collection = []
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        location = api.location_search(foursquare_v2_id=foursquare_venue_id)
        media = api.location_recent_media(location_id=location[0].id)

        for lst in media:
            for medium in lst:
                dict = {'type': medium.type, 'image': medium.get_standard_resolution_url(), 'likes': medium.like_count,
                        'comments': medium.comment_count}
                collection.append(dict)
    except Exception as e:
        print(e)

    return collection


############
# API ROUTES
############

@route('/api/venues/search/<term>', defaults={'category': None})
@route('/api/venues/search/<term>/<category>')
def find_venues(term, category=None):
    print "term:", term, "category:", category
    venues = venues_search_place(term)
    venues_in_category = []
    i = f = 0
    if venues:
        while (f < 3):
            collection = venues_images(venues['venues'][i]['id'])
            if len(collection) > 0:
                f = f + 1
                venues['venues'][i]['instagram'] = collection[0]
            venues_in_category.append(venues['venues'][i])
            i = i + 1
    return json.dumps(venues_in_category)


@route('/api/venues/show/<lat>/<lng>', defaults={'category': None})
@route('/api/venues/show/<lat>/<lng>/<category>')
def get_venues(lat, lng, category=None):
    print "lat:", lat, "lng:", lng, "category:", category
    venues = venues_search_geolocation(lat, lng, category)
    venues_in_category = []
    i = f = 0
    if venues:
        while (f < 3):
            collection = venues_images(venues['venues'][i]['id'])
            if len(collection) > 0:
                f = f + 1
                venues['venues'][i]['instagram'] = collection[0]
            venues_in_category.append(venues['venues'][i])
            i = i + 1
    return json.dumps(venues_in_category)


@route('/api/venue/<id>')
def location_media(id):
    access_token = request.session['access_token']
    collection = []
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        # get instagram location id for this foursquare location id
        instagram_location_id = api.location_search(foursquare_v2_id=id)
        media = api.location_recent_media(location_id=instagram_location_id[0].id)
        for lst in media:
            for medium in lst:
                dict = {'type': medium.type, 'image': medium.get_standard_resolution_url(), 'likes': medium.like_count,
                        'comments': medium.comment_count}
                collection.append(dict)

                # print media
    except Exception as e:
        print(e)
    # return jsonpickle.encode(media)

    print "Collection", collection
    return json.dumps(collection)

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


bottle.run(app=app, host='localhost', port=8515, reloader=True)