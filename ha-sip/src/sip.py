import pjsua2 as pj

from log import log


class MyEndpointConfig(object):
    def __init__(
        self,
        port: int,
        log_level: int,
        name_server: list[str],
        transport: int = pj.PJSIP_TRANSPORT_UNSPECIFIED,
    ) -> None:
        self.port = port
        self.log_level = log_level
        self.name_server = name_server
        self.transport = transport


def resolve_transport(transport: str | int | None = None) -> int:
    # Return transport if a digit is provided
    if isinstance(transport, int):
        return transport

    # Return unspecified transport if none provided
    if transport is None:
        return pj.PJSIP_TRANSPORT_UNSPECIFIED

    # Return unspecified transport if empty provided
    transport = str(transport).strip()
    if not transport:
        return pj.PJSIP_TRANSPORT_UNSPECIFIED

    # Check if provided transport is a string consisting of digits
    if transport.isdigit():
        return int(transport)

    try:
        # Attempt to retrieve constant from library by name
        return getattr(pj, "PJSIP_TRANSPORT_" + transport.upper())
    except AttributeError:
        raise ValueError("invalid transport type provided")


def create_endpoint(config: MyEndpointConfig) -> pj.Endpoint:
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.threadCnt = 0
    ep_cfg.uaConfig.mainThreadOnly = True
    if config.name_server:
        nameserver = pj.StringVector()
        for ns in config.name_server:
            nameserver.append(ns)
        ep_cfg.uaConfig.nameserver = nameserver
    ep_cfg.logConfig.level = config.log_level
    end_point = pj.Endpoint()
    end_point.libCreate()
    end_point.libInit(ep_cfg)
    codecs = end_point.codecEnum2()
    log(None, "Supported audio codecs: %s" % ", ".join(c.codecId for c in codecs))
    end_point.audDevManager().setNullDev()
    sip_tp_config = pj.TransportConfig()
    sip_tp_config.port = config.port
    end_point.transportCreate(config.transport, sip_tp_config)
    end_point.libStart()
    return end_point
