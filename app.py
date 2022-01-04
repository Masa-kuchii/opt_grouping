import streamlit as st
import pandas as pd
import model

"""
# グループ分け最適化アプリ

オンライン飲み会の幹事や研修担当等に任命されたはいいものの、グループ分けにお困りではないでしょうか？  
このアプリを使えば、参加者情報を入力するだけで、以下のようなグループ分けを実現できます！  
- 参加者全員が新人と一度は話せるように複数回グループ分けを実施したい！
- 複数セッションで男女比はそろえつつ、メンバーの被りは減らしたい！
- 研修では同じ部署の人が被らないようにしたい！

"""

NUM_SESSION = "num_session"
NAME_COL = "name_col"
W_SESSION_DUP = "weight_session_duplicate"
VIP = "vip_member_list"


def input_data() -> pd.DataFrame:        
    st.header("Step1: 参加者情報の入力")
    st.write("以下のような参加者データを`csv形式`でアップロードしてください")
    sample_df = pd.DataFrame.from_dict(
        {"名前(必須)": ["田中さん", "鈴木さん", "佐藤さん", "藤原さん"],"性別(オプション)": ["男", "女", "男", "女"],"主賓かどうか(オプション)": [1, 0, 0, 0],"部署(オプション)": ["情報", "情報", "製造", "製造"]
        }
    )
    st.write(sample_df)
    f = st.file_uploader(label="")
    st.info("参加者データはどこにも保存されませんのでご安心ください")
    # df = pd.read_csv(f, index = None)
    st.write("アップロードされたファイル", f)
    # TODD:ファイル形式の例外処理、NA処理    
    return sample_df


def pre_process(data: pd.DataFrame):
    st.header("Step2: グループ分けの設定")
    if data is None:
        st.error("データがアップロードしてください")
        return None
    else:
        setting = {}
        cols = list(data.columns)
        # セッション回数入力
        inp_num_session = st.number_input(label="グループ分けの回数(セッション数)を入力してください", 
        min_value = 1,
        value = 1)
        setting[NUM_SESSION] = inp_num_session
        # 名前列の選択
        inp_name_col = st.selectbox("参加者の名前が入った列を選んでください", 
        cols)
        mem_list = list(data[inp_name_col].unique())
        setting[NAME_COL] = inp_name_col
        #　重み設定
        if (inp_num_session > 1):
            w_sessions = {"重複させたい":-1, "どちらでも":0, "重複させたくない":1}
            w_sessions_keys = list(w_sessions.keys())
            input_w_session = st.select_slider(label="複数回セッションがある場合に、どの程度メンバーの重複をさせたいですか？", options = w_sessions_keys, value = w_sessions_keys[int(len(w_sessions_keys)/2)])
            setting[W_SESSION_DUP] = w_sessions[input_w_session]
            if (w_sessions[input_w_session] > 0):
                input_vip_mem = st.multiselect(label = "主賓、ボス、先生など、全員と一度は話せるように特に重複がないように分けたい人はいますか？いればその人を選んでください", options = mem_list)
                setting[VIP] = input_vip_mem
        # TODO：他の重み考える
        # for col in cols:
        #     if col is inp_name_col:
        #         continue
        #     else:
        #         w_normal = 
        return setting


def optimize(data: pd.DataFrame, setting):
    st.header("Step3: 最適化の実行")
    if (data is None) or (setting is None):
        st.error("データのセット or ルール決めが正しくありません")
        return None
    else:
        st.write(data)
        st.write(setting)
        if (st.button('最適化実行')):
            model.main()
        #TODO:プログレスバーを使う


def output_data(result):
    st.header("Step4: 結果の出力") 
    if (result is None):
        st.error("結果がありません")
        return None
    else:
        st.write(result)
# # 関数の出力をキャッシュする
# @st.cache
# def cached_data():
#     data = {
#         'x': np.random.random(20),
#         'y': np.random.random(20),
#     }
#     df = pd.DataFrame(data)
#     return df

def main():    
    data = input_data()
    setting = pre_process(data)
    result = optimize(data, setting)
    output_data(result)


if __name__=="__main__":
    main()


