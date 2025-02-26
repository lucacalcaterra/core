"""Test Gardena Bluetooth sensor."""


from gardena_bluetooth.const import Battery, Valve
import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import setup_entry

from tests.common import MockConfigEntry


@pytest.mark.parametrize(
    ("uuid", "raw", "entity_id"),
    [
        (
            Battery.battery_level.uuid,
            [Battery.battery_level.encode(100), Battery.battery_level.encode(10)],
            "sensor.mock_title_battery",
        ),
        (
            Valve.remaining_open_time.uuid,
            [
                Valve.remaining_open_time.encode(100),
                Valve.remaining_open_time.encode(10),
                Valve.remaining_open_time.encode(0),
            ],
            "sensor.mock_title_valve_closing",
        ),
    ],
)
async def test_setup(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_entry: MockConfigEntry,
    mock_read_char_raw: dict[str, bytes],
    uuid: str,
    raw: list[bytes],
    entity_id: str,
) -> None:
    """Test setup creates expected entities."""

    mock_read_char_raw[uuid] = raw[0]
    coordinator = await setup_entry(hass, mock_entry, [Platform.SENSOR])
    assert hass.states.get(entity_id) == snapshot

    for char_raw in raw[1:]:
        mock_read_char_raw[uuid] = char_raw
        await coordinator.async_refresh()
        assert hass.states.get(entity_id) == snapshot
