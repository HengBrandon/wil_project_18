from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, \
    UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
import os
import pickle
import lime
import lime.lime_tabular
import numpy as np
from django.conf import settings as django_settings

from .models import *

module_dir = os.path.dirname(__file__)
model_dir = os.path.join(module_dir, 'models')
credit_score_model_file = os.path.join(model_dir, 'credit_score_classifier_model.pkl')
classifier = pickle.load(open(credit_score_model_file, 'rb'))

train_data_file = os.path.join(model_dir, 'out.csv')
train_data = np.loadtxt(train_data_file, delimiter=',')
target_name = ['0', '1', '2', '3', '4', '5']
feature_names = [
    'TotalMonthlyIncomeAmount',
    'LoanAcquisitionActualUPBAmt',
    'NumericPropertyType',
    'PropertyUnitCount',
    'FIPSStateNumericCode',
    'CensusTractMedFamIncomeAmount',
    'LTVRatioPercent',
    'ScheduledTotalPaymentCount',
    'NoteRatePercent',
    'TotalDebtExpenseRatioPercent',
    'HousingExpenseRatioPercent',
    'Borrower1AgeAtApplicationYears'
]

explainer = lime.lime_tabular.LimeTabularExplainer(train_data, feature_names=feature_names, class_names=target_name,
                                                   discretize_continuous=True)


def index(request):
    context = {
        'segment': 'index',
        # 'products' : Product.objects.all()
    }
    return render(request, "pages/index.html", context)


def tables(request):
    context = {
        'segment': 'tables'
    }
    return render(request, "pages/dynamic-tables.html", context)


def loan_predict(request):
    context = {
        'segment': 'loan_predict',
        # 'products' : Product.objects.all()
    }
    return render(request, "pages/predict-loan.html", context)


def sec_elem(s):
    print("sort")
    print(s, s[0], s[1])
    return s[1]


def predict_request(request):
    context = {
        'segment': 'loan_predict',
        # 'products' : Product.objects.all()
    }

    label_name_match = {
        'TotalMonthlyIncomeAmount': 'Total Monthly Income Amount',
        'LoanAcquisitionActualUPBAmt': 'Borrow Amount',
        'NumericPropertyType': 'Property Type',
        'PropertyUnitCount': 'Property Unit Count',
        'FIPSStateNumericCode': 'State Code',
        'CensusTractMedFamIncomeAmount': 'Census Tract Median Family Income Amount',
        'LTVRatioPercent': 'Loan-to-value ratio',
        'ScheduledTotalPaymentCount': 'Payment Periods (months)',
        'NoteRatePercent': 'Interest rate',
        'TotalDebtExpenseRatioPercent': 'Total Debt Expense Ratio Percent',
        'HousingExpenseRatioPercent': 'Housing Expense Ratio Percent',
        'Borrower1AgeAtApplicationYears': 'Borrower Age'
    }

    states_mean_income = {23: 90040.89,
                          25: 110320.88,
                          33: 104105.29,
                          9: 115383.69,
                          50: 79216.46,
                          36: 82857.15,
                          44: 94253.43,
                          6: 107706.51,
                          51: 128030.0,
                          45: 84415.26,
                          12: 85675.01,
                          13: 103628.87,
                          37: 91172.69,
                          26: 79675.59,
                          48: 99864.48,
                          8: 87018.3,
                          24: 116626.2,
                          17: 82661.87,
                          18: 80347.44,
                          29: 72200.17,
                          31: 84908.76,
                          55: 81258.31,
                          19: 80086.79,
                          27: 90981.78,
                          32: 85953.51,
                          47: 84169.97,
                          38: 91835.18,
                          39: 89316.27,
                          4: 90043.92,
                          1: 89559.29,
                          49: 88198.8,
                          28: 73576.24,
                          5: 81128.82,
                          46: 82281.4,
                          42: 81573.55,
                          34: 124013.34,
                          16: 71222.01,
                          30: 76482.88,
                          53: 101001.04,
                          22: 84007.88,
                          11: 129982.75,
                          21: 80265.97,
                          54: 57340.36,
                          40: 81211.21,
                          20: 80130.67,
                          56: 85770.26,
                          10: 97866.82,
                          35: 79716.52,
                          41: 71501.79,
                          2: 125996.33,
                          15: 92174.83
                          }
    if request.method == "POST":
        data = request.POST
        input_list = []
        for val in label_name_match:
            new_val = float(data.get(val))
            if val == 'LTVRatioPercent':
                new_val = (float(data.get('LoanAcquisitionActualUPBAmt')) / (float(
                    data.get('LoanAcquisitionActualUPBAmt')) + float(data.get(val)))) * 100

            if val == 'TotalDebtExpenseRatioPercent':
                new_val = (float(data.get(val)) / float(data.get('TotalMonthlyIncomeAmount'))) * 100

            if val == 'HousingExpenseRatioPercent':
                month = float(data.get('ScheduledTotalPaymentCount'))
                monthly_interest = (float(data.get('NoteRatePercent')) / 100 ) / 12
                principle = float(data.get('LoanAcquisitionActualUPBAmt'))
                monthly_house_payment = (principle * monthly_interest * pow((1 + monthly_interest), month))/ (pow((1 + monthly_interest), month) - 1)
                total_monthly_expense = monthly_house_payment + float(data.get('HousingExpenseRatioPercent'))
                new_val = (total_monthly_expense / float(data.get('TotalMonthlyIncomeAmount'))) * 100

            if val == 'CensusTractMedFamIncomeAmount':
                code = int(data.get("FIPSStateNumericCode"))
                new_val = states_mean_income[code]

            input_list.append(new_val)
        print("input_list")
        print(input_list)
        prediction = classifier.predict([input_list])
        np_input_list = np.array(input_list)
        exp = explainer.explain_instance(np_input_list, classifier.predict_proba, num_features=12, top_labels=1)
        result = prediction.tolist().pop()
        contributions = exp.as_map()[result]
        sorted_contributions = sorted(contributions, key=lambda tup: tup[1], reverse=True)
        dfns = exp.domain_mapper.discretized_feature_names
        reasons = {}
        count = 0
        for contribution in sorted_contributions:
            feature_name = feature_names[contribution[0]]
            if feature_name != 'FIPSStateNumericCode' and feature_name != 'CensusTractMedFamIncomeAmount' and count < 3:
                for dfn in dfns:
                    if feature_name in dfn:
                        reasons[feature_name] = dfn
                count += 1
        reason_string = {}
        count = 1
        for key, val in reasons.items():
            label = label_name_match[key]
            new_val = val.replace(key, label)
            reason_string[count] = new_val
            count += 1

        result = prediction.tolist().pop()
        context["prediction"] = result
        context["explains"] = reason_string

        banks_scores = {
            "Chicago Bank": {1: 0.0007, 2: 0.047, 3: 0.113, 4: 0.28, 5: 0.55},
            "Topeka Bank": {1: 0.005, 2: 0.041, 3: 0.103, 4: 0.28, 5: 0.57},
            "Indianapolis Bank": {2: 0.0005, 3: 0.07, 4: 0.32, 5: 0.61},
            "Des Moines Bank": {1: 0.0006, 2: 0.045, 3: 0.14, 4: 0.31, 5: 0.51},
            "Cincinnati Bank": {3: 0.06, 4: 0.27, 5: 0.66},
            "Pittsburgh Bank": {2: 0.04, 3: 0.14, 4: 0.32, 5: 0.50},
            "Dallas Bank": {2: 0.05, 3: 0.16, 4: 0.38, 5: 0.45},
            "Boston Bank": {2: 0.04, 3: 0.13, 4: 0.29, 5: 0.54},
            "New York Bank": {2: 0.006, 3: 0.06, 4: 0.28, 5: 0.65},
            "San Francisco Bank": {2: 0.05, 3: 0.29, 4: 0.43, 5: 0.23}
        }
        recommend_banks = {}
        for key, val in banks_scores.items():
            if result in val:
                recommend_banks[key] = val[result]

        sorted_recommend_banks = sorted(recommend_banks.items(), key=lambda x: x[1], reverse=True)[:3]
        sorted_recommend_banks = dict(sorted_recommend_banks)
        sorted_recommend_banks = {key: "{:.2f}% acceptance rate".format(value * 100) for key, value in
                                  sorted_recommend_banks.items()}
        context["recommend_banks"] = dict(sorted_recommend_banks)
    return render(request, "pages/predict-result.html", context)
