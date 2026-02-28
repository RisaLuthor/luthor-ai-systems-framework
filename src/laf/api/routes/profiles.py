from pathlib import Path

from fastapi import APIRouter, HTTPException

from laf.governance.profiles import load_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _repo_root() -> Path:
    # repo root is 4 up from src/laf/api/routes/
    return Path(__file__).resolve().parents[4]


@router.get("")
def list_profiles():
    pol_dir = _repo_root() / "policies"
    if not pol_dir.exists():
        return {"profiles": []}

    names = sorted([p.stem for p in pol_dir.glob("*.y*ml")])
    return {"profiles": names}


@router.get("/{name}")
def get_profile(name: str):
    try:
        prof = load_profile(name)
        return {
            "name": prof.name,
            "version": prof.version,
            "description": prof.description,
            "rules": prof.rules,
            "source_path": prof.source_path,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
