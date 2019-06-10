from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from utils.database import Database as PhaazeDatabase

import asyncio, mimetypes
from aiohttp.web import Request, Response

async def webInterface(cls:"PhaazeDatabase", WebRequest:Request) -> Response:
	path:str = WebRequest.path
	if path == '/admin':
		main_html:str = open("admin/source/html/main.html","rb").read()

		part_header:str = open("admin/source/html/parts/header.html","rb").read()
		part_main:str = open("admin/source/html/parts/main.html","rb").read()
		part_footer:str = open("admin/source/html/parts/footer.html","rb").read()
		part_modals:str = open("admin/source/html/parts/modals.html","rb").read()

		if cls.PhaazeDBS.token == None:
			part_header:str = htmlFormat(
				part_header,
				sys_message_class=b"show red text-white",
				sys_message=b"PhaazeDB running without token, please set one"
			)

		finished_html:str = htmlFormat(
			main_html,
			header=part_header,
			main=part_main,
			footer=part_footer,
			modals=part_modals
		)

		return cls.response(status=200, body=finished_html, headers={'Content-Type': 'text/html'} )

	else:
		path = path.replace("..", "")
		path = path.strip('/')

		try:
			file_content:bytes = open(path, "rb").read()
			return cls.response(status=200, body=file_content, headers={'Content-Type': mimetypes.guess_type(path)[0]})

		except:
			return cls.response(status=404)

def htmlFormat (raw:str, **kwargs:Any) -> str:
	for key in kwargs:
		raw = raw.replace(bytes(f"|>>>({key})<<<|", "UTF-8"), kwargs[key])
	return raw
