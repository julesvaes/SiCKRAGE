# Author: echel0n <echel0n@sickrage.ca>
# URL: https://sickrage.ca
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import importlib
import os
import re

import sickrage
from sickrage.core.helpers import is_ip_private


class Notifiers(object):
    def __init__(self):
        self.name = "Generic"

        ### Notification Types
        self.NOTIFY_SNATCH = 1
        self.NOTIFY_DOWNLOAD = 2
        self.NOTIFY_SUBTITLE_DOWNLOAD = 3
        self.NOTIFY_GIT_UPDATE = 4
        self.NOTIFY_GIT_UPDATE_TEXT = 5
        self.NOTIFY_LOGIN = 6
        self.NOTIFY_LOGIN_TEXT = 7

        self.notifyStrings = {
            self.NOTIFY_SNATCH: _("Started Download"),
            self.NOTIFY_DOWNLOAD: _("Download Finished"),
            self.NOTIFY_SUBTITLE_DOWNLOAD: _("Subtitle Download Finished"),
            self.NOTIFY_GIT_UPDATE: _("SiCKRAGE Updated"),
            self.NOTIFY_GIT_UPDATE_TEXT: _("SiCKRAGE Updated To Commit#:"),
            self.NOTIFY_LOGIN: _("SiCKRAGE new login"),
            self.NOTIFY_LOGIN_TEXT: _("New login from IP: {0}. http://geomaplookup.net/?ip={0}")
        }

    @property
    def id(self):
        return str(re.sub(r"[^\w\d_]", "_", str(re.sub(r"[+]", "plus", self.name))).lower())

    @staticmethod
    def mass_notify_download(ep_name):
        for n in sickrage.app.notifier_providers.values():
            try:
                n.notify_download(ep_name)
            except Exception:
                continue

    @staticmethod
    def mass_notify_subtitle_download(ep_name, lang):
        for n in sickrage.app.notifier_providers.values():
            try:
                n.notify_subtitle_download(ep_name, lang)
            except Exception:
                continue

    @staticmethod
    def mass_notify_snatch(ep_name):
        for n in sickrage.app.notifier_providers.values():
            try:
                n.notify_snatch(ep_name)
            except Exception:
                continue

    @staticmethod
    def mass_notify_version_update(new_version=""):
        if sickrage.app.config.notify_on_update:
            for n in sickrage.app.notifier_providers.values():
                try:
                    n.notify_version_update(new_version)
                except Exception:
                    continue

    @staticmethod
    def mass_notify_login(ipaddress):
        if sickrage.app.config.notify_on_login and not is_ip_private(ipaddress):
            for n in sickrage.app.notifier_providers.values():
                try:
                    n.notify_login(ipaddress)
                except Exception:
                    continue


class NotifierProviders(dict):
    def __init__(self):
        super(NotifierProviders, self).__init__()

        pregex = re.compile('^(.*)\.py$', re.IGNORECASE)
        names = [pregex.match(m) for m in os.listdir(os.path.dirname(__file__))]

        for name in names:
            try:
                klass = self._get_klass(name.group(1))
                self[klass().id] = klass()
            except:
                continue

    @staticmethod
    def _get_klass(name):
        import inspect

        try:
            return dict(
                inspect.getmembers(
                    importlib.import_module('.{}'.format(name), 'sickrage.notifiers'),
                    predicate=lambda o: inspect.isclass(o) and issubclass(o, Notifiers) and o is not Notifiers)
            ).values()[0]
        except:
            pass