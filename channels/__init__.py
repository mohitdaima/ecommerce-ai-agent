"""Marketplace connectors (extension point).

The core team works fully offline and free. When you're ready to connect a real
marketplace, implement a subclass of `ChannelConnector` here using that
marketplace's official API (most are free to obtain with your own account).
"""

from channels.base import DryRunConnector

# Marketplaces that have no public developer API -> use catalog-file export.
EXPORT_ONLY = {"Myntra", "Meesho", "Ajio"}


def get_connectors(config: dict) -> dict:
    """Return one connector per configured marketplace.

    - Amazon / Flipkart  -> real API connector (falls back to dry-run until you
      add credentials in secrets.yaml)
    - Myntra/Meesho/Ajio -> catalog-export connector (writes a bulk-upload CSV)
    - anything else       -> safe dry-run
    """
    channels = config.get("business", {}).get("channels", [])
    connectors = {}
    for ch in channels:
        if ch == "Amazon":
            from channels.amazon import AmazonConnector
            connectors[ch] = AmazonConnector()
        elif ch == "Flipkart":
            from channels.flipkart import FlipkartConnector
            connectors[ch] = FlipkartConnector()
        elif ch in EXPORT_ONLY:
            from channels.export_connector import CatalogExportConnector
            connectors[ch] = CatalogExportConnector(ch)
        else:
            connectors[ch] = DryRunConnector(ch)
    return connectors

