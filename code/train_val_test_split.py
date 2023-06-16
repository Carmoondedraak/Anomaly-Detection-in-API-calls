def split(data_n,data_a):
    '''split the data into 70-20-10'''
    
    train_n = data_n.sample(frac=0.70)
    train_a = data_a.sample(frac=0.70)
    int_n = data_n.drop(train_n.index)
    int_a = data_a.drop(train_a.index)
    val_n = int_n.sample(frac=0.2)
    val_a = int_a.sample(frac=0.2)
#     test_n = int_n.drop(val_n.index)
    test_a = int_a.drop(val_a.index)
    
    train = pd.concat([train_n,train_a], ignore_index=True)
#     validation = pd.concat([val_n,val_a], ignore_index=True)
#     test = pd.concat([val_n,val_a], ignore_index=True)
    return train

#     return train, validation, test
train = split(data_n_e,data_a_e)
print(train)
