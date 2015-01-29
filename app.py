import bottle
import json
import foursquare
from bottle import route, redirect, post, run, request, hook, template, static_file, default_app
from instagram import client, models
import config
import time
from datetime import datetime

bottle.debug(True)

CATEGORIES = config.CATEGORIES
app = bottle.app()
unauthenticated_api = client.InstagramAPI(**config.INSTAGRAM)



def join_all_categories():
    str = ""
    for key, value in CATEGORIES.iteritems():
        str += ''.join(value) + ','
    return str


# ########
# HELPERS
# ########
# def get_page():
# return template('index')


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
    params = {'ll': lat + ',' + lng, }
    if category:
        if category in CATEGORIES.keys():
            params['categoryId'] = ''.join(CATEGORIES[category])
        else:
            raise ValueError('Provided category not found', category)
    else:
        params['categoryId'] = join_all_categories()

    results = fs.venues.explore(params=params)
    # print results['groups']

    #TODO get this rate call working
    # print "RATE REMAINING", fs.rate_remaining()

    print "fs.venues.explore, results[groups] len", len(results['groups'])
    # print results['groups'][0]['items']

    #TODO check what other groups this returns?!
    return results['groups'][0]['items']
    # return results


def venues_images(access_token, foursquare_venue_id, sort_by=None):
    collection = []
    api = client.InstagramAPI(access_token=access_token)
    location = api.location_search(foursquare_v2_id=foursquare_venue_id)
    if len(location) > 0:
        media = api.location_recent_media(location_id=location[0].id)
    else:
        return

    try:
        for lst in media:
            if lst:
                for medium in lst:
                    # TODO WTF is going on here, why would there by some strings spread over an array in this lst?
                    # print type(medium)
                    if (medium and type(medium) is models.Media):

                        # print "medium", medium
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
        # return e


    if sort_by and sort_by is "popular":
        collection = sorted(collection, key=lambda k: k['likes'])
        collection.reverse()

    return collection


def venue_info(access_token, foursquare_venue_id):
    try:
        fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)
        result = fs.venues(foursquare_venue_id)
        return result
    except Exception as e:
        print e
        return False


# ###########
# API ROUTES
############

@route('/api/venues/search/<term>', defaults={'category': None})
@route('/api/venues/search/<term>/<category>')
def find_venues(term, category=None):
    print str(datetime.now()), "term:", term, "category:", category

    if 'access_token' in request.query.keys():
        access_token = request.query['access_token']
        if not access_token:
            return 'Invalid access_token'
    else:
        return 'Missing access_token'

    if 'limit' in request.query.keys():
        limit = request.query['limit']
    else:
        limit = 3

    venues = venues_search_place(term, category)
    venues_in_category = []
    i = f = 0
    max = min(int(limit), len(venues) - 1)
    if venues:
        while (f < max):
            collection = venues_images(venues[i]['venue']['id'], "popular")
            if len(collection) > 0:
                f = f + 1
                venues[i]['instagram'] = collection[0]
                venues[i]['instagram_stats'] = {'num_photos': len(collection)}
            venues_in_category.append(venues[i])
            i = i + 1

    print str(datetime.now())
    return json.dumps(venues_in_category)


@route('/api/venues/show/<lat>/<lng>', defaults={'category': None})
@route('/api/venues/show/<lat>/<lng>/<category>')
def get_venues(lat, lng, category=None):
    print str(datetime.now()), "lat:", lat, "lng:", lng, "category:", category

    try:
        if 'access_token' in request.query.keys():
            access_token = request.query['access_token']
            if not access_token:
                raise Exception('Invalid access_token')
        else:
            raise Exception('Missing access_token')

        if 'limit' in request.query.keys():
            limit = request.query['limit']
        else:
            limit = 3

        venues = venues_search_geolocation(lat, lng, category)
        venues_in_category = []
        i = f = 0
        max = min(int(limit), (len(venues) - 1))
        if venues:
            while (f < max):
                collection = venues_images(access_token, venues[i]['venue']['id'], "popular")
                if collection and len(collection) > 0:
                    f = f + 1
                    venues[i]['instagram'] = collection[0]
                    venues[i]['instagram_stats'] = {'num_photos': len(collection)}
                venues_in_category.append(venues[i])
                i = i + 1

        print str(datetime.now())
        return json.dumps(venues_in_category)
    except Exception as e:
        print str(datetime.now())
        print e
        return "api/venues/show returned error"



@route('/api/venue/<id>')
def location_media(id):
    print str(datetime.now())
    try:
        if 'access_token' in request.query.keys():
            access_token = request.query['access_token']
            if not access_token:
                raise Exception('Invalid access_token')
        else:
            raise Exception('Missing access_token')

        venue = venue_info(access_token, id)
        collection = venues_images(access_token, id, "popular")
        result = { 'venue': venue['venue'], 'images': collection }
        print str(datetime.now())
        return json.dumps(result)
    except Exception as e:
        print str(datetime.now())
        print e
        return "api/venue/id returned error"


@route('/')
def home():
    return '<a href="http://koala-prototype.meteor.com">prototype frontend moved, click me :)</a>'
