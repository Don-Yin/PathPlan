import pandas
from io import StringIO


class FCSV:
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
