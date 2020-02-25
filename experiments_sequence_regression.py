from dataframe_sequence import DataFrameSequence
from metrics import Metrics
from models_ts import regression_model
import threading
import sys


start = 6
end = 19
prediction_horizons = list(range(1, 21))


def Reg_experiment_thread(prediction_horizon, minutes_sequence, cams,img):
    print('start reg: ' + str(prediction_horizon))
    data = DataFrameSequence(False,prediction_horizon, True, img)
    data.build_ts_df(start,end,[7,8,9,10,11,12],minutes_sequence, cams)
    data.normalize_mega_df()
    name_time = '_sequence_' + str(minutes_sequence)
    name_cam = 'CAM_' + str(cams)
    name_img = '_img_' + str(img)
    name_pred = 'predhor_' + str(prediction_horizon)
    reg = regression_model.Regression_predictor(data, 'REG SEQUENCE PREM_' + name_time + name_cam + name_img + name_pred)
    reg.run_experiment()
    print('Finish reg: ' + str(prediction_horizon))

def REG_test():
    data = DataFrameSequence(False, 20, True, True)
    data.build_ts_df(7, 11, [8,9], 5, 1)
    reg = regression_model.Regression_predictor(data, 'REG SEQUENCE TEST')
    reg.data.normalize_mega_df()
    reg.data.split_data_set(9, 11)
    # reg.data.flatten_data_set()
    data.flatten_data_set_to_3d()

    data.train_x_df = data.train_x_df.reshape(data.train_x_df.shape[0], data.train_x_df.shape[1] * data.train_x_df.shape[2])
    data.test_x_df = data.test_x_df.reshape(data.test_x_df.shape[0], data.test_x_df.shape[1] * data.test_x_df.shape[2])
    data.val_x_df= data.val_x_df.reshape(data.val_x_df.shape[0], data.val_x_df.shape[1] * data.val_x_df.shape[2])

    reg.train()
    y_pred, rmse, mae, mape = reg.predict()
    print(rmse)
    print(y_pred)
    # Metrics.write_results_SVR('SVR SEQ TEST', data.test_x_df.reshape(
    #     (data.test_x_df.shape[0], data.sequence_len_minutes, data.number_of_features)), data.test_y_df, y_pred, data.pred_horizon)

def run_reg_multi_thread(minutes_sequence, cams):
    for i in prediction_horizons:
        x = threading.Thread(target=Reg_experiment_thread, args=(i,minutes_sequence,cams))
        x.start()

# def optimize():
#     data = DataFrameSequence(False, 20, True, False)
#     data.build_ts_df(6, 18, [7,8,9,10,11,12], 60, 1)
#     data.normalize_mega_df()
#     data.split_data_set(12, 1)
#     data.flatten_data_set()
#     svr = regression_model.SVM_predictor(data, 'SVR optimze')
#     svr.optimize()


# data = DataFrameSequence(False, 20, True, False)
# data.build_ts_df(10, 14, [8,9], 1, 1)
# data.normalize_mega_df(ctn = [6,7,8], metoer_to_normalize= [9,10,13])
# data.split_data_set(9, 15)
# data.flatten_data_set_to_3d()

# data.train_x_df = data.train_x_df.reshape(data.train_x_df.shape[0], data.train_x_df.shape[1] * data.train_x_df.shape[2])
# data.test_x_df = data.test_x_df.reshape(data.test_x_df.shape[0], data.test_x_df.shape[1] * data.test_x_df.shape[2])
# data.val_x_df= data.val_x_df.reshape(data.val_x_df.shape[0], data.val_x_df.shape[1] * data.val_x_df.shape[2])

# minutes_sequence = int(sys.argv[1])
# cams = int(sys.argv[2])
# img = int(sys.argv[3])
#
# if img == 1:
#     img = True
# else:
#     img = False
#
# print('Minutes sequence: ' + str(minutes_sequence))
# print('cams: ' + str(cams))
# print('IMG: ' + str(img))

REG_test()