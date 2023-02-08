import pandas
from io import StringIO


class FCSV:
    """
    FCSV Class for parsing .fcsv files.

    This class takes the path of a .fcsv file and parses its contents. The contents are separated into two parts: `entries` and `content_df`. `entries` is a list of strings that starts with "#" and `content_df` is a pandas dataframe of the remaining contents of the file, where each row represents a data point and each column represents a feature.

    Attributes:
        - path_fcsv (str): The path of the .fcsv file.
        - entries (list): A list of strings that start with "#".
        - content_df (pandas.DataFrame): A pandas dataframe of the remaining contents of the .fcsv file, where each row represents a data point and each column represents a feature.

    Methods:
        - parse_fcsv: Parse the .fcsv file and extract the entries and content_df.
    """

    def __init__(self, path_fcsv):
        self.path_fcsv = path_fcsv
        self.parse_fcsv()

    def parse_fcsv(self):
        with open(self.path_fcsv, "r") as loader:
            data = loader.read()

        data = data.splitlines()
        entries = [i for i in data if i.startswith("#")]
        entries = [i.replace("# ", "") for i in entries]
        content = [i for i in data if not i.startswith("#")]

        content = StringIO("\n".join(content))
        content_df = pandas.read_csv(content, sep=",")

        columns = [i for i in entries if i.startswith("columns")][0].replace("columns = ", "").split(",")

        # add columns to content_df
        content_df.columns = columns

        self.entries = entries
        self.content_df = content_df
