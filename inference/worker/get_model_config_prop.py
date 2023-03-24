import sys

from oasst_shared import model_configs
from settings import settings

if __name__ == "__main__":
    model_config = model_configs.MODEL_CONFIGS.get(settings.model_config_name)
    if model_config is None:
        print(f"Unknown model config name: {settings.model_config_name}")
        sys.exit(2)
    if len(sys.argv) != 2:
        print("Usage: get_model_config_prop.py <property>")
        sys.exit(2)
    prop = sys.argv[1]
    if not hasattr(model_config, prop):
        print(f"Unknown property: {prop}")
        sys.exit(2)
    val = getattr(model_config, prop)
    if isinstance(val, bool):
        val = str(val).lower()
    print(val, end="")
