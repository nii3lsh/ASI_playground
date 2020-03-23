from metrics import *
from data import data_visuals, data_helper
import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib import cm, colors

style.use('seaborn-poster') #sets the size of the charts
style.use('ggplot')

def mean(a):
    return sum(a) / len(a)

def avg_lol(lol):
    return list(map(mean, zip(*lol)))

def proces_lists_stack(lst):
    ls = lst
    for i in ls:
        for x in range(0, 19):
            i[x + 1] = i[x + 1] - i[x]
            if i[x] < 0:
                i[x] = 0

    return ls

def getColor(N, idx):
    import matplotlib as mpl
    c = 'BrBG'
    cmap = mpl.cm.get_cmap(c)
    norm = mpl.colors.Normalize(vmin=0.0, vmax=N - 1)
    return cmap(norm(idx))

def get_files_names(model):
    if model == 'ann':
        files, names = data_helper.get_files_ann_multi()
        folders, names_ = data_helper.get_folders_ann()
    elif model == 'rf':
        files, names = data_helper.get_files_rf_multi()
        folders, names_ = data_helper.get_folders_rf()
    elif model == 'lstm':
        files, names = data_helper.get_files_lstm_test()
    elif model == 'p':
        return ['p'], ['Persistence']

    return files, names

def plot_err_per_day(model, save_as=0):
    days = data_helper.get_thesis_test_days()
    files, names = get_files_names(model)
    file = files[0]
    name = names[0]

    sunny = [(9, 15), (10, 15), (11, 15), (12, 15)]
    pcloudy = [(10, 21), (11, 17), (12, 16)]
    cloudy = [(10, 22), (12, 3)]

    errors_sunny = []
    errors_pcloudy = []
    errors_cloudy = []

    for t in days:
        # merge names
        trmse, tmae, tmape = [[] for x in range(3)]
        predictions = list(range(1, 21))

        if model == 'p':
            # get persistence errors:
            rmse_persistence, mae_persistence, mape_persistence = [[] for x in range(3)]
            # get persistence
            for i in range(0, 20):
                actual, pred, _ = data_helper.get_persistence_df(t[0], t[1], 7, 17, i + 1)
                rmse, mae, mape = Metrics.get_error(actual, pred)
                rmse_persistence.append(rmse)
                mae_persistence.append(mae)
                mape_persistence.append(mape)

            if t in sunny:
                errors_sunny.append(rmse_persistence)
            elif t in pcloudy:
                errors_pcloudy.append(rmse_persistence)
            elif t in cloudy:
                errors_cloudy.append(rmse_persistence)
        else:
            tmp_rmse = []
            tmp_mae = []
            tmp_mape = []
            actual, pred, _ = data_visuals.get_all_TP_multi(file, md_split=t)

            for i in range(0, 20):
                rmse, mae, mape = Metrics.get_error(actual[i], pred[i])
                tmp_rmse.append(rmse)
                tmp_mae.append(mae)
                tmp_mape.append(mape)
            if t in sunny:
                errors_sunny.append(tmp_rmse)
            elif t in pcloudy:
                errors_pcloudy.append(tmp_rmse)
            elif t in cloudy:
                errors_cloudy.append(tmp_rmse)

    labels = ['Sunny', 'Par. cloudy', 'Cloudy']
    y_pos = np.arange(len(labels))
    r = list(range(0, len(labels)))

    # average weather
    errors_sunny = avg_lol(errors_sunny)
    errors_pcloudy = avg_lol(errors_pcloudy)
    errors_cloudy = avg_lol(errors_cloudy)

    errors = [errors_sunny] + [errors_pcloudy] + [errors_cloudy]
    # process for bar
    proces_lists_stack(errors)

    plt.bar(r, [item[0] for item in errors], color=getColor(20, 0), edgecolor='white', width=1, label='PH 1')
    for i in range(1, 20):
        plt.bar(r, [item[i] for item in errors], bottom=[item[i - 1] for item in errors], color=getColor(20, i),
                edgecolor='white', width=1, label='PH ' + str(i + 1))

    # Custom X axis
    plt.xticks(r, labels, fontweight='bold')
    plt.xlabel("Weather circumstances")
    plt.legend()

    plt.ylim(0, 100)
    plt.ylabel('Error RMSE')
    plt.title('Average error per weather circumstance for '+ str(name))
    plt.show()

def plot_all_days(model):
    days = data_helper.get_thesis_test_days()
    files, names = get_files_names(model)
    file = files[0]
    name = names[0]


    for t in days:
        # merge names
        trmse, tmae, tmape = [[] for x in range(3)]
        predictions = list(range(1, 21))

        if model == 'p':
            # get persistence errors:
            rmse_persistence, mae_persistence, mape_persistence = [[] for x in range(3)]
            # get persistence
            for i in range(0, 20):
                actual, pred, _ = data_helper.get_persistence_df(t[0], t[1], 7, 17, i + 1)
                rmse, mae, mape = Metrics.get_error(actual, pred)
                rmse_persistence.append(rmse)
                mae_persistence.append(mae)
                mape_persistence.append(mape)

        else:
            tmp_rmse = []
            tmp_mae = []
            tmp_mape = []
            actual, pred, _ = data_visuals.get_all_TP_multi(file, md_split=t)

            for i in range(0, 20):
                rmse, mae, mape = Metrics.get_error(actual[i], pred[i])
                tmp_rmse.append(rmse)
                tmp_mae.append(mae)
                tmp_mape.append(mape)




            # process for bar
            tmp_rmse = proces_lists_stack(tmp_rmse)
            plt.bar(r, [item[0] for item in tmp_rmse], color=getColor(20, 0), edgecolor='white', width=1, label='PH 1')
            for i in range(1, 20):
                plt.bar(r, [item[i] for item in tmp_rmse], bottom=[item[i - 1] for item in tmp_rmse], color=getColor(20, i),
                        edgecolor='white', width=1, label='PH ' + str(i + 1))

            labels = ['model']
            y_pos = np.arange(len(labels))
            r = list(range(0, len(labels)))
            # Custom X axis
            plt.xticks(r, labels, fontweight='bold')
            plt.xlabel("Weather circumstances")
            plt.legend()

            plt.ylim(0, 100)
            plt.ylabel('Error RMSE')
            plt.title('Average error per weather circumstance for '+ str(name))
            plt.show()


def plot_err_hor_test(model, max_models=7, save=0):
    t = data_helper.get_thesis_test_days()
    files, names = get_files_names(model)

    # merge names
    trmse = []
    tmae = []
    tmape = []
    predictions = list(range(1, 21))

    # get persistence errors:
    rmse_persistence = []
    mae_persistence = []
    mape_persistence = []

    for i in range(0, 20):
        actual, pred, _ = data_helper.get_persistence_dates(t, 6, 19, i + 1)
        rmse, mae, mape = Metrics.get_error(actual, pred)
        rmse_persistence.append(rmse)
        mae_persistence.append(mae)
        mape_persistence.append(mape)

    for file in files:  # get multi model data
        tmp_rmse = []
        tmp_mae = []
        tmp_mape = []
        actual, pred, _ = data_visuals.get_all_TP_multi(file)

        for i in range(0, 20):
            rmse, mae, mape = Metrics.get_error(actual[i], pred[i])
            tmp_rmse.append(rmse)
            tmp_mae.append(mae)
            tmp_mape.append(mape)

        trmse.append(tmp_rmse)
        tmae.append(tmp_mae)
        tmape.append(tmp_mape)

    id = 0
    for i in range(0, len(trmse), max_models):
        if save == 0:
            save_as = ['none', 'none', 'none']
        else:
            name_rmse = 'final_plots_val/' + model + '_prem_rmse_' + str(id) + '.jpg'
            name_mae = 'final_plots_val/' + model + '_prem_mae_' + str(id) + '.jpg'
            name_mape = 'final_plots_val/' + model + '_prem_mape_' + str(id) + '.jpg'
            save_as = [name_rmse, name_mae, name_mape]

        data_visuals.plot_error_per_horizons([rmse_persistence] + trmse[i:i + max_models], predictions,
                                ['Persistence'] + names[i:i + max_models],
                                'RMSE per prediction horizon', 'Prediction Horizon in minutes', 'Error in RMSE',
                                save_as[0])

        data_visuals.plot_error_per_horizons([mae_persistence] + tmae[i:i + max_models], predictions,
                                ['Persistence'] + names[i:i + max_models],
                                'MAE per prediction horizon', 'Prediction Horizon in minutes', 'Error in MAE',
                                save_as[1])

        data_visuals.plot_error_per_horizons([mape_persistence] + tmape[i:i + max_models], predictions,
                                ['Persistence'] + names[i:i + max_models],
                                'MAPE per prediction horizon', 'Prediction Horizon in minutes', 'Error in MAPE',
                                save_as[2])
        id = id + 1

model = 'lstm'
days = data_helper.get_thesis_test_days()
files, names = get_files_names(model)
file = files[0]
name = names[0]


for t in days:
    # merge names
    trmse, tmae, tmape = [[] for x in range(3)]
    predictions = list(range(1, 21))

    if model == 'p':
        # get persistence errors:
        rmse_persistence, mae_persistence, mape_persistence = [[] for x in range(3)]
        # get persistence
        for i in range(0, 20):
            actual, pred, _ = data_helper.get_persistence_df(t[0], t[1], 7, 17, i + 1)
            rmse, mae, mape = Metrics.get_error(actual, pred)
            rmse_persistence.append(rmse)
            mae_persistence.append(mae)
            mape_persistence.append(mape)

    else:
        tmp_rmse = []
        tmp_mae = []
        tmp_mape = []
        actual, pred, _ = data_visuals.get_all_TP_multi(file, md_split=t)

        for i in range(0, 20):
            rmse, mae, mape = Metrics.get_error(actual[i], pred[i])
            tmp_rmse.append(rmse)
            tmp_mae.append(mae)
            tmp_mape.append(mape)

        labels = ['model']
        y_pos = np.arange(len(labels))
        r = list(range(0, len(labels)))

        # process for bar
        tmp_rmse = proces_lists_stack([tmp_rmse])
        plt.bar(r, [item[0] for item in tmp_rmse], color=getColor(20, 0), edgecolor='white', width=1, label='PH 1')
        for i in range(1, 20):
            plt.bar(r, [item[i] for item in tmp_rmse], bottom=[item[i - 1] for item in tmp_rmse], color=getColor(20, i),
                    edgecolor='white', width=1, label='PH ' + str(i + 1))


        # Custom X axis
        plt.xticks(r, labels, fontweight='bold')
        plt.xlabel("Weather circumstances")
        plt.legend()

        plt.ylim(0, 200)
        plt.ylabel('Error RMSE')
        plt.title(str(t))
        plt.show()