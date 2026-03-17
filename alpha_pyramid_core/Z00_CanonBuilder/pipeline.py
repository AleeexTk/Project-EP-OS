import json
import argparse
from pathlib import Path
from . import loader
from .validators import geometry, uniqueness, sector
from .generators import atlas, routing, occupancy, link_passports

class CanonBuilder:
    def __init__(self, modules_path: Path, output_path: Path):
        self.modules_path = modules_path
        self.output_path = output_path

    def run(self):
        manifests = loader.load_manifests(self.modules_path)
        geometry.validate(manifests)
        uniqueness.validate(manifests)
        sector.validate(manifests)
        atlas_data = atlas.generate(manifests)
        routing_data = routing.generate(manifests)
        occupancy_data = occupancy.generate(manifests)
        passports_data = link_passports.generate(manifests, routing_data)

        self._write("atlas.json", atlas_data)
        self._write("routing_table.json", routing_data)
        self._write("occupancy.json", occupancy_data)
        self._write("link_passports.json", passports_data)

    def _write(self, name, data):
        self.output_path.mkdir(parents=True, exist_ok=True)
        path = self.output_path / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Canon Builder v1.0")
    parser.add_argument("--modules", required=True, help="Path to modules directory")
    parser.add_argument("--output", required=True, help="Output directory for artifacts")
    args = parser.parse_args()
    builder = CanonBuilder(Path(args.modules), Path(args.output))
    builder.run()

if __name__ == "__main__":
    main()
