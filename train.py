import os.path
import matplotlib.pyplot as plt
import numpy as np
from HSIDataset import HSIDataset
from model import SSResNet
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.callbacks import ModelCheckpoint

DATA_NAME = ['IN', 'KSC', 'UP']
RUN = 10
EPOCHS = 200
BATCHSZ = 16
LR = [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5]
NUM_FILTERS = list(range(8, 33, 8))
PATCHSZ = [5, 7, 9, 11]

def main(run, data_name, patchsz, lr, num_filters, is_bn, is_dropout):
    HSI = HSIDataset(data_name, patchsz, run)
    x_train = HSI.x_train
    y_train = HSI.y_train
    x_val = HSI.x_val
    y_val = HSI.y_val
    nc = np.max(y_train) + 1
    model = SSResNet(nc=nc, filters=num_filters, is_bn=is_bn, is_dropout=is_dropout)
    rms_prop = RMSprop(learning_rate=lr)
    model.compile(optimizer=rms_prop, loss=SparseCategoricalCrossentropy(from_logits=False),
                  metrics=['sparse_categorical_accuracy'])
    model_path = './model_ckp/{}/{}/patchsz-{}-lr-{}-num_filters-{}-is_bn-{}-is_dropout-{}'.format(
        run, data_name, patchsz, lr, num_filters, is_bn, is_dropout)
    if os.path.exists(model_path + '.index'):
        print('*'*5, 'loading saved model', '*'*5)
        model.load_weights(model_path)
    checkpointer = ModelCheckpoint(filepath=model_path, verbose=1, save_best_only=True)
    history = model.fit(x_train, y_train,
                        batch_size=BATCHSZ,
                        epochs=EPOCHS,
                        verbose=1,
                        validation_data=(x_val, y_val),
                        callbacks=[checkpointer],
                        shuffle=True)
    model.summary()
    acc = history.history['sparse_categorical_accuracy']
    val_acc = history.history['val_sparse_categorical_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Training Accuracy')
    plt.plot(val_acc, label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.show()

# first test SSRN in different LR condition
for name in DATA_NAME:
    for lr in LR:
        for run in range(RUN):
            main(run=run, data_name=name, patchsz=7, lr=lr, num_filters=24, is_bn=True, is_dropout=True)

# test SSRN with different num filters
for name in DATA_NAME:
    for n in NUM_FILTERS:
        for run in range(RUN):
            main(run=run, data_name=name, patchsz=7, lr=3e-4, num_filters=n, is_bn=True, is_dropout=True)

# test SSRN with and without BN and dropout
for name in DATA_NAME:
    for run in range(RUN):
        main(run=run, data_name=name, patchsz=7, lr=3e-4, num_filters=24, is_bn=True, is_dropout=True)

for name in DATA_NAME:
    for run in range(RUN):
        main(run=run, data_name=name, patchsz=7, lr=3e-4, num_filters=24, is_bn=True, is_dropout=False)

for name in DATA_NAME:
    for run in range(RUN):
        main(run=run, data_name=name, patchsz=7, lr=3e-4, num_filters=24, is_bn=False, is_dropout=True)

for name in DATA_NAME:
    for run in range(RUN):
        main(run=run, data_name=name, patchsz=7, lr=3e-4, num_filters=24, is_bn=False, is_dropout=False)

# TEST SSRN with different input patch size
for name in DATA_NAME:
    for p in PATCHSZ:
        for run in range(RUN):
            main(run=run, data_name=name, patchsz=p, lr=3e-4, num_filters=24, is_bn=True, is_dropout=True)

