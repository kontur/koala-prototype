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


@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']


def process_tag_update(update):
    print(update)


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')


def search_location(place):
    fs = foursquare.Foursquare(client_id=FOURSQURE_CLIENT_ID, client_secret=FOURSQURE_CLIENT_SECRET)
    results = fs.venues.search(params={'near': place})
    return results


reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)


@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["likes", "comments"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)


def get_page():
    return template('index')


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


@route('/recent')
def on_recent():
    content = "<h2>User Recent Media</h2>"
    access_token = request.session['access_token']
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.user_recent_media()
        photos = []
        for media in recent_media:
            photos.append('<div style="float:left;">')
            if (media.type == 'video'):
                photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (
                media.get_standard_resolution_url()))
            else:
                photos.append('<img src="%s"/>' % (media.get_low_resolution_url()))
            print(media)
            photos.append(
                "<br/> <a href='/media_like/%s'>Like</a>  <a href='/media_unlike/%s'>Un-Like</a>  LikesCount=%s</div>" % (
                media.id, media.id, media.like_count))
        content += ''.join(photos)
    except Exception as e:
        print(e)
    content += access_token
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/media_like/<id>')
def media_like(id):
    access_token = request.session['access_token']
    api = client.InstagramAPI(access_token=access_token)
    api.like_media(media_id=id)
    redirect("/recent")


@route('/media_unlike/<id>')
def media_unlike(id):
    access_token = request.session['access_token']
    api = client.InstagramAPI(access_token=access_token)
    api.unlike_media(media_id=id)
    redirect("/recent")


@route('/user_media_feed')
def on_user_media_feed():
    access_token = request.session['access_token']
    content = "<h2>User Media Feed</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        media_feed, next = api.user_media_feed()
        photos = []
        for media in media_feed:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
        counter = 1
        while next and counter < 3:
            media_feed, next = api.user_media_feed(with_next_url=next)
            for media in media_feed:
                photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
            counter += 1
        content += ''.join(photos)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


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


@route('/media_popular')
def media_popular():
    access_token = request.session['access_token']
    content = "<h2>Popular Media</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        media_search = api.media_popular()
        photos = []
        for media in media_search:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())
        content += ''.join(photos)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/user_search')
def user_search():
    access_token = request.session['access_token']
    content = "<h2>User Search</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        user_search = api.user_search(q="Instagram")
        users = []
        for user in user_search:
            users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))
        content += ''.join(users)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/user_follows')
def user_follows():
    access_token = request.session['access_token']
    content = "<h2>User Follows</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        # 25025320 is http://instagram.com/instagram
        user_follows, next = api.user_follows('25025320')
        users = []
        for user in user_follows:
            users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))
        while next:
            user_follows, next = api.user_follows(with_next_url=next)
            for user in user_follows:
                users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))
        content += ''.join(users)
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
        dict = { "id": place["id"] }
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


@route('/tag_search')
def tag_search():
    access_token = request.session['access_token']
    content = "<h2>Tag Search</h2>"
    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        tag_search, next_tag = api.tag_search(q="catband")
        tag_recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name)
        photos = []
        for tag_media in tag_recent_media:
            photos.append('<img src="%s"/>' % tag_media.get_standard_resolution_url())
        content += ''.join(photos)
    except Exception as e:
        print(e)
    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_page(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
    mode = request.GET.get("hub.mode")
    challenge = request.GET.get("hub.challenge")
    verify_token = request.GET.get("hub.verify_token")
    if challenge:
        return challenge
    else:
        x_hub_signature = request.header.get('X-Hub-Signature')
        raw_response = request.body.read()
        try:
            reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            print("Signature mismatch")


bottle.run(app=app, host='localhost', port=8515, reloader=True)