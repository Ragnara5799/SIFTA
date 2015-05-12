# separator used by search.py, categories.py, ...
SEPARATOR = ";"

LANG            = "en_US" # can be en_US, fr_FR, ...
ANDROID_ID      = "394afbc69a7e18f4" # "xxxxxxxxxxxxxxxx"
GOOGLE_LOGIN    = "androidhaxor42@gmail.com" # "username@gmail.com"
GOOGLE_PASSWORD = "niklashaxor42"
AUTH_TOKEN      = None # "yyyyyyyyy"

# force the user to edit this file
if any([each == None for each in [ANDROID_ID, GOOGLE_LOGIN, GOOGLE_PASSWORD]]):
    raise Exception("config.py not updated")