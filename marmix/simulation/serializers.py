# -*- coding: UTF-8 -*-
# serializers.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of MarMix.
#
# MarMix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MarMix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MarMix. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports

# Core Django imports
from django.forms import widgets

# Third-party app imports
from rest_framework import serializers

# MarMix imports
from .models import Simulation, Currency


class SimulationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    #currency = serializers.ReadOnlyField(source='currency.code')

    class Meta:
        model = Simulation
        fields = ('id', 'code', 'customer', 'user', 'simulation_type', 'teams', 'capital', 'currency', 'state')


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code', 'symbol')
