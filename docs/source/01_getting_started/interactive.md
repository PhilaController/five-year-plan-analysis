# Working in IPython or a Jupyter Notebook

When running a pipeline with `kedro`, the software will automatically
load the Data Catalog and parameters using the YAML files in the `conf/`
folder and make those available to the functions in the pipeline.
This information is part of the "context" that `kedro` uses to 
run each pipeline. 

Rather than simply running the pipelines from the command line, it
will sometimes be easier to work in an interactive environment, either
by using IPython or Jupyter Notebook/Lab. This section describes how to work 
interactively with `kedro` and be able to load datasets from the 
Data Catalog and have access to the configuration parameters. 

```eval_rst
.. note::
    Additional information is available on the `kedro documentation <https://kedro.readthedocs.io/en/latest/11_tools_integration/02_ipython.html#use-kedro-with-ipython-and-jupyter-notebooks-lab>`__.
```


We will use the `kedro` command to work interactively with the code and
automatically have a few key context variables loaded for us. 

To start a new IPython session in the command line, use:

```
kedro ipython
```

You should see the following log messages printed out:

```
INFO - ** Kedro project Five Year Plan Analysis
INFO - Defined global variable `context`, `session` and `catalog`
```

The global `catalog` variable will hold all of the entries from the `catalog.yml` file.
We can load a data frame by referencing the desired dataset's name in the YAML file. 
For example, we can load the economic indicators using:

```python
indicators = catalog.load("economic_indicators")

indicators.head()
```

And this is the output you'll see:
```
            BuildingPermitsPhilly  ActivityLicensesPhilly  BizLicensesPhilly  ...  MeanDaysToSalePhillyMSA  MedianListPricePhillyMSA  RentIndexPhillyMSA
Date                                                                          ...
1913-01-01                    NaN                     NaN                NaN  ...                      NaN                       NaN                 NaN
1913-02-01                    NaN                     NaN                NaN  ...                      NaN                       NaN                 NaN
1913-03-01                    NaN                     NaN                NaN  ...                      NaN                       NaN                 NaN
1913-04-01                    NaN                     NaN                NaN  ...                      NaN                       NaN                 NaN
1913-05-01                    NaN                     NaN                NaN  ...                      NaN                       NaN                 NaN

[5 rows x 62 columns]
```

We also have the configuration parameters available to us via the `context` 
variables:

```python
parameters = context.params

parameters
```
And you'll see this output:
```
{'fresh_indicators': False,
 'seasonal_adjustments': ['ActivityLicensesPhilly',
  'BizLicensesPhilly',
  'BuildingPermitsPhilly',
  'CPIPhillyMSA',
  'ContinuedClaimsPA',
  'WeeklyEconomicIndex',
  'DeedTransfersPhilly',
  'InitialClaimsPA',
  'UncertaintyIndex',
  'UnemploymentPhilly'],
 'min_feature_year': 1996,
 'max_fit_date': '2021-06-30',
 'grangers_maxlag': 6,
 'grangers_max_date': '2019-12-31',
 'plan_start_year': 2022,
 'cbo_forecast_date': 'latest'}
```

We can also launch a [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/) with the `kedro` command. From 
the command line, run:

```
kedro jupyter notebook
```

This will launch a new browser window and you can create a new notebook
file that will have the same global variables automatically initialized for you.

If instead you want to use [Jupyter Lab](https://jupyterlab.readthedocs.io/en/latest/) 
(the successor to Jupyter Notebook), you can use the following command:

```
kedro jupyter lab
```

