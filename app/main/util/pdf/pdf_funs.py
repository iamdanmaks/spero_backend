import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy.io import wavfile
import os, codecs

from flask.ext.babel import gettext

FONT = 'DejaVu'
FONT_PATH = './app/main/util/pdf/fonts/DejaVuSansCondensed.ttf'
FONT_BOLD_PATH = './app/main/util/pdf/fonts/DejaVuSansCondensed-Bold.ttf'
MODES = ['B', '']
FONT_SIZES = [12, 14, 16]


def generate_front_page(pdf, diagnosis, name, locale):
    if diagnosis.result == 0:
        diagnosis_text = read_text('normal', locale)
    elif diagnosis.result == 1:
        diagnosis_text = read_text('murmur', locale)
    elif diagnosis.result == 2:
        diagnosis_text = read_text('extrasystole', locale)
    
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font(FONT, MODES[0], FONT_SIZES[2])
    pdf.cell(0,25,'',0,1,'C')
    
    if locale == 'en':
        pdf.cell(0,20,gettext('DIAGNOSTICS REPORT FROM ') +
            diagnosis.checked_on.strftime('%m.%d.%Y %H:%M:%S'),
            0,1,'C')
    elif locale == 'uk':
        pdf.cell(0,20,gettext('DIAGNOSTICS REPORT FROM ') +
            diagnosis.checked_on.strftime('%d.%m.%Y %H:%M:%S'),
            0,1,'C')

    pdf.set_font(FONT, '', FONT_SIZES[0])
    pdf.ln(0)
    pdf.multi_cell(0,8,diagnosis_text,0,1,'C')

    pdf = generate_results(
        pdf, 
        [
            diagnosis.normal_probability,
            diagnosis.murmur_probability,
            diagnosis.extrasystole_probability
        ],
        name
    )

    return pdf


def generate_results(pdf, probas, name):
    epw = pdf.w - 2*pdf.l_margin
    col_width = epw/3
    th = pdf.font_size

    pdf.cell(0, 10, '',0,1,'C')
    pdf.set_font(FONT, MODES[0], 14)
    pdf.cell(epw, 0, gettext('Probabilities of possible diagnostics results'), align='C')

    data = [
        [gettext('Possible result'), gettext('Probability')],
        [gettext('Normal heartbeat'), '{}%'.format(probas[0] * 100)],
        [gettext('Murmurs'), '{}%'.format(probas[1] * 100)],
        [gettext('Extrasystole'), '{}%'.format(probas[2] * 100)]
    ]

    pdf.set_font(FONT, '', FONT_SIZES[0])
    for row in data:
        pdf.cell(28)
        for datum in row:
            pdf.cell(col_width, th, str(datum), border=1)
    
        pdf.ln(th)

    pdf = generate_donut_chart(pdf, probas, name)

    return pdf


def generate_donut_chart(pdf, probas, name):
    pdf.set_font(FONT, MODES[0], FONT_SIZES[1])
    pdf.cell(0,10,'',0,1,'C')
    pdf.cell(0, 0, gettext('Diagnostics result visualization'), align='C')

    names=gettext('normal heartbeat'), gettext('murmurs'), gettext('extrasystole'),

    plt.clf()

    my_circle=plt.Circle( (0,0), 0.8, color='white')

    plt.pie(probas, labels=names, colors=['green','red','orange'])
    p=plt.gcf()
    p.gca().add_artist(my_circle)
    plt.savefig('./app/main/util/pdf/temp/{}-donut.png'.format(name),
     format='png')

    pdf.image('./app/main/util/pdf/temp/{}-donut.png'.format(name),
    h=105,w=105,x=52,y=140,type="png")
    os.remove('./app/main/util/pdf/temp/{}-donut.png'.format(name))

    return pdf


def generate_visualizations(pdf, diagnosis, wav_name, locale):
    pdf.add_page()
    pdf.set_font(FONT, MODES[0], FONT_SIZES[2])
    pdf.cell(0,25,'',0,1,'C')
    pdf.cell(0,20,gettext('Your heartbeat visualizations'),0,1,'C')

    with codecs.open(
        './app/main/util/pdf/texts/visualization.{}'.format(locale),
         'r',
         encoding='utf-8'
        ) as file:
        visualization_text = file.read()

    pdf.set_font(FONT, '', FONT_SIZES[0])
    pdf.ln(0)
    pdf.multi_cell(0,8,visualization_text,0,1,'C')

    pdf.cell(0, 10, '',0,1,'C')
    pdf.set_font(FONT, MODES[0], FONT_SIZES[1])
    pdf.cell(0, 0, gettext('Heartbeat waveform'), align='C')

    _, audio = wavfile.read('./app/main/uploads/' + wav_name + '.wav')
    audio = audio.astype(float)

    pdf = generate_waveform(pdf, audio, wav_name)
    os.remove('./app/main/util/pdf/temp/{}-waveplot.png'.format(wav_name))

    pdf = generate_spec(pdf, audio, wav_name)
    os.remove('./app/main/util/pdf/temp/{}-spec.png'.format(wav_name))

    pdf.add_page()

    pdf = generate_mel(pdf, audio, wav_name)
    os.remove('./app/main/util/pdf/temp/{}-mel.png'.format(wav_name))

    pdf = generate_chroma(pdf, audio, wav_name)
    os.remove('./app/main/util/pdf/temp/{}-chroma.png'.format(wav_name))

    return pdf


def generate_waveform(pdf, audio, wav_name):
    plt.figure(figsize=(14,5))
    librosa.display.waveplot(audio)
    plt.xlabel(gettext('Time'), fontsize=18)
    plt.savefig('./app/main/util/pdf/temp/{}-waveplot.png'.format(wav_name), 
    format='png')

    pdf.image('./app/main/util/pdf/temp/{}-waveplot.png'.format(wav_name),
    h=70,w=160,x=30,y=105,type="png")

    return pdf


def generate_spec(pdf, audio, wav_name):
    ft = librosa.stft(audio)
    ftDb = librosa.amplitude_to_db(abs(ft))
    plt.figure(figsize=(14,5))
    librosa.display.specshow(ftDb, sr=16000, x_axis='time', y_axis='log')
    plt.colorbar()
    plt.xlabel(gettext('Time'), fontsize=18)
    plt.savefig('./app/main/util/pdf/temp/{}-spec.png'.format(wav_name), 
    format='png')

    pdf.cell(0, 85, '',0,1,'C')
    pdf.cell(0, 0, gettext('Heartbeat spectrogram'), align='C')
    pdf.image('./app/main/util/pdf/temp/{}-spec.png'.format(wav_name),
    h=70,w=160,x=38,y=189,type="png")

    return pdf


def generate_mel(pdf, audio, wav_name):
    mfccs = librosa.feature.mfcc(audio, sr=16000)
    plt.figure(figsize=(14,5))
    librosa.display.specshow(mfccs, sr=16000, x_axis='time', y_axis='log')
    plt.xlabel(gettext('Time'), fontsize=18)
    plt.savefig('./app/main/util/pdf/temp/{}-mel.png'.format(wav_name), 
    format='png')

    pdf.cell(0, 25, '',0,1,'C')
    pdf.cell(0, 0, gettext('Mel-cepstral coefficients'), align='C')
    pdf.image('./app/main/util/pdf/temp/{}-mel.png'.format(wav_name),
    h=70,w=160,x=24,y=50,type="png")

    return pdf


def generate_chroma(pdf, audio, wav_name):
    hop_length = 512
    chromagram = librosa.feature.chroma_stft(audio, sr=16000, hop_length=hop_length)
    plt.figure(figsize=(15,5))
    librosa.display.specshow(chromagram, x_axis='time', y_axis='chroma', hop_length=hop_length, cmap='coolwarm')
    plt.xlabel(gettext('Time'), fontsize=18)
    plt.ylabel(gettext('Pitch class'), fontsize=18)
    plt.savefig('./app/main/util/pdf/temp/{}-chroma.png'.format(wav_name), 
    format='png')

    pdf.cell(0, 85, '',0,1,'C')
    pdf.cell(0, 0, gettext('Heartbeat chromagram'), align='C')
    pdf.image('./app/main/util/pdf/temp/{}-chroma.png'.format(wav_name),
    h=70,w=160,x=24,y=138,type="png")

    return pdf


def read_text(result, lang):
    with codecs.open(
        './app/main/util/pdf/texts/{}.{}'.format(result, lang), 
        'r',
        encoding='utf-8'
    ) as file:
        return file.read()
