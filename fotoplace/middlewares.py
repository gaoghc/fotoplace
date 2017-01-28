from fotoplace import settings

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.HTTP_PROXY

