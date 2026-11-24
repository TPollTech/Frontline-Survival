"""Generate original material library outside the production baseline."""
import argparse
from .pbr import generate_library

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory")
    p.add_argument("--size",type=int,default=128)
    p.add_argument("--seed",type=int,default=9133)
    a=p.parse_args()
    library=generate_library(a.size,a.seed)
    library.write(a.directory)
    library.verify(a.directory)
    print("PBR_LIBRARY_PASS",len(library.materials),len(library.textures),library.sha256())

if __name__=="__main__":
    main()
