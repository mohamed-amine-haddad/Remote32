from sqlmodel import Session

try:
    from backend.services.config_loader import SessionConfig
    from backend.services.session.session import get_active_by_board, get_reserved_by_board
except ImportError:
    from services.config_loader import SessionConfig
    from services.session.session import get_active_by_board, get_reserved_by_board


def get_all(configs: dict[str, SessionConfig]) -> list[tuple[str, SessionConfig]]:
    """Returns (json_path, config) pairs for all application configs (configs with control boards)."""
    return [(path, cfg) for path, cfg in configs.items() if cfg.is_application]


def get_by_path(configs: dict[str, SessionConfig], json_path: str) -> SessionConfig:
    """Raises RuntimeError if no application config matches the given json_path."""
    config = configs.get(json_path)
    if config is None:
        raise RuntimeError(f"Config '{json_path}' not found")
    return config
