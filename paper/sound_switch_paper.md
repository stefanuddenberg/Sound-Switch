---
jupyter:
  hide_input: false
  jupytext:
    metadata_filter:
      cells:
        additional: all
      notebook:
        additional: all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.6.7
  toc:
    base_numbering: 1
    nav_menu: {}
    number_sections: true
    sideBar: true
    skip_h1_title: false
    title_cell: Table of Contents
    title_sidebar: Contents
    toc_cell: false
    toc_position: {}
    toc_section_display: block
    toc_window_display: false
  toc-autonumbering: false
  varInspector:
    cols:
      lenName: 16
      lenType: 16
      lenVar: 40
    kernels_config:
      python:
        delete_cmd_postfix: ''
        delete_cmd_prefix: 'del '
        library: var_list.py
        varRefreshCmd: print(var_dic_list())
      r:
        delete_cmd_postfix: ') '
        delete_cmd_prefix: rm(
        library: var_list.r
        varRefreshCmd: 'cat(var_dic_list()) '
    types_to_exclude:
    - module
    - function
    - builtin_function_or_method
    - instance
    - _Feature
    window_display: false
---

# Sound Switch


# Imports

```python
%reset -f
%matplotlib inline
%config InlineBackend.figure_format = "retina" # High-res graphs (rendered irrelevant by svg option below)
%config InlineBackend.print_figure_kwargs = {"bbox_inches": "tight"} # No extra white space
%config InlineBackend.figure_format = "svg" # 'png' is default
 
import warnings
warnings.filterwarnings("ignore") # Because we are adults
from IPython.core.debugger import set_trace
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
from dfply import *

# iPyPublish imports
# from ipypublish.scripts.ipynb_latex_setup import *
# from IPython.display import SVG, display, Markdown
```

# Experiment 1


## Methods


### Stimuli
- Two types of sound stimuli: tones and guitar chords
    - Beeps alternate between pure C4 tone (261.626 Hz) and pure G tone (391.995 Hz)
    - Guitar chords alternate between a C chord and a G chord strummed on guitar, taken from [here](https://www.apronus.com/music/onlineguitar.htm), which were subsequently recorded and amplified (25.98 db and 25.065 db respectively) using Audacity version 2.3.0 (using Effect --> Amplify) via Windows 10's Stereo Mix drivers.
- 20 sounds per stimulus
- Crossfade of 50 ms between sounds
- Each stimulus was 10,000 milliseconds long, with an additional 150 ms of silence at the start of the recording.
- 9 switch rates between 0.1 and 0.9
- 10 stimuli for each switch rate, for a total of 180 stimuli, all presented as a single block. 30 frame ITI.
- 20 repeated stimuli chosen via the same random choice for each subject (presentation order was via a unique random choice for each subject, however).
- One practice beep stimulus at 0.5 switch rate presented at the start of the experiment.



## Results


### Read in data

```python
import glob, os

separator = r"\t"
data_dir = "../data"
prefix = "Sound Switch"
extension = ".txt"
search = f"{data_dir}/{prefix}*{extension}"

# Get each subject's data and concatenate into 
# one larger DataFrame
all_data = pd.DataFrame()
for file_name in glob.glob(search):
    subject_data = pd.read_csv(file_name, sep=separator)
    if all_data.shape == (0, 0):
        all_data = subject_data
    else: 
        all_data = all_data.append(subject_data)

all_data.reset_index(inplace=True, drop=True)
all_data.head()
```

### Determine stimulus type

```python
def get_stimulus_type(row):
    """
    All stimuli under 10 are guitar; the rest are tones.
    """
    return "guitar" if row["Exemplar"] < 10 else "tone"

all_data["Stimulus Type"] = all_data.apply(get_stimulus_type, axis=1)
all_data.head()
```

### Determine if trial is a repeated stimulus

```python
num_trials = 200
num_repeated_trials = 20 # at end of task
start_repeated_trial_index = num_trials - num_repeated_trials + 1

all_data["Repeat Trial"] = all_data["Trial #"] >= start_repeated_trial_index
all_data.head()
```

### Remove subjects with "None" ratings

```python
subjects_with_missing_data = all_data[all_data["Rating"] == "None"]["Subject ID"]
print(f"Bad subjects: \n {subjects_with_missing_data}")
all_data = all_data[~all_data["Subject ID"].isin(subjects_with_missing_data)]
```

### Re-convert ratings to numeric

```python
all_data["Rating"] = pd.to_numeric(all_data["Rating"])
```

### Get subject reliability

```python
subject_reliability_df = pd.DataFrame(
    index=[],
    columns=[
        "subject_id",
        "condition",        
        "correlation",
        "p-value",
        "fisher_z",
    ],
)
subject_ids = all_data["Subject ID"].unique()
for subject_id in subject_ids:
    subject_data = all_data >> mask(X["Subject ID"] == subject_id)
    subject_data.sort_values(by=["File Name"], inplace=True)
    repeated_stimuli = (
        subject_data 
        >> mask(X["Repeat Trial"] == True)
        >> select(["File Name"])
    )
    
    first_ratings_data = subject_data[
        (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
        & (subject_data["Repeat Trial"] == False)
    ]["Rating"].tolist()
    
    second_ratings_data = subject_data[
        (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
        & (subject_data["Repeat Trial"] == True)
    ]["Rating"].tolist()
    
    subject_reliability_corr = scipy.stats.pearsonr(
        first_ratings_data, second_ratings_data
    )
    
    # Needs to be in arrays for pandas
    # XXX break down by stimulus type?
    this_corr_row = {
        "subject_id": [subject_id],
        "condition": [subject_data["Condition"].iloc[0]],        
        "correlation": [subject_reliability_corr[0]],
        "p-value": [subject_reliability_corr[1]],
        "fisher_z": [np.arctanh(subject_reliability_corr[0])],
    }
    this_corr_row = pd.DataFrame.from_dict(this_corr_row)
    subject_reliability_df = subject_reliability_df.append(this_corr_row)
    
subject_reliability_df
```

### Remove unreliable subjects

```python
# Keep subjects with positive correlation
subject_reliability_df = subject_reliability_df[subject_reliability_df["correlation"] >= 0]
# Keep subjects that have defined data
subject_reliability_df = subject_reliability_df.replace(
    [np.inf, -np.inf], np.nan
).dropna()
reliable_subjects = subject_reliability_df["subject_id"].unique()
no_repeat_data = all_data[(all_data["Subject ID"].isin(reliable_subjects)) & (all_data["Repeat Trial"]==False)]
print(f"Remaining participants: {subject_reliability_df.shape[0]}")
print(f"Data without repeat trials:")
no_repeat_data.head()
```

### Group results
Keep only reliable subjects and remove repeated trials.

```python
main_results = (
    no_repeat_data
    >> group_by("Condition", "Switch Rate", "Stimulus Type")
    >> summarize(mean_ratings=X.Rating.mean(), sd_ratings=X.Rating.std())
)
main_results.head()
```

### Plot results

```python
f, ax = plt.subplots(2, 1, figsize=(8, 12), sharex=True)
sns.despine()
for i, condition in enumerate(main_results["Condition"].unique()):
    these_results = main_results >> mask(X["Condition"] == condition)
    # Convert complexity labels to more informative string labels.
    # Note that seaborn has problems with numbers as categories, 
    # and simple string conversion via `str` doesn't work.    
    sns.lineplot(
        x="Switch Rate",
        y="mean_ratings",
        hue="Stimulus Type",
        data=these_results,
        ax=ax[i],
        linewidth=4
    )
    ax[i].set_title(f"'{condition.title()}' Results")
    ax[i].set(xlabel='Switch Rate', ylabel='Mean Rating')    
plt.show()
```

# Sanity checks


## Same number of trials for all subjects?
All subjects should have exactly 200 trials.

```python
subject_ids = all_data["Subject ID"].unique()
for subject_id in subject_ids:
    subject_data = all_data >> mask(X["Subject ID"] == subject_id)
    print(subject_data.shape)
```

## All stimuli same length?
Should all be 10,100 ms long.

```python
test_sanity = False
if test_sanity:
    from pydub import AudioSegment

    stimulus_dir = "../stimuli/combined"
    prefix = "switch-"
    extension = ".mp3"
    search = f"{stimulus_dir}/{prefix}*{extension}"

    song_durations = []
    for song_name in glob.glob(search):
        song = AudioSegment.from_mp3(song_name)
        song_durations.append(len(song))

    print(set(song_durations))
```

# Exploration


## RT

```python
sns.set_style("ticks")
sns.distplot(all_data["RT"])
sns.despine()
```

# Scrap

```python
# Remove subjects with "None" rating data
all_data = all_data.replace(to_replace="None", value=np.nan).dropna()
```

```python
# subject_reliability_df = pd.DataFrame(
#     index=[],
#     columns=[
#         "subject_id",
#         "condition",        
#         "correlation",
#         "p-value",
#         "fisher_z",
#     ],
# )
# subject_ids = all_data["Subject ID"].unique()
# for subject_id in subject_ids:
#     subject_data = all_data >> mask(X["Subject ID"] == subject_id)
#     subject_data.sort_values(by=["File Name"], inplace=True)
#     repeated_stimuli = (
#         subject_data 
#         >> mask(X["Repeat Trial"] == True)
#         >> select(["File Name"])
#     )
    
#     first_ratings_data = subject_data[
#         (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
#         & (subject_data["Repeat Trial"] == False)
#     ]["Rating"].tolist()
    
#     second_ratings_data = subject_data[
#         (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
#         & (subject_data["Repeat Trial"] == True)
#     ]["Rating"].tolist()
    
#     # Correct for subjects where one or more repeat trials had to be discarded
#     if len(first_ratings_data) != len(second_ratings_data):
#         first_ratings_stimuli = subject_data[
#             (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
#             & (subject_data["Repeat Trial"] == False)
#         ]["File Name"].tolist()
        
#         second_ratings_stimuli = subject_data[
#             (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
#             & (subject_data["Repeat Trial"] == True)
#         ]["File Name"].tolist()
                
#         if len(first_ratings_stimuli) < len(second_ratings_stimuli):
#             smaller_set = set(first_ratings_stimuli)
#             larger_set = set(second_ratings_stimuli)
#         else:
#             smaller_set = set(second_ratings_stimuli)
#             larger_set = set(first_ratings_stimuli)
                    
#         missing_stimuli = larger_set.difference(smaller_set)
#         pass
    
#     subject_reliability_corr = scipy.stats.pearsonr(
#         first_ratings_data, second_ratings_data
#     )
    
#     # Needs to be in arrays for pandas
#     # XXX break down by stimulus type?
#     this_corr_row = {
#         "subject_id": [subject_id],
#         "condition": [subject_data["Condition"].iloc[0]],        
#         "correlation": [subject_reliability_corr[0]],
#         "p-value": [subject_reliability_corr[1]],
#         "fisher_z": [np.arctanh(subject_reliability_corr[0])],
#     }
#     this_corr_row = pd.DataFrame.from_dict(this_corr_row)
#     subject_reliability_df = subject_reliability_df.append(this_corr_row)
    
# subject_reliability_df
```



