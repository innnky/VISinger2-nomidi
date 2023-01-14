import librosa
import numpy as np

from text import npu

def resize2d_f0(x, target_len):
    source = np.array(x)
    source[source < 0.001] = np.nan
    target = np.interp(np.arange(0, len(source) * target_len, len(source)) / target_len, np.arange(0, len(source)),
                       source)
    res = np.nan_to_num(target)
    return res


def preprocess(ds):
    note_list = ds["note_seq"]
    midis = [librosa.note_to_midi(x.split("/")[0]) if x != 'rest' else 0
                         for x in note_list.split(" ")]
    f0_seq = None
    if ds["f0_seq"] is not None:
        f0_seq = [float(i.strip()) for i in ds["f0_seq"].split(" ")]
        f0_seq = np.array(f0_seq)
    phseq = ds["ph_seq"].split(" ")
    newphseq = []
    for ph in phseq:
        newphseq.append(npu.ttsing_phone_to_int[ph])
    phseq = newphseq
    phseq = np.array(phseq)
    pitch = 440 * (2 ** ((np.array(midis) - 69) / 12))
    durations = [float(i) for i in ds["ph_dur"].split(" ")]
    accu_dur = 0
    accu_durs = []
    for dur in durations:
        accu_dur += dur
        accu_durs.append(accu_dur)
    accu_durs = np.array(accu_durs)
    accu_durs = (accu_durs * 44100 // 512).astype(int)
    sub_durs = np.zeros_like(accu_durs)
    sub_durs[1:accu_durs.shape[0]] = accu_durs[:accu_durs.shape[0]-1]
    durations = accu_durs-sub_durs
    f0_seq = resize2d_f0(f0_seq, sum(durations))
    pos = 0
    for i, d in enumerate(durations):
        if phseq[i] == 0:
            f0_seq[pos:pos + d] = 0
        pos += d

    return f0_seq,pitch, phseq, durations

if __name__ == '__main__':
    inp = {
        "text": "SP 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 SP 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 SP 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 啊 SP",
        "ph_seq": "SP x ing z ou z ai w ei x ian b ian y van s i0 y i d e g uai d ao SP z i0 y ou d e t iao zh e zh ir j ian sh ang d e w u d ao SP q ing y ing d e x iang an y ing zh ong c ang f u d e b o s i0 m ao d eng d ai x ia y i g e m u u b iao SP",
        "note_seq": "rest D5 D5 B4 B4 D5 D5 G5 G5 D5 D5 C5 C5 B4 B4 A#4 A#4 A4 A4 G4 G4 D4 D4 G4 G4 rest D5 D5 B4 B4 D5 D5 G5 G5 D5 D5 C5 C5 B4 B4 C5 C5 C5 C5 G5 G5 C5 C5 rest D5 D5 B4 B4 D5 D5 G5 G5 D5 C5 C5 B4 B4 A#4 A#4 A#4 A#4 A#4 A#4 A#4 A#4 A#4 A#4 G4 G4 D4 D4 G4 G4 F4 F4 G4 G4 A#4 A#4 C5 C5 C#5 D5 D5 rest",
        "note_dur_seq": "0.6 0.136 0.136 0.137 0.137 0.545 0.545 0.546 0.546 0.2720001 0.2720001 0.273 0.273 0.273 0.273 0.2719998 0.2719998 0.546 0.546 0.5450001 0.5450001 0.2730002 0.2730002 0.4089999 0.4089999 0.1370001 0.1359997 0.1359997 0.1360002 0.1360002 0.546 0.546 0.5450001 0.5450001 0.2729998 0.2729998 0.2730002 0.2730002 0.2719998 0.2719998 0.546 0.546 0.2730002 0.2730002 0.5449996 0.5449996 0.6820002 0.6820002 0.1359997 0.1370001 0.1370001 0.1360006 0.1360006 0.5450001 0.5450001 0.5459995 0.5459995 0.2729998 0.2720003 0.2720003 0.2729998 0.2729998 0.3640003 0.3640003 0.1809998 0.1809998 0.3640003 0.3640003 0.1820002 0.1820002 0.3639994 0.3639994 0.1810007 0.1810007 0.3639994 0.3639994 0.1820002 0.1820002 0.4090004 0.4090004 0.4089994 0.4089994 0.2729998 0.2729998 0.2720003 0.2720003 0.5460005 0.8179989 0.8179989 0.5",
        "is_slur_seq": "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0",
        "ph_dur": "0.3875 0.2125 0.070091 0.065909 0.082455 0.054545 0.474545 0.070455 0.339182 0.206818 0.244727 0.027273 0.207091 0.065909 0.163909 0.109091 0.272 0 0.442591 0.103409 0.447273 0.097727 0.224137 0.048864 0.409 0.088136 0.048864 0.070091 0.065909 0.081455 0.054545 0.452818 0.093182 0.37 0.175 0.103682 0.169318 0.115046 0.157955 0.1845 0.0875 0.475545 0.070455 0.273 0 0.506363 0.038636 0.682 0.054182 0.081818 0.076773 0.060227 0.097364 0.038636 0.354091 0.190909 0.546 0.202545 0.070455 0.168591 0.103409 0.218454 0.054545 0.2765 0.0875 0.148045 0.032955 0.325364 0.038636 0.067227 0.114773 0.270818 0.093182 0.148046 0.032955 0.286727 0.077273 0.057 0.125 0.409 0 0.381727 0.027273 0.152545 0.120455 0.272 0.441653 0.104348 0.817999 0.5",
        "f0_timestep": "0.005",
        "f0_seq": "587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.2 587.0 586.9 586.7 586.1 585.4 584.8 584.1 583.4 582.9 582.5 582.3 582.5 582.9 583.4 584.1 584.9 585.5 586.1 586.7 587.0 587.3 587.6 587.9 588.0 588.1 588.4 588.7 588.7 588.7 588.0 586.4 584.1 580.8 575.8 568.7 560.8 552.0 540.9 531.0 522.2 513.8 506.6 501.7 497.9 495.0 493.8 493.0 492.6 492.6 492.7 492.7 492.7 492.7 492.7 492.5 492.6 493.2 494.1 495.6 498.7 502.5 507.6 515.5 523.9 532.9 543.2 553.7 562.4 570.3 577.2 581.7 584.6 586.9 588.2 588.7 588.7 588.6 588.3 588.1 588.0 587.8 587.5 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.2 586.9 586.7 587.0 587.0 587.0 587.0 587.5 588.7 590.8 594.1 599.0 607.7 617.7 630.6 647.9 667.1 686.3 706.4 727.1 743.0 755.2 765.1 773.3 778.6 781.6 783.4 784.4 784.4 784.4 784.4 784.7 784.7 784.3 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.1 784.5 784.9 784.4 784.4 784.4 784.4 783.8 782.3 779.9 775.1 768.7 759.5 747.9 731.5 712.9 694.2 674.0 652.5 636.1 622.4 610.1 601.9 596.0 591.8 589.1 587.8 587.0 587.0 587.0 587.0 586.8 586.8 587.1 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.6 587.9 588.0 588.1 588.5 589.1 589.4 589.4 589.1 588.4 586.8 584.5 581.2 575.9 570.6 564.1 556.0 548.8 542.3 536.2 531.1 527.3 524.8 522.6 521.9 521.5 521.4 521.6 521.9 522.4 522.6 522.6 522.9 523.2 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.6 523.9 524.1 524.4 524.8 525.4 525.8 526.0 526.2 525.7 524.9 523.3 521.1 518.6 515.3 511.3 507.6 504.0 499.9 497.3 495.0 493.1 492.0 491.4 491.1 491.4 491.6 492.1 492.6 492.9 493.2 493.4 493.7 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 494.1 494.3 494.5 494.8 495.1 495.6 496.1 496.4 496.6 496.5 495.8 494.7 493.2 491.0 487.9 484.7 481.2 477.3 473.8 470.9 468.4 466.2 464.8 464.1 463.6 463.7 463.9 464.2 464.7 465.1 465.4 465.6 465.8 466.1 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.4 466.7 466.9 467.2 467.5 468.0 468.4 468.6 468.9 468.3 467.6 466.4 464.4 462.0 459.3 456.0 452.2 449.0 446.0 443.1 441.0 439.5 438.5 437.9 437.5 437.7 437.9 438.4 438.8 439.1 439.3 439.6 439.8 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.0 440.3 440.5 440.5 440.7 441.0 441.4 441.5 441.5 441.3 440.6 439.1 437.0 434.2 430.6 426.3 420.5 415.3 410.1 404.6 400.5 397.2 394.5 392.6 391.4 390.9 390.6 390.6 390.8 391.1 391.4 391.5 391.6 391.8 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.2 392.4 392.3 392.2 392.2 392.2 392.1 391.5 390.6 388.6 385.6 381.6 375.9 368.3 360.1 351.0 339.3 329.8 321.3 313.1 306.8 302.4 298.9 296.3 294.9 294.1 293.7 293.5 293.5 293.5 293.5 293.4 293.5 293.6 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.6 293.5 293.4 293.5 293.5 293.5 293.5 293.7 294.3 295.4 297.0 299.5 303.8 308.9 315.3 323.9 333.6 343.2 353.2 363.5 371.5 377.6 382.5 386.6 389.3 390.8 391.7 392.2 392.2 392.2 392.2 392.4 392.3 392.1 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 391.8 391.8 391.6 391.3 390.9 390.5 390.1 389.5 389.1 388.9 389.1 389.6 390.3 391.2 392.8 394.5 397.0 400.6 405.3 411.1 419.5 431.0 443.7 458.9 479.8 497.9 515.2 532.6 546.7 557.1 565.4 571.7 575.6 577.8 579.1 580.0 580.4 580.8 581.5 582.7 582.9 583.5 584.4 585.1 585.6 586.2 586.8 587.0 587.3 587.7 588.0 588.0 588.2 588.5 588.7 588.7 588.5 587.7 586.3 583.3 579.0 573.7 567.1 558.7 548.3 538.6 529.1 519.2 511.5 505.6 500.7 496.9 494.8 493.6 492.7 492.5 492.6 492.7 492.7 492.7 492.7 492.7 492.5 492.7 493.3 494.5 496.5 499.4 503.7 510.1 517.2 525.5 536.3 546.3 555.5 564.6 572.6 578.1 582.6 585.6 587.3 588.3 588.7 588.7 588.6 588.3 588.0 588.0 587.7 587.4 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.1 586.8 586.8 587.0 587.0 587.0 587.0 587.8 589.1 591.4 595.5 601.9 609.7 619.7 636.1 652.5 670.9 692.6 712.9 730.2 745.9 759.5 768.7 775.1 779.9 782.3 783.8 784.4 784.4 784.4 784.4 784.8 784.5 784.1 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.2 784.6 784.7 784.4 784.4 784.4 784.4 783.5 781.7 778.6 773.8 766.5 755.2 743.0 727.1 706.4 686.3 667.1 649.2 632.8 617.7 607.7 600.4 594.3 590.8 588.9 587.6 587.0 587.0 587.0 587.0 586.7 586.9 587.2 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.7 588.0 588.0 588.2 588.7 589.1 589.4 589.3 589.0 588.2 586.1 583.4 579.6 574.8 569.0 561.3 554.4 547.5 540.1 534.7 530.2 526.6 524.1 522.5 521.7 521.4 521.4 521.6 522.1 522.5 522.6 522.7 523.0 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.4 523.7 523.9 524.2 524.5 525.0 525.6 525.9 526.1 526.1 525.5 524.5 522.9 520.7 517.6 514.2 510.6 506.6 502.6 499.4 496.7 494.2 492.7 491.9 491.3 491.2 491.4 491.7 492.3 492.7 493.0 493.2 493.5 493.7 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.6 493.4 493.1 492.9 492.6 492.1 491.6 491.3 491.1 491.5 492.2 493.3 495.2 497.8 500.6 504.0 508.4 512.0 515.6 518.9 521.6 523.6 524.9 525.8 526.3 526.0 525.8 525.3 524.8 524.4 524.1 523.8 523.6 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.5 523.8 524.0 524.4 525.0 525.5 526.0 526.9 527.4 527.7 527.8 527.5 527.0 526.4 525.5 524.5 523.5 522.4 521.3 520.4 519.7 519.2 518.7 518.7 519.0 519.5 520.2 520.8 521.4 521.9 522.4 522.6 522.9 523.2 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.2 522.9 522.6 523.3 523.3 523.5 523.9 524.8 526.3 529.0 533.6 539.5 548.4 560.5 577.8 598.5 620.8 646.5 675.9 700.1 720.9 741.4 755.4 765.4 773.0 778.1 781.1 782.6 783.5 783.9 784.0 784.5 784.7 784.3 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.1 784.5 784.9 784.1 784.0 783.7 783.1 782.0 780.0 775.7 770.5 762.0 748.5 731.9 712.5 688.4 660.8 635.5 611.2 586.0 569.0 555.3 543.8 535.9 531.0 527.6 525.2 524.2 523.7 523.3 523.3 522.9 522.7 523.0 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.2 522.9 522.9 522.7 522.2 521.7 521.1 520.5 519.8 519.3 519.0 519.0 519.2 519.7 520.5 521.5 522.7 524.5 526.0 528.0 530.9 534.3 538.4 543.6 549.7 555.5 561.5 568.0 572.4 575.9 578.8 580.8 581.9 582.6 582.6 582.6 582.3 582.0 581.9 582.3 582.7 583.1 583.8 584.6 585.2 585.8 586.4 586.8 587.1 587.4 587.7 588.0 588.0 588.3 588.6 588.7 588.7 588.3 587.3 585.1 582.6 578.1 572.6 564.6 555.5 546.3 536.3 525.5 517.2 510.1 503.7 499.4 496.5 494.5 493.3 492.7 492.5 492.7 492.7 492.7 492.7 492.7 492.6 492.5 492.9 493.6 494.8 497.3 501.0 505.6 511.5 519.2 529.1 538.6 548.3 558.7 567.1 573.7 579.4 583.6 586.0 587.7 588.7 588.7 588.7 588.5 588.2 588.0 587.9 587.6 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.0 586.7 586.9 587.0 587.0 587.0 587.2 588.0 589.4 592.4 597.0 603.3 612.5 625.1 639.3 655.8 678.6 698.1 716.6 735.3 750.3 761.4 770.3 777.1 780.8 782.7 784.0 784.4 784.4 784.4 784.5 784.8 784.4 784.1 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.0 784.4 784.7 784.7 784.4 784.4 784.4 784.4 783.1 781.2 777.8 771.8 763.2 752.8 739.1 720.2 702.1 682.4 663.3 643.9 627.9 615.7 605.9 598.0 593.1 590.3 588.3 587.3 587.0 587.0 587.0 586.9 586.7 587.0 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.4 587.7 588.0 588.0 588.3 588.8 589.2 589.4 589.3 588.8 587.6 585.6 582.8 578.7 573.1 566.7 559.9 552.7 544.8 538.6 533.7 528.8 525.8 523.7 522.3 521.6 521.4 521.4 521.7 522.2 522.5 522.6 522.8 523.0 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.5 523.7 524.0 524.3 524.6 525.2 525.7 525.9 526.2 525.9 525.2 524.2 522.4 519.7 516.9 513.5 509.2 505.4 501.9 498.6 495.9 493.9 492.5 491.6 491.1 491.2 491.5 491.9 492.4 492.8 493.1 493.3 493.6 493.8 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 493.9 494.2 494.5 494.7 494.9 495.4 495.9 496.3 496.5 496.6 496.2 495.5 493.9 491.9 489.5 486.4 482.6 479.1 475.7 471.9 469.4 467.2 465.5 464.4 463.8 463.5 463.8 464.0 464.5 465.0 465.3 465.5 465.7 465.9 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.3 466.5 466.8 467.1 467.5 468.0 468.5 469.1 469.7 470.0 470.2 470.1 469.7 469.2 468.5 467.6 466.7 465.7 464.7 463.9 463.2 462.7 462.2 462.1 462.3 462.7 463.2 463.9 464.4 464.8 465.3 465.5 465.8 466.0 466.2 466.2 466.2 466.4 466.7 466.9 467.3 467.8 468.3 468.9 469.5 469.9 470.2 470.2 469.9 469.4 468.7 468.0 467.0 466.0 465.1 464.2 463.4 462.9 462.4 462.1 462.2 462.5 462.9 463.6 464.2 464.6 465.1 465.5 465.7 465.9 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.3 466.5 466.7 467.0 467.4 467.9 468.4 469.0 469.6 470.0 470.2 470.2 469.7 469.2 468.6 467.7 466.7 465.8 464.9 463.9 463.2 462.8 462.3 462.1 462.3 462.6 463.1 463.8 464.3 464.7 465.2 465.5 465.8 466.0 466.2 466.2 466.2 466.4 466.7 466.9 467.3 467.8 468.2 468.8 469.5 469.9 470.2 470.2 469.9 469.4 468.9 468.1 467.1 466.2 465.3 464.2 463.5 462.9 462.5 462.1 462.2 462.4 462.9 463.6 464.1 464.6 465.1 465.4 465.7 465.9 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.3 466.5 466.7 466.7 466.9 467.2 467.2 467.2 467.0 466.1 464.4 462.4 458.9 454.5 448.1 440.9 433.6 425.7 417.1 410.5 404.8 399.8 396.4 394.0 392.4 391.5 391.1 391.1 391.1 391.3 391.5 391.5 391.7 391.8 392.0 392.0 392.0 392.2 392.4 392.3 392.2 392.2 392.2 392.1 391.5 390.6 388.6 385.6 381.6 375.9 368.3 360.1 351.0 339.3 329.8 321.3 313.1 306.8 302.4 298.9 296.3 294.9 294.1 293.7 293.5 293.5 293.5 293.5 293.4 293.5 293.6 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.7 293.6 293.5 293.3 293.5 293.5 293.5 293.5 293.7 294.2 295.1 296.6 299.0 303.0 307.8 313.9 322.0 331.7 341.2 351.0 362.0 369.9 376.4 382.2 386.3 388.9 390.6 391.7 392.2 392.2 392.2 392.2 392.3 392.4 392.2 392.2 392.0 392.2 392.2 392.4 392.4 392.5 392.8 393.2 393.4 393.4 393.2 392.7 391.5 389.7 387.4 384.2 380.0 375.6 370.9 366.3 361.5 357.5 354.4 351.9 350.0 348.8 348.3 348.1 348.0 348.1 348.4 348.7 348.8 348.8 349.0 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.2 349.0 348.9 348.8 348.7 348.4 348.2 348.0 348.1 348.2 348.7 350.0 351.6 353.9 356.8 360.5 365.4 370.0 374.7 379.8 383.6 386.8 389.5 391.4 392.6 393.1 393.4 393.4 393.2 392.9 392.6 392.4 392.4 392.2 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 392.0 391.7 391.5 391.5 391.4 391.2 391.1 391.1 391.2 392.0 393.1 394.8 398.1 402.1 407.1 413.7 421.4 429.0 436.7 445.1 451.4 456.3 460.7 463.6 465.4 466.6 467.2 467.2 467.2 467.0 466.8 466.7 466.6 466.4 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.2 466.0 465.8 465.6 465.6 465.3 464.8 464.6 464.6 464.7 465.2 466.4 468.4 470.9 474.6 479.8 485.4 491.4 498.4 504.8 510.2 514.9 519.2 521.7 523.5 524.6 525.0 525.1 525.0 524.6 524.1 523.9 523.9 523.6 523.4 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.3 523.2 522.9 522.7 522.4 522.1 521.7 521.2 520.7 520.5 520.2 520.8 521.6 522.9 525.2 528.0 531.1 534.9 539.4 543.3 546.9 550.5 553.1 555.0 556.3 557.1 557.5 557.3 557.0 556.4 555.9 555.5 555.2 554.9 554.6 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.4 554.0 553.8 553.5 553.2 552.8 552.2 551.7 551.4 551.2 551.7 552.6 554.0 556.1 558.8 562.0 566.5 570.6 574.7 579.3 582.7 585.5 587.8 589.4 590.2 590.7 590.4 590.1 589.6 589.0 588.5 588.2 587.9 587.6 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.3 587.1 587.0 586.9 586.4 585.9 585.3 584.6 583.8 583.2 582.7 582.4 582.4 582.7 583.0 583.6 584.5 585.1 585.7 586.3 586.8 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0 587.0",
        "input_type": "phoneme",
        "offset": 72.491
    }
    res = preprocess(inp)
    print(res)
    print([float(i) for i in res[0]])

def cross_fade(a: np.ndarray, b: np.ndarray, idx: int):
    result = np.zeros(idx + b.shape[0])
    fade_len = a.shape[0] - idx
    np.copyto(dst=result[:idx], src=a[:idx])
    k = np.linspace(0, 1.0, num=fade_len, endpoint=True)
    result[idx: a.shape[0]] = (1 - k) * a[idx:] + k * b[: fade_len]
    np.copyto(dst=result[a.shape[0]:], src=b[fade_len:])
    return result





#
# midis = [librosa.note_to_midi(x.split("/")[0]) if x != 'rest' else 0
#                      for x in note_lst]