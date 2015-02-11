import bottle
import json
import foursquare
from bottle import route, redirect, post, run, request, hook, template, static_file, default_app
from instagram import client, models
import config
import time
from datetime import datetime
from urlparse import urlparse

bottle.debug(True)

CATEGORIES = config.CATEGORIES
app = bottle.app()
unauthenticated_api = client.InstagramAPI(**config.INSTAGRAM)


# ########
# HELPERS
# ########


def join_all_categories():
    str = ""
    for key, value in CATEGORIES.iteritems():
        str += ''.join(value) + ','
    return str




def limitFromRequest(request, default=3):
    if 'limit' in request.query.keys():
        return request.query['limit']
    else:
        return default

def fromRequest(request, param, default):
    print "fromRequest", param

    if param in request.query.keys():
        return request.query[param]
    else:
        if default:
            return default
        else:
            return False

def fromRequestObj(request, object):
    defaulted = {}
    for key in object.keys():
        print "fromReqObj", key, object[key]
        defaulted[key] = fromRequest(request, key, object[key])

    print "defaulted", defaulted
    return defaulted


def venues_get_id(id):
    fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)
    results = fs.venues(id)
    print results['groups'][0]
    return results['groups'][0]['items']


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

    # TODO get this rate call working
    # print "RATE REMAINING", fs.rate_remaining()

    print "fs.venues.explore, results[groups] len", len(results['groups'])
    # print results['groups'][0]['items']

    # TODO check what other groups this returns?!
    return results['groups'][0]['items']


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
                            'instagram_id': medium.id,
                            'type': medium.type,
                            'image': medium.get_standard_resolution_url(),
                            'likes': medium.like_count,
                            'comments_count': medium.comment_count,
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


def venue_info(foursquare_venue_id):
    try:
        fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)
        result = fs.venues(foursquare_venue_id)
        print "FS API calls remaingin", fs.rate_remaining
        result['api_calls_remaining'] = fs.rate_remaining
        return result
    except Exception as e:
        print e
        return False


def instagram_comments(access_token, instagram_id):
    try:
        api = client.InstagramAPI(access_token=access_token)
        result = api.media_comments(instagram_id)
        comments = []
        print len(result)
        print result
        if result:
            for v in result:
                comments.append({
                    'text': v.text,
                    'username': v.user.username,
                    'profile_picture': v.user.profile_picture
                })

            print comments
            return comments
        else:
            return False
    except Exception as e:
        print "excep", e
        return False


# ###########
# API ROUTES
# ###########

@route('/api/venues/search/<term>', defaults={'category': None})
@route('/api/venues/search/<term>/<category>')
def find_venues(term, category=None):
    print str(datetime.now()), "term:", term, "category:", category

    access_token = fromRequest(request, 'access_token', False)
    limit = limitFromRequest(request, 3)

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





# Retrieves a list of venues based on a geolocation
# @route('/api/venues/show/<lat>/<lng>', defaults={'category': None})
@route('/api/venues/show/<lat>/<lng>')
def api_venues_show(lat, lng):
    print str(datetime.now()), "lat:", lat, "lng:", lng

    for key in request.query.decode():
        print "request param", key, request.query[key]

    try:
        access_token = fromRequest(request, 'access_token', False)
        limit = fromRequest(request, 'limit', 3)


        requestParams = fromRequestObj(request, {
            'limit': 3,
            'offset': 10
        })

        print "requParams", requestParams

        params = {
            'll': lat + ',' + lng,
        }
        params.update(requestParams);

        category = fromRequest(request, 'category', False)
        if category:
            if category in CATEGORIES.keys():
                params['categoryId'] = ''.join(CATEGORIES[category])
            else:
                raise ValueError('Provided category not found', category)
        else:
            params['categoryId'] = join_all_categories()
        print "PARAMS", params

        # venues = venues_search_geolocation(lat, lng, category)

        fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID, client_secret=config.FOURSQURE_CLIENT_SECRET)


        results = fs.venues.explore(params=params)

        # TODO get this rate call working
        # print "RATE REMAINING", fs.rate_remaining()

        # print "fs.venues.explore, results[groups] len", len(results['groups'])
        # print results['groups'][0]['items']

        # TODO check what other groups this returns?!
        # print "ITEMS", results['groups'][0]['items']
        venues = results['groups'][0]['items']

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
        access_token = fromRequest(request, 'access_token', False)
        venue = venue_info(id)
        collection = venues_images(access_token, id, "popular")
        result = {'venue': venue['venue'], 'images': collection, 'fq_api_calls_remaining': venue['api_calls_remaining']}
        print str(datetime.now())
        return json.dumps(result)
    except Exception as e:
        print str(datetime.now())
        print e
        return "api/venue/id returned error"


@route('/api/image_comments/<id>')
def image_comments(id):
    print str(datetime.now())
    try:
        access_token = fromRequest(request, 'access_token', False)
        result = instagram_comments(access_token, id)
        return json.dumps(result)
    except Exception as e:
        print str(datetime.now())
        print e
        return "api/image_comments/id returned error"


# TODO fix these are complete SUDO results, just instagram trending people, nothing to do with venue photos
# idea for this: query instagram top 100 popular, crosscheck for photos with location / venue, show those for now?
@route('/api/trendsetters/<lat>/<lng>')
def trendsetters(lat, lng):
    print str(datetime.now())
    try:
        access_token = fromRequest(request, 'access_token', False)
        api = client.InstagramAPI(access_token=access_token)
        # TODO get limit from query param
        result = api.media_popular(count=2)
        users = []
        for media in result:
            # print media.images['standard_resolution'].url
            dict = {
                'username': media.user.username,
                'id': media.user.id,
                'profile_picture': media.user.profile_picture
            }
            users.append(dict)

        return json.dumps(users)

    except Exception as e:
        print str(datetime.now())
        print e
        return "api/transetters returned error"


# TODO checkout proper logging library instead of noobster printing times etc...
# TODO return http errors, not text


@route('/api/user/network/feed')
def network_summary():
    try:
        access_token = fromRequest(request, 'access_token', False)
        api = client.InstagramAPI(access_token=access_token)
        # TODO count from query param
        media = api.user_media_feed(count=4)

        print access_token

        collection = []

        try:
            for lst in media:
                if lst:
                    for medium in lst:
                        # TODO WTF is going on here, why would there by some strings spread over an array in this lst?
                        # print type(medium)
                        if (medium and type(medium) is models.Media):
                            print "MEDIUM", medium

                            print dir(medium)

                            # if medium.location:
                            # print "LOCATION", medium.location
                            # else:
                            # print "LOCATION none"
                            dict = {
                                'instagram_id': medium.id,
                                'type': medium.type,
                                'image': medium.get_standard_resolution_url(),
                                'likes': medium.like_count,
                                'comments_count': medium.comment_count,
                                'api_calls_remaining': api.x_ratelimit_remaining,
                                'user': medium.user.username,
                                'user_profile': medium.user.profile_picture,
                                'created_time': time.asctime(medium.created_time.timetuple()),
                                # 'location': medium.location
                            }
                            collection.append(dict)
        except Exception as e:
            print(e)
            # return e

        return json.dumps(collection)
    except Exception as e:
        print e
        return "api/user/network/feed returned error"


# just a test route to see how much photos have venue info
# TODO WIP
@route('/api/popular')
def popular():
    access_token = fromRequest(request, 'access_token', False)
    api = client.InstagramAPI(access_token=access_token)
    # TODO count from query param
    # media = api.user_media_feed(count=4)

    c = 10
    withlocation = 0
    withoutlocation = 0
    media = api.media_popular(count=c)

    print access_token
    print media

    collection = []

    try:
        for medium in media:
            if medium:
                # print "lst", lst
                # for medium in lst:
                # TODO WTF is going on here, why would there by some strings spread over an array in this lst?
                print type(medium)
                print medium.id, medium.type

                if hasattr(medium, "location"):
                    print "LOCATION", medium.location
                    withlocation += 1

                    print medium.location.point.latitude

                    print medium.location.id
                    print medium.location.name

                    fs = foursquare.Foursquare(client_id=config.FOURSQURE_CLIENT_ID,
                                               client_secret=config.FOURSQURE_CLIENT_SECRET)
                    params = {
                        'query': medium.location.name,
                        'll': str(medium.location.point.latitude) + "," + str(medium.location.point.longitude)
                    }

                    results = fs.venues.search(params=params)

                    print "RESULTS", results


                    # location = venues_get_id(medium.location.id)
                    dict = {
                        'type': medium.type,
                        'id': medium.id
                    }
                    collection.append(dict)

                else:
                    print "NO LOCATION"
                    withoutlocation += 1


                    # if (medium and type(medium) is models.Media):
                    # print "MEDIUM", medium
                    # dict = {
                    # 'instagram_id': medium.id,
                    # 'type': medium.type,
                    # }
                    # collection.append(dict)

        print withlocation, c, withlocation / c, float(float(withlocation) / float(c))
        perc = float(float(withlocation) / float(c)) * 100
        print c, withlocation, perc

        return json.dumps(collection)
    except Exception as e:
        print e

    return False


@route('/')
def home():
    return '<a href="http://koala-prototype.meteor.com">prototype frontend moved, click me :)</a>'


from PIL import Image
import urllib, cStringIO

R_OLD, G_OLD, B_OLD = (255, 255, 255)
R_NEW, G_NEW, B_NEW = (0, 174, 239)


# https://ss3.4sqi.net/img/categories_v2/food/mediterranean_32.png
@app.route('/file/icon/<color>/<filename:path>')
def serve_img(color, filename):
    f = urllib.unquote_plus(filename)
    name = f.rsplit('/', 1)

    # TODO check that those color values are valid rgb values; default to something
    cols = color.split(",")

    file = cStringIO.StringIO(urllib.urlopen(f).read())
    im = Image.open(file)
    pixels = im.load()

    width, height = im.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if (r, g, b) == (R_OLD, G_OLD, B_OLD):
                pixels[x, y] = (int(cols[0]), int(cols[1]), int(cols[2]), a)

    # TODO save icon per color in name
    im.save("icons/" + name[1])
    return static_file(name[1], root='icons', mimetype='image/png')

