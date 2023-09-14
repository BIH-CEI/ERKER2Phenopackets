# Dataset Title

## EDA & Parsing

### Categorical Variable Name <button type="button">Drop Column</button>

#### Visualization

![image](https://github.com/BIH-CEI/ERKER2Phenopackets/assets/43171336/1c2235e7-c668-410a-8697-52699605a9d6)


#### Values

| **Value** | **Count** | **Percentage** |
|-----------|-----------|----------------|
| a         | 1         | 25%            |
| b         | 1         | 25%            |
| c         | 1         | 25%            |
| d         | 1         | 25%            |

**Null values:** There are x rows with null values.

Select how you want to deal with missing values. Dropdown menu with options:
- Ignore
- Fill with value (select one of the values from the column or other)
- Drop rows

#### Parsing

**Mapping**

Here it would automatically create a dictionary that lets the user map each user to a different value.

*a* -> [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]

*b* -> [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]

*c* -> [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]

*d* -> [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]

*default* -> [&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]

**Parsing function (Python)**

```python
def parse_categorical_variable_name(value):
    # TODO: Write your parsing function here
    return value
```

A green/ red check indicates whether the syntax is correct or not.

**Errors**: Here syntax errors would be shown.


### Numerical Variable Name <button type="button">Drop Column</button>

#### Visualization

![image](https://github.com/BIH-CEI/ERKER2Phenopackets/assets/43171336/598d827e-138b-42a6-8a50-685dd6f52a7b)


#### Values

| **Name**           | **Value** |
|--------------------|-----------|
| mean               | 1         |
| mode               | 1         |
| standard deviation | 1         |
| min                | 1         |
| Q1                 | 1         |
| Q2                 | 1         |
| Q3                 | 1         |
| max                | 1         |

Automatically fit **distribution name** to the data:

| **parameter name** | **value** |
|--------------------|-----------|
| alpha              | 1         |
| beta               | 1         |


**Null values:** There are x rows with null values.

Select how you want to deal with missing values. Dropdown menu with options:
- Ignore
- Fill with value (select one of the statistical descriptors or 0 or other)
- Drop rows

#### Parsing

**Parsing function (Python)**

```python
def parse_numerical_variable_name(value):
    # TODO: Write your parsing function here
    return value
```

A green/ red check indicates whether the syntax is correct or not.

**Errors**: Here syntax errors would be shown.

### Others
Could be string, date, etc.

## Summary

| Columns to drop |
|-----------------|
| a               |
| b               |
| c               |
| ...             |

Confirm drop. <button type="button">Confirm</button>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<button type="button">Next</button>
