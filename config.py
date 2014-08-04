class Default:
    DEBUG=False
    USE_THIRD_PARTY_CDN=False
    PORT = None  # default

class Development:
    DEBUG=True

class Testing:
    TESTING = True
    PORT = 5001  # avoid conflicts with a running dev server

class Production:
    USE_THIRD_PARTY_CDN=True
