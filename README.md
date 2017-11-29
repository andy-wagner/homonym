# Homonym
A mini web crawler to get hundreds of websites' content  based on a list of keywords. This help if, in case
of homonyms, we want to obtain a large amount of data for each meaning. 


## Intalling

- create a python >= 3.4 [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) environment
- `git clone git@github.com:QwantResearch/homonym.git && cd homonym`
- `pip install -r requirements.txt`

## Running

Simply:

    python main.py
    
# Usage

# List of keywords

Suppose we want to retrieve all the websites about python search word. We have two main meanings :
* python : the reptile
* python : the computer language

We need to define a list of words related to the right meaning : 
```python
mainSearchedWord = "python"
myKeywords = {"python_reptile": ["reptile", "serpent"],
              "python_computer": ["langage", "linux", ]
              }
```

Homonym will compute several query strings based on those wordlists for each meaning. 

# Storage in MongoDb

We obtain 3 values for each website : *url*,*content* and *category*. 
We store them in mongoDB.
