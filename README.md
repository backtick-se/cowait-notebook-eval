# Cowait Notebook Evaluation

## Introduction

Cowait is a system for packaging a project with its dependencies into a Docker image, which can then be run as a container either on the local machine or on a Kubernetes cluster. It alleviates several problems in data engineering such as dependency management, reproducibility, version control and parallel computation. Cowait runs code as tasks, and a task can start subtasks with parameters and return values. These subtasks run in parallel as separate containers, which enables parallel computation.

A Cowait notebook is essentially a Jupyter notebook running with a Cowait kernel. This enables the notebook to act as if it was as Cowait task, which enables it to start new Cowait tasks in parallel. The notebook can run either locally or in a Kubernetes cluster, and the notebook works in the same way in both cases.

One of the defining differences between Cowait notebooks and regular notebooks is the access to the local file system. When starting a Cowait notebook from the command line it will get access to the current working directory. This is also true if the notebook runs on a cluster. The files are accessed over the network, and the notebook will not be able to tell that the files are in fact on your computer and not on the computer in the cluster. This is not the case with regular notebooks, in which a separate storage provider would be needed.

In this lab you will learn how to use Cowait Notebooks by creating a simple, yet realistic, project. The notebooks will run on a Kubernetes cluster, but all the files will be on your computer. The lab takes around 20 minutes.

## Preparations

Please complete the following steps before proceeding.

### Prerequisite Software
- git
- Docker
- Python 3.7

### Initial Setup
- Install Cowait:
  ```bash
  $ pip3 install cowait
  $ docker pull cowait/task
  ```
  If you already have Cowait installed, make sure it is at least version 0.4.23.

- Clone the demo repository:
  ```bash
  $ git clone https://github.com/backtick-se/cowait-notebook-eval
  $ cd cowait-notebook-eval
  ```

### Docker Registry

You will need an image registry to distribute your code to the cluster. The easiest way is to sign up for a free account on Docker Hub at https://hub.docker.com/signup 

After signing up, ensure your Docker client is logged in:

```bash
$ docker login
```

### Cluster Configuration

Participants of the evaluation study should have received a `kubeconfig.yaml` file that can be used to access the evaluation cluster. If you are not participating in the evaluation, you will have to set up your own Cowait cluster. A traefik2 reverse proxy deployment is required.

Put the provided kubeconfig file in the current working directory. Then, set the `KUBECONFIG` environment variable:
```bash
$ export KUBECONFIG=$(pwd)/kubeconfig.yaml
```

## Lab

### Part 1: Your first Notebook Task

The goal of part one is to create a notebook that computes a value we are interested in. Then, we turn the notebook into a Cowait task, so that it can be executed as a batch job.

1. Open `cowait.yml` and update the `image` setting to `<your dockerhub username>/cowait-notebook-eval`. This configures the name of the container image that will contain all our code and dependencies.

1. Create a `requirements.txt` file and add `pandas`

1. Build the container image, and push it to your registry:
   ```bash
   $ cowait build --push
   ```

1. Launch a Cowait Notebook using your newly created image: 
   ```bash
   $ cowait notebook --cluster demo
   ```
   It might take a few minutes for the cluster to download the image. Once the task is running, a link will be displayed. Open it to access the notebook.

1. Create a new notebook called `volume.ipynb`. Make sure to select the Cowait kernel.

1. Download some data into a pandas dataframe. The dataset contains every trade executed on the Bitmex cryptocurrency derivatives platform, divided into one file per day. 

   ```python
   import pandas
   date = '20210101'
   df = pandas.read_csv(f'https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{date}.csv.gz')
   ```

1. We want to compute the total US dollar value of Bitcoin contracts over the course of the day. Bitcoin Perpetual Futures contracts have the ticker symbol `XBTUSD`. To do this, use pandas to find all the rows containing `XBTUSD` transactions, and sum the `size` column.

   ```python
   volume = df[df.symbol == 'XBTUSD'].size.sum()
   print(volume)
   ```

1. Parameterize the notebook by changing the date variable to an input parameter:
  
   ```python
   date = cowait.input('date', '20210101')
   ```

   In Cowait, *inputs* allow us to send arguments to tasks. Later, we can substitute the input value to execute the notebook code for any date we like. If no input is set, the default value `20210101` will be used.

1. Return the total volume from the notebook using `cowait.exit()`:

   ```python
   cowait.exit(volume)
   ```

   Similarly to *inputs*, tasks can also return *outputs*. Returning an output allows us to invoke the notebook and use the computed value elsewhere.

1. Write a simple sanity test for the notebook that verifies the computation for a date with a known volume. Create a file called `test_compute_volume.py`, either with Jupyter or your favorite text editor:

   ```python
   # test_compute_volume.py
   from cowait.tasks.notebook import NotebookRunner

   async def test_compute_volume():
       vol = await NotebookRunner(path='volume.ipynb', date='20210101')
       assert vol == 2556420
   ```

   The `NotebookRunner` task executes a notebook file and returns any value provided to `cowait.exit()`.

1. Open a new terminal in the same folder and run the test. Make sure it passes.

   ```bash
   $ cowait test
   ```
   Contrary to the notebook, the tests will run in a Docker container on your computer.

1. Now is a good time to save your progress. Since the files are available on your local machine, use your git client to create a commit.

   ```bash
   $ git add .
   $ git commit -m 'Volume notebook'
   ```

### Part 2: Going Parallel

We now have a notebook for calculating the volume for one day. But what if we want to know the volume for several days? While we could create a loop and download each day in sequence, it would be much more efficient to do it all at once, in parallel.

1. Create a new notebook with the Cowait kernel, and call it `batch.ipynb`.

1. First, we will create two input parameters and create a range of dates that we are interested in.

   ```python
   from helpers import daterange

   start = cowait.input('start', '20210101')
   end = cowait.input('end', '20210104')

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

1. Finally let's return the results:

   ```python
   cowait.exit(results)
   ```

1. Use the `Run All Cells` feature in the `Run` menu to try out the notebook. This will run a tasks for each day in the date range, in paralell, on the cluster.

1. Now is a good time to save your progress.

   ```bash
   $ git add .
   $ git commit -m 'Volume batch notebook'
   ```

### Part 3: Production

We now have a runnable notebook, and it is time to put it into production. We can run the `batch` notebook without Jupyter using the command line.

1. Open a terminal in the same folder and make sure the `KUBECONFIG` environment variable is set:

   ```bash
   $ export KUBECONFIG=$(pwd)/kubeconfig.yaml
   ```

1. Before we can run tasks on the cluster we have to push an updated container image to a docker registry. This image will bundle all the code you've written along with any dependencies required to run it. It will continue to work as written, forever.

   ```bash
   $ cowait build --push
   ```

1. The notebook can now be executed on the cluster as a batch job for a range of dates.

   ```bash
   $ cowait notebook run batch.ipynb \
       --cluster demo \
       --input start=20210201 \
       --input end=20210207
   ```

## Evaluation
- Briefly describe your overall impression of working with Cowait notebooks. Any questions? Any difficulties?
- What solutions do you currently use for notebooks/cloud compute?
- Breifly describe your current process of moving code from notebooks to production jobs.
- Do you think Cowait notebooks could help improve the data science workflow in your organization? Why/why not? 
- Do you currently experience any problems related to dependency management for notebooks in your organization?
- Do you currently experience any problems working with cloud notebooks in your organization?
- Do you see any advantage in having access to your local file system when working in a cloud notebook? Any drawbacks?
