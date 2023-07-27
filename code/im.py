import pandas as pd
# p1 = pd.read_pickle('../../Dataset/Mixed/final_normal_dataset_with_health.pkl')
# p2 = pd.read_pickle('../../Dataset/Mixed/final_abnormal_dataset_with_health.pkl')
# print(p1)

# print(p2)
# print('is this a thing',pd.merge(p1,p2, 'inner'))
p1_n = pd.read_pickle('../../Dataset/New/final_preprocessed_normal.pkl')
p2_n =  pd.read_pickle('../../Dataset/Mixed/final_abnormal_dataset_with_health.pkl')
p1_a = pd.read_pickle('../../Dataset/New/final_preprocessed_abnormal.pkl')
p2_a = pd.read_pickle('../../Dataset/Mixed/final_normal_dataset_with_health.pkl')
p_normal = pd.concat([p1_n,p2_n],ignore_index=True)
p_abnormal = pd.concat([p1_a,p2_a],ignore_index=True)

p_normal.to_pickle('../../Dataset/New/normal_final_preprocessed_all_together.pkl')
p_abnormal.to_pickle('../../Dataset/New/abnormal_final_preprocecssed_all_togheter.pkl')
print(p_normal)
print(p_abnormal)