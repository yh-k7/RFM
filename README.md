# RFM
RFM

### 데이터 만들기
- 지정 폴더 안의 모든 데이터 읽어와서 병합
- R, F, M 값 계산
- 계산한 값 하나의 데이터로 합치기
```
df = read_multi_csv(f'{path}/CRM', "utf-8")

df_r = recency(df[['ID', 'DT']], 'recency', ['ID'], 'DT', ref_date)
df_f = frequency(df[['ID', 'DT']], 'frequency', ['ID'], 'DT')
df_m = monetary(df[['ID', 'PRICE']], 'monetary', ['ID'], 'PRICE')

rfm_df = rfm_merge(['ID'], df_r, df_f, df_m)
```

### 등급화
- 등급화 방법 지정
- 등급화 대상 및 방법 매핑
- 등급화 계산
```
rfm_tick_point = {
    'R': 'quantile',
    'F': 'quantile',
    'M': 'quantile',
}

rfm_col_map = {
    'R': 'recency',
    'F': 'frequency',
    'M': 'monetary',
}

result = get_rfm_grade(df=rfm_df, num_class=10, rfm_tick_point=rfm_tick_point, rfm_col_map=rfm_col_map)
```

### 점수 계산
- 가중치 지정
- 점수 계산
```
rfm_weight_point = {
    'recency_R': 0.5,
    'frequency_F': 0.2,
    'monetary_M': 0.3,
}

result = get_rfm_score(result, rfm_weight_point)
```

### 번외
- 등급별 범위 계산
```
r_range = get_grade_range(result[['recency_R', 'recency']], 'recency_R')
f_range = get_grade_range(result[['frequency_F', 'frequency']], 'frequency_F')
m_range = get_grade_range(result[['monetary_M', 'monetary']], 'monetary_M')
```
