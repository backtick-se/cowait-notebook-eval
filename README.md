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
- Check out the demo repository:
  ```bash
  $ git clone https://github.com/backtick-se/cowait-notebook-eval
  $ cd cowait-notebook-eval
  ```

### Docker Registry

You will need an image registry to distribute your code to the cluster. The easiest way is to sign up for a free account on Docker Hub at https://hub.docker.com/signup 

### Cluster Configuration

Participants of the evaluation study should have received a `kubeconfig` file that can be used to access the evaluation cluster. If you are not participating in the evaluation, you will have to set up your own Cowait cluster. A traefik2 reverse proxy deployment is required.

Put the provided kubeconfig file in the current working directory. Then, set the `KUBECONFIG` environment variable:
```bash
$ export KUBECONFIG=$(pwd)/kubeconfig
```

## Lab

### Part 1: The notebook

1. Create a `requirements.txt` file and add `pandas`
1. Open `cowait.yml` and update the `image` setting to `<your dockerhub username>/cowait-notebook-eval`
1. Build and push the notebook image:
   ```bash
   $ cowait build --push
   ```
1. Launch a Cowait Notebook using your newly created image: 
   ```bash
   $ cowait notebook -c kubernetes
   ```
   It might take a few minutes for the cluster to download the image. Once the task is running, a link should be displayed. Open it to access the notebook.
1. Create a new notebook called `volume.ipynb`. Make sure to select the Cowait interpreter.
1. Take a moment to appreciate the magic of `clientfs`

   **TODO: How? Briefly explain clientfs**
1. Download some data into a pandas dataframe. The dataset contains every trade executed on the Bitmex derivatives platform.

   **TODO: Add some more background**
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
  
   **TODO: Explain cowait inputs**
   ```python
   date = cowait.input('date', '20200101')
   ```
1. Return the total volume from the notebook using `cowait.exit()`:

   **TODO: Explain cowait outputs**
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
       assert vol == 2556420
   ```
1. Make sure the test passes:

   **TODO: Describe cowait tests & how they run on your local machine**
   ```bash
   $ cowait test
   ```
1. Now is a good time to save your progress. Since the files are available on your local machine, use your git client to create a commit.
   ```bash
   $ git add .
   $ git commit -m 'Volume notebook works'
   ```

### Part 2: Going parallel

We now have a notebook for calculating the volume for one day. But what if we want the volume for several days? While we could create a loop and download each day in sequence, it would be much more efficient to do it all at once, in parallel.

1. Create a new notebook in the same way as above (we will refer to it as `batch.ipynb`)
1. First, we will create two input parameters and create a range of dates that we are interested in.
   ```python
   from helpers import daterange

   start = cowait.input('start', '20210101')
   end = cowait.input('end', '20210110')

   dates = [ date for date in daterange(start, end) ]
   dates
   ```
1. Then, we can create a `NotebookRunner` for each date in the list.  This will start four new tasks, each calculating the volume for one day. While these are running the notebook can perform other calculations.
   ```python
   subtasks = [ NotebookRunner(path='volume.ipynb', date=date) for date in dates ]
   ```
1. To get the results of the calculations we need to wait for each task to finish:
   ```python
   # just for reference, dont try to run this
   result1 = await task1
   result2 = await task2
   ```
   Since we have a list of pending tasks, we can use `cowait.join`. Create a new cell with the following code:
   ```python
   results = await cowait.join(subtasks)
   ```
1. Finally let's print the results:
   ```python
   print(results)
   ```
1. Use the `Run All Cells` feature in the `Run` menu to try out the notebook. This will run the tasks on the cluster.
1. Now is a good time to save your progress.
   ```bash
   $ git add .
   $ git commit -m 'Volume batch notebook works'
   ```

### Part 3: Production

We now have a runnable notebook, and it is time to put it into production. We can run the `batch` notebook without Jupyter using the command line.

1. Before we can run the tasks on the cluster we have to push the image to a docker registry:
   ```bash
   $ cowait build --push
   ```

2. The notebook can now be run on the cluster by adding `-c kubernetes`:
   ```bash
   $ cowait notebook run batch.ipynb -c kubernetes -i start=20210201 -i end=20210210
   ```

## Evaluation
- Briefly describe your overall impression of working with Cowait notebooks.  Any questions? Any difficulties?
- What solutions do you currently use for notebooks/cloud compute?
- Breifly describe your current process of moving code from notebooks to production jobs.
- Do you think Cowait notebooks could help improve the data science workflow in your organization? Why/why not? 
- Do you currently experience any problems related to dependency management for notebooks in your organization?
- Do you currently experience any problems working with cloud notebooks in your organization?
- Do you see any advantage in having access to your local file system when working in a cloud notebook? Any drawbacks?
