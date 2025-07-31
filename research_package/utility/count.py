class Count:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.unique_item = {}

    def exact_unique_item(self):
        for column in self.dataframe.columns:
            if self.dataframe[column].dtype == 'object':
                self.dataframe[column] = self.dataframe[column].astype('str')
                try:
                    self.unique_item[column] = {}
                    for i in self.dataframe[column]:
                        if i != i:
                            self.unique_item[column] = self.unique_item[column].get("nan value", 0) + 1
                        else:
                            if i in self.unique_item[column]:
                                self.unique_item[column][i] += 1
                            else:
                                self.unique_item[column][i] = 1
                except TypeError as e:
                    print(f"The column {column} has an error: {e}")
        return self.unique_item