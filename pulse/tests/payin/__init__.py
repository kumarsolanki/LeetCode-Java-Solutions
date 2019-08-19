from payin_client import ApiClient, DefaultApi, Configuration
from ..utils import SERVICE_URI

import os

STAGING_PULSE_API_KEY = os.getenv("API_KEY_PAYMENT_SERVICE", "")

payin_configuration = Configuration(host=SERVICE_URI)
payin_configuration.verify_ssl = False
api_client = ApiClient(configuration=payin_configuration)
api_client.set_default_header("x-api-key", STAGING_PULSE_API_KEY)
payin_client_pulse = DefaultApi(api_client)
