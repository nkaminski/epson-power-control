import aiofiles
import aiohttp
import asyncio
import click
import yaml
import epson_projector as epson
from functools import wraps

def coroutine(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@click.command()
@click.option('--config', default='epsonctl-config.yaml')
@click.option('--power-state', required=True, type=str)
@coroutine
async def cli(config, power_state):
    # Read config
    async with aiofiles.open(config, mode='r') as f:
        raw_cfg = await f.read()
    cfg = yaml.safe_load(raw_cfg)

    # Determine command
    if 'on' in power_state.lower():
        state = epson.const.PWR_ON
    elif 'off' in power_state.lower():
        state = epson.const.PWR_OFF
    else:
        raise click.BadParameter("Unexpected power state command")

    # Instantiate a basic auth object if needed
    auth = None
    if ('username' in cfg) and ('password' in cfg):
        auth = aiohttp.BasicAuth(cfg['username'], cfg['password'])

    # Create a ClientSession with the auth
    async with aiohttp.ClientSession(auth=auth) as session:
        projector = epson.Projector(host=cfg['hostname'], websession=session)
        await projector.send_command(state)


if __name__ == '__main__':
    cli()
