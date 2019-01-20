import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter('ignore')

import pickle
import json
import tensorflow as tf
from ._utils._utils import check_file, load_graph
from ._models._sklearn_model import DEPENDENCY
from ._models._tensorflow_model import DEPENDENCY as TF_DEPENDENCY
from ._utils._parse_dependency import DependencyGraph
from ._utils._paths import PATH_DEPEND, S3_PATH_DEPEND


def dependency_graph(tagging, indexing):
    result = []
    for i in range(len(tagging)):
        result.append(
            '%d\t%s\t_\t_\t_\t_\t%d\t%s\t_\t_'
            % (i + 1, tagging[i][0], int(indexing[i][1]), tagging[i][1])
        )
    return DependencyGraph('\n'.join(result), top_relation_label = 'root')


def available_deep_model():
    """
    List available deep learning dependency models, ['concat', 'bahdanau', 'luong']
    """
    return ['concat', 'bahdanau', 'luong']


def crf():
    """
    Load CRF dependency model.

    Returns
    -------
    DEPENDENCY : malaya._models._sklearn_model.DEPENDENCY class
    """
    check_file(PATH_DEPEND['crf'], S3_PATH_DEPEND['crf'])
    try:
        with open(PATH_DEPEND['crf']['model'], 'rb') as fopen:
            model = pickle.load(fopen)
        with open(PATH_DEPEND['crf']['depend'], 'rb') as fopen:
            depend = pickle.load(fopen)
    except:
        raise Exception(
            "model corrupted due to some reasons, please run malaya.clear_cache('dependency/crf') and try again"
        )
    return DEPENDENCY(model, depend)


def deep_model(model = 'bahdanau'):
    """
    Load deep learning dependency model.

    Parameters
    ----------
    model : str, optional (default='bahdanau')
        Model architecture supported. Allowed values:

        * ``'concat'`` - Concating character and word embedded for BiLSTM
        * ``'bahdanau'`` - Concating character and word embedded including Bahdanau Attention for BiLSTM
        * ``'luong'`` - Concating character and word embedded including Luong Attention for BiLSTM

    Returns
    -------
    DEPENDENCY: malaya._models._tensorflow_model.DEPENDENCY class
    """
    assert isinstance(model, str), 'model must be a string'
    model = model.lower()
    if model in ['concat', 'bahdanau', 'luong']:
        check_file(PATH_DEPEND[model], S3_PATH_DEPEND[model])
        try:
            with open(PATH_DEPEND[model]['setting'], 'r') as fopen:
                nodes = json.loads(fopen.read())
            g = load_graph(PATH_DEPEND[model]['model'])
        except:
            raise Exception(
                "model corrupted due to some reasons, please run malaya.clear_cache('dependency/%s') and try again"
                % (model)
            )
        return TF_DEPENDENCY(
            g.get_tensor_by_name('import/Placeholder:0'),
            g.get_tensor_by_name('import/Placeholder_1:0'),
            g.get_tensor_by_name('import/logits:0'),
            g.get_tensor_by_name('import/logits_depends:0'),
            nodes,
            tf.InteractiveSession(graph = g),
            model,
            g.get_tensor_by_name('import/transitions:0'),
            g.get_tensor_by_name('import/depends/transitions:0'),
            g.get_tensor_by_name('import/Variable:0'),
        )

    else:
        raise Exception(
            'model not supported, please check supported models from malaya.dependency.available_deep_model()'
        )
