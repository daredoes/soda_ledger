from darecms.common import *

from ._version import __version__
from .config import *
from .models import *
from .model_checks import *

static_overrides(join(config['module_root'], 'static'))
template_overrides(join(config['module_root'], 'templates'))
mount_site_sections(config['module_root'])

admin_menu = MenuItem(name='Soda', access=[c.SODA, c.SODA_ADMIN], submenu=[
    MenuItem(name='Buy',  href='{{ c.PATH }}/soda'),
    MenuItem(name='Manage Soda', access=[c.SODA_ADMIN],  href='{{ c.PATH }}/soda_admin/add_soda'),
    MenuItem(name='Manage Users', href='{{ c.PATH }}/soda_admin/users'),

])

c.MENU.append_menu_item(admin_menu)
