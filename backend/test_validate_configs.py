"""
Test script for validate_configs.
Run from backend/ folder: python test_validate_configs.py
"""
from sqlmodel import Session
from database import engine
from models import Board
from services.config_loader import load_all_configs, validate_configs, SessionConfig, TargetConfig, PiConfig

# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid():
    configs = load_all_configs()
    with Session(engine) as db:
        try:
            validate_configs(configs, db)
            print("PASS — valid configs accepted")
        except Exception as e:
            print(f"FAIL — {e}")


if __name__ == "__main__":
    print("--- Test 1: valid configs ---")
    test_valid()
