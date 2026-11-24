"""Emit neutral collision/LOD fixture for a real Godot smoke test."""
import sys
from pathlib import Path
from .recipes import Cylinder
from .lod import ColliderSpec, build_single_recipe_lods

def main():
    asset=build_single_recipe_lods(Cylinder("column",0.5,2,64),"object",
        colliders=(ColliderSpec("proxy","root","box",dimensions_m=(1,2,1)),))
    Path(sys.argv[1]).write_text(asset.canonical_json(),encoding="utf-8")
if __name__=="__main__":
    main()
