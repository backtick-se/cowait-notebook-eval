from cowait.tasks.notebook import NotebookRunner


async def test_compute_volume():
    vol = await NotebookRunner(path='volume', date='20210101')
    assert vol == 2556420
