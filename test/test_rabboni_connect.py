import pytest

from unittest.mock import patch, AsyncMock
from rabboni_multi_python_sdk import Rabboni, DeviceNotFoundError


@pytest.mark.asyncio
async def test_connect_with_provided_mac():
    with patch("rabboni_multi_python_sdk.BleakClient") as MockClient:
        # 創建一個模擬的 BleakClient 連接成功的情況
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect = AsyncMock(return_value=True)

        rabo = Rabboni(mode="BLE")
        await rabo.connect(mac_address="00:00:00:00:00:00")

        mock_client_instance.connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_with_discovery():
    with patch(
        "rabboni_multi_python_sdk.BleakScanner.discover",
        AsyncMock(return_value=[{"name": "Rabboni", "address": "00:00:00:00:00:01"}]),
    ), patch("rabboni_multi_python_sdk.BleakClient") as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect = AsyncMock(return_value=True)

        rabo = Rabboni(mode="BLE")
        await rabo.connect()

        mock_client_instance.connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_device_not_found():
    with patch(
        "rabboni_multi_python_sdk.BleakScanner.discover", AsyncMock(return_value=[])
    ):
        rabo = Rabboni(mode="BLE")
        with pytest.raises(DeviceNotFoundError):
            await rabo.connect()
