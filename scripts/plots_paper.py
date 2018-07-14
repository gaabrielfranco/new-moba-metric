from modules.data import read_data, normalizes
import matplotlib
import matplotlib.pyplot as plt
import argparse
import json
import pandas as pd
from modules.plots import radarplot, radarplot_top_k, plot_silhouette_analysis
from statsmodels.distributions.empirical_distribution import ECDF
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def main():
    parser = argparse.ArgumentParser(
        description='Plots for paper', prog="plots_paper.py")
    parser.add_argument('--all', '-a', action='store_true',
                        help='plot all figures (defaut = False)')
    parser.add_argument('--fig1', '-f1', action='store_true',
                        help='plot fig1 - inértia x k (defaut = False)')
    parser.add_argument('--fig2', '-f2', action='store_true',
                        help='plot fig2 - players distribution per cluster (defaut = False)')
    parser.add_argument('--fig3', '-f3', action='store_true',
                        help='plot fig3 - starplot of attributes distribution (defaut = False)')
    parser.add_argument('--fig4', '-f4', action='store_true',
                        help='plot fig4 - silhouette score per cluster (defaut = False)')
    parser.add_argument('--fig5', '-f5', action='store_true',
                        help='plot fig5 - all metrics CDFs (defaut = False)')
    parser.add_argument('--fig6', '-f6', action='store_true',
                        help='plot fig6 - all top 10 starplots (defaut = False)')
    parser.add_argument('--fig7', '-f7', action='store_true',
                        help='plot fig7 - starplots players comparison (defaut = False)')
    parser.add_argument('--show', '-s', action='store_true',
                        help='show plots (defaut = False)')
    args = parser.parse_args()

    plots_path = "files/plots_paper/"
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42
    # matplotlib.use('Agg')
    matplotlib.style.use('ggplot')

    if args.fig1 or args.all:
        file_name = plots_path + "inertia_x_k.pdf"
        with open("files/output_k-analysis/output_k_analysis.json") as file:
            data = json.load(file)

        fig = plt.figure(figsize=(3.55, 2))
        plt.rc('font', size=7)
        plt.ylabel("Inertia")
        plt.xlabel("Number of clusters")
        plt.xticks(list(range(0, 101, 10)))

        plt.plot(data["all"]["n_clusters"], data["all"]["inertia"])
        plt.xlim((0, 100))
        plt.tight_layout()
        plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
        print('Graph %s saved.' % file_name)
        if args.show:
            plt.show()
        plt.clf()

    if args.fig2 or args.all:
        file_name = plots_path + "players_distribution_per_cluster.pdf"
        data = read_data("df_w_metrics_all")

        clusters = data["cluster"].values
        num_occur = [0] * (max(clusters) + 1)

        for i in clusters:
            num_occur[i] += 1

        labels = []

        for i in num_occur:
            labels.append((i / len(clusters)) * 100)

        fig = plt.figure(figsize=(3.55, 2))
        plt.rc('font', size=7)
        plt.ylabel("Percentage")
        plt.xlabel("Clusters")
        plt.xticks(range(1, max(clusters) + 2))

        plt.bar(range(1, max(clusters) + 2), labels)
        plt.tight_layout()
        plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
        print('Graph %s saved.' % file_name)
        if args.show:
            plt.show()
        plt.clf()

    if args.fig3 or args.all:
        file_name = plots_path + "radar_plot_all_10.pdf"

        _, _, data = read_data('k-means_experiments')

        for i in data:
            if i == "all_10":
                data_norm = normalizes(data[i]['centroids'])[0]
                columns = ['kills', 'deaths', 'assists',
                           'denies', 'gpm', 'hd', 'hh', 'lh', 'xpm']
                df = pd.DataFrame(data_norm, columns=columns)
                label = ['Centroid ' + str(x + 1)
                         for x in range(len(data_norm))]
                radarplot(df, file_name, label=label,
                          show_plots=args.show)

    if args.fig4 or args.all:
        file_name = plots_path + "silhouette_score_all_10.pdf"

        data = read_data("df_data_pruned")

        for column in data:
            data[column] = (data[column] - data[column].min()) / \
                (data[column].max() - data[column].min())

        km = KMeans(n_clusters=10, n_jobs=-1)
        labels = km.fit_predict(data)

        sil_score = silhouette_score(
            data, labels, metric="euclidean")
        plot_silhouette_analysis(
            data, None, 10, labels, sil_score, file_name, args.show)

    if args.fig5 or args.all:
        data = read_data("df_w_metrics_all")

        for metric in ["kda", "adg", "g", "x"]:
            fig = plt.figure(figsize=(3.55, 2.7))
            plt.rc('font', size=7)
            colors_vec = ["#e6194b", "#3cb44b", "#ffe119", "#0082c8",
                          "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#fabebe", "#008080"]

            pallete = sns.color_palette(colors_vec)
            for cluster in range(0, 10):
                data_cluster = data[data.cluster == cluster]
                ecdf = ECDF(data_cluster[metric])
                plt.plot(ecdf.x, ecdf.y, label="Cluster " +
                         str(cluster + 1), color=pallete[cluster])
            plt.legend()
            plt.ylabel("CDF")
            plt.xlabel(metric.upper() + " values")
            plt.tight_layout()
            file_name = plots_path + metric + "_ecdf.pdf"
            plt.savefig(file_name, bbox_inches='tight', pad_inches=0.01)
            if args.show:
                plt.show()
            plt.clf()
            print('Graph %s saved.' % file_name)

    if args.fig6 or args.all:
        data = read_data("df_w_metrics_all")

        top_10_kda = data.sort_values(by=['kda'], ascending=False)[:10]
        top_10_adg = data.sort_values(by=['adg'], ascending=False)[:10]
        top_10_g = data.sort_values(by=['g'], ascending=False)[:10]
        top_10_x = data.sort_values(by=['x'], ascending=False)[:10]

        exclude_list = ['kda', 'adg', 'g', 'x', 'cluster']

        radarplot_top_k(top_10_kda, plots_path +
                        'radar_plot_top_10_kda.pdf', exclude_list, show_plots=args.show)

        radarplot_top_k(top_10_adg, plots_path +
                        'radar_plot_top_10_adg.pdf', exclude_list, show_plots=args.show)

        radarplot_top_k(top_10_g, plots_path +
                        'radar_plot_top_10_g.pdf', exclude_list, show_plots=args.show)

        radarplot_top_k(top_10_x, plots_path +
                        'radar_plot_top_10_x.pdf', exclude_list, show_plots=args.show)

    if args.fig7 or args.all:
        data = read_data("df_w_metrics_all")
        file_name = plots_path + "starplot_players_comparison.pdf"

        top_kda = data.sort_values(by=['kda'], ascending=False)[:1]
        top_adg = data.sort_values(by=['adg'], ascending=False)[:4]

        top_adg = top_adg.loc[7795:, :]

        top_kda = top_kda.append(top_adg)

        print(top_kda)

        label = ["Player 1", "Player 2"]
        exclude_list = ['kda', 'adg', 'g', 'x', 'cluster']

        radarplot_top_k(top_kda, file_name, exclude_list,
                        show_plots=args.show, label=label)


if __name__ == "__main__":
    main()