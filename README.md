# Cowait Notebook Evaluation

### Prerequisites
- git
- Docker
- Python 3.7

### Initial Setup
- Install Cowait:
  ```bash
  $ pip3 install cowait
  ```
- Check out the repository:
  ```bash
  $ git clone https://github.com/backtick-se/cowait-notebook-eval
  $ cd cowait-notebook-eval
  ```

### Cluster Configuration

Participants of the evaluation study should have received a `kubeconfig` file that can be used to access the evaluation cluster. If you are not participating in the evaluation, you will have to set up your own Cowait cluster. A traefik2 reverse proxy deployment is required.

Put the provided kubeconfig file in the current working directory. Then, set the `KUBECONFIG` environment variable:
```bash
$ export KUBECONFIG=$(pwd)/kubeconfig
```

## Lab

### Part 1: The notebook

1. Create a `requirements.txt` file and add `pandas`
1. Open `cowait.yml` and set the image name
1. Build and push the notebook image:
   ```bash
   $ cowait build --push
   ```
1. Launch the Cowait Notebook: 
   ```bash
   $ cowait notebook -c kubernetes
   ```
   When the task is running, a link should be displayed. Open it to access the notebook.
1. Create a new notebook using the Cowait interpreter. Give it the name `volume.ipynb`
1. Download some data into a pandas dataframe. The dataset contains every trade executed on the Bitmex derivatives platform.
   ```python
   date = '20210101'
   df = pandas.read_csv(f'https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{date}.csv.gz')
   ```
1. Compute the total daily volume for the `XBTUSD` instrument using pandas:
   ```python
   volume = df[df.symbol == 'XBTUSD'].size.sum()
   print(volume)
   ```
1. Parameterize the notebook by changing the date variable to an input parameter:
   ```python
   date = cowait.input('date', '20200101')
   ```
1. Return the total volume from the notebook using `cowait.exit()`:
   ```python
   cowait.exit(volume)
   ```
1. Write a simple sanity test for the notebook that verifies the computation for a date with a known volume.
   
   **TODO: Explain NotebookRunner**
   ```python
   # test_compute_volume.py
   from cowait.tasks.notebook import NotebookRunner

   async def test_compute_volume():
       vol = await NotebookRunner(path='volume.ipynb', date='20210101')
       assert vol == 46500012
   ```
1. Make sure the test passes:
   ```bash
   $ cowait build
   $ cowait test
   ```
1. Now is a good time to save your progress. Since the files are available on your local machine, use your git client to create a commit.
   ```bash
   $ git add .
   $ git commit -m 'Volume notebook works'
   ```

### Part 2: Going parallel

We now have a notebook for calculating the volume for one day. But what if we want the volume for several days?

1. Create a new notebook in the same way as above (we will refer to it as `notebook_batch.ipynb`)
2. Invoke the Volume notebook a few times:
   ```python
   day1 = NotebookRunner(path='volume.ipynb', date='20210101')
   day2 = NotebookRunner(path='volume.ipynb', date='20210102')
   day3 = NotebookRunner(path='volume.ipynb', date='20210103')
   day4 = NotebookRunner(path='volume.ipynb', date='20210104')
   ```
   This will start four new tasks, each calculating the volume for one day. While these are running the notebook can perform other calculations.
3. To get the results of the calculations we need to wait:
   ```python
   result1 = await day1
   result2 = await day2
   result3 = await day3
   result4 = await day4
   ```
   This can also be done with `cowait.join`:
   ```python
   results = await cowait.join([day1, day2, day3, day4])
   ```
4. Finally let's print the results:
   ```python
   print(results)
   ```
   If you now run all the cells in the notebook there should be some results printed. This will run the tasks on the cluster.
5. Parameterize the notebook using `cowait.input` and return the results using `cowait.exit`:
   ```python
   # notebook_batch.ipynb
   from helpers import daterange

   start_day = cowait.input('start_day', '20210101')
   end_day = cowait.input('end_day', '20210110')

   dates = [date for day in daterange(start_day, end_day)]
   
   runners = [NotebookRunner('volume.ipynb', date=date) for date in dates]

   results = await cowait.join(runners)

   cowait.exit(results)
   ```
   The notebook should still be runnable in Jupyter, and will use the default values for the inputs. 
6. The notebook can now be run as a task from the command line.
   ```bash
   $ cowait build
   $ cowait notebook run notebook_batch -i start_day=7 -i end_day=12
   ```
   This will run the tasks as containers on the local computer.
7. Now is a good time to save your progress.
   ```bash
   $ git add .
   $ git commit -m 'Volume batch notebook works'
   ```

### Part 3: Production

We now have a runnable notebook, and it is time to put it into production. Instead of running the tasks on the local computer we will run the tasks on a cluster.

1. Before we can run the tasks on the cluster we have to push the image to a docker registry:
   ```bash
   $ cowait build
   $ cowait push
   ```

2. The notebook can now be run on the cluster by adding `-c kubernetes`:
   ```bash
   $ cowait notebook run run notebook_batch -c kubernetes -i start_day=20210201 -i end_day=20210210
   ```

## Evaluation
- Briefly describe your overall impression of working with Cowait notebooks
- Do you think Cowait notebooks could help improve the workflow in your organization? Why/why not? 
- Do you see any advantage in having access to your local file system when working in a cloud notebook? Any drawbacks?
