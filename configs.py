from datetime import timedelta
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
JSON_AS_ASCII = False ##編碼不使用ASCII
# DEBUG = True
SECRET_KEY = b'\x00I<\xa4Vn1\xf7\xc5\xfb\xed\xcc"+\xce\xdc'
PERMANENT_SESSION_LIFETIME = timedelta(days=31)
SESSION_USE_SIGNER = True
SESSION_COOKIE_NAME = "session"
APISPEC_SPEC = APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    )
APISPEC_SWAGGER_URL = '/swagger/'  # URI to access API Doc JSON
APISPEC_SWAGGER_UI_URL = '/swagger-ui/'  # URI to access UI of API Doc