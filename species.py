
from numpy import array
from sklearn.cluster import MeanShift
from sklearn.metrics import pairwise_distances_argmin
from distinctipy import get_colors

BANDWIDTH = 20

class Species():
    """
    A cluster-analysis of the current `World`'s organisms.

    The clustering algorithm used is "mean shift" which automatically determines the number of clusters
    and can use the previous clusters as the initial `seeds` to search for the next set of clusters.

    The `BANDWIDTH` constant is used to determine how large of a space to consider for a cluster.
    If there are too many clusters, increase the bandwidth and vice-versa.
    This parameter is sensitive to the number of traits and the gene size.

    `self.seeds` is a list of the centers of the current clusters, where the `i`th seed .
    `self.labels` is a list of integers where the `i`th organism belongs to the cluster `self.labels[i]` centered at `self.seeds[i]`.
    `self.labels_colors` is a dictionary from `self.labels` to that cluster's color.
    """
    def __init__(self, organisms):
        self.seeds = None
        self.labels_colors = {}
        self.cluster(organisms)

    def cluster(self, organisms):
        """
        Use `self.seeds` to specify the initial centers of clusters and determine a new set of clusters.

        The first time calling this method will generate a color for each cluster such that each color is as distinct as possible.
        Otherwise, the previous colors will be reused. If there are more clusters than previously,
        new colors will be associated with those clusters.
        """
        mean_shift = MeanShift(seeds = self.seeds, bandwidth = BANDWIDTH).fit(array(
            [[organism.genome.genotype[key] for key in organism.genome.genotype] for organism in organisms]))
        self.labels, seeds = mean_shift.labels_, mean_shift.cluster_centers_
        self.organisms_labels = {organism: label for organism, label in zip(organisms, self.labels)}

        if self.labels_colors:
            if len(self.seeds) < len(seeds):
                self.labels_colors = {j: self.labels_colors[i] for i, j in enumerate(pairwise_distances_argmin(self.seeds, seeds))}
                seeds = [seed for seed in range(len(seeds)) if seed not in self.labels_colors]
                for seed, color in zip(seeds, get_colors(len(seeds)), self.labels_colors.values()):
                    self.labels_colors[seed] = color
            else:
                self.labels_colors = {i: self.labels_colors[j] for i, j in enumerate(pairwise_distances_argmin(seeds, self.seeds))}
        else:
            self.labels_colors = {seed: color for seed, color in enumerate(get_colors(len(seeds)))}

        self.seeds = seeds
