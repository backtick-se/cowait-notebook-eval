# Cowait Notebook Evaluation

### Prerequisites
- git
- Docker
- Python 3.7
- Poetry

### Initial Setup
- Check out the repository:
  ```bash
  $ git clone https://github.com/backtick-se/cowait-notebook-eval
  $ cd cowait-notebook-eval
  ```
- Download the clientfs client for your platform
  - OSX:
    ```bash
    wget .... -O clientfs
    ```
  - Linux
    ```bash
    wget .... -O clientfs
    ```

### Cluster Configuration

Participants of the evaluation study should have received a `kubeconfig` file that can be used to access the evaluation cluster. If you are not participating in the evaluation, you will have to set up your own Cowait cluster. A traefik2 reverse proxy deployment is required.

Put the provided kubeconfig file in the current working directory. Then, set the `KUBECONFIG` environment variable:
```bash
$ export KUBECONFIG=$(pwd)/kubeconfig
```

## Lab

1. Launch the Cowait Notebook using the provided base image. The image is pre-built with the necessary dependencies. 
   ```bash
   $ cowait notebook -c kubernetes
   ```
   When the task is running, a link should be displayed. Open it to access the notebook.
1. Create a new notebook using the Cowait interpreter.
1. First, we will import some code to download sample data:
   ```python
   from sample_data import download_daily_trades
   ```
1. Download some data into a pandas dataframe. The dataset contains every trade executed on the Bitmex derivatives platform.
   ```python
   df = pandas.read_csv('http://public.bitmex.com .... ')
   ```
1. Compute the total daily volume for the `XBTUSD` instrument using pandas:
   ```python
   volume = df[df.symbol == 'XBTUSD'].size.sum()
   ```
1. Parameterize the notebook by using an input parameter:
   ```python
   date = cowait.input('date', '20200101')
   ```
1. Return the total volume from the notebook using `cowait.exit()`:
   ```python
   cowait.exit(volume)
   ```
1. Write a simple sanity test for the notebook that verifies the computation for a date with a known volume.
   ```python
   # test_compute_volume.py
   async def test_compute_volume():
       vol = await NotebookRunner('volume.ipynb', date='20210101')
       assert vol == 46500012
   ```

### todo
- create a notebook
- import code to download bitmex trading data
- (add pandas dependency. rebuild image & restart notebook)
- calculate OHLC values using pandas in a notebook
- create a simple test for the notebook
- commit your work
- parameterize the notebook (input date, return total volume or similar)
- create a new notebook to launch several instances in parallel
- once it works, rewrite the notebook as a task
- launch the task from CLI
- commit your work

## Evaluation

