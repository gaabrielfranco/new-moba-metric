import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
import numbers
from statsmodels.distributions.empirical_distribution import ECDF


def main():
    df = pd.read_csv("create_database/df_database.csv", index_col=0)

    # Plot params
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    matplotlib.style.use('ggplot')

    # Normalize data
    df = (df - df.min()) / (df.max() - df.min())

    # K-means
    clusterer = KMeans(n_clusters=10, n_jobs=-1)
    cluster_labels = clusterer.fit_predict(df)

    # Cluster distribution
    count = [0] * 10

    count = (np.array([(cluster_labels == i).sum()
                       for i in range(0, 10)]) / len(df.index)) * 100
    fig = plt.figure(figsize=(6, 4))
    plt.rc('font', size=7)
    plt.ylabel("Percentage")
    plt.xlabel("Clusters")
    plt.xticks(range(1, 11))
    plt.bar(list(range(1, 11)), count)
    plt.tight_layout()
    file_name = "img/cluster_dist.png"
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
    print('Graph %s saved.' % file_name)

    # Centroids starplot

    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    matplotlib.style.use('ggplot')

    df_centroids = pd.DataFrame(clusterer.cluster_centers_, columns=df.columns)

    label = ["Centroid " + str(i) for i in range(1, 11)]

    candidates = list(df_centroids.columns)
    dimensions = []
    for i, c in enumerate(candidates):
        if isinstance(df_centroids.loc[0, c], numbers.Number):
            dimensions.append(candidates[i])

    dimensions = np.array(dimensions)
    angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(10, 7))
    plt.rc('font', size=7)
    ax = fig.add_subplot(111, polar=True)
    colors_vec = ["#e6194b", "#3cb44b", "#ffe119", "#0082c8",
                  "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#fabebe", "#008080"]
    pallete = sns.color_palette(colors_vec)
    for index, i in enumerate(df_centroids.index):
        values = df_centroids[dimensions].loc[i].values
        values = np.concatenate((values, [values[0]]))
        ax.plot(angles, values, 'o-', linewidth=2,
                label=label[i], color=pallete[index])
        ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids(angles * 180/np.pi, dimensions)
    ax.grid(True)
    plt.tight_layout()
    plt.legend(loc="center right", bbox_to_anchor=(1.32, 0.5),
               title="Centroid")
    file_name = "img/cluster_starplot.png"
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
    plt.clf()
    print('Graph %s saved.' % file_name)

    # Silhouette score analysis

    n_clusters = 10

    fig, ax1 = plt.subplots(1, 1)
    fig.set_size_inches(6, 4)
    plt.rc('font', size=7)

    ax1.set_xlim([-0.1, 1])
    ax1.set_ylim([0, len(df) + (n_clusters + 1) * 10])

    silhouette_avg = silhouette_score(df, cluster_labels)
    print("For n_clusters =", n_clusters,
          "The average silhouette_score is :", silhouette_avg)

    sample_silhouette_values = silhouette_samples(df, cluster_labels)

    y_lower = 10
    for i in range(n_clusters):
        ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]

        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = (sns.color_palette("husl", 10))
        ax1.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color[i], edgecolor=color[i], alpha=0.7)

        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

        y_lower = y_upper + 10

    ax1.set_title("The silhouette plot for the various clusters.")
    ax1.set_xlabel("The silhouette coefficient values")
    ax1.set_ylabel("Cluster label")

    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    ax1.set_yticks([])
    ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    plt.tight_layout()
    file_name = "img/silhouette_score.png"
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
    print('Graph %s saved.' % file_name)
    plt.clf()

    # Create data with cluster result
    df.insert(loc=len(df.columns), column="cluster", value=cluster_labels)
    df.to_csv("create_database/df_database_clusters.csv")

    # ECDF KDA
    fig = plt.figure(figsize=(5.55, 4.7))
    plt.rc('font', size=7)
    colors_vec = ["#e6194b", "#3cb44b", "#ffe119", "#0082c8",
                  "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#fabebe", "#008080"]

    pallete = sns.color_palette(colors_vec)

    for cluster in range(0, 10):
        data_cluster = df[df.cluster == cluster]
        ecdf = ECDF(data_cluster["kills"] +
                    data_cluster["assists"] / (1 + data_cluster["deaths"]))
        plt.plot(ecdf.x, ecdf.y, label="Cluster " +
                 str(cluster + 1), color=pallete[cluster])
    plt.legend()
    plt.tight_layout()
    file_name = "img/kda_ecdf.png"
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
    plt.clf()
    print('Graph %s saved.' % file_name)


if __name__ == "__main__":
    main()