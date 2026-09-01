from typing import List

from dm_control import mjcf
from gello.paths import menagerie_root

# Path to the Menagerie asset checkout.
MENAGERIE_ROOT = menagerie_root()


def safe_find_all(
    root: mjcf.RootElement,
    feature_name: str,
    immediate_children_only: bool = False,
    exclude_attachments: bool = False,
) -> List[mjcf.Element]:
    """Find all given elements or throw an error if none are found."""
    features = root.find_all(feature_name, immediate_children_only, exclude_attachments)
    if not features:
        raise ValueError(f"No {feature_name} found in the MJCF model.")
    return features
