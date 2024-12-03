import subprocess
from pathlib import Path

if __name__ == "__main__":
    source_dir = Path(__file__).parent.resolve()
    root_dir = source_dir.parent.resolve()
    subprocess.run(["python", root_dir.joinpath("detector/model.py").resolve()])
    subprocess.run(["python", "-m", "spacy", "init", "fill-config", root_dir.joinpath("config/base_config.cfg").resolve(), root_dir.joinpath("config/config.cfg").resolve()])
    subprocess.run(["python", "-m", "spacy", "train", root_dir.joinpath("config/config.cfg").resolve(), "--output", root_dir.joinpath("output").resolve(), "--gpu-id", "0"])

