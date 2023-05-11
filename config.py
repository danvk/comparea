class Default:
    DEBUG=False
    USE_THIRD_PARTY_CDN=False
    PORT = 5050  # port 5000 conflicts with AirPlay Receiver

class Development:
    DEBUG=True

class Testing:
    TESTING = True
    PORT = 5001  # avoid conflicts with a running dev server

class Production:
    USE_THIRD_PARTY_CDN=True
