from __future__ import annotations
import asyncio
import json
import logging
import socket
from pathlib import Path
from typing import Any
from eidolon.core.config import QUIC_PORT

logger = logging.getLogger("eidolon.mesh.discovery")

class DeviceDiscovery:
    def __init__(self, device_id: str, device_name: str, device_type: str = "host", port: int | None = None, broadcast_port: int = 37891) -> None:
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.port = port if port is not None else QUIC_PORT
        self.broadcast_port = broadcast_port
        self._callbacks: list[Any] = []
        self._running = False
        self._known: dict[str, dict[str, Any]] = {}

    def on_device_found(self, callback: Any) -> None:
        self._callbacks.append(callback)

    async def _notify(self, device: dict[str, Any]) -> None:
        for callback in self._callbacks:
            try:
                await callback(device)
            except Exception as exc:
                logger.error("Discovery callback failed: %s", exc)

    async def _broadcast_loop(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self._running:
            try:
                payload = json.dumps({
                    "device_id": self.device_id,
                    "device_name": self.device_name,
                    "device_type": self.device_type,
                    "port": self.port,
                }).encode("utf-8")
                sock.sendto(payload, ("255.255.255.255", self.broadcast_port))
            except Exception as exc:
                logger.debug("Broadcast error: %s", exc)
            await asyncio.sleep(2)

    async def _listen_loop(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", self.broadcast_port))
        except OSError:
            sock.bind(("", self.broadcast_port))
        sock.setblocking(False)
        loop = asyncio.get_event_loop()
        while self._running:
            try:
                data, addr = await loop.sock_recvfrom(sock, 4096)
                try:
                    payload = json.loads(data.decode("utf-8"))
                except Exception:
                    continue
                if payload.get("device_id") == self.device_id:
                    continue
                device = {
                    "id": payload.get("device_id"),
                    "name": payload.get("device_name"),
                    "type": payload.get("device_type"),
                    "port": payload.get("port"),
                    "address": addr[0],
                    "last_seen": __import__("datetime").datetime.utcnow().isoformat(),
                }
                self._known[device["id"]] = device
                await self._notify(device)
            except Exception as exc:
                logger.debug("Listener error: %s", exc)

    async def start(self) -> None:
        self._running = True
        logger.info("Discovery started for '%s' (%s)", self.device_name, self.device_id)
        asyncio.create_task(self._broadcast_loop())
        asyncio.create_task(self._listen_loop())

    async def stop(self) -> None:
        self._running = False
        logger.info("Discovery stopped")

    @property
    def known_devices(self) -> list[dict[str, Any]]:
        return list(self._known.values())
