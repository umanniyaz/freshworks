import json
import fcntl
import threading
from os import path
from datetime import datetime, timedelta
from dateutil.parser import parse
from configs.configurations import DEFAULT_DB_NAME


class DataStoreCRD:
    def check_time_to_live(self, value):
        # Checks how long the data is accessible.

        created_time = value['CreatedAt']

        # Parse the datetime from the string date.
        created_time = parse(created_time)

        time_to_live = value['Time-To-Live']

        if time_to_live is not None:
            # Calculate the data expire time.
            expired_datetime = created_time + timedelta(seconds=time_to_live)

            # Calculate the remaining seconds of expired time(may/may not expired) from current time.
            remaining_seconds = (expired_datetime - datetime.now()).total_seconds()

            if remaining_seconds <= 0:
                return False

        return value

    def check_create_data(self, json_data, db_path):
        if not isinstance(json_data, dict):
            return False, "Incorrect request data format. Only JSON object with key-value pair is acceptable."

        # Check for request data size. If size is greater than 1GB ignore the data.
        data_obj = json.dumps(json_data)

        if len(data_obj) > 1000000000:
            return False, "DataStore limit will exceed 1GB size."

        for key, value in json_data.items():
            # Check for key in data for 32 char length.
            if len(key) > 32:
                return False, "The keys must be in 32 characters length."

            # Check for value in data whether it is JSON object or not.
            if not isinstance(value, dict):
                return False, "The values must be in JSON object formats."

            value_obj = json.dumps(value)

            # Check for value JSON object is 16KB or less in size.
            if len(value_obj) > 16384:
                return False, "The values must be in 16KB size."

        # Checks if DataStore exists.
        # If datastore exists append existing datastore,
        # else create a new datastore with data inserted.
        datastore = path.join(db_path, DEFAULT_DB_NAME)
        data = {}
        if path.isfile(datastore):
            with open(datastore) as f:
                # Make sure single process only allowed to access the file at a time.
                # Locking file.
                fcntl.flock(f, fcntl.LOCK_EX)
                data = json.load(f)
                # Releasing the file lock.
                fcntl.flock(f, fcntl.LOCK_UN)

                # Check if file size exceeded 1GB size.
                prev_data_obj = json.dumps(data)
                if len(prev_data_obj) >= 1000000000:
                    return False, "File Size Exceeded 1GB."

        # Check any key present in previous datastore data.
        # If present return Error message
        '''
        # for key in json_data.keys():
        #     if key in data.keys():
        #         return False, "Key already exist in DataStore."
        '''
        have_key = any(x in json_data.keys() for x in data.keys())
        if have_key:
            return False, "Key already exist in DataStore."

        """ Threading Mechanism Start """
        def prepare_data_create(json_data_keys):
            # Add CreatedAt time to data. Also add Time-To-Live if the data dont have in it.
            for key in json_data_keys:
                singleton_json = json_data[key]
                singleton_json["CreatedAt"] = datetime.now().isoformat()
                singleton_json["Time-To-Live"] = singleton_json["Time-To-Live"] if 'Time-To-Live' in singleton_json else None
                data[key] = singleton_json

        # No of threads are set to 4.
        thread_count = 4
        items = list(json_data.keys())

        split_size = len(items) // thread_count

        threads = []
        for i in range(thread_count):
            start = i * split_size
            end = None if i+1 == thread_count else (i+1) * split_size

            threads.append(threading.Thread(target=prepare_data_create, args=(items[start:end], ), name=f"t{i+1}"))
            threads[-1].start()

        # Wait for all threads to finish.
        for t in threads:
            t.join()

        """ Threading Mechanism End """

        # Write the new data.
        with open(datastore, 'w+') as f:
            # Make sure single process only allowed to access the file at a time.
            # Locking file.
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f)
            # Releasing the file lock.
            fcntl.flock(f, fcntl.LOCK_UN)

        return True, "Data created in DataStore."

    def read_delete_preprocess(self, key, db_path):
        datastore = path.join(db_path, DEFAULT_DB_NAME)

        # Check for datastore existance.
        if not path.isfile(datastore):
            return False, "Empty DataStore. Data not found for the key."

        # Read previous datastore data if exists.
        with open(datastore) as f:
            # Make sure single process only allowed to access the file at a time.
            # Locking file.
            fcntl.flock(f, fcntl.LOCK_EX)
            data = json.load(f)
            # Releasing the file lock.
            fcntl.flock(f, fcntl.LOCK_UN)

        # Check for the input key available in data.
        if key not in data.keys():
            return False, "No data found for the key provided."

        # Check for the data for the key is active or inactive.
        target = data[key]
        target_active = self.check_time_to_live(target)
        if not target_active:
            return False, "Requested data is expired for the key."

        return True, data

    def check_read_data(self, key, db_path):
        # Read data from the datasource for the given key.
        status, message = self.read_delete_preprocess(key, db_path)
        if not status:
            return status, message

        data = message[key]

        del data['CreatedAt']

        return status, data

    def check_delete_data(self, key, db_path):
        status, message = self.read_delete_preprocess(key, db_path)
        if not status:
            return status, message

        datastore = path.join(db_path, DEFAULT_DB_NAME)

        # Delete the data from the datastore.
        # This action is not reversible.
        del message[key]

        # Write the new data to the datasource after data deletion.
        with open(datastore, 'w+') as f:
            # Make sure single process only allowed to access the file at a time.
            # Locking file.
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(message, f)
            # Releasing the file lock.
            fcntl.flock(f, fcntl.LOCK_UN)

        return True, "Data is deleted from the datastore."
