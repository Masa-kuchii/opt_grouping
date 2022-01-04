from simanneal import Annealer
from copy import deepcopy
from collections import defaultdict
from random import choice
import streamlit as st
import app


class GroupingProblem(Annealer):
    def __init__(self, init_state, num_same_team, num_team, num_members, members):
        # super(GroupingProblem, self).__init__(init_state)  # important!
        if init_state is not None:
            self.state = self.copy_state(init_state)
        else:
            raise ValueError('No valid values supplied for neither \
            init_state nor load_state')

        self.num_same_team = num_same_team
        self.num_team = num_team
        self.num_members = num_members
        self.members = members
 
    def move(self):
         
        # ランダムにa,bの２人選ぶ
        a = choice(range(self.num_members))
        b = choice(range(self.num_members))
        # 同一人物だった場合、何もせず終了(重cl複度の差分は0)
        if a == b:
            return 0
        # a,bそれぞれのチーム
        a_team = self.state[0][a]
        b_team = self.state[0][b]
        # ２人が同一チームだった場合、何もせず終了(重複度の差分は0)
        if a_team == b_team:
            return 0
         
        # 各チームのメンバー交換前の重複度
        cost_a_before = calc_team_cost(a_team, self.state[1], self.state[2], self.num_same_team)
        cost_b_before = calc_team_cost(b_team, self.state[1], self.state[2], self.num_same_team)
 
        # aのチームのaの部署の人数をデクリメント
        self.state[2][a_team][self.members[a][1]] -= 1
        # bのチームのbの部署の人数をデクリメント
        self.state[2][b_team][self.members[b][1]] -= 1
         
        # aのチームのリストからaを除く(効率悪いが横着)
        self.state[1][a_team].remove(a)
        # bのチームのリストからbを除く(効率悪いが横着)
        self.state[1][b_team].remove(b)
         
        # a,bの所属チームを交換
        self.state[0][a], self.state[0][b] = self.state[0][b], self.state[0][a]
 
        # aの新しいチームのaの部署の人数をインクリメント
        self.state[2][b_team][self.members[a][1]] += 1
        # bの新しいチームのbの部署の人数をインクリメント
        self.state[2][a_team][self.members[b][1]] += 1
         
        # aの新しいチームのリストにaを追加
        self.state[1][b_team].append(a)
        # bの新しいチームのリストにbを追加
        self.state[1][a_team].append(b)
         
        # 各チームのメンバー交換後の重複度
        cost_a_after = calc_team_cost(a_team, self.state[1], self.state[2], self.num_same_team)
        cost_b_after = calc_team_cost(b_team, self.state[1], self.state[2], self.num_same_team)
         
        # メンバー交換による重複度の差分を返す
        return cost_a_after - cost_a_before + cost_b_after - cost_b_before
         
         
     
    # 目的関数
    def energy(self):
        # 各チームの重複度の和を返す
        return sum(calc_team_cost(i, self.state[1], self.state[2], self.num_same_team) for i in range(self.num_team))


# チームtにおける重複度の計算（主賓とは被らないように！）
def calc_team_cost(t, team_to_members, department_count_by_team, num_same_team):
    g = 0
     
    # チームtに属するメンバー
    team = team_to_members[t]
     
    # チーム構成の重複度：過去にチームメンバー同士が同じチームになった回数 ** 2
    for i in range(len(team)):
        m1 = team[i]
        for j in range(i+1,len(team)):
            m2 = team[j]
            # 主賓と被っていると重み大きく
            if ((m1 < 2) or (m2 < 2)):
              g += (num_same_team[m1][m2]) * 10000
            else:
              g += num_same_team[m1][m2] ** 3 + num_same_team[m1][m2] * 10


    # 部署の重複度: 重複した人数の二乗
    d = 0
    for v in department_count_by_team[t].values():
        d += max(0,v-1)**2
    return g + d


# メンバー同士が同じチームに属した回数を記録
def record_num_same_team(num_same_team, team_to_member):
 
    num_same_team_next = deepcopy(num_same_team)
 
    for m in team_to_member:
        for i in range(len(m)):
            m1 = m[i]
            for j in range(i+1, len(m)):
                m2 = m[j]
                num_same_team_next[m1][m2] += 1
                num_same_team_next[m2][m1] += 1
    return num_same_team_next


def visualize_group(members, state_1, num_split_screen=3):
    team_bangou = 0
    for team in state_1:
        team_bangou += 1
        st.write("ルーム" + str(team_bangou), unsafe_allow_html=True)
        for id in team:
            st.write(" ", members[id][0])


def main(df, setting):
    # 設定
    df[app.VIP] = 0
    if app.VIP in setting.keys():
        for vip in setting[app.VIP]:
            df.loc[df[setting[app.NAME_COL]]==vip, app.VIP] = 1
    cols = [setting[app.NAME_COL], app.VIP] + [col for col in df.columns if col not in [setting[app.NAME_COL], app.VIP]]
    df = df.reindex(columns=cols)
    members = df.to_numpy().tolist()
    num_members = len(members)
    num_team = setting[app.NUM_GROUP]
    num_session = setting[app.NUM_SESSION]
    member_team = [ i % num_team for i in range(num_members)]
    num_same_team = [[0]*num_members for _ in range(num_members)]
    # 各チームのメンバー
    team_to_member = [[] for _ in range(num_team)]
    # 同じプロジェクトの人数
    department_count_by_team = [defaultdict(int) for _ in range(num_team)]
    for i in range(num_members):
        team_to_member[member_team[i]].append(i)
        department_count_by_team[member_team[i]][members[i][1]] += 1
    init_state = [member_team, team_to_member, department_count_by_team]
    status_text = st.empty()
    progress_bar = st.progress(0)
    result = {}
    # 最適化計算実行
    for i in range(num_session):
        percent = int(100/num_session*(i+1))
        status_text.text(f"Progress: {percent}%")
        progress_bar.progress(percent)
        prob = GroupingProblem(init_state, num_same_team, num_team, num_members, members)
        if (i==2):
            prob.steps = 10**5
        else:
            prob.steps = 10**5
        prob.copy_strategy = "deepcopy"
        state, e = prob.anneal()
        num_same_team = record_num_same_team(num_same_team, prob.state[1])
        result[str(i+1)] = state[1]
    status_text.text('Done!')
    st.balloons()
    return (members, result)

if __name__ == "__main__":
    main()