"""Support for Airbnk locks, treated as covers."""
import logging

from homeassistant.components.lock import LockEntity

from .const import (
    DOMAIN as AIRBNK_DOMAIN,
    AIRBNK_DEVICES,
    LOCK_STATE_LOCKED,
    LOCK_STATE_UNLOCKED,
    LOCK_STATE_JAMMED,
    LOCK_STATE_OPERATING,
    LOCK_STATE_FAILED,
)

_LOGGER = logging.getLogger(__name__)

LOCK_STATE_ICONS = {
    LOCK_STATE_LOCKED: "hass:door-closed-lock",
    LOCK_STATE_UNLOCKED: "hass:door-closed",
    LOCK_STATE_JAMMED: "hass:lock-question",
    LOCK_STATE_OPERATING: "hass:lock-reset",
    LOCK_STATE_FAILED: "hass:lock-alert",
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up the platform.

    Can only be called when a user accidentally mentions the platform in their
    config. But even in that case it would have been ignored.
    """


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Airbnk covers based on config_entry."""
    locks = []
    for dev_id, device in hass.data[AIRBNK_DOMAIN][AIRBNK_DEVICES].items():
        lock = AirbnkLock(device, dev_id)
        locks.append(lock)
    async_add_entities(locks)


class AirbnkLock(LockEntity):
    """Representation of a lock."""

    def __init__(self, device, lock_id: str):
        """Initialize the zone."""
        self._device = device
        self._lock_id = lock_id
        deviceName = self._device._lockConfig["deviceName"]
        self._name = f"{deviceName}"

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    @property
    def available(self):
        """Return if entity is available or not."""
        return self._device.is_available

#    @property
#    def supported_features(self):
#        """Flag supported features."""
#        supported_features = SUPPORT_OPEN
#        return supported_features

    @property
    def unique_id(self):
        """Return a unique ID."""
        devID = self._device._lockConfig["sn"]
        return f"{devID}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return LOCK_STATE_ICONS[self._device.curr_state]

    @property
    def name(self):
        """Return the name of the lock."""
        return self._name

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.device_info

    @property
    def is_unlocking(self):
        """Return if lock is opening."""
        return False

    @property
    def is_locking(self):
        """Return if lock is closing."""
        return False

    @property
    def is_jammed(self):
        """Return if the lock is jammed or not."""
        if self._device.curr_state == LOCK_STATE_JAMMED:
            return True
        else:
            return False

    @property
    def is_locked(self):
        """Return if the lock is locked or not."""
        if self._device.curr_state == LOCK_STATE_LOCKED:
            return True
        else:
            return False

    async def async_unlock(self, **kwargs):
        """Open the lock."""
        if self._device.curr_state == LOCK_STATE_OPERATING:
            _LOGGER.warning("Operation already in progress: please wait")
            raise Exception("Operation already in progress: please wait")
            return

        _LOGGER.debug("Launching command to unlock")
        await self._device.operateLock(1)

    async def async_lock(self, **kwargs):
        """Close the lock."""
        if self._device.curr_state == LOCK_STATE_OPERATING:
            _LOGGER.warning("Operation already in progress: please wait")
            raise Exception("Operation already in progress: please wait")
            return

        _LOGGER.debug("Launching command to lock")
        await self._device.operateLock(2)

    async def async_update(self):
        """Retrieve latest state."""
        # _LOGGER.debug("async_update")