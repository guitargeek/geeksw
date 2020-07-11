import datetime


def print_with_time(*args, **kwargs):
    time_string = datetime.datetime.now()
    print(f"[{time_string}]", *args, **kwargs)


def make_data_loader(content, producers={}, verbosity=0):

    print_log = lambda x: None
    if verbosity >= 2:
        print_log = print_with_time

    def _load_column_with_function(col_name, df, container):
        """Careful, this adds columns to the DataFrame in-place.
        """

        def load_impl(branch):
            if branch in producers:
                _load_column_with_function(branch, df, container)
            else:
                df[branch] = container[branch]
                print_log(branch, "read from source")

        success = False
        while not success:
            try:
                func = producers[col_name]
                df[col_name] = func(df)
                print_log(col_name, "produced")
                success = True
            except BaseException as e:
                message = str(e)
                if message[0] == "'" and message[-1] == "'":
                    # This is the message from a KeyError when the branch could not be found in the DataFrame,
                    # we can just get the branch from the tree to solve it
                    branch = message[1:-1]
                    load_impl(branch)
                elif message.endswith("not defined"):
                    # Sometimes we also get errors like "name 'branch' is not defined",
                    # so we have to treat them separately
                    branch = message.split("'")[1]
                    load_impl(branch)
                else:
                    # raise exception again if we don't know how to fix the problem
                    raise e

    def load_data(container):
        """
        """

        # If one of our derived variables is called like one in that exists in the TTree, we have an ambiguity
        for key in producers.keys():
            if key in container:
                raise RuntimeError("Duplicate name '" + key + "' in producers and source")

        # Let's check in beforehand if the requested columns can be retrieved
        for label in content:
            if label not in producers.keys() and not label in container:
                raise RuntimeError(
                    "Requested column '" + label + "' can neither be found in the source nor the producers"
                )

        data = dict()

        for label in content:

            if label in container:
                data[label] = container[label]

            if label in producers.keys():
                _load_column_with_function(label, data, container)

        # Finally we drop the original branches from the skim such that only what we want to have remains
        to_delete = []
        for key in data:
            if not key in content:
                to_delete.append(key)

        for key in to_delete:
            del data[key]
            print_log(key, "deleted")

        return data

    return load_data


class TreeWrapper(object):
    def __init__(self, tree, n_max_events=None):
        self.tree_ = tree
        self.n_max_events_ = n_max_events
        # self.cache_ = mycache = uproot.ArrayCache("100 MB")
        self.cache_ = {}

    def __getitem__(self, key):
        return self.tree_.array(key, entrystop=self.n_max_events_, cache=self.cache_)

    def __len__(self):
        return min(len(self.tree_), self.n_max_events_)

    def __contains__(self, key):
        return key.encode("utf-8") in self.tree_.keys()
