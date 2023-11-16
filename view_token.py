import pickle

def view_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        credentials = pickle.load(file)
        #print(data.expiry)

        # Use vars() or __dict__ to get all attributes and their values
        credentials_dict = vars(credentials)
        # or credentials_dict = credentials.__dict__

        # Print or inspect the attributes
        for attribute, value in credentials_dict.items():
            print(f"{attribute}: {value}")


# Replace 'path/to/your/file.pickle' with the actual path to your pickle file
view_pickle_file('token.pickle')
