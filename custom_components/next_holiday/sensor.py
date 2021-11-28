"""Finds the next holiday.

May be useful for e.g. controlling programmable holiday lights or
changing music, etc."""
from __future__ import annotations

import datetime

import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
)

import holidays


CONF_SOURCES = "sources"
CONF_COUNTRY = "country"
CONF_STATE = "state"
CONF_PROVINCE = "province"
CONF_OBSERVED = "observed"
CONF_MULTIDAY = "multiday"
CONF_FILTER = "filter"

ICON = "mdi:sun"

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=1)


ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_COUNTRY): cv.string,
        vol.Optional(CONF_STATE, default=None): vol.Any(None, cv.string),
        vol.Optional(CONF_PROVINCE, default=None): vol.Any(None, cv.string),
        vol.Optional(CONF_OBSERVED, default=True): cv.boolean,
        vol.Optional(CONF_MULTIDAY, default=True): cv.boolean,
        vol.Optional(CONF_FILTER, default=[""]): vol.All(
            cv.ensure_list, [cv.string]
        )
    }
)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
  {
      vol.Required(CONF_SOURCES): vol.All(
          cv.ensure_list, [ENTRY_SCHEMA]
      )
  }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([NextHolidaySensor(config)])


class NextHolidaySensor(SensorEntity):
    """Sensor that finds the next holiday"""

    def __init__(self, config):
        """Initialize the sensor."""
        self._state = None
        self._holidays = dict()
        self._config = config

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Next Holiday'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Update the next holiday based on current date."""
        today = datetime.date.today()
        self._state, self._holidays = _find_next_holiday(today, self._config)

    @property
    def extra_state_attributes(self):
        return self._holidays


def _find_next_holiday(today: datetime.date, config: dict) -> str:
    """Find the next holiday"""
    options = _load_holidays(today.year, config)
    for holiday_date, holiday_name in sorted(options.items()):
        if holiday_date >= today:
            next_holiday = holiday_name
            break
    else:
        next_holiday = "none"

    attrs = {str(dt):val for dt, val in sorted(options.items())}

    return next_holiday, attrs

def _load_holidays(year, config):
    """Load holiday data based on config and year.

    We re-instantiate this at each update so it keeps working as
    the years change."""

    options = holidays.HolidayBase()
    for entry in config.get(CONF_SOURCES):
        candidates = holidays.CountryHoliday(
            country=entry.get(CONF_COUNTRY),
            state=entry.get(CONF_STATE),
            prov=entry.get(CONF_PROVINCE),
            observed=entry.get(CONF_OBSERVED),
            years=year
        )
        for query in entry.get(CONF_FILTER):
            # allow text filter (default to add all)
            for date in sorted(candidates.get_named(query)):
                holiday_name = candidates[date]
                if entry.get(CONF_MULTIDAY) or (holiday_name not in options.values()):
                    options[date] = holiday_name

    return options





