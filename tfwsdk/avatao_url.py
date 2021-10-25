import os
import json

def avatao_url_for_port(port):

    port = str(port)
    
    if not ("AVATAO_PROXY_INGRESS_HOST" in os.environ or "AVATAO_PROXY_SERVICES" in os.environ):
        url = f"http://localhost:{ port }/"
        return url

    challenge_host = os.environ["AVATAO_PROXY_INGRESS_HOST"]
    proxy_services = json.loads(os.environ["AVATAO_PROXY_SERVICES"])

    target_proxy_id = ""
    for proxy_id, service in proxy_services.items():
        if service.split("/")[0] == port:
            target_proxy_id = proxy_id

    url = f"https://{ target_proxy_id }.{ challenge_host }/"
    return url