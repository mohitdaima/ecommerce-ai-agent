"""Marketplace connectors (extension point).

The core team works fully offline and free. When you're ready to connect a real
marketplace, implement a subclass of `ChannelConnector` here using that
marketplace's official API (most are free to obtain with your own account).
"""

from channels.base import DryRunConnector


def get_connectors(config: dict) -> dict:
    """Return one connector per configured marketplace.

    Today every channel uses the safe DryRunConnector (it prepares the publish
    package without touching a real marketplace). When you build a real
    connector (e.g. AmazonConnector), map it here and it becomes live.
    """
    channels = config.get("business", {}).get("channels", [])
    return {ch: DryRunConnector(ch) for ch in channels}

