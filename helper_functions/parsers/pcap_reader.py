import pcapkit
import pandas as pd
# # extraction = pcapkit.extract(fin='in.pcap', store=False, nofile=True, http=True, strict=True)
# extraction = pcapkit.extract(fin='../network.pcap', fout='out.json', format='json', extension=False)
# frame0 = extraction.frame[0]
# # check if IP in this frame, otherwise ProtocolNotFound will be raised
# for packet in extraction.reassembly.tcp:
#     for reassembly in packet.packets:
#         if pcapkit.HTTP in reassembly.protochain:
#             print(reassembly.info)
import pyshark




filtered_cap = pyshark.FileCapture('../network2.pcap', display_filter='http')

cap_dict = {}
for i, cap in enumerate(filtered_cap):
    feats = {}
    for j, feat in enumerate(cap.http.field_names):
        
        if feat == '':
            pass
        else:
            feats[cap.http.field_names[j]] = getattr(cap.http, feat)

    cap_dict[i] = feats

df = pd.DataFrame(data=cap_dict).T
df.to_pickle('out.pkl')
df.to_csv('out.csv', index=False)
print(df)

