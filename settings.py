from appdirs import user_data_dir
from strings import APP_AUTHOR_DIR, APP_NAME_DIR
import os


class SettingsError(Exception):
    pass


class Site:
    def __init__(self, url, key):
        self.url = url.lower()
        self.key = key


class Settings:

    def __init__(self):
        self._sites = []
        pass

    @staticmethod
    def file_path(filename):
        user_dir = user_data_dir(appname=APP_NAME_DIR, appauthor=APP_AUTHOR_DIR)
        if not (os.path.exists(user_dir) and os.path.isdir(user_dir)):
            os.makedirs(user_dir)
        return os.path.join(user_dir, filename)

    def load_from_file(self, filename="config.yaml"):
        from yaml import load
        from codecs import open

        full_file_path = Settings.file_path(filename)

        try:
            with open(full_file_path, mode='rb', encoding='utf-8') as f:
                loaded_settings = load(f)
                for loaded_site in loaded_settings['sites']:
                    try:
                        self._sites.append(Site(loaded_site['url'], loaded_site['master_key']))
                    except KeyError:
                        pass
        except KeyError:
            raise SettingsError("This settings file is missing a 'sites' parameter!")
        except TypeError:
            raise SettingsError("This settings file is badly formatted!")
        except IOError:
            open(full_file_path, mode='wb+', encoding='utf-8').close()

    def write_to_file(self, filename="config.yaml"):
        from yaml import dump
        from codecs import open

        full_file_path = Settings.file_path(filename)

        print "WRITE TO FILE!!!!!!"
        settings_dict = {'sites': [{'url': s.url, 'master_key': s.key} for s in self._sites]}
        with open(full_file_path, mode='wb+', encoding='utf-8') as f:
            dump(settings_dict, stream=f, default_flow_style=False)

    def add_site(self, site):
        if not (site.url.startswith('http://') or site.url.startswith('https://')):
            raise SettingsError("URLs must start with http:// or https://")
        self._sites.append(site)

    def remove_site(self, site):
        self._sites = [s for s in self._sites if (s.url != site.url or s.key != site.key)]

    def get_sites(self):
        return sorted(self._sites, key=lambda x: x.url)

site_settings = Settings()

try:
    site_settings.load_from_file()
except SettingsError:
    pass
