from juntagrico.util import addons


def show_admin_menu(user):
    return user.has_perm('juntagrico_pg.can_sql')


addons.config.register_admin_menu('jpg/menu.html')
addons.config.register_show_admin_menu_method(show_admin_menu)
