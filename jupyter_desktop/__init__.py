import os
import shlex
import tempfile
from jupyterhub.utils import random_port

HERE = os.path.dirname(os.path.abspath(__file__))

# import some enironment variables 
HOME = os.environ.get('HOME')

# pull in Davidson's JupyterHub environment variables 
HUB_PATH = os.environ.get('HUB_PATH', '')
HUB_PRIVATE = os.environ.get('HUB_PRIVATE', '')

def setup_desktop():
    # make a secure temporary directory for sockets
    # This is only readable, writeable & searchable by our uid

    # XXX: the following need to be node-local
    sockets_dir = tempfile.mkdtemp() 
    sockets_path = os.path.join(sockets_dir, 'vnc-socket')

    vnc_command = ' '.join((shlex.quote(p) for p in [
        os.path.join(HERE, 'share/tigervnc/bin/vncserver'),
        '-verbose',
        '-xstartup', os.path.join(HUB_PRIVATE, 'xstartup'),
        '-geometry', '1280x1024',
        '-SecurityTypes', 'None',
        '-rfbunixpath', sockets_path,
        '-fg',
        '-auth', os.path.join(HOME,'.Xauthority'),
        '-nolisten', 'tcp',
        # XXX: quick hack to enable multi. users
        ':'+str(min([ii for ii in range(1,7) \
                     if not os.path.exists(f'/tmp/.X11-unix/X{ii}')])),
    ]))
    port = random_port()
    return {
        'command': [
            'websockify', '-v',
            '--web', os.path.join(HERE, 'share/web/noVNC-1.1.0'),
            '--heartbeat', '30',
            f'{port}',
            '--unix-target', sockets_path,
            '--',
            '/bin/sh', '-c',
            f'cd {os.getcwd()} && {vnc_command}'
        ],
        'port': port,
        'timeout': 30,
        'mappath': {'/': '/vnc_lite.html'},
        'launcher_entry': { 'enabled': True,
                            'title': 'Desktop' },
    }
