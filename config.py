
# middleware session config
SESSION_OPTIONS = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

# instagram api client configuration
INSTAGRAM = {
    'client_id': '6175f60283394342b0a720fb596ae0b6',
    'client_secret': '67534712185146dc8ca6bbe94aabff7b',
    'redirect_uri': 'http://localhost:8515/app'
}

# foursquare api client config
FOURSQURE_CLIENT_ID = 'CA1FI3A2KJ3ZDRIUF5DJUZIXXES24XFVICYON34GBBOKBXSB'
FOURSQURE_CLIENT_SECRET = 'FRHDILCEV0Y0E1WR3VWPWT03X0N01AKZU5SJVHK4M0NE2HF0'

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