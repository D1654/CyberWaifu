#!/usr/bin/env python
# coding: utf-8
from torch import no_grad, LongTensor

from . import commons
from . import utils
from .models import SynthesizerTrn
from .text import text_to_sequence
from .text import symbols
from scipy.io.wavfile import write

def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, [])
    else:
        text_norm = text_to_sequence(text, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


model = "VITS_GENSHIN/models/Genshin.pth"
config = "VITS_GENSHIN/configs/genshin.json"
hps_ms = utils.get_hparams_from_file(config)
net_g_ms = SynthesizerTrn(
    len(symbols),
    hps_ms.data.filter_length // 2 + 1,
    hps_ms.train.segment_size // hps_ms.data.hop_length,
    n_speakers=hps_ms.data.n_speakers,
    **hps_ms.model)
_ = net_g_ms.eval()
utils.load_checkpoint(model, net_g_ms)


def Trans_GS(text = "前面的区域，以后再来探索吧。",speaker_id=0,out_path='voice.wav'):
    stn_tst = get_text(text, hps_ms)
    #print_speakers(hps_ms.speakers)
    with no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = LongTensor([stn_tst.size(0)])
        sid = LongTensor([speaker_id])
        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8, length_scale=1)[0][0,0].data.cpu().float().numpy()
    write(out_path, hps_ms.data.sampling_rate, audio)
    print('voice Successfully saved!')