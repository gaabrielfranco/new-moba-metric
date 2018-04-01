from modules.data import read_data
import json
from scipy.spatial.distance import euclidean
from numpy.random import randint
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    kmeans, kmeans_corr, kmeans_pruned = read_data('k-means_experiments')
    show_plots = False
    '''f = open('files/output_cluster_evaluation/cluster_eval.txt', 'w')
    for experiment in kmeans:
        if experiment.split('_')[0] == 'all' or experiment.split('_')[0] == 'kda':
            f.writelines("================ " +
                         experiment + " ================\n")
            for centroid in kmeans[experiment]['centroids']:
                f.writelines(str(centroid) + '\n')
            f.writelines('\n')
    f.close()

    f = open('files/output_cluster_evaluation/cluster_eval_corr.txt', 'w')
    for experiment in kmeans_corr:
        f.writelines("================ " +
                     experiment + " ================\n")
        for centroid in kmeans_corr[experiment]['centroids']:
            f.writelines(str(centroid) + '\n')
        f.writelines('\n')
    f.close()

    f = open('files/output_cluster_evaluation/cluster_eval_pruned.txt', 'w')
    for experiment in kmeans_pruned:
        if experiment.split('_')[0] == 'all' or experiment.split('_')[0] == 'kda':
            f.writelines("================ " +
                         experiment + " ================\n")
            for centroid in kmeans_pruned[experiment]['centroids']:
                f.writelines(str(centroid) + '\n')
            f.writelines('\n')
    f.close()

    distance = {}
    for experiment in kmeans:
        distance[experiment] = []
        for k, cluster in enumerate(kmeans[experiment]['clusters']):
            dist = 10000000
            player_dist = []
            for player in cluster:
                euc_dist = euclidean(
                    kmeans[experiment]['centroids'][k], player)
                if euc_dist < dist:
                    dist = euc_dist
                    player_dist = player
            distance[experiment].append(
                {"distance": dist, "player": player_dist})

    distance_corr = {}
    for experiment in kmeans_corr:
        distance_corr[experiment] = []
        for k, cluster in enumerate(kmeans_corr[experiment]['clusters']):
            dist = 10000000
            player_dist = []
            for player in cluster:
                euc_dist = euclidean(
                    kmeans_corr[experiment]['centroids'][k], player)
                if euc_dist < dist:
                    dist = euc_dist
                    player_dist = player
            distance_corr[experiment].append(
                {"distance": dist, "player": player_dist})

    distance_pruned = {}
    for experiment in kmeans_pruned:
        distance_pruned[experiment] = []
        for k, cluster in enumerate(kmeans_pruned[experiment]['clusters']):
            dist = 10000000
            player_dist = []
            for player in cluster:
                euc_dist = euclidean(
                    kmeans_pruned[experiment]['centroids'][k], player)
                if euc_dist < dist:
                    dist = euc_dist
                    player_dist = player
            distance_pruned[experiment].append(
                {"distance": dist, "player": player_dist})

    f = open('files/output_cluster_evaluation/distance_eval.txt', 'w')
    for experiment in distance:
        f.writelines("===================== " +
                     experiment + " =====================\n")
        for i in range(len(distance[experiment])):
            f.writelines("\tCluster " + str(i+1) + ":\n")
            f.writelines(
                "\t\tDistance = " + str(distance[experiment][i]['distance']) + '\n')
            f.writelines("\t\tPlayer = " +
                         str(distance[experiment][i]['player']) + '\n')
            f.writelines("\t\tCentroid = " +
                         str(kmeans[experiment]['centroids'][i]) + '\n')
            f.writelines("\n")
    f.close()

    f = open('files/output_cluster_evaluation/distance_eval_corr.txt', 'w')
    for experiment in distance_corr:
        f.writelines("===================== " +
                     experiment + " =====================\n")
        for i in range(len(distance_corr[experiment])):
            f.writelines("\tCluster " + str(i+1) + ":\n")
            f.writelines(
                "\t\tDistance = " + str(distance_corr[experiment][i]['distance']) + '\n')
            f.writelines("\t\tPlayer = " +
                         str(distance_corr[experiment][i]['player']) + '\n')
            f.writelines("\t\tCentroid = " +
                         str(kmeans_corr[experiment]['centroids'][i]) + '\n')
            f.writelines("\n")
    f.close()

    f = open('files/output_cluster_evaluation/distance_eval_pruned.txt', 'w')
    for experiment in distance_pruned:
        f.writelines("===================== " +
                     experiment + " =====================\n")
        for i in range(len(distance_pruned[experiment])):
            f.writelines("\tCluster " + str(i+1) + ":\n")
            f.writelines(
                "\t\tDistance = " + str(distance_pruned[experiment][i]['distance']) + '\n')
            f.writelines("\t\tPlayer = " +
                         str(distance_pruned[experiment][i]['player']) + '\n')
            f.writelines("\t\tCentroid = " +
                         str(kmeans_pruned[experiment]['centroids'][i]) + '\n')
        f.writelines("\n")
    f.close()'''

    plt.rcParams["figure.figsize"] = (25, 16)
    plt.rcParams['font.size'] = 18.0

    columns_kda = ['kills', 'deaths', 'assists', 'dist to centroid']
    columns_all = ['kills', 'deaths', 'assists', 'denies',
                   'gpm', 'hero_damage', 'hero_healing', 'LH', 'xp_p_min', 'dist to centroid']
    index_df = ['centroid', 'player 1', 'player 2', 'player 3', 'player 4',
                'player 5', 'player 6', 'player 7', 'player 8', 'player 9', 'player 10']

    for experiment in kmeans_pruned:
        if experiment.split('_')[0] == 'all' or experiment.split('_')[0] == 'kda':
            for i, cluster in enumerate(kmeans_pruned[experiment]['clusters']):
                random_players = randint(len(cluster), size=10)
                centroid = kmeans_pruned[experiment]['centroids'][i]
                centroid.append(0.0)
                player_matrix = []
                player_matrix.append(centroid)
                for player in random_players:
                    player_i = kmeans_pruned[experiment]['clusters'][i][player]
                    player_i.append(
                        euclidean(kmeans_pruned[experiment]['centroids'][i], player))
                    player_matrix.append(player_i)

                if experiment.split('_')[0] == 'all':
                    df = pd.DataFrame(player_matrix, index=index_df,
                                      columns=columns_all)
                else:
                    df = pd.DataFrame(player_matrix, index=index_df,
                                      columns=columns_kda)
                ax = sns.heatmap(df, annot=True, fmt=".3f")
                ax.set_title('Experiment ' + experiment +
                             ' - Cluster ' + str(i+1))
                plt.xticks(rotation=30)
                plt.yticks(rotation=0)
                file_name = 'files/output_cluster_evaluation/plots/' + \
                    experiment + '_C' + str(i+1)
                plt.savefig(file_name)
                print('Graph %s saved.' % file_name)
                if show_plots:
                    plt.show()
                plt.clf()


if __name__ == "__main__":
    main()
