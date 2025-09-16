from aiohttp import web
import asyncio

async def home(request):
    return web.Response(text="Hello. I am alive!")

async def start_server():
    app = web.Application()
    app.add_routes([web.get('/', home)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    return loop