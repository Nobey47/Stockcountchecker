import pandas as pd
import numpy as np
import sys


pd.options.display.float_format = '{:.2f}'.format

class StockData:
    def __init__(self, dataframe):
        raw_data = dataframe.dropna(axis=0, thresh=10)

        colnames = []
        for col in raw_data.columns:
            colnames.append(col[0] + ' ' + col[1])
        raw_data.columns = colnames

        current_group = ''
        for ind in raw_data.index:
            if raw_data["Code No."][ind] != raw_data["Stock Description"][ind]:
                raw_data.at[ind, "Group"] = current_group
            else:
                current_group = raw_data.at[ind, "Stock Description"]
                raw_data = raw_data.drop(axis=0, index=ind)

        datatypes = {
            "Code No.": "string",
            "Stock Description": "string",
            "Case Size": "string",
            "Latest Cost": "float",
            "Open Qty": "float",
            "Goods In|Out": "float",
            "Transfers In|Out": "float",
            "Waste Qty": "float",
            "Close Qty": "float",
            "Actual Usage Qty": "float",
            "Sales Qty": "float",
            "Var Qty": "float",
            "Var Cost": "float",
            "Var LW Qty": "float",
            "Theo COS Excl Waste": "float",
            "Actual COS Incl Waste": "float",
            "Var Qty Incl Waste": "float",
            "Var Cost Inc Waste": "float",
            "Audit £": "float",
            "Group": "string"
        }

        self.data = raw_data.astype(datatypes)

    def analyze(self):
        analysis_text = '\n'
        # missing/too much
        self.data["Var Percent"] = self.data["Var Qty"]/self.data["Sales Qty"] * 100
        var_outliers = self.data.loc[((self.data["Var Percent"] <= -50) & (self.data["Group"] != "Actual = Theo Usage")) | ((self.data["Var Percent"] >= 50) & (self.data["Group"] != "Actual = Theo Usage"))]
        if len(var_outliers) >= 1:
            analysis_text = analysis_text + "These numbers look off. consider recounting\n\n"

            analysis_text = analysis_text + var_outliers[["Stock Description", "Case Size", "Close Qty", "Actual Usage Qty", "Sales Qty", "Var Cost", "Var Qty", "Var Percent"]].to_string(index=False) + '\n'

        analysis_text = analysis_text + "\n\n\n"

        # CoGs %
        self.data["CoGs Percent"] = (self.data["Goods In|Out"] - self.data["Actual Usage Qty"])/\
                                    self.data["Actual Usage Qty"] * 100
        CoGs_outliers = self.data.loc[(self.data["CoGs Percent"] >= 200) | (self.data["CoGs Percent"] <= -100)]
        if len(CoGs_outliers) >= 1:
            analysis_text = analysis_text + "These items appear to be ordered wrong. consider ordering less next week\n\n"

            analysis_text = analysis_text + CoGs_outliers[["Stock Description", "CoGs Percent"]].to_string(index=False) + '\n'

        analysis_text = analysis_text + "\n\n\n"

        # Negative Actual Usage
        negative_actual = self.data.loc[self.data["Actual Usage Qty"] < 0]
        if len(negative_actual) >= 1:
            analysis_text = analysis_text + "The actual usage for these items is negative. Consider recounting\n\n"

            analysis_text = analysis_text + negative_actual[["Stock Description", "Case Size", "Actual Usage Qty"]].to_string(index=False) + '\n'

        return analysis_text

    def save_to_csv(self, path):
        self.data["Var Percent"] = self.data["Var Qty"]/self.data["Sales Qty"] * 100
        self.data["CoGs Percent"] = (self.data["Goods In|Out"] - self.data["Actual Usage Qty"])/\
                                    self.data["Actual Usage Qty"] * 100
        try:
            self.data.to_csv(path)
        except Exception as ex:
            print(ex)
            return False
        else:
            return True

    def UPT(self, sales):
        self.data["UPT"] = (self.data["Actual Usage Qty"]/(sales/1000))
        self.data[["Stock Description", "Case Size", "UPT"]].to_csv("2023-01-22_UPT.csv", index=False)


if len(sys.argv) > 1:
    try:
        SD = StockData(pd.read_html(sys.argv[1])[0])
        print(SD.analyze())
    except Exception as ex:
        print(ex)

