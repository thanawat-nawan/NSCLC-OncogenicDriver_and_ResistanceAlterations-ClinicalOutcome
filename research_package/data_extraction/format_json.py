import numpy as np

class FormatJSON:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def remove_data_missing(self):
        self.dataframe = self.dataframe[
            (self.dataframe['status'] == "Completed") &
            (self.dataframe['Code'].notnull())
        ].reset_index(drop=True)
        return self.dataframe

    def remove_unnecessary_data(self, analysis_columns):
        self.dataframe = self.dataframe[analysis_columns]
        return self.dataframe

    def filter_specimen(self, blood_specimens, tissue_specimens):
        self.dataframe = self.dataframe[
            (self.dataframe['type'].isin(blood_specimens)) |
            (self.dataframe['type'].isin(tissue_specimens))
        ]
        return self.dataframe

    def filter_diagnosis(self, non_small_cell_lung_cancer, lung_cancer, metastasis, squamous_cell_carcinoma):
        conditions = [
            (self.dataframe['Diag'].isin(non_small_cell_lung_cancer)),
            (self.dataframe['Diag'].isin(lung_cancer)),
            (self.dataframe['Diag'].isin(metastasis)),
            (self.dataframe['Diag'].isin(squamous_cell_carcinoma)),
        ]
        diagnosis_groups = [
            "Non small cell lung cancer",
            "Lung cancer",
            "Metastasis",
            "Squamous cell carcinoma"
        ]
        self.dataframe['diagnosis_group'] = np.select(conditions, diagnosis_groups, default='Other')
        self.dataframe = self.dataframe.drop(columns=['Diag'])
        return self.dataframe

    def create_patient_dictionary(self):
        code_dictionary = {}
        for i in range(self.dataframe.__len__()):
            try:
                code = self.dataframe['Code'][i]
            except KeyError:
                print(f"The code at row {i} was not found in the dataframe.")
                continue

            if code not in code_dictionary:
                code_dictionary[code] = {}
                code_dictionary[code]['count_times'] = 1
            else:
                code_dictionary[code]['count_times'] += 1

            time_n = "time_" + str(code_dictionary[code]['count_times'])
            code_dictionary[code][time_n] = {}
            time_n_templete = code_dictionary[code][time_n]

            time_n_templete['age'] = float(self.dataframe['Age'][i])
            time_n_templete['sex'] = self.dataframe['SEX'][i]
            time_n_templete['cost'] = float(self.dataframe['cost'][i])
            time_n_templete['specimen_type'] = self.dataframe['Specimen Type'][i]
            time_n_templete['source'] = self.dataframe['Source'][i]
            time_n_templete['tumor_percentage'] = float(self.dataframe['%tumor'][i]) * 100
            time_n_templete['diagnosis_group'] = self.dataframe['diagnosis_group'][i]

            # Match test with result in order
            for index, test in enumerate(self.dataframe['test'][i].split("&")):
                test = test.strip()
                time_n_templete[test] = []
                result_n = "Result" + str(index + 1)
                time_n_templete[test].append(self.dataframe[result_n][i])
        return code_dictionary