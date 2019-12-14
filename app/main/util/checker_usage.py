import tensorflow as tf
import keras
from keras.models import load_model


def define_checker_model():
    def auc(y_true, y_pred):
        auc = tf.metrics.auc(y_true, y_pred)[1]
        keras.backend.get_session().run(tf.local_variables_initializer())
        return auc

    global graph
    graph = tf.get_default_graph()
    model = load_model('./app/main/util/checker/checker.h5', custom_objects={'auc': auc})

    return tuple([model, graph])
