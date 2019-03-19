import asyncio, mimetypes

async def web_interface(self, request):
    path = request.path
    if path == '/admin':
        main_html = open("admin/source/html/main.html","rb").read()

        part_header = open("admin/source/html/parts/header.html","rb").read()
        part_main = open("admin/source/html/parts/main.html","rb").read()
        part_footer = open("admin/source/html/parts/footer.html","rb").read()
        part_modals = open("admin/source/html/parts/modals.html","rb").read()

        finished_html = html_format(
            main_html,
            header=part_header,
            main=part_main,
            footer=part_footer,
            modals=part_modals
        )

        return self.response(status=200, body=main_html, headers={'Content-Type': 'text/html'} )

    else:
        path = path.replace("..", "")
        path = path.strip('/')

        try:
            r = open(path, "rb").read()
            return self.response(status=200, body=r, headers={'Content-Type': mimetypes.guess_type(path)[0]})

        except:
            return self.response(status=404)

def html_format (raw, **kwargs):
    for key in kwargs:
        raw = raw.replace(f"|>>>({key})<<<|", kwargs[key])
    return raw
