import os
from opencc import OpenCC
from tqdm import tqdm
import json
import wave
import torch
import wenetruntime as wenet

def streaming_decode(args, decoder):
    #print("Decoding...")

    tmp_wav = os.path.join(args.tmp_dir, 'tmp_{}.wav'.format(args.taskID))
    with wave.open(tmp_wav, 'rb') as fin:
        assert fin.getnchannels() == 1
        wav = fin.readframes(fin.getnframes())

    cc = OpenCC('s2t')
    all_decode_result = []
    interval = int(0.5 * 16000) * 2
    #for i in tqdm(range(0, len(wav), interval)):
    for i in range(0, len(wav), interval):
        f = open('data/.tmp_{}'.format(args.taskID), 'w')
        #print('data/.tmp_{}'.format(args.taskID))
        f.write(str(round((i + 1) * 100 / len(wav), 0)))
        f.close()

        last = False if i + interval < len(wav) else True
        chunk_wav = wav[i: min(i + interval, len(wav))]
        ans = decoder.decode(chunk_wav, last)
        try:
            ans = cc.convert(ans)
            ans = json.loads(ans)
            if ans['type'] == 'final_result':
                all_decode_result.append(ans)
        except json.decoder.JSONDecodeError:
            pass
    
    print("Done")
    return all_decode_result
