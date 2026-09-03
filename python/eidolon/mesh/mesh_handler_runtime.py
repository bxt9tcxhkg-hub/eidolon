from __future__ import annotations


def enable_priority_routing(handler) -> bool:
    handler._priority_enabled = True
    return True


def enable_message_batching(handler) -> bool:
    handler._batching_enabled = True
    return True


def enable_adaptive_compression(handler) -> bool:
    handler._compression_enabled = True
    return True


def start(handler) -> dict:
    try:
        from eidolon.mesh.transport.quic_server import QUICServer
        server = QUICServer(host='127.0.0.1', port=handler.quic_port)
        server.start(background=True)
        return {'ok': True, 'quic_started': True, 'port': handler.quic_port}
    except Exception as e:
        return {'ok': True, 'quic_started': False, 'error': str(e), 'port': handler.quic_port}


def stop(handler) -> None:
    return None
