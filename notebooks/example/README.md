# Example Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LAION-AI/Open-Assistant/blob/main/notebooks/example/example.ipynb)

This folder contains an example reference notebook structure and approach for
this project. Please try and follow this structure as closely as possible. While
things will not exactly be the same for each notebook some principles we would
like to try ensure are:

1. Each notebook or collection of related or dependent notebooks should live in
   its own folder.
1. Each notebook should have a markdown file with the same name as the notebook
   (or README.md if it's a single notebook folder) that explains what the
   notebook does and how to use it.
1. Add an "Open in Colab" badge to the top of the notebook (see the markdown
   cell near the top of `example.ipynb` as an example you can adapt).
1. Make it as easy as possible for someone to run the notebook in Google Colab
   or some other environment based on standard practices like providing a
   `requirements.txt` file or anything else needed to successfully run the
   notebook.

## Running in Google Colab

At the top of the [example notebook](example.ipynb) there is a code cell that
will (once uncommented):

1. clone the repository into your colab instance.
1. `cd` into the relevant notebook directory.
1. run `pip install -r requirements.txt` to install the required packages.

At this point you can run the notebook as normal and the folder structure will
match that of the repository and the colab notebook will be running from the
same directory that the notebook lives in so relative links etc should work as
expected (for example `example.ipynb` will read some sample data from
`data/data.csv`).

If you are adding a notebook please try and add a similar cell to the top of the
notebook so that it is easy for others to run the notebook in colab. If your
notebook does not have any dependencies beyond what already comes as standard in
Google Colab then you do not need such a cell, just an "Open in Colab" badge
will suffice.

## example.ipynb

This notebook contains an example "Open In Colab" badge and a code cell to
prepare the colab environment to run the notebook. It also contains a code cell
that will read in some sample data from the `data` folder in the repository and
display it as a pandas dataframe.
