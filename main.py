from src.RFM import read_multi_csv
from src.RFM import recency, frequency, monetary, rfm_merge
from src.grade import get_rfm_grade, get_rfm_score, get_grade_range

path = "D:data"
ref_date = '2022-02-16'

# 데이터 불러오기
df = read_multi_csv(f'{path}/CRM', "utf-8")
df_r = recency(df[['ID', 'DT']], 'recency', ['ID'], 'DT', ref_date)
df_f = frequency(df[['ID', 'PRICE']], 'frequency', ['ID'], 'PRICE')
df_m = monetary(df[['ID', 'PRICE']], 'monetary', ['ID'], 'PRICE')

# 데이터 병합
rfm_df = rfm_merge(['ID'], df_r, df_f, df_m)
rfm_df.to_csv("rfm_df.csv", index=False)

# 등급화 방법 지정
rfm_tick_point = {
    'R': 'quantile',
    'F': 'quantile',
    'M': 'quantile',
}
# 등급화 대상 및 방법 매핑
rfm_col_map = {
    'R': 'recency',
    'F': 'frequency',
    'M': 'monetary',
}

# 등급화 계산
result = get_rfm_grade(df=rfm_df, num_class=10, rfm_tick_point=rfm_tick_point, rfm_col_map=rfm_col_map)

# 가중치 지정
rfm_weight_point = {
    'recency_R': 0.5,
    'frequency_F': 0.2,
    'monetary_M': 0.3,
}

# 점수 계산
result2 = get_rfm_score(result, rfm_weight_point)
result2.to_csv("result.csv", index=False)

# 범위 계산
m_range = get_grade_range(result[['monetary_M', 'monetary']], 'monetary_M')
print(m_range)
