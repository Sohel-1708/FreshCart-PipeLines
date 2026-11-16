if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@transformer
def validate(df, *args, **kwargs):
    return df.copy()

@test
def test_valid(output, *args):
    assert not output.isna().any().any(), 'Missing values'
    assert output['target'].nunique() == 3, 'Expected three classes'
