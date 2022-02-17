import datetime
import logging

# TODO this needs to be adopted to read the list of dates from the place configuration has saved it

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_ICON, TIME_DAYS
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle


ATTR_NEXT = "next"
ATTR_ADAPTIVE_NEXT = "adaptive_next"
DEFAULT_NAME = "Date List Countdown"
DEFAULT_ICON = "mdi:calendar"
CONF_FILE_NAME = "file_name"

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(hours=1)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_FILE_NAME): cv.isfile,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up date list countdown sensor."""
    sensor_name = config.get(CONF_NAME)
    file_name = config.get(CONF_FILE_NAME)
    icon = config.get(CONF_ICON)
    add_devices([DateListCountdown(sensor_name, file_name, icon)])



class DateListCountdown(Entity):
    """Implementation of the date list countdown sensor."""

    def __init__(self, sensor_name, file_name, icon):
        """Initialize the sensor."""
        self._name = sensor_name
        self._file_name = file_name
        self._icon = icon
        self._state = None
        self._data = {}
        self.update()

    @property
    def name(self):
        """Return name of sensor."""
        return self._name

    @property
    def icon(self):
        """Return icon of sensor."""
        return self._icon

    @property
    def state(self):
        """Return state of sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return state of sensor."""
        return TIME_DAYS

    @property
    def extra_state_attributes(self):
        return {
            ATTR_NEXT: self._data.get("next"),
            ATTR_ADAPTIVE_NEXT: self._data.get("adaptive_next")
        }

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Find next date and calculate difference in days"""

        _LOGGER.info("begin update()")
        allDates = []

        # Liste einlesen
        with open(self._file_name) as f:
            for line in f:
                try:
                    l = line.strip()
                    if not l:
                        continue
                    _LOGGER.info("read line: " + l)
                    d = datetime.datetime.strptime(l, "%Y-%m-%d")
                    _LOGGER.info("converted to datetime: " + str(d))
                    allDates.append(d)
                except Exception as e:
                    _LOGGER.warning("Unable to convert date: '" + line + "'")
                    _LOGGER.warning(e)

        # return when list empty
        if not allDates:
            self._state = None
            _LOGGER.error("no valid dates found")
            return

        # sortieren
        allDates.sort()

        # nächstes Datum raussuchen
        dt = datetime.datetime.now()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        currentNext = None
        adaptiveNext = None

        i = 0
        for i in range(len(allDates)):
            date = allDates[i]
            if date < today:
                continue
            if date == today:
                currentNext = date
                if i + 1 < len(allDates):
                    adaptiveNext = allDates[i+1]
                break
            if date > today:
                currentNext = date
                adaptiveNext = date
                break

        self._state = -1
        self._data["next"] = None
        self._data["adaptive_next"] = None

        if(currentNext == None):
            return

        delta = currentNext - today
        self._state = delta.days
        self._data["next"] = datetime.date(currentNext.year, currentNext.month, currentNext.day).isoformat()
        if adaptiveNext != None:
            self._data["adaptive_next"] = datetime.date(adaptiveNext.year, adaptiveNext.month, adaptiveNext.day).isoformat()
        _LOGGER.info("end update()")

