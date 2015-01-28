import bottle
import beaker.middleware
import json
import foursquare
from bottle import route, redirect, post, run, request, hook, template, static_file, default_app
from instagram import client
import config
import calendar
import time

bottle.debug(True)

session_opts = config.SESSION_OPTIONS
CATEGORIES = config.CATEGORIES
app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)
unauthenticated_api = client.InstagramAPI(**config.INSTAGRAM)



# ######
# HOOKS
# ######

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


def join_all_categories():
    str = ""
    for key, value in CATEGORIES.iteritems():
        str += ''.join(value) + ','
    return str


#########
# HELPERS
#########
# def get_page():
#     return template('index')


def venues_search_place(place, category):
    fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)
    params = {'near': place}
    if category:
        if category in CATEGORIES.keys():
            params['categoryId'] = ''.join(CATEGORIES[category])
        else:
            raise ValueError('Provided category not found', category)
    else:
        params['categoryId'] = join_all_categories()

    # results = fs.venues.search(params=params)
    # return results
    results = fs.venues.explore(params=params)
    return results['groups'][0]['items']


def venues_search_geolocation(lat, lng, category=None):
    fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)
    params = {'ll': lat + ',' + lng,}
    if category:
        if category in CATEGORIES.keys():
            params['categoryId'] = ''.join(CATEGORIES[category])
        else:
            raise ValueError('Provided category not found', category)
    else:
        params['categoryId'] = join_all_categories()

    results = fs.venues.explore(params=params)
    #print results['groups']

    #TODO get this rate call working
    # print "RATE REMAINING", fs.rate_remaining()

    #TODO check what other groups this returns?!
    return results['groups'][0]['items']
    # return results


def venues_images(foursquare_venue_id, sort_by=None):
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
                dict = {
                    'type': medium.type,
                    'image': medium.get_standard_resolution_url(),
                    'likes': medium.like_count,
                    'comments': medium.comment_count,
                    'api_calls_remaining': api.x_ratelimit_remaining,
                    'user': medium.user.username,
                    'user_profile': medium.user.profile_picture,
                    'created_time': time.asctime(medium.created_time.timetuple())
                }
                collection.append(dict)
    except Exception as e:
        print(e)

    if sort_by and sort_by is "popular":
        collection = sorted(collection, key=lambda k: k['likes'])
        collection.reverse()

    return collection

############
# API ROUTES
############

@route('/api/venues/search/<term>', defaults={'category': None})
@route('/api/venues/search/<term>/<category>')
def find_venues(term, category=None):
    print "term:", term, "category:", category
    venues = venues_search_place(term, category)
    venues_in_category = []
    i = f = 0
    max = min(3, len(venues) - 1)
    if venues:
        while (f < max):
            collection = venues_images(venues[i]['venue']['id'], "popular")
            if len(collection) > 0:
                f = f + 1
                venues[i]['instagram'] = collection[0]
                venues[i]['instagram_stats'] = {'num_photos': len(collection)}
            venues_in_category.append(venues[i])
            i = i + 1
    return json.dumps(venues_in_category)


@route('/api/venues/show/<lat>/<lng>', defaults={'category': None})
@route('/api/venues/show/<lat>/<lng>/<category>')
def get_venues(lat, lng, category=None):
    print "lat:", lat, "lng:", lng, "category:", category

    # TODO smarter way of pushing possibly existing request.query access_token to session for all calls
    if 'access_token' in request.query.keys():
        request.session['access_token'] = request.query['access_token']


    venues = venues_search_geolocation(lat, lng, category)
    venues_in_category = []
    i = f = 0
    max = min(3, len(venues) - 1)
    if venues:
        while (f < max):
            collection = venues_images(venues[i]['venue']['id'], "popular")
            if len(collection) > 0:
                f = f + 1
                venues[i]['instagram'] = collection[0]
                venues[i]['instagram_stats'] = {'num_photos': len(collection)}
            venues_in_category.append(venues[i])
            i = i + 1
    return json.dumps(venues_in_category)


@route('/api/venue/<id>')
def location_media(id):
    collection = venues_images(id, "popular")
    return json.dumps(collection)

#
# ############
# # APP ROUTES
# ############
#
# @route('/static/<filepath:path>')
# def server_static(filepath):
#     return static_file(filepath, root='./static')
#
#
# @route('/')
# def home():
#     try:
#         url = unauthenticated_api.get_authorize_url(scope=["likes", "comments"])
#         return '<a href="%s">Connect with Instagram</a>' % url
#     except Exception as e:
#         print(e)
#
#
# @route('/app')
# def on_callback():
#     code = request.GET.get("code")
#     if not code:
#         access_token = request.session['access_token']
#         if not access_token:
#             return 'Missing code'
#     try:
#         access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
#         if not access_token:
#             return 'Could not get access token'
#         api = client.InstagramAPI(access_token=access_token)
#         request.session['access_token'] = access_token
#         print ("access token=" + access_token)
#     except Exception as e:
#         print(e)
#     return get_page()


# bottle.run(app=app, host='localhost', port=5000, reloader=True)