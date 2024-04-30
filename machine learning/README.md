# Data Modelling and Analysis

## Instructions and Setup

Make sure to unzip the provided data folder of the clothing-co-parsing dataset

```bash
!unzip data.zip
```

Then install all the requirements

```bash
python3 -m pip install -r requirements.txt
```

Now you can use the following scripts/notebooks for their respective purpose:

1. `segmentationTraining.ipynb`: For training the segmentation model.
2. `fit_co_occurance_matrix.py`: For constructing the co-occurance matrix.
3. `measure_accociation_matrix.ipynb`: Analysis and measurements of recommendation vi co-occurance matrix.
4. `visualization.ipynb`: Visualization of Co-occurance matrix and the segmentation training loss.
5. `generate_plots.ipynb`: It contains:
    1. API query RTT experiment and analysis/visualization.
    2. Cache hit vs. miss analysis.
    3. Analysis of different end.to-end recommendaiton strategies.