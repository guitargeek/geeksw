import pandas as pd


def make_data_loader(
    content,
    functions={},
    get=lambda container, key: container[key],
    is_available=lambda container, key: key in container,
):
    def _load_column_with_function(col_name, df, container):
        """Careful, this adds columns to the DataFrame in-place.
        """
        success = False
        while not success:
            try:
                func = functions[col_name]
                df[col_name] = func(df)
                success = True
            except BaseException as e:
                message = str(e)
                if message[0] == "'" and message[-1] == "'":
                    # This is the message from a KeyError when the branch could not be found in the DataFrame,
                    # we can just get the branch from the tree to solve it
                    branch = message[1:-1]
                    if branch in functions:
                        _load_column_with_function(branch, df, container)
                    else:
                        df[branch] = get(container, branch)
                elif message.endswith("not defined"):
                    # Sometimes we also get errors like "name 'branch' is not defined",
                    # so we have to treat them separately
                    branch = message.split("'")[1]
                    if branch in functions:
                        _load_column_with_function(branch, df, container)
                    else:
                        df[branch] = get(container, branch)
                else:
                    # raise exception again if we don't know how to fix the problem
                    raise e

    def load_data(container):
        """Load a sample from a tree into pandas DataFrame.
        """

        # If one of our derived variables is called like one in that exists in the TTree, we have an ambiguity
        for key in functions.keys():
            if is_available(container, key):
                raise RuntimeError("Duplicate name '" + key + "' in functions and actual TTree branches")

        # Let's check in beforehand if the requested columns can be retrieved
        for label in content:
            if label not in functions.keys() and not is_available(container, label):
                raise RuntimeError(
                    "Requested column '" + label + "' can neither be found in the TTree nor in the fuctions"
                )

        df = pd.DataFrame()

        for label in content:

            if is_available(container, label):
                df[label] = get(container, label)

            if label in functions.keys():
                _load_column_with_function(label, df, container)

        # Finally we drop the original branches from the skim such that only what we want to have remains
        return df[content]

    return load_data


def make_tree_loader(content, functions={}):
    def is_available(tree, key):
        # Encode the branch names to binary strings because uproot gets them as binary strings unfortunately
        return key.encode("utf-8") in tree.keys()

    return make_data_loader(
        content, functions=functions, get=lambda tree, branch: tree.array(branch), is_available=is_available
    )
