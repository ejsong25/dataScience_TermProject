import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    classification_report,
    mean_absolute_error,
    r2_score,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# plot 한글 깨짐 방지
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 정규화된 월세 데이터셋 로드 (onehot encoding, district score method)
wolse_data_score = pd.read_csv("wolse_dataset_normalized_score.csv")
wolse_data_onehot = pd.read_csv("wolse_dataset_normalized_onehot.csv")


""" 
    regression (특정 조건(도로상태, 면적, 계약기간, 방 개수, 건물연식)에 따른 월세 예측)
"""
""" score method를 사용한 데이터셋 """

# independent variable와 target variable 설정
X = wolse_data_score.drop("monthly_rent_bill", axis=1)  # independent variables
y = wolse_data_score["monthly_rent_bill"]  # target variable (continuous)

# 데이터를 train_set와 test_set로 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    shuffle=True,
    random_state=None,
)

# Linear Regression 모델 생성 및 훈련
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

# 테스트 세트에 대한 예측 수행
y_pred = linear_model.predict(X_test)

# RMSE, R2 Score 계산
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean_Absolute_Error: {mae}, R2_Score: {r2}\n")

# 예측 결과 시각화
plt.scatter(y_test, y_pred, s=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], "r-", lw=1)
plt.xlabel("Actual Monthly Rent Bill")
plt.ylabel("Predicted Monthly Rent Bill")
plt.title("Linear Regression Plot(score method)")
plt.show()

""" onehot encoding method를 사용한 데이터셋 """

# independent variable와 target variable 설정
X = wolse_data_onehot.drop("monthly_rent_bill", axis=1)  # independent variables
y = wolse_data_onehot["monthly_rent_bill"]  # target variable (continuous)

# 데이터를 train_set와 test_set로 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    shuffle=True,
    random_state=None,
)

# Linear Regression 모델 생성 및 훈련
model = LinearRegression()
model.fit(X_train, y_train)

# 테스트 세트에 대한 예측 수행
y_pred = model.predict(X_test)

# RMSE, R2 Score 계산
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean_Absolute_Error: {mae}, R2_Score: {r2}\n")

# 예측 결과 시각화
plt.scatter(y_test, y_pred, s=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], "r-", lw=1)
plt.xlabel("Actual Monthly Rent Bill")
plt.ylabel("Predicted Monthly Rent Bill")
plt.title("Linear Regression Plot(onehot encoding)")
plt.show()


""" 
classification (월세를 특정 기준에 따라 분류) 
"""
""" score method를 사용한 데이터셋 """

# 월세의 mean, std 계산
monthly_rent_mean = wolse_data_score["monthly_rent_bill"].mean()
monthly_rent_std = wolse_data_score["monthly_rent_bill"].std()

# 수치형 레이블로 분류 기준 설정
criterion_labels = [
    0,  # 매우 저렴
    1,  # 저렴
    2,  # 보통
    3,  # 비쌈
    4,  # 매우 비쌈
]

# 월세를 분류 기준에 따라 범주화
"""
    very cheap: -inf ~ (monthly_rent_mean - 1.5 * monthly_rent_std)
    cheap: (monthly_rent_mean - 1.5 * monthly_rent_std) ~ (monthly_rent_mean - 0.5 * monthly_rent_std))
    appropriate: (monthly_rent_mean - 0.5 * monthly_rent_std) ~ (monthly_rent_mean + 0.5 * monthly_rent_std))
    expensive: (monthly_rent_mean + 0.5 * monthly_rent_std) ~ (monthly_rent_mean + 1.5 * monthly_rent_std))
    very expensive: (monthly_rent_mean + 1.5 * monthly_rent_std) ~ inf
"""
wolse_data_score["monthly_rent_bill_category"] = pd.cut(
    wolse_data_score["monthly_rent_bill"],
    bins=[
        -float("inf"),
        monthly_rent_mean - 1.5 * monthly_rent_std,
        monthly_rent_mean - 0.5 * monthly_rent_std,
        monthly_rent_mean + 0.5 * monthly_rent_std,
        monthly_rent_mean + 1.5 * monthly_rent_std,
        float("inf"),
    ],
    labels=criterion_labels,
    right=False,
)

# independent variable과 target variable 설정
X = wolse_data_score.drop(
    ["monthly_rent_bill", "monthly_rent_bill_category"], axis=1
)  # independent variables
y = wolse_data_score["monthly_rent_bill_category"]  # target variable

# 데이터를 train_set와 test_set로 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    shuffle=True,
    stratify=y,
    random_state=None,
)

# Decision Tree 모델 생성 및 훈련
dt_model = DecisionTreeClassifier()
dt_model.fit(X_train, y_train)

# test_set에 대한 예측 수행
y_pred = dt_model.predict(X_test)

# confusion matrix 생성 (모든 레이블 포함)
labels = np.arange(len(criterion_labels))
cm = confusion_matrix(y_test, y_pred, labels=labels).T
print(f"cm(score method)\n{cm}\n")

# Accuracy, Precision, Recall, F1 Score 계산
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted")
recall = recall_score(y_test, y_pred, average="weighted")
f1_ = f1_score(y_test, y_pred, average="weighted")

print(f"Decision_tree_Accuracy: {accuracy}")
print(f"Decision_tree_Precision: {precision}")
print(f"Decision_tree_Recall: {recall}")
print(f"Decision_tree_F1 Score: {f1_}")
print(classification_report(y_test, y_pred))

# Confusion Matrix 시각화
plt.figure(figsize=(10, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="viridis",
    xticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
    yticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
)
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Wolse Deposit Confusion Matrix (score method)")
plt.show()

# # 훈련된 결정 트리 모델의 트리 구조 시각화
# plt.figure(figsize=(20, 10))  # 그래프의 크기 조절
# plot_tree(
#     dt_model,
#     filled=True,
#     rounded=True,
#     class_names=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
#     feature_names=X_train.columns,
# )
# plt.title("Decision Tree Visualization")
# plt.show()

# 하이퍼파라미터 그리드 설정
param_grid = {
    "max_depth": [3, 4, 5, 6, 7, 8, 10, 12, 15],
    "min_samples_split": [2, 5, 10, 15, 20],
    "min_samples_leaf": [1, 2, 4, 6, 8],
    "criterion": ["gini", "entropy"],
}

# GridSearchCV 객체 생성
grid_search = GridSearchCV(
    estimator=dt_model,
    param_grid=param_grid,
    cv=5,
    verbose=1,
    scoring="accuracy",
)

# 그리드 탐색 실행
grid_search.fit(X_train, y_train)

# 최적의 하이퍼파라미터와 그 성능 출력
print("Best parameters:", grid_search.best_params_)
print("Best cross-validation score: {:.2f}".format(grid_search.best_score_))

# 최적의 모델로 예측 및 평가
best_dt = grid_search.best_estimator_
y_pred = best_dt.predict(X_test)
print(classification_report(y_test, y_pred))

# 최적화된 모델의 confusion matrix 시각화
cm_optimized = confusion_matrix(y_test, y_pred, labels=labels).T
print(f"cm_optimized(score method)\n{cm_optimized}\n")
plt.figure(figsize=(10, 6))
sns.heatmap(
    cm_optimized,
    annot=True,
    fmt="d",
    cmap="viridis",
    xticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
    yticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
)
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Optimized Decision Tree Confusion Matrix")
plt.show()

############################################################################################################
""" onehot encoding method를 사용한 데이터셋 """

# 월세의 mean, std 계산
monthly_rent_mean = wolse_data_onehot["monthly_rent_bill"].mean()
monthly_rent_std = wolse_data_onehot["monthly_rent_bill"].std()

# 수치형 레이블로 분류 기준 설정
criterion_labels = [
    0,  # 매우 저렴
    1,  # 저렴
    2,  # 보통
    3,  # 비쌈
    4,  # 매우 비쌈
]

# 월세를 분류 기준에 따라 범주화
"""
    very cheap: -inf ~ (monthly_rent_mean - 1.5 * monthly_rent_std)
    cheap: (monthly_rent_mean - 1.5 * monthly_rent_std) ~ (monthly_rent_mean - 0.5 * monthly_rent_std))
    appropriate: (monthly_rent_mean - 0.5 * monthly_rent_std) ~ (monthly_rent_mean + 0.5 * monthly_rent_std))
    expensive: (monthly_rent_mean + 0.5 * monthly_rent_std) ~ (monthly_rent_mean + 1.5 * monthly_rent_std))
    very expensive: (monthly_rent_mean + 1.5 * monthly_rent_std) ~ inf
"""
wolse_data_onehot["monthly_rent_bill_category"] = pd.cut(
    wolse_data_onehot["monthly_rent_bill"],
    bins=[
        -float("inf"),
        monthly_rent_mean - 1.5 * monthly_rent_std,
        monthly_rent_mean - 0.5 * monthly_rent_std,
        monthly_rent_mean + 0.5 * monthly_rent_std,
        monthly_rent_mean + 1.5 * monthly_rent_std,
        float("inf"),
    ],
    labels=criterion_labels,
    right=False,
)

# independent variable과 target variable 설정
X = wolse_data_onehot.drop(
    ["monthly_rent_bill", "monthly_rent_bill_category"], axis=1
)  # independent variables
y = wolse_data_onehot["monthly_rent_bill_category"]  # target variable

# 데이터를 train_set와 test_set로 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    shuffle=True,
    stratify=y,
    random_state=None,
)

# Decision Tree 모델 생성 및 훈련
dt_model = DecisionTreeClassifier()
dt_model.fit(X_train, y_train)

# test_set에 대한 예측 수행
y_pred = dt_model.predict(X_test)

# confusion matrix 생성 (모든 레이블 포함)
labels = np.arange(len(criterion_labels))
cm = confusion_matrix(y_test, y_pred, labels=labels).T
print(f"cm(onehot encoding)\n{cm}\n")

# Accuracy, Precision, Recall, F1 Score 계산
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted")
recall = recall_score(y_test, y_pred, average="weighted")
f1_ = f1_score(y_test, y_pred, average="weighted")

print(f"Decision_tree_Accuracy: {accuracy}")
print(f"Decision_tree_Precision: {precision}")
print(f"Decision_tree_Recall: {recall}")
print(f"Decision_tree_F1 Score: {f1_}")
print(classification_report(y_test, y_pred))

# Confusion Matrix 시각화
plt.figure(figsize=(10, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="viridis",
    xticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
    yticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
)
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Wolse Deposit Confusion Matrix (onehot encoding)")
plt.show()

# # 훈련된 결정 트리 모델의 트리 구조 시각화
# plt.figure(figsize=(20, 10))  # 그래프의 크기 조절
# plot_tree(
#     dt_model,
#     filled=True,
#     rounded=True,
#     class_names=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
#     feature_names=X_train.columns,
# )
# plt.title("Decision Tree Visualization")
# plt.show()

# 하이퍼파라미터 그리드 설정
param_grid = {
    "max_depth": [3, 4, 5, 6, 7, 8, 10, 12, 15],
    "min_samples_split": [2, 5, 10, 15, 20],
    "min_samples_leaf": [1, 2, 4, 6, 8],
    "criterion": ["gini", "entropy"],
}

# GridSearchCV 객체 생성
grid_search = GridSearchCV(
    estimator=dt_model,
    param_grid=param_grid,
    cv=5,
    verbose=1,
    scoring="accuracy",
)

# 그리드 탐색 실행
grid_search.fit(X_train, y_train)

# 최적의 하이퍼파라미터와 그 성능 출력
print("Best parameters:", grid_search.best_params_)
print("Best cross-validation score: {:.2f}".format(grid_search.best_score_))

# 최적의 모델로 예측 및 평가
best_dt = grid_search.best_estimator_
y_pred = best_dt.predict(X_test)
print(classification_report(y_test, y_pred))

# 최적화된 모델의 confusion matrix 시각화
cm_optimized = confusion_matrix(y_test, y_pred, labels=labels).T
print(f"cm_optimized(onehot encoding)\n{cm_optimized}\n")
plt.figure(figsize=(10, 6))
sns.heatmap(
    cm_optimized,
    annot=True,
    fmt="d",
    cmap="viridis",
    xticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
    yticklabels=["very cheap", "cheap", "appropriate", "expensive", "very expensive"],
)
plt.xlabel("Actual")
plt.ylabel("Predicted")
plt.title("Optimized Decision Tree Confusion Matrix")
plt.show()