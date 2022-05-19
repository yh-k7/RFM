import numpy as np
import pandas as pd
from sklearn import preprocessing


def get_score(level, data) -> list:
    """
    주어진 기준에 따라 데이터에 점수를 매겨주는 함수.
    level안에 있는 원소를 기준으로
    1 ~ len(level)+ 1 까지 점수를 부여하는 함수
    :param level: 튜플 또는 리스트 타입의 숫자형 데이터이며 반드시 오름차순으로 정렬되어 있어야함.
    예 - [1,2,3,4,5] O, [5,4,3,2,1] X, [1,3,2,10,4] X
    :param data: 점수를 부여할 데이터. 순회가능한(iterable) 데이터 형식
    :return: 점수를 담고 있는 리스트 반환
    """
    score = []

    for j in range(len(data)):
        for i in range(len(level)):
            if data[j] <= level[i]:
                score.append(i + 1)
                break
            elif data[j] > max(level):
                score.append(len(level) + 1)
                break
            else:
                continue

    return score


def get_rfm_grade(df: pd.DataFrame, num_class: int, rfm_tick_point: dict, rfm_col_map: dict, suffix=None) -> pd.DataFrame:
    """
    개별 고객에 대한 최근방문일/방문횟수/구매금액 데이터가 주어졌을때
    최근방문일/방문횟수/구매금액 점수를 계산하여 주어진 데이터 오른쪽에 붙여줍니다.
    :param df: pandas.DataFrame 데이터
    :param num_class: 등급(점수) 개수
    :param rfm_tick_point: 최근방문일/방문횟수/구매금액에 대해서 등급을 나눌 기준이 되는 값
                    'quantile', 'min_max' 또는 리스트를 통하여 직접 값을 정할 수 있음.
                    단, 리스트 사용시 원소의 개수는 반드시 num_class - 1 이어야함.
                    quatile = 데이터의 분위수를 기준으로 점수를 매김
                    min_max = 데이터의 최소값과 최대값을 동일 간격으로 나누어 점수를 매김
    :param rfm_col_map: 최근방문일/방문횟수/구매금액에 대응하는 칼럼명
    예 - {'R':'Recency','F':'Frequency','M':'Monetary'}
    :param suffix: 최근방문일/방문횟수/구매금액에 대응하는 칼럼명 뒤에 붙는 접미사
    :return: pandas.DataFrame
    """
    # 파라미터 체크
    # 데이터는 pd.DataFrame이어야 함.
    if not isinstance(df, pd.DataFrame):
        print('데이터는 pandas.DataFrame 객체여야 합니다.')
        return

    # rfm_tick_point와 rfm_col_map은 모두 딕셔너리
    if isinstance(rfm_tick_point, dict) == False or isinstance(rfm_col_map, dict) == False:
        print(f'rfm_tick_point와 rfm_col_map은 모두 딕셔너리여야합니다.')
        return

    # rfm_tick_point와 rfm_col_map은 같은 키를 가져야함.
    if set(rfm_tick_point.keys()) != set(rfm_col_map.keys()):
        print(set(rfm_tick_point.keys()))
        print(set(rfm_col_map.keys()))
        print(f'rfm_tick_point와 rfm_col_map은 같은 키를 가져야 합니다.')
        return

    if not set(rfm_col_map.values()).issubset(set(df.columns)):
        not_in_df = set(rfm_col_map.values()) - set(df.columns)
        print(f'{not_in_df}이 데이터 칼럼에 있어야 합니다.')
        return

    for k, v in rfm_tick_point.items():
        if isinstance(v, str):
            if not v in ['quantile', 'min_max']:
                print(f'{k}의 값은 "quantile" 또는 "min_max"중에 하나여야 합니다.')
                return
        elif isinstance(v, list) or isinstance(v, tuple):
            if len(v) != num_class - 1:
                print(f'{k}에 대응하는 리스트(튜플)의 원소는 {num_class - 1}개여야 합니다.')
                return

    if suffix:
        if not isinstance(suffix, str):
            print('suffix인자는 문자열이어야합니다.')
            return

    # 최근방문일/방문횟수/구매금액 점수 부여
    for k, v in rfm_tick_point.items():
        if isinstance(v, str):
            # 데이터 변환
            if v == 'quantile':
                # 분위수
                scale = preprocessing.StandardScaler()  # 데이터의 범위 조작하기 쉽게 해주는 클래스
                temp_data = np.array(df[rfm_col_map[k]])  # 데이터를 Numpy 배열로 변환
                temp_data = temp_data.reshape((-1, 1))  # scale을 적용하기위해 1차원 배열을 2차원으로 변환
                temp_data = scale.fit_transform(temp_data)  # 데이터를 평균은 0, 표준편차는 1을 갖도록 변환
                temp_data = temp_data.squeeze()  # 데이터를 다시 1차원으로 변환

                # 분위수를 구할 기준값을 지정 0과 1은 제외
                quantiles_level = np.linspace(0, 1, num_class + 1)[1:-1]
                quantiles = []
                for ql in quantiles_level:
                    # 분위수를 계산하고 리스트에 삽입
                    quantiles.append(np.quantile(temp_data, ql))
            else:
                # min_max인 경우
                temp_data = np.array(df[rfm_col_map[k]])

                # 등분점 계산
                # 최소값과 최대값을 점수 개수만큼 등간격으로 분할하는 점
                quantiles = np.linspace(np.min(temp_data), np.max(temp_data), num_class + 1)[1:-1]
        else:
            # 직접 구분 값을 지정하는 경우
            temp_data = np.array(df[rfm_col_map[k]])
            quantiles = v
        score = get_score(quantiles, temp_data)
        new_col_name = rfm_col_map[k] + '_' + k  # 점수값을 담는 변수의 이름
        if suffix:
            new_col_name = rfm_col_map[k] + '_' + suffix
        df[new_col_name] = score
    return df


def get_rfm_score(df: pd.DataFrame, weight_point: dict) -> pd.DataFrame:
    """
    인자의 가중치별 등급 합산
    :param df: pd.DataFrame, 대상 데이터
    :param weight_point: dict, 인자별 가중치 값에 대한 map
    :return: pd.DataFrame
    """
    df["sum"] = sum([df[key] for key, val in weight_point.items()])
    df["score"] = sum([df[key] * val for key, val in weight_point.items()])
    return df


def get_grade_range(data: pd.DataFrame, ref_col: str) -> pd.DataFrame:
    """
    등급별 실제 값 범위를 구하는 함수
    :param data: pd.DataFrame, 대상 데이터 (등급, 실제값)
    :param ref_col: str, 등급 컬럼명, groupby할 컬럼명
    :return: pd.DataFrame
    """
    temp = data.groupby(ref_col).agg(['min', 'max', 'count'])
    return temp
