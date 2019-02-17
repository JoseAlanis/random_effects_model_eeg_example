# --- jose c. garcia alanis
# --- utf-8
# --- Python 3.6.2
#
# --- LIMO data set - create custom epochs structure
# --- feb 2019
#
# --- get data info from LIMO structures in the LIMO data set
# --- create new custom epochs structure for LIMO epochs

# import packages
import numpy as np
import scipy.io
import mne

# path
path_to_files = '/Volumes/INTENSO/'
# subject
sub = 'S3'

# -- 1) import .mat files
data_info = scipy.io.loadmat(path_to_files + sub + '/LIMO.mat')
data = scipy.io.loadmat(path_to_files + sub + '/Yr.mat')

# -- 2) get channel labels from LIMO structure
labels = data_info['LIMO']['data'][0][0][0][0]['chanlocs']['labels']

# extract them and set channel type
chans_found = []
types = []
for i in range(labels.shape[1]):
    chans_found.append(labels[:, i][0][0])
    if labels[:, i][0][0] in {'EXG1', 'EXG2', 'EXG3', 'EXG4'}:
        types.append('eog')
    else:
        types.append('eeg')

# data is stored as channels x time points x epochs
# data['Yr'].shape  # <-- see here
# transpose to epochs x channels time points
obs_data = np.transpose(data['Yr'], (2, 0, 1))

# -- 3) get epochs information from structure
# sampling rate
sfreq = data_info['LIMO']['data'][0][0][0][0]['sampling_rate'][0][0]
# tmin and tmax
tmin = data_info['LIMO']['data'][0][0][0][0]['start'][0][0]
tmax = data_info['LIMO']['data'][0][0][0][0]['end'][0][0]
# number of epochs per condition
epo_x_cond = data_info['LIMO']['design'][0][0][0][0]['nb_items'][0].tolist()

# -- 4) Create custom info for mne epochs structure
# create info
info = mne.create_info(
    ch_names=chans_found,
    ch_types=types,
    sfreq=sfreq)
# events matrix
events = []
for i in range(sum(epo_x_cond)):
    if i <= epo_x_cond[0]:
        events.append([i, 0, 0])
    else:
        events.append([i, 0, 1])
# to array
events = np.array(events)
# event ids
event_id = dict(cond_1=0, cond_2=1)

# -- 5) Create custom epochs array
limo_epochs = mne.EpochsArray(obs_data, info, events, tmin, event_id)

# check results
print(limo_epochs)
limo_epochs['cond_1'].average().plot(time_unit='s')
