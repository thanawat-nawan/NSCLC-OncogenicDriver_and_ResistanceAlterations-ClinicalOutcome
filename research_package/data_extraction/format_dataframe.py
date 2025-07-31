import numpy as np
import pandas as pd
from cryptography.fernet import Fernet

class FormatDataFrame:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.patient_dictionary = {}

    def remove_data_missing_with_reset_index(self):
        self.dataframe = self.dataframe[
            (self.dataframe['status'] == "Completed") &
            (self.dataframe['Code'].notnull())
        ] \
            .reset_index(drop=True)
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
        for i in range(self.dataframe.__len__()):
            try:
                code = self.dataframe['Code'][i]
            except KeyError:
                print(f"The code at row {i} was not found in the dataframe.")
                continue

            if code not in self.patient_dictionary:
                self.patient_dictionary[code] = {}
                self.patient_dictionary[code]["times"] = {}
                self.patient_dictionary[code]['count_times'] = 1
            else:
                self.patient_dictionary[code]['count_times'] += 1

            time_n = "time_" + str(self.patient_dictionary[code]['count_times'])
            self.patient_dictionary[code]["times"][time_n] = {}
            time_n_template = self.patient_dictionary[code]["times"][time_n]

            time_n_template['age'] = float(self.dataframe['Age'][i])
            time_n_template['sex'] = self.dataframe['SEX'][i]
            time_n_template['cost'] = float(self.dataframe['cost'][i])
            time_n_template['specimen_type'] = self.dataframe['Specimen Type'][i]
            time_n_template['source'] = self.dataframe['Source'][i]
            time_n_template['tumor_percentage'] = float(self.dataframe['%tumor'][i]) * 100
            time_n_template['diagnosis_group'] = self.dataframe['diagnosis_group'][i]

            # Match test with result in order
            for index, test in enumerate(self.dataframe['test'][i].split("&")):
                test = test.strip().rstrip(" ")
                result_n = "Result" + str(index + 1)
                gene_result = self.dataframe[result_n][i]
                # Remove nan, Invalid, แปรผลไม่ได้, ไม่สามารถแปรผลได้
                # Otherwise append result
                remove_list = ["nan", "Invalid", "แปลผลไม่ได้", "ไม่สามารถแปลผลได้"]
                if gene_result in remove_list:
                    continue
                else:
                    time_n_template[test] = []
                    time_n_template[test].append(gene_result)

        return self.patient_dictionary

    def create_normalize_dataframe(self, encryption=True):
        records = []
        key = Fernet.generate_key()
        fernet = Fernet(key)
        for record_id, record_data in self.patient_dictionary.items():
            # Extract 'count_times' and 'times'
            count_times = record_data.get('count_times')
            times_data = record_data.get('times', {})

            # Iterate through each 'time_n' entry within the 'times' dictionary
            for time_label, time_details in times_data.items():
                # Combine the top-level ID, count_times, the time_label,
                # and the details from the current 'time_n' entry
                if encryption:
                    encrypted_record_id = fernet.encrypt(record_id.encode())
                else:
                    encrypted_record_id = record_id
                combined_record = {
                    'id': encrypted_record_id,
                    'count_times': count_times,
                    'time_label': time_label,
                    **time_details
                }
                records.append(combined_record)
        normalized_df = pd.json_normalize(records)
        return normalized_df