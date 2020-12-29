# Problem Statement
Build a file-based key-value data store that supports the basic CRD (create, read, and delete)
operations. This data store is meant to be used as a local storage for one single process on one
laptop. The data store must be exposed as a library to clients that can instantiate a class and work
with the data store.

# Given Functional requirements.(All satisfied)
1. It can be initialized using an optional file path. If one is not provided, it will reliably
create itself in a reasonable location on the laptop.
2. A new key-value pair can be added to the data store using the Create operation. The key
is always a string - capped at 32chars. The value is always a JSON object - capped at
16KB.
3. If Create is invoked for an existing key, an appropriate error must be returned.
4. A Read operation on a key can be performed by providing the key, and receiving the
value in response, as a JSON object.
5. A Delete operation can be performed by providing the key.
6. Every key supports setting a Time-To-Live property when it is created. This property is
optional. If provided, it will be evaluated as an integer defining the number of seconds
the key must be retained in the data store. Once the Time-To-Live for a key has expired,
the key will no longer be available for Read or Delete operations.
7. Appropriate error responses must always be returned to a client if it uses the data store in
unexpected ways or breaches any limits.

# Given non-functional requirements (All satisfied)
1. The size of the file storing data must never exceed 1GB.
2. More than one client process cannot be allowed to use the same file as a data store at any
given time.
3. A client process is allowed to access the data store using multiple threads, if it desires to.
The data store must therefore be thread-safe.
4. The client will bear as little memory costs as possible to use this data store, while
deriving maximum performance with respect to response times for accessing the data
store.

# Requirements or prerequisites(Environment)
1. A good standard OS
2. Language: Python--> 3.6 or higher
3. IDE (i use vs code)
4. Flask framework for web application (Requirements.txt)

    1. To start the project from default loc.  run `python3 app.py`
    2. To start datastore from user defined file location, run `python3 app.py --datastore=<absolute_path_of_your_datastore>` 

# Unit tests of App.(Test Environment)
#Create operation
1.  run `python3 test_create_data.py` for default datastore or run `python3 test_create_data.py --datastore=<absolute_path_of_your_datastore>` for custom datastore location.(For testing  the Create operation of data in datastore)

#Read operation
2.  run `python3 test_read_data.py` for default datastore or run `python3 test_read_data.py --datastore=<absolute_path_of_your_datastore>` for custom datastore location.

#Delete operation
3.  run `python3 test_delete_data.py` for default datastore or run `python3 test_delete_data.py --datastore=<absolute_path_of_your_datastore>` for custom datastore location.

# Accessing DataStore Create-Read-Delete operations as a library
1. A class named `DataStoreCRD` in the file `datastore/CRD/functions.py` contains all the CRD operations.
2. A class function `DataStoreCRD().check_create_data(<key-value-data>, <datastore directory>)` can be used to create a data in DataStore.
3. A class function `DataStoreCRD().check_read_data(<key>, <datastore directory>)` can be used to read a data from the DataStore.
4. A class function `DataStoreCRD().check_delete_data(<key>, <datastore directory>)` can be used to delete a data from the DataStore.

# API set to "localhost" :'127.0.0.1:5000'
1. Create data in DataStore - **API**: `http://localhost:5000/datastore/create` & **Data**: `{"abc": {"data1": "value1", "data2": "value2", "data3": "value3", "Time-To-Live": 5000, "CreatedAt": "2020-02-27T05:07:53.133320"}, "def": {"data1": "value1", "data2": "value2", "data3": "value3", "Time-To-Live": 50, "CreatedAt": "2020-02-27T05:07:53.133343"}}` & **API Type**: `POST`.
2. Read data from datastore - **API**: `http://localhost:5000/datastore/read?key=abc` & **API Type**: `GET`.
3. Delete data from datastore - **API**: `http://localhost:5000/datastore/delete?key=abc` & **API Type**: `DELETE`.
