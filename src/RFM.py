from os import listdir
import pandas as pd
from tqdm import trange


def read_multi_csv(target_dir: str, enc: str = "cp949") -> pd.DataFrame:
    """
    경로에 있는 폴더를 읽어서 내부의 csv 파일을 불러와 합치는 기능.
    csv 파일들의 인코딩은 동일해야함.
    :param target_dir: str, 폴더을 읽어올 경로
    :param enc: str, 파일의 인코딩
    :return:
    """
    print(f'path: {target_dir}')
    # 폴더 안에 파일 목록을 생성하고 csv 파일 찾음
    dir_list = listdir(target_dir)
    dir_list = [_ for _ in dir_list if _.endswith(".csv")]

    temp_pd = pd.DataFrame([])

    for file in dir_list:
        target_file = f'{target_dir}/{file}'
        print(f'file: {target_file}', end=" => ")
        temp = pd.read_csv(target_file, encoding=enc, low_memory=False)
        print(f'{len(temp):,}')
        temp_pd = pd.concat([temp_pd, temp])
    print(f'누적 데이터 수:{len(temp_pd)}')

    return temp_pd


def group_cnt(g_list: pd.DataFrame, g_col: str, t_list: pd.DataFrame):
    for _ in g_list:
        temp = t_list[t_list[g_col] == _]
        print(f'{_}: {len(temp):,}')


def recency(data: pd.DataFrame, cre_col: str = 'Recency',
            ref_col: list = [], tg_col: str = [], ref_date: str = []) -> pd.DataFrame:
    """
    최신성 계산
    :param data: DataFrame, 대상 데이터
    :param ref_col: str, 참조할 컬럼, id나 식별 값에 해당하는 컬럼명
    :param tg_col: str, target_column 기준 컬럼, 날짜 컬럼에 해당하는 컬럼명
    :param ref_date: str, 기준 날짜
    :return: DataFrame, 최신성을 계산한 데이터 리턴
    """
    # 날짜 포맷 변경
    try:
        data[tg_col] = pd.to_datetime(data[tg_col], format='%Y%m%d')    # 참조 데이터 날짜
    except ValueError:
        data[tg_col] = pd.to_datetime(data[tg_col])  # 참조 데이터 날짜
    current_day = pd.to_datetime(ref_date)                          # 기준일
    
    # 날짜 순으로 오름차순 중복 제거하여 계산후 마지막 날짜만 남김
    data = data.sort_values(by=[tg_col])
    data = data.drop_duplicates(subset=ref_col, keep='last')
    data = data.reset_index(drop=True)
    print(len(data))
    
    # 기준점과의 차이를 계산, 일수 단위로 계산
    data[cre_col] = (data[tg_col] - current_day).dt.days - 16

    del data[tg_col]

    return data


def frequency(data: pd.DataFrame, cre_col: str = 'Frequency',
              ref_col: list = [], tg_col: str = []) -> pd.DataFrame:
    """
    빈도수 계산
    :param data: DataFrame, 대상 데이터
    :param ref_col: list, 참조할 컬럼, id나 식별 값에 해당하는 컬럼명
    :param tg_col: str, target_column 기준 컬럼, 날짜 컬럼에 해당하는 컬럼명
    :return: DataFrame, 빈도수를 계산한 데이터 리턴
    """
    # 기준 컬럼 기반으로 해당 컬럼의 빈도수 계산
    data = data.groupby(ref_col)[tg_col].count()
    # 인덱싱 및 컬럼 이름 재정의
    data = data.reset_index()
    data = data.rename(columns={tg_col: cre_col})

    return data


def monetary(data: pd.DataFrame, cre_col: str = 'Monetary',
             ref_col: list = [], tg_col1: str = [], tg_col2: str = None) -> pd.DataFrame:
    """
    누적 금액
    :param data: DataFrame, 대상 데이터
    :param ref_col: list, 참조할 컬럼, id나 식별 값에 해당하는 컬럼명
    :param tg_col1: str, 가격 컬럼, 누적 금액을 계산할 핵심 컬럼명
    :param tg_col2: str, 수량 컬럼, 누적 금액 계산의 보조 컬럼명, 수량이 없을 수 있음
    :return: DataFrame, 누적 금액이 계산된 데이터 리턴
    """
    main_key = dict([(col, len(data[[col]].drop_duplicates())) for col in ref_col])
    main_key = max(main_key.keys())

    temp_list = data.drop_duplicates(subset=ref_col, keep='last')
    temp_list = temp_list.reset_index(drop=True)
    monetary_data = []

    if tg_col2:
        # 수량이 있는 경우
        for i in trange(len(temp_list)):
            temp = data.query(f'{main_key}=="{temp_list[main_key][i]}"')
            amount = sum(temp[tg_col1] * temp[tg_col2])
            monetary_data.append(amount)
    else:
        # 수량이 없는 경우
        for i in trange(len(temp_list)):
            temp = data.query(f'{main_key}=="{temp_list[main_key][i]}"')
            amount = sum(temp[tg_col1])
            monetary_data.append(amount)

    temp_list[cre_col] = monetary_data

    del temp_list[tg_col1]

    return temp_list


def rfm_merge(keys: list, *args) -> pd.DataFrame:
    """
    테이블 머지
    :param keys: list, 병합에 키로 활용할 컬럼리스트
    :param args: pandas.DataFrame, 해당 키들로 병합할 대상의 데이터들
    :return: 병합된 결과물
    """

    rfm_df = args[0]
    for ls in args[1:]:
        rfm_df = pd.merge(rfm_df, ls, how='outer', on=keys)
    rfm_df = rfm_df.fillna(0)
    print(len(rfm_df))

    return rfm_df
