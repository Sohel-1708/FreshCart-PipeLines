# Import Mage's decorator only if it isn't already loaded
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


# data_exporter marks this as a step that sends data out of the pipeline
# 'df' is the 30 predicted rows returned by train_model, passed in automatically by Mage
# It saves them to a CSV file and returns nothing, because this is an end of the pipeline
@data_exporter
def export_data(df, *args, **kwargs):
    df.to_csv('iris_predictions.csv', index=False)
    print('Saved', len(df), 'predictions to iris_predictions.csv')
    return df

if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@test
def test_saved(output, *args):
    import pandas as pd
    from pathlib import Path
    path = Path('iris_predictions.csv')
    assert path.exists()
    assert len(pd.read_csv(path)) == len(output) == 30