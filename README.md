# pandas + django = pandjas
A framework for adding context, state, and validation to pandas DataFrames.

## The Problem with Pandas
I love pandas for its power.  It's a really fast engine for working with tabular data, which is expressed in pandas as DataFrame objects.

However, in many respects pandas seems like it was designed as a tool for parsing data at the command line.  In pandas, dataframes are created and transformed in a series of steps.  The syntax is very terse and unpythonic and I'm sorry but the documentation sucks. The pandas docs are thorough, but one example runs into the next, which it makes it hard to understand the state of data as it is transformed.

In fact, this is an overriding problem with pandas.  DataFrame objects are created and transformed in a series of steps, without any clearly defined expectation of what valid data should look like.  This is a problem, because running an operation on a DataFrame object assumes an understanding of the underlying data.

For example, suppose you write a statement that finds maximum monthly revenue with:

`max_revenue = monthly_balances['revenue'].max()`

This statement assumes that the monthly_balances dataframe has a column named 'revenue' that contains numerical values.  Otherwise the statement will fail.

## Panjas: How to Rule Like a God Over Structured Data
Panjas is a toolbox that helps us 'wrap' a pandas dataframe inside a container object that includes a definition of the dataframe's  structure.  This allows us to:

+ Easily initialize a new container object with a correctly structured DataFrame at its core.
+ Write methods and properies for indirectly adding to and interacting with the DataFrame through the container object. This way other programmers can access the container object's structured data without the burden of learning pandas.
+ Validate the structure and content of a DataFrame object.

### pandas + django
Pandjas is backed by django, which gives our container objects the power to store structured data as flat files and relate them to other objects with more structured data.  Django gives us the ability to:

+ Create DataFrame structure definitions, which is used for validating DataFrame content.
+ Save validated structured data in a fast, native flat file format.
+ Surround structured data with the context of methods, properties, and metadata that can help validate, interpret, and operate on the structured data content.
+ Relate different types of container objects to one another to create vast networks of structured data.

One way to work with Pandjas is to think of the container object as the equivalent of a template in excel, designed to accept tabular data in a particular format and then crunch out an analysis of that data.  The analysis results can be stored in the container object, along with all the data used to derive the result.

## Example:
### Sequential Energy Data
In California, most electricity customers have their energy usage measured by the utility every 15 minutes.  When all goes well, this produces 34,050 (4 x 24 x 365) energy measurements per year.  However, sometimes the data collection fails, which leaves gaps in the data that must be filled before an analysis can be completed.

For a given electrical circuit, energy data is always consumed in sequential order.  It never needs to be rearranged or filtered by some criteria, so it doesn't need to be stored in a relational database.  Relational databases provide wonderful flexibility to filter and rearrange data, but relational database storage is expensive and slow compared to flat-file storage.

Energy data also obeys the law of superposition.  This means that the aggregate, minute-by-minute usage of any group of circuits is achieved by simply summing the energy usage of each individual ciruit.  In this way, we can express the aggregate usage of an arbitrary number of circuits in the same format of 34,050 measurements per year that we use to express the usage of a single circuit.

Let's take a look at how we can use panjas to validate and store a circuit's sequential energy data, and relate that data to a network of customer data.

Because our energy data is periodic and it will be related to customer data, we'll subclass the IntervalModelABC abstract base class.  This has the effect of requiring our stored energy data to be indexed with sequential timestamps of the correct period.  It also requires that the timestamps be timezone-aware.  For each energy measurement, we'll store measured power, in kilowatts (kW) and we'll include a boolean indication of whether the measurement is real, or estimated.

First, we define the column strucure of the data by creating a FrameDef object:
```
from pandjas.objects import FrameDef

energy_def = FrameDef(
    [
        {
            "name": "kW",
            "dtype_str": "float"
        },
        {
            "name": "is_estimate",
            "dtype_str": "boolean"
        }
    ]
)
```

Next we subclass IntervalModelABC:

```
from django.db import models
from pandjas.models import IntervalModelABC

class PowerUsage(IntervalModelABC):
    frame_def = energy_def
    folder = 'power_usage/'
    name = models.CharField(
        max_length=100,
        blank=True
        )
    customer_circuit = models.ForiegnKey{
        'CustomerCircuit',
        on_delete=models.SET_NULL
    }
```

This new PowerUsage object will 'wrap' a pandas dataframe, which will be stored in a folder named 'power_usage', which will be located in the root of the django installation's media folder.  The PowerUsage object will inherit fields named 'timezone', and 'period' which will charectorize the index of the dataframe.  The dataframe itself will include columns named 'kW' and 'is_estimate'.

Saving the PowerUsage object will save changes to the associated dataframe object, unless the dataframe fails validation, which would raise an exception.

Finally, methods and properties can be added to the PowerUsage object to perform common energy analyses.  For example, we often want to know the total energy used between the start and end of two dates.  By adding methods for extracting analytical results from the wrapped dataframe, other developers can use the PowerUsage object without having to learn or understand pandas. 

