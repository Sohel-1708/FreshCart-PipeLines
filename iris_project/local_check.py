"""Direct-call checks of block code; Mage orchestration itself is NOT tested."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import pandas as pd

def block(path):
    def identity(fn): return fn
    env={k:identity for k in ('data_loader','transformer','data_exporter','test')}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),env)
    return env

def run_checks():
    root=Path(__file__).resolve().parent
    load=block(root/'data_loaders/load_iris.py'); prep=block(root/'transformers/prepare_data.py'); train=block(root/'transformers/train_model.py'); save=block(root/'data_exporters/save_results.py'); evaluate=block(root/'transformers/evaluate_model.py'); validate=block(root/'transformers/validate_data.py')
    data=load['load_data'](); load['test_output'](data); validated=validate['validate'](data);validate['test_valid'](validated);assert validated.equals(data)
    split=prep['transform'](validated);prep['test_output'](split);assert (split['split']=='train').sum()==120 and (split['split']=='test').sum()==30
    results=[]; orig=Path.cwd()
    with TemporaryDirectory() as tmp:
        try:
            os.chdir(tmp)
            for depth in range(1,6):
                Path('iris_predictions.csv').unlink(missing_ok=True)
                pred=train['train'](split,max_depth=depth)
                accuracy=float((pred.predicted==pred.target).mean())
                try:train['test_accuracy'](pred);passed=True
                except AssertionError:passed=False
                if passed:save['test_saved'](save['export_data'](pred))
                results.append(dict(max_depth=depth,accuracy=accuracy,gate_passed=passed,csv_created=Path('iris_predictions.csv').exists()))
                if depth==3:
                    metrics=evaluate['evaluate'](pred);evaluate['test_metrics'](metrics)
                    matrix=pd.crosstab(pred.target,pred.predicted,rownames=['actual'],colnames=['predicted'])
        finally:os.chdir(orig)
    return pd.DataFrame(results),matrix,metrics

if __name__=='__main__':
    for table in run_checks(): print(table.to_string())
