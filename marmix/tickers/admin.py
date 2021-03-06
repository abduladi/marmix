# -*- coding: UTF-8 -*-
# admin.py
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
from django.contrib import admin

# Third-party app imports

# MarMix imports
from .models import Ticker, TickerCompany, TickerTick


class TickerAdmin(admin.ModelAdmin):
    pass


class TickerCompanyAdmin(admin.ModelAdmin):
    pass



class TickerTickAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ticker, TickerAdmin)
admin.site.register(TickerCompany, TickerCompanyAdmin)
admin.site.register(TickerTick, TickerTickAdmin)