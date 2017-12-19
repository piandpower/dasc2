#!/usr/bin/env python
#
# Copyright 2017 David Kuhta & Anshul Sacheti. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import json
import os
import time

from mpyq import MPQArchive

class SC2ReplayFilter(object):

    def __init__(self, mmr=1000, apm=10, races=['Zerg','Terr','Prot'],
                winning_races=['Zerg','Terr','Prot'],
                game_map=None, data_build=None,
                replays_dir='./replays', filter_dir='./filters',
                name='SC2Filter'):
        self.name = name
        self.mmr_threshold = mmr
        self.apm_threshold = apm
        self.races = races
        self.winning_races = winning_races
        self.map_title = game_map
        self.game_version = int(data_build) if data_build else None
        self.replays_dir = replays_dir
        self.filter_dir = filter_dir

    def _info(self):
        print("\nFiltering for replays for:")
        if self.game_version:
          print("\tGame Build Version:\t"+str(self.game_version))
        if self.map_title:
          print("\tMap:\t\t"+str(self.map_title))
        print("\tMinimum MMR of:\t"+str(self.mmr_threshold))
        print("\tMinimum APM of:\t"+str(self.apm_threshold))
        print("\tRaces:\t\t" + ', '.join(self.races))
        print("\tWinning Races:\t\t" + ', '.join(self.winning_races))
        print('')

    def filter(self, replay):
        archive =  MPQArchive(replay).extract()
        metadata = json.loads(archive[b"replay.gamemetadata.json"].decode("utf-8"))

        replay_game_version = int(metadata['DataBuild'])
        if self.game_version:
            if not self.game_version == replay_game_version:
                return None

        replay_map_title = metadata['Title']
        if self.map_title:
            if not self.map_title == replay_map_title:
                return None

        players = metadata["Players"]
        raceFound = False
        for player in players:
            try:
                if player['APM'] < self.apm_threshold or player['MMR'] < self.mmr_threshold:
                    return None
                player_race = player['AssignedRace']
                if player_race in self.races:
                    raceFound = True
                if player['Result'] == 'Win':
                    if not player_race in self.winning_races:
                        return None

            except KeyError:
                return None

        if not raceFound:
            return None

        return metadata
