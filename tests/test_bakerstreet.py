import requests
import time

def test_resolve_service_with_path(wc_host):
    """Test that Baker Street will route traffic from the name to the proper path while also preserving URL query
    parameters"""

    load_watson_with_config(wc_host, "watson-test_service-path.conf")
    time.sleep(5)
    requests.get("http://localhost:8000/foobar", params=dict(name="Homer")) == "Hi, Homer!"

def test_resolve_service_without_path(wc_host):
    """Test that Baker Street will route traffic properly"""

    load_watson_with_config(wc_host, "watson-test_service-nopath.conf")
    time.sleep(5)
    requests.get("http://localhost:8000/foobar", params=dict(name="Homer")) == "Hi, everybody!"

def load_watson_with_config(wc_host, config_name):
    resp = requests.post("http://%s/watsons" % wc_host, params=dict(config_name=config_name))
