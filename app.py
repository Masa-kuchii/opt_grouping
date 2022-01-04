import streamlit as st
import pandas as pd
import model

"""
# グループ分け最適化アプリ

オンライン飲み会の幹事や研修担当等に任命されたはいいものの、グループ分けでお困りではないでしょうか？  
このアプリを使えば、参加者情報を入力するだけで、以下のようなグループ分けを実現できます！  
- 参加者全員が新人と一度は話せるように複数回グループ分けを実施したい！
- 複数セッションで男女比はそろえつつ、メンバーの被りは減らしたい！
- 研修では同じ部署の人が被らないようにしたい！

"""

NUM_SESSION = "num_session"
NAME_COL = "name_col"
W_SESSION_DUP = "weight_session_duplicate"
VIP = "vip"
NUM_GROUP = "number_of_groups"


def input_data() -> pd.DataFrame:        
    st.header("Step1: 参加者情報の入力")
    st.write("以下のような参加者データを`csv形式`でアップロードしてください")
    st.info("参加者データはどこにも保存されませんのでご安心ください")
    sample_df = pd.DataFrame.from_dict(
        {"名前(必須)": ["田中さん", "鈴木さん", "佐藤さん", "藤原さん", "藤井さん"],"性別(オプション)": ["男", "女", "男", "女", "男"],"部署(オプション)": ["情報", "情報", "製造", "製造", "製造"]
        }
    )
    st.write(sample_df)
    f = st.file_uploader(label="", type = "csv")
    # st.write("アップロードされたファイル", f)
    # df = pd.read_csv(f, index = None)
    if f is not None:
        uploaded_df = pd.read_csv(f)
        st.dataframe(uploaded_df.head(20), width = 1000, height = 1000)
        return uploaded_df
    # TODD:ファイル形式の例外処理、NA処理    
    return None


def pre_process(data: pd.DataFrame):
    st.header("Step2: グループ分けの設定")
    if data is None:
        st.error("データをアップロードしてください")
        return None
    else:
        setting = {}
        cols = list(data.columns)
        # グループ数入力
        inp_num_group = st.number_input(label="グループ数を入力してください", min_value = 1, value=1)
        setting[NUM_GROUP] = inp_num_group
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
                input_vip_mem = st.multiselect(label = "主賓、ボス、先生など、全員と一度は話せるように特に重複がないように分けたい人はいますか？いればその人達を選んでください", options = mem_list)
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
        st.error("Step1のデータアップロード or Step2の設定を正しく実行してください")
        return None
    else:
        # st.write(data)
        # st.write(setting)
        if (st.button('最適化実行')):          
            results = model.main(data, setting)
            return results


def output_data(results):
    st.header("Step4: 結果の出力") 
    if (results is None):
        st.error("結果がありません")
        return None
    else:
        members = results[0]
        opt_result = results[1]
        for session_id, gourp_members in opt_result.items():
            st.subheader(str(session_id)+"回目")
            model.visualize_group(members, gourp_members)

def main():    
    data = input_data()
    setting = pre_process(data)
    results = optimize(data, setting)
    output_data(results)


if __name__=="__main__":
    main()


