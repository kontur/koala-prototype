# copy this as config.py and insert correct values

# middleware session config
SESSION_OPTIONS = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

# instagram api client configuration
INSTAGRAM = {
    'client_id': '',
    'client_secret': '',
    'redirect_uri': ''
}

# foursquare api client config
FOURSQURE_CLIENT_ID = ''
FOURSQURE_CLIENT_SECRET = ''

# foursquare categories config
CATEGORY_NIGHTLIFE = 'nightlife'
CATEGORY_FOOD = 'food'
CATEGORY_CAFE = 'cafes'
CATEGORY_HOTEL = 'hotels'

CATEGORIES = {
    CATEGORY_NIGHTLIFE: ['4d4b7105d754a06376d81259'],
    CATEGORY_FOOD: ['4d4b7105d754a06374d81259'],
    CATEGORY_CAFE: ['4bf58dd8d48988d16d941735'],
    CATEGORY_HOTEL: ['4bf58dd8d48988d1fa931735']
}