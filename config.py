class Default:
    DEBUG=False
    VERSION=1
    USE_THIRD_PARTY_CDN=False

class Development:
    DEBUG=True

class Production:
    USE_THIRD_PARTY_CDN=True
    VERSION="2014-08-03"
