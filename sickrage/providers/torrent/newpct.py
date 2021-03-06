# Author: CristianBB
# Greetings to Mr. Pine-apple
#
# URL: http://github.com/SiCKRAGETV/SickRage/
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
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import traceback
from urllib import urlencode

import sickrage
from sickrage.core.caches.tv_cache import TVCache
from sickrage.core.helpers import bs4_parser, convert_size
from sickrage.providers import TorrentProvider


class newpctProvider(TorrentProvider):
    def __init__(self):
        super(newpctProvider, self).__init__("Newpct",'www.newpct.com', False)

        self.supports_backlog = True
        self.onlyspasearch = None

        self.cache = TVCache(self, min_time=20)

        self.urls.update({
            'search': '{base_url}/buscar-descargas/'.format(base_url=self.urls['base_url'])
        })

    def search(self, search_strings, search_mode='eponly', epcount=0, age=0, epObj=None):
        results = []

        search_params = {
            'cID': 0,
            'tLang': 0,
            'oBy': 0,
            'oMode': 0,
            'category_': 767,
            'subcategory_': 'All',
            'idioma_': 1,
            'calidad_': 'All',
            'oByAux': 0,
            'oModeAux': 0,
            'size_': 0,
            'btnb': 'Filtrar+Busqueda',
            'q': ''
        }

        items = {'Season': [], 'Episode': [], 'RSS': []}

        lang_info = '' if not epObj or not epObj.show else epObj.show.lang

        # Only search if user conditions are true
        if self.onlyspasearch and lang_info != 'es':
            sickrage.srCore.srLogger.debug("Show info is not spanish, skipping provider search")
            return results

        for mode in search_strings.keys():
            sickrage.srCore.srLogger.debug("Search Mode: %s" % mode)

            for search_string in search_strings[mode]:
                search_params.update({'q': search_string.strip()})

                sickrage.srCore.srLogger.debug(
                        "Search URL: %s" % self.urls['search'] + '?' + urlencode(search_params))

                try:
                    data = sickrage.srCore.srWebSession.post(self.urls['search'], data=search_params, timeout=30).text
                except Exception:
                    continue

                try:
                    with bs4_parser(data) as html:
                        torrent_tbody = html.find('tbody')

                        if len(torrent_tbody) < 1:
                            sickrage.srCore.srLogger.debug("Data returned from provider does not contain any torrents")
                            continue

                        torrent_table = torrent_tbody.findAll('tr')
                        num_results = len(torrent_table) - 1

                        iteration = 0
                        for row in torrent_table:
                            try:
                                if iteration < num_results:
                                    torrent_size = row.findAll('td')[2]
                                    torrent_row = row.findAll('a')[1]

                                    download_url = torrent_row.get('href')
                                    title_raw = torrent_row.get('title')
                                    size = convert_size(torrent_size.text)

                                    title = self._processTitle(title_raw)

                                    item = title, download_url, size
                                    sickrage.srCore.srLogger.debug("Found result: %s " % title)

                                    items[mode].append(item)
                                    iteration += 1

                            except (AttributeError, TypeError):
                                continue

                except Exception:
                    sickrage.srCore.srLogger.warning("Failed parsing provider. Traceback: %s" % traceback.format_exc())

            results += items[mode]

        return results

    @staticmethod
    def _processTitle(title):

        title = title.replace('Descargar ', '')

        # Quality
        title = title.replace('[HDTV]', '[720p HDTV x264]')
        title = title.replace('[HDTV 720p AC3 5.1]', '[720p HDTV x264]')
        title = title.replace('[HDTV 1080p AC3 5.1]', '[1080p HDTV x264]')
        title = title.replace('[DVDRIP]', '[DVDrip x264]')
        title = title.replace('[DVD Rip]', '[DVDrip x264]')
        title = title.replace('[DVDrip]', '[DVDrip x264]')
        title = title.replace('[DVDRIP-AC3.5.1]', '[DVDrip x264]')
        title = title.replace('[BLuRayRip]', '[720p BlueRay x264]')
        title = title.replace('[BRrip]', '[720p BlueRay x264]')
        title = title.replace('[BDrip]', '[720p BlueRay x264]')
        title = title.replace('[BluRay Rip]', '[720p BlueRay x264]')
        title = title.replace('[BluRay 720p]', '[720p BlueRay x264]')
        title = title.replace('[BluRay 1080p]', '[1080p BlueRay x264]')
        title = title.replace('[BluRay MicroHD]', '[1080p BlueRay x264]')
        title = title.replace('[MicroHD 1080p]', '[1080p BlueRay x264]')

        return title
