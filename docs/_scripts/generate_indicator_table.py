from pathlib import Path

import pandas as pd

current_dir = Path(__file__).parent
path = (
    current_dir
    / ".."
    / ".."
    / "src/fyp_analysis/pipelines/data_processing/indicators/sources"
)

columns = ["name", "description", "source", "frequency", "geography"]
out = []
for f in sorted(path.glob("*.json")):
    source = f.stem
    df = pd.read_json(f).sort_values(by="name")
    for _, row in df.iterrows():
        out.append(
            [
                row["name"],
                row["description"],
                source,
                row["frequency"],
                row["geography"],
            ]
        )
out = pd.DataFrame(out, columns=columns)
out.to_csv(current_dir / "../assets/data/indicators.csv", index=False)
