# ---
# jupyter:
#   hide_input: false
#   jupytext:
#     cell_metadata_filter: all
#     metadata_filter:
#       cells:
#         additional: all
#       notebook:
#         additional: all
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.7.2
#   toc:
#     base_numbering: 1
#     nav_menu: {}
#     number_sections: true
#     sideBar: true
#     skip_h1_title: false
#     title_cell: Table of Contents
#     title_sidebar: Contents
#     toc_cell: false
#     toc_position: {}
#     toc_section_display: block
#     toc_window_display: false
#   toc-autonumbering: false
#   varInspector:
#     cols:
#       lenName: 16
#       lenType: 16
#       lenVar: 40
#     kernels_config:
#       python:
#         delete_cmd_postfix: ''
#         delete_cmd_prefix: 'del '
#         library: var_list.py
#         varRefreshCmd: print(var_dic_list())
#       r:
#         delete_cmd_postfix: ') '
#         delete_cmd_prefix: rm(
#         library: var_list.r
#         varRefreshCmd: 'cat(var_dic_list()) '
#     types_to_exclude:
#     - module
#     - function
#     - builtin_function_or_method
#     - instance
#     - _Feature
#     window_display: false
# ---

# %% [markdown]
# # Sound Switch

# %% [markdown]
# # TODOs
# - Include musical background in analyses; clean up data to allow for continuous analysis. Dichotomous analysis shows no visible difference.
# - Time course analysis; do beauty ratings go down over the course of the experiment? -- Yes, they do seem to be slightly numerically lower across halves, but the pattern persists. Haven't done stats on this.
# - Are the repeated stimuli liked more than the first time they were shown? Yes, very slightly (only 1.83 points), and only for beauty condition
# - Do their RTs go down? Yes, they are quicker for repeated stimuli.
# - Color vs. sound pitted against each other. So it's a cross-modal experiment. Both shapes and sounds are perfectly correlated (but randomly assigned to one another, so white goes with beep for half the participants, boop for the other half). How do beauty ratings look? More like color or sound? 
#     - Decide at a later date which stimuli to use. We don't want the auditory stimuli to be much more beautiful than the visual stimuli, for example. Then they might dominate for no good reason.
# - Note the asymmetry in pattern judgments; lower switch rate less patterned than high switch rate; why?

# %% [markdown]
# # Imports

# %%
# %reset -f
# %matplotlib inline
# %config InlineBackend.figure_format = "retina" # High-res graphs (rendered irrelevant by svg option below)
# %config InlineBackend.print_figure_kwargs = {"bbox_inches": "tight"} # No extra white space
# %config InlineBackend.figure_format = "svg" # 'png' is default
 
import warnings
warnings.filterwarnings("ignore") # Because we are adults
from IPython.core.debugger import set_trace
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import seaborn as sns
from dfply import *
from IPython.display import SVG, display, Markdown

# iPyPublish imports
# from ipypublish.scripts.ipynb_latex_setup import *


# %% [markdown]
# # Experiment 1

# %% [markdown]
# ## Methods

# %% [markdown]
# ### Stimuli
# - Two types of sound stimuli: tones and guitar chords
#     - Beeps alternate between pure C4 tone (261.626 Hz) and pure G tone (391.995 Hz)
#     - Guitar chords alternate between a C chord and a G chord strummed on guitar, taken from [here](https://www.apronus.com/music/onlineguitar.htm), which were subsequently recorded and amplified (25.98 db and 25.065 db respectively) using Audacity version 2.3.0 (using Effect --> Amplify) via Windows 10's Stereo Mix drivers.
# - 20 sounds per stimulus
# - Crossfade of 50 ms between sounds
# - Each stimulus was 10,000 milliseconds long, with an additional 150 ms of silence at the start of the recording.
# - 9 switch rates between 0.1 and 0.9
# - 10 stimuli for each switch rate, for a total of 180 stimuli, all presented as a single block. 30 frame ITI.
# - 20 repeated stimuli chosen via the same random choice for each subject (presentation order was via a unique random choice for each subject, however).
# - One practice beep stimulus at 0.5 switch rate presented at the start of the experiment.
#

# %% [markdown]
# ## Results

# %% [markdown]
# ### Read in data

# %%
import glob, os

separator = r"\t"
data_dir = "../data/2019-04-18"
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

# %% [markdown]
# ### Demographics
# Race demographics are borked for the moment; will fix later.

# %%
# Load data
debriefing_file_name = f"{data_dir}/sound_switch_debriefing.xlsx"
debriefing_data = pd.read_excel(debriefing_file_name)

# %%
# Get NA subjects
na_subjects_index = debriefing_data[debriefing_data["Initials"].isna()].index
print(f"NA subjects: {na_subjects_index}")
# Remove NA subjects
debriefing_data.drop(index=na_subjects_index, axis=0, inplace=True)

debriefing_data.iloc[30:36]

# %% [markdown]
# #### Gender

# %%
debriefing_data["Gender"].value_counts()

# %% [markdown]
# #### Age

# %%
debriefing_data["Age"].describe().round(2)

# %% [markdown]
# ### Preprocessing

# %% [markdown]
# #### Determine stimulus type

# %%
def get_stimulus_type(row):
    """
    All stimuli under 10 are guitar; the rest are tones.
    """
    return "guitar" if row["Exemplar"] < 10 else "tone"

all_data["Stimulus Type"] = all_data.apply(get_stimulus_type, axis=1)
all_data.head()

# %% [markdown]
# #### Determine if trial is a repeated stimulus

# %%
num_trials = 200
num_repeated_trials = 20 # at end of task
start_repeated_trial_index = num_trials - num_repeated_trials + 1

all_data["Repeat Trial"] = all_data["Trial #"] >= start_repeated_trial_index
all_data.head()

# %% [markdown]
# #### Remove subjects with "None" ratings

# %%
subjects_with_missing_data = all_data[all_data["Rating"] == "None"]["Subject ID"]
print(f"Bad subjects: \n {subjects_with_missing_data}")
all_data = all_data[~all_data["Subject ID"].isin(subjects_with_missing_data)]

# %% [markdown]
# #### Re-convert ratings to numeric

# %%
all_data["Rating"] = pd.to_numeric(all_data["Rating"])

# %% [markdown]
# #### Get subject reliability

# %%
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
    
subject_reliability_df.round(3)

# %% [markdown]
# #### Remove unreliable subjects

# %%
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

# %% [markdown]
# #### Group results
# Keep only reliable subjects and remove repeated trials.

# %%
main_results = (
    no_repeat_data
    >> group_by("Condition", "Switch Rate", "Stimulus Type")
    >> summarize(mean_ratings=X.Rating.mean(), sd_ratings=X.Rating.std())
)
main_results.head().round(3)

# %% [markdown]
# ### Plot results

# %%
results_for_plot = (
    no_repeat_data
    >> group_by("Condition", "Switch Rate", "Stimulus Type")
)

# %%
def plot_results(data):
    f, ax = plt.subplots(2, 1, figsize=(8, 12), sharex=True)
    sns.despine()
    for i, condition in enumerate(data["Condition"].unique()):
        these_results = data >> mask(X["Condition"] == condition)
        # Convert complexity labels to more informative string labels.
        # Note that seaborn has problems with numbers as categories, 
        # and simple string conversion via `str` doesn't work.    
        sns.lineplot(
            x="Switch Rate",
            y="Rating",
            hue="Stimulus Type",
            data=these_results,
            ax=ax[i],
            linewidth=4,
            ci=95
        )
        ax[i].set_title(f"'{condition.title()}' Results")
        ax[i].set(xlabel='Switch Rate', ylabel='Mean Rating')    
    plt.show()

plot_results(results_for_plot)

# %% [markdown]
# ### Statistical tests

# %% [markdown]
# #### Mixed measures ANOVA.

# %%
# %load_ext rpy2.ipython

# %%
# Convert data to R format
from rpy2.robjects import pandas2ri

R_data = no_repeat_data >> select(
    X["Subject ID"],
    X["Condition"],
    X["Stimulus Type"],
    X["Switch Rate"],
    X["Rating"],
)
R_data = pandas2ri.py2ri(R_data)
R_data.head()

# %% {"magic_args": "-i R_data -o anova_model,anova_model_summary,ref_poly,poly_contrasts", "language": "R"}
# library(afex)
# library(lsmeans)
# # afex_options(emmeans_model = "multivariate")
# # afex_options("emmeans_mode")
# # model = afex_options("emmeans_model")
#
# # Convert to numeric, due to pandas converting everything to strings
# R_data <- transform(R_data, Subject.ID = as.numeric(Subject.ID))
# R_data <- transform(R_data, Rating = as.numeric(Rating))
# R_data <- transform(R_data, Switch.Rate = as.numeric(Switch.Rate))
# anova_model <- aov_ez(
#     "Subject.ID",
#     "Rating",
#     R_data,
#     between=c("Condition"),
#     within=c("Switch.Rate", "Stimulus.Type"),
#     type=3, # type of sum squares to use; default is 3,
#     anova_table=list(es = "pes") # partial eta-squared; default is ges (generalized)
# )
# anova_model_summary <- summary(anova_model)
# anova_model_names <- names(summary(anova_model))
# ref_poly <- lsmeans(anova_model, specs = c("Switch.Rate"))
# poly_contrasts <- contrast(ref_poly,method="poly")

# %%
print(anova_model)

# %% [markdown]
# To reproduce our smallest observed effect size at 80% power, we'd need a sample size of 18 (per question condition) according to GPower. XXX Need to check via other means as well. XXX

# %%
print(poly_contrasts)

# %% [markdown]
# XXX Contrasts are not interpretable right now, since it collapses across both condition and stimulus type. Will need to separate those out.

# %% [markdown]
# #### Mixed linear model

# %%
# # %%R -i R_data -o linear_model
# library(afex)
# # Convert to numeric, due to pandas converting everything to strings
# R_data <- transform(R_data, Subject.ID = as.numeric(Subject.ID))
# R_data <- transform(R_data, Rating = as.numeric(Rating))
# R_data <- transform(R_data, Switch.Rate = as.numeric(Switch.Rate))
# linear_model <- mixed(Rating~Condition*Switch.Rate*Stimulus.Type+(Switch.Rate|Subject.ID)+(Stimulus.Type|Subject.ID),data=R_data)

# %%
# print(linear_model)

# %%
subject_ids = no_repeat_data["Subject ID"].unique()
sum(subject_ids % 2 == 0)

# %%
subject_ids

# %% [markdown]
# # Sanity checks

# %% [markdown]
# ## Same number of trials for all subjects?
# All subjects should have exactly 200 trials.

# %%
subject_ids = all_data["Subject ID"].unique()
for subject_id in subject_ids:
    subject_data = all_data >> mask(X["Subject ID"] == subject_id)
    print(subject_data.shape)

# %% [markdown]
# ## All stimuli same length?
# Should all be 10,100 ms long.

# %%
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

# %% [markdown]
# # Exploration

# %% [markdown]
# ## Effect of musical experience on ratings

# %%
music_experience = ["Yes.", "No."]
for experience in music_experience:
    these_participants = (
        debriefing_data
        >> mask(X["Any Musical Background or Experience?"] == experience)
        >> select(["Sub #"])
    )
    
    these_data = (
        no_repeat_data
        >> group_by("Condition", "Switch Rate", "Stimulus Type")
        >> mask(X["Subject ID"].isin(these_participants["Sub #"].unique()))
    )
    
    display(Markdown(f"#### Music Experience: {experience}"))
    plot_results(these_data)

# %% [markdown]
# ## Timecourse analysis
# Do ratings change over the course of the experiment?

# %%
num_trials = max(no_repeat_data["Trial #"])

first_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] <= num_trials/2)    
)

second_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] > num_trials/2)    
)

dfs = [first_half_trials_data, second_half_trials_data]

for i, df in enumerate(dfs):
    half_for_plot = (
        df
        >> group_by("Condition", "Switch Rate", "Stimulus Type")
    )
    display(Markdown(f"#### Half: {i+1}"))
    plot_results(half_for_plot)

# %% [markdown]
# ### Looking at first 50 vs. second 50 trials

# %%
first_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] <= 50)    
)

second_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] > 50)
    >> mask(X["Trial #"] <= 100)
)

dfs = [first_half_trials_data, second_half_trials_data]

for i, df in enumerate(dfs):
    half_for_plot = (
        df
        >> group_by("Condition", "Switch Rate", "Stimulus Type")
    )
    display(Markdown(f"#### Half: {i+1}"))
    plot_results(half_for_plot)

# %% [markdown]
# ### How about RTs?
# Doesn't look like it makes a big difference.

# %%
num_trials = max(no_repeat_data["Trial #"])

first_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] <= num_trials/2)    
)

second_half_trials_data = (
    no_repeat_data
    >> mask(X["Trial #"] > num_trials/2)    
)

dfs = [first_half_trials_data, second_half_trials_data]

for i, df in enumerate(dfs):
    half_for_RTs = (
        df
        >> group_by("Condition", "Switch Rate", "Stimulus Type")
    )
    display(Markdown(f"#### Half: {i+1}, mean RT: {half_for_RTs['RT'].mean().round(3)}"))

# %% [markdown]
# ## Are repeated stimuli liked more the first time they are shown?

# %%
template_df = pd.DataFrame(
    index=[],
    columns=[
        "subject_id",
        "condition",
        "first_ratings",
        "second_ratings",
        "differences",
        "first_RTs",
        "second_RTs",
        "RT_differences",
    ],
)

repeated_differences_df = template_df.copy(deep=True)

subject_ids = all_data["Subject ID"].unique()
for subject_id in subject_ids:
    subject_df = template_df.copy(deep=True)
    subject_data = all_data >> mask(X["Subject ID"] == subject_id)
    subject_data.sort_values(by=["File Name"], inplace=True)
    repeated_stimuli = (
        subject_data >> mask(X["Repeat Trial"] == True) >> select(["File Name"])
    )

    subject_df["first_ratings"] = np.array(
        subject_data[
            (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
            & (subject_data["Repeat Trial"] == False)
        ]["Rating"].tolist()
    )

    subject_df["second_ratings"] = np.array(
        subject_data[
            (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
            & (subject_data["Repeat Trial"] == True)
        ]["Rating"].tolist()
    )

    subject_df["first_RTs"] = np.array(
        subject_data[
            (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
            & (subject_data["Repeat Trial"] == False)
        ]["RT"].tolist()
    )

    subject_df["second_RTs"] = np.array(
        subject_data[
            (subject_data["File Name"].isin(repeated_stimuli["File Name"]))
            & (subject_data["Repeat Trial"] == True)
        ]["RT"].tolist()
    )

    subject_df["differences"] = (
        subject_df["second_ratings"] - subject_df["first_ratings"]
    )
    subject_df["RT_differences"] = (
        subject_df["second_RTs"] - subject_df["first_RTs"]
    )
    subject_df["subject_id"] = subject_id
    subject_df["condition"] = subject_data["Condition"].iloc[0]

    repeated_differences_df = repeated_differences_df.append(subject_df)

# Convert to numeric type, since it's all objects for some reason
cols = [
    "first_ratings",
    "second_ratings",
    "differences",
    "first_RTs",
    "second_RTs",
    "RT_differences",
]
repeated_differences_df[cols] = repeated_differences_df[cols].apply(
    pd.to_numeric
)
repeated_differences_df.head()

# %%
ax = sns.scatterplot(
    x="first_ratings",
    y="second_ratings",
    hue="condition",
    data=repeated_differences_df,
)

# %%
from scipy import stats

conditions = ["beautiful", "patterned"]
for condition in conditions:        
    condition_data = (
        repeated_differences_df
        >> mask(X.condition == condition)        
    )
    t, p = stats.ttest_1samp(condition_data["differences"],0)
    md = condition_data["differences"].mean().round(3)
    print(f"{condition}: t:{round(t, 3)}, p:{round(p, 4)}, mean diff: {md}")


# %%
ax = sns.regplot(
    x="first_ratings",
    y="second_ratings",        
    data=repeated_differences_df[repeated_differences_df["condition"] == "beautiful"]
)

# %% [markdown]
# ### Are repeated stimuli responded to faster?
# Yes, by up to 0.62 s in the beauty condition, and 0.53 s in the pattern condition. (Negative values mean the second RT is smaller, i.e. faster.)

# %%
conditions = ["beautiful", "patterned"]
for condition in conditions:        
    condition_data = (
        repeated_differences_df
        >> mask(X.condition == condition)        
    )
    t, p = stats.ttest_1samp(condition_data["RT_differences"],0)
    md = condition_data["RT_differences"].mean().round(3)
    print(f"{condition}: t:{round(t, 3)}, p:{round(p, 4)}, mean diff: {md}")

# %%


# %%


# %%


# %% [markdown]
# ## RT

# %%
sns.set_style("ticks")
sns.distplot(all_data["RT"])
sns.despine()

# %%
no_repeat_data["RT"].describe()

# %%
no_repeat_data[no_repeat_data["RT"] > 18].head()

# %%
sns.distplot(no_repeat_data["RT"])
sns.despine()

# %% [markdown]
# # Scrap

# %%
fmri = sns.load_dataset("fmri")
fmri.head()

# %%
# Remove subjects with "None" rating data
# all_data = all_data.replace(to_replace="None", value=np.nan).dropna()

# %% {"lines_to_next_cell": 0}
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
# %% [markdown]
#
#
#
