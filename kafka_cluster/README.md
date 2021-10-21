## Application URL

The final application can be accessed from this link:

http://k8s-shortsqueezeingre-bdf54e695e-1796258414.us-east-1.elb.amazonaws.com


## Quick start instructions 
1. Install the following packages in your development environment before making git commmits:
> `conda install black flake8 isort mypy pre-commit`
2. Clone repo `cd` into root directory of project
3. Install the pre-commit configuration
> `pre-commit install`
4. Install the foobar_gamestop code as python package, `pip install -e ./` (again from root of project)
5. Make your changes now as usual on a branch and when you run `git commit` the linters will be run to auto-format your code to PEP8

## EKS cluster
You'll have to configure access to the cluster with eksctl and kubectl.
(more info coming.)

All commands have to be run from gamestop/deploy root directory

### Creating the EKS cluster
```
eksctl create cluster -f cluster.yaml

```

### Install the application using Helm

```
helm install shortsqueeze ./

```

### Connect to cassandra
```
kubectl exec --stdin --tty shortsqueeze-cassandra-0 -- /bin/bash
cqlsh --cqlversion=3.4.4 -u admin -p welcome1

```

### Uninstalling the application
```
helm delete shortsqueeze

```
### Delete the EKS cluster
```
kubectl delete cluster -f cluster.yaml
```

### Overview of project tree structure
------------

```
.
├── setup.py
├── setup.cfg
├── README.md
├── LICENSE.txt
├── .pre-commit-config.yaml
├── .gitignore
│
├── foobar
│   ├── __init__.py
│   ├── trainer
│   │   ├── __init__.py
│   │   ├── _base_trainer.py
│   │   └── autoencoder_trainer.py
│   ├── model
│   │   ├── __init__.py
│   │   └── _base_model.py
│   ├── data_loader
│   │   ├── __init__.py
│   │   ├── _reddit_data.py
│   │   ├── _kaggle_wsb_get_data.py
│   │   ├── _finnhub_data.py
│   │   ├── _base.py
│   │   └── conf
│   │      ├── praw.ini
│   │      └── kaggle.json
│   └── data
│       ├── samples
│       │   ├── submission_sample_object.json
│       │   ├── stock_candle_timeseries.csv
│       │   ├── shortinterest.csv.zip
│       │   ├── README.md
│       │   ├── filling_sentiment_ts.csv
│       │   └── comment_sample_object.json
│       ├── raw
│       │   └── README.md
│       └── processed
│           └── README.md
│
├── notebooks
│   └── wsb-senti-analysis.ipynb
│
├── microservices
│   ├── reddit_wsb_producer
│   │   ├── wsb_posts_producer.py
│   │   ├── wsb_comments_producer.py
│   │   ├── requirements.txt
│   │   ├── .env
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── finnhub_producer
│   │   ├── requirements.txt
│   │   ├── finnancial_data_producer.py
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── dash_app
│       ├── __init__.py
│       ├── components.py
│       ├── app.py
│       └── figures
│           ├── __init__.py
│           ├── network.py
│           └── line_chart.py
│
└── deploy
    └── README.md

## Notes on naming conventions
------------
1. Python file names use snake case
2. Test file names are prefixed with 'test_', followed by the module name they are testing.
